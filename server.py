"""FinGenius dashboard web server (FastAPI).

Serves the pixel-perfect dashboard (web/index.html) and exposes a /api/chat
endpoint that drives the real LangGraph agent.

    uvicorn server:app --reload --port 8000
    # then open http://localhost:8000
"""

import io
import re
import secrets
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import fingenius  # noqa: F401  (imports inject truststore for TLS)
from fingenius.agent import chat as agent_chat
from fingenius.analysis import categorize_transaction
from fingenius.dashboard import dashboard_snapshot, snapshot_summary
from fingenius.privacy import redact
from fingenius.tools.transaction_tools import set_active_transactions

WEB_DIR = Path(__file__).parent / "web"

app = FastAPI(title="FinGenius Dashboard")

_COOKIE = "fg_sid"


@app.middleware("http")
async def session_cookie(request: Request, call_next):
    """Issue a strong, server-side session id in an HttpOnly cookie. The id is
    never accepted from the client, so no one can guess or set another user's
    session to reach their data."""
    sid = request.cookies.get(_COOKIE)
    fresh = sid is None
    if fresh:
        sid = secrets.token_urlsafe(32)  # ~256 bits of entropy
    request.state.sid = sid
    response = await call_next(request)
    if fresh:
        # Secure only over real HTTPS; on plain http (localhost/127.0.0.1) a
        # Secure cookie would never be sent back, breaking the session. With
        # --proxy-headers, scheme reflects the proxy's X-Forwarded-Proto in prod.
        secure = request.url.scheme == "https"
        response.set_cookie(_COOKIE, sid, httponly=True, samesite="lax",
                            secure=secure, max_age=60 * 60 * 24)
    return response


CONN_HINT = (
    "Can't reach OpenAI — your machine is blocking the connection (the API key "
    "is fine). Allow python.exe through NetLimiter/your firewall, disable "
    "antivirus HTTPS scanning, or try a phone hotspot, then ask again."
)


def _is_connection_error(exc: Exception) -> bool:
    text = f"{type(exc).__name__} {exc}".lower()
    return any(
        s in text
        for s in ("connection error", "apiconnection", "connecterror",
                  "certificate_verify", "max retries", "failed to establish",
                  "getaddrinfo")
    )


class ChatIn(BaseModel):
    message: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


# Uploaded statement (+ detected currency) per session id (absent = sample data).
# ponytail: in-memory dict, no eviction; add a TTL/LRU if it runs long with many users.
_uploaded: dict = {}
_currency: dict = {}

CURRENCY_SYMBOLS = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£",
                    "JPY": "¥", "AUD": "A$", "CAD": "C$", "SGD": "S$", "AED": "د.إ"}


def _detect_currency(raw: pd.DataFrame) -> str:
    """Find the statement currency (e.g. 'Currency : INR') in the preamble.
    Defaults to USD when absent (keeps the built-in sample data in $)."""
    text = " ".join(str(v) for v in raw.to_numpy().ravel() if pd.notna(v))
    m = re.search(r"currency\s*[:\-]?\s*([A-Za-z]{3})", text, re.IGNORECASE)
    if m and m.group(1).upper() in CURRENCY_SYMBOLS:
        return m.group(1).upper()
    return "USD"


# Real bank statements name columns many ways. Map each field to its aliases.
_ALIASES = {
    "date": ("date", "transaction date", "txn date", "tran date", "value date",
             "posting date", "trans date", "date of transaction"),
    "description": ("description", "narration", "particulars", "details",
                    "remarks", "transaction details", "payee", "transaction remarks"),
    "amount": ("amount", "amt", "transaction amount", "txn amount"),
    "debit": ("debit", "debit amount", "withdrawal", "withdrawal amt",
              "withdrawal amt.", "withdrawal amount", "dr", "paid out"),
    "credit": ("credit", "credit amount", "deposit", "deposit amt",
               "deposit amt.", "deposit amount", "cr", "paid in"),
    "category": ("category", "type"),
}


def _pick(cols: dict, field: str):
    """Return the actual column name for a field, matching known aliases."""
    for alias in _ALIASES[field]:
        if alias in cols:
            return cols[alias]
    return None


def _money(series: pd.Series) -> pd.Series:
    """Parse a money column: strip currency symbols, commas, spaces, blanks."""
    cleaned = series.astype(str).str.replace(r"[^\d.\-]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


_KNOWN_HEADERS = {a for aliases in _ALIASES.values() for a in aliases}


def _strip_preamble(raw: pd.DataFrame) -> pd.DataFrame | None:
    """Bank statements (e.g. SBI) put account-info rows above the transaction
    table. Read with header=None, then find the real header row (the one naming
    a date column plus a debit/credit/amount column) and reframe from there."""
    for i in range(min(len(raw), 40)):
        row = [str(v).lower().strip() for v in raw.iloc[i].tolist()]
        if "date" in row and any(c in row for c in
                                 ("debit", "credit", "amount", "withdrawal amt",
                                  "deposit amt", "withdrawal amt.", "deposit amt.")):
            body = raw.iloc[i + 1:].copy()
            body.columns = [str(v).strip() for v in raw.iloc[i].tolist()]
            return body.reset_index(drop=True)
    return None


def _normalize(df: pd.DataFrame) -> pd.DataFrame | None:
    """Map a real bank-statement CSV to Date/Description/Amount(/Category).

    Handles aliased column names, separate debit/credit columns, day-first
    dates, and comma-formatted amounts. Returns None if date+description plus
    some amount column are missing.
    """
    if df is None:
        return None
    cols = {c.lower().strip(): c for c in df.columns}
    date_c, desc_c = _pick(cols, "date"), _pick(cols, "description")
    amt_c = _pick(cols, "amount")
    deb_c, cred_c = _pick(cols, "debit"), _pick(cols, "credit")
    if date_c is None or desc_c is None or not (amt_c or deb_c or cred_c):
        return None

    if amt_c:
        amount = _money(df[amt_c])
    else:
        # Debit/credit split: debit -> money out (negative), credit -> in.
        debit = _money(df[deb_c]).fillna(0) if deb_c else 0
        credit = _money(df[cred_c]).fillna(0) if cred_c else 0
        amount = credit - debit

    out = pd.DataFrame({
        # dayfirst=True: most non-US banks use DD/MM/YYYY.
        "Date": pd.to_datetime(df[date_c], errors="coerce", dayfirst=True),
        "Description": df[desc_c].astype(str).str.strip(),
        "Amount": amount,
    })
    out["Merchant"] = out["Description"].map(_merchant)
    cat_c = _pick(cols, "category")
    if cat_c:
        out["Category"] = df[cat_c].astype(str)
    out = out.dropna(subset=["Date", "Amount"]).reset_index(drop=True)
    if "Category" not in out.columns:
        out["Category"] = _auto_categorize(out)
    return out


def _merchant(desc: str) -> str:
    """Pull the payee/merchant out of a raw bank narration.

    Indian UPI/IMPS strings look like
    'WDL TFR UPI/DR/651523675021/Blinkit/YESB/pa ytm-blin/...': the party name
    is the segment right after the long numeric reference. Falls back to the
    cleaned head of the description for non-UPI rows (mandates, charges, etc.).
    """
    parts = [p.strip() for p in str(desc).split("/")]
    for i, p in enumerate(parts[:-1]):
        if re.fullmatch(r"\d{6,}", p) and parts[i + 1]:
            return parts[i + 1]
    cleaned = re.sub(r"\b\d{6,}\b", "", str(desc)).strip()
    cleaned = re.sub(r"\bAT \d+ \w+$", "", cleaned).strip()
    return (cleaned or str(desc))[:40]


# Free keyword map for common Indian merchants -> category. Avoids an LLM call
# for the bulk of UPI spend; only unknown merchants fall through to the model.
_MERCHANT_KEYWORDS = {
    "blinkit": "Groceries", "zepto": "Groceries", "bigbasket": "Groceries",
    "dmart": "Groceries", "jiomart": "Groceries", "instamart": "Groceries",
    "grofers": "Groceries", "swiggy": "Dining", "zomato": "Dining",
    "domino": "Dining", "mcdonald": "Dining", "kfc": "Dining", "cafe": "Dining",
    "restaurant": "Dining", "eatclub": "Dining", "rapido": "Transportation",
    "uber": "Transportation", "ola": "Transportation", "irctc": "Transportation",
    "redbus": "Transportation", "makemytr": "Transportation",
    "goibibo": "Transportation", "ixigo": "Transportation",
    "indrive": "Transportation", "petrol": "Transportation",
    "fuel": "Transportation", "hpcl": "Transportation", "iocl": "Transportation",
    "bpcl": "Transportation", "metro": "Transportation",
    "hotstar": "Entertainment", "netflix": "Entertainment",
    "spotify": "Entertainment", "prime": "Entertainment",
    "bookmyshow": "Entertainment", "pvr": "Entertainment", "inox": "Entertainment",
    "youtube": "Entertainment", "amazon": "Shopping", "flipkart": "Shopping",
    "myntra": "Shopping", "ajio": "Shopping", "meesho": "Shopping",
    "nykaa": "Shopping", "snapdeal": "Shopping", "tatacliq": "Shopping",
    "recharge": "Utilities", "jio": "Utilities", "airtel": "Utilities",
    "vodafone": "Utilities", "electricity": "Utilities", "broadband": "Utilities",
    "cred": "Utilities", "tatapower": "Utilities", "bescom": "Utilities",
    "pharmacy": "Healthcare", "apollo": "Healthcare", "pharmeasy": "Healthcare",
    "1mg": "Healthcare", "netmeds": "Healthcare", "hospital": "Healthcare",
    "clinic": "Healthcare", "medical": "Healthcare", "udemy": "Education",
    "coursera": "Education", "byju": "Education", "unacademy": "Education",
}


def _keyword_category(merchant: str) -> str | None:
    s = merchant.lower()
    for kw, cat in _MERCHANT_KEYWORDS.items():
        if kw in s:
            return cat
    return None


def _auto_categorize(df: pd.DataFrame) -> list[str]:
    """Categorize by extracted merchant. Known Indian merchants are matched for
    free via a keyword map; unknown merchants go to the LLM (deduped, capped at
    50 to bound cost); the rest default to Income (credits) / Transfers (debits).
    """
    base = [_keyword_category(m) for m in df["Merchant"]]

    todo = sorted({m for m, c in zip(df["Merchant"], base) if c is None})
    mapping: dict[str, str] = {}
    if 0 < len(todo) <= 50:  # bound LLM calls regardless of statement size
        for m in todo:
            amt = float(df.loc[df.Merchant == m, "Amount"].iloc[0])
            try:
                mapping[m] = categorize_transaction(redact(m), amt).category
            except Exception:  # noqa: BLE001 - offline/blocked -> heuristic fallback
                pass

    out = []
    for m, amt, c in zip(df["Merchant"], df["Amount"], base):
        c = c or mapping.get(m)
        if c is None:
            c = "Income" if amt > 0 else "Transfers"
        out.append(c)
    return out


@app.get("/api/data")
def api_data(request: Request) -> dict:
    """Real KPIs / categories / budget / cash flow from this session's data."""
    sid = request.state.sid
    code = _currency.get(sid, "USD")
    out = dashboard_snapshot(_uploaded.get(sid), symbol=CURRENCY_SYMBOLS[code])
    out["currency"] = code
    return out


@app.post("/api/upload")
async def api_upload(request: Request, file: UploadFile = File(...)):
    """Upload a bank statement (CSV or Excel). Skips account-info preamble rows,
    handles Debit/Credit columns and day-first dates automatically."""
    sid = request.state.sid
    try:
        raw_bytes = await file.read()
        if len(raw_bytes) > 8_000_000:  # 8 MB cap; statements are tiny
            return JSONResponse(status_code=400, content={"error": "File too large (max 8 MB)."})
        name = (file.filename or "").lower()
        # header=None: keep every row so we can locate the real header ourselves.
        if name.endswith((".xlsx", ".xls")):
            raw = pd.read_excel(io.BytesIO(raw_bytes), header=None, dtype=str)
        else:
            # SBI/bank CSVs are often cp1252, not UTF-8. Try UTF-8, fall back.
            try:
                raw = pd.read_csv(io.BytesIO(raw_bytes), header=None, dtype=str,
                                  encoding="utf-8-sig")
            except UnicodeDecodeError:
                raw = pd.read_csv(io.BytesIO(raw_bytes), header=None, dtype=str,
                                  encoding="cp1252")
        df = _normalize(_strip_preamble(raw))
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(status_code=400, content={"error": f"Could not read file: {exc}"})
    if df is None or df.empty:
        return JSONResponse(status_code=400, content={"error": "Couldn't find a Date + Debit/Credit (or Amount) table in this statement."})
    _uploaded[sid] = df
    _currency[sid] = _detect_currency(raw)
    return {"ok": True, "rows": len(df), "currency": _currency[sid]}


@app.post("/api/reset")
def api_reset(request: Request) -> dict:
    """Switch this session back to the built-in sample data."""
    sid = request.state.sid
    _uploaded.pop(sid, None)
    _currency.pop(sid, None)
    return {"ok": True}


@app.post("/api/chat")
def api_chat(request: Request, body: ChatIn) -> dict:
    sid = request.state.sid  # cookie session, not the client-supplied thread_id
    try:
        # Ground the advisor in the data currently shown on the dashboard, and
        # point semantic search at the same (redacted) statement.
        df = _uploaded.get(sid)
        set_active_transactions(df, sid)
        sym = CURRENCY_SYMBOLS[_currency.get(sid, "USD")]
        grounded = f"{snapshot_summary(df, symbol=sym)}\n\nUser question: {body.message}"
        return {"reply": agent_chat(grounded, sid)}
    except Exception as exc:  # noqa: BLE001 - surface a friendly message
        if _is_connection_error(exc):
            return {"reply": CONN_HINT}
        print(f"chat error: {exc!r}")  # logged server-side, not shown to users
        return {"reply": "Something went wrong on the server. Please try again."}


if __name__ == "__main__":
    import os

    import uvicorn

    # Host platforms inject $PORT; bind 0.0.0.0 so it's reachable. Local default 8000.
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
