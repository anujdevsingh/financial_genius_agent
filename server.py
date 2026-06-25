"""FinGenius dashboard web server (FastAPI).

Serves the pixel-perfect dashboard (web/index.html) and exposes a /api/chat
endpoint that drives the real LangGraph agent.

    uvicorn server:app --reload --port 8000
    # then open http://localhost:8000
"""

import io
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import fingenius  # noqa: F401  (imports inject truststore for TLS)
from fingenius.agent import chat as agent_chat
from fingenius.analysis import categorize_transaction
from fingenius.dashboard import dashboard_snapshot, snapshot_summary

WEB_DIR = Path(__file__).parent / "web"

app = FastAPI(title="FinGenius Dashboard")

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
    thread_id: str = "default"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


# In-memory uploaded statement (None = use sample data).
# ponytail: single global, fine for one-user local demo; use a session store if multi-user.
_uploaded = {"df": None}


def _normalize(df: pd.DataFrame) -> pd.DataFrame | None:
    """Map a statement CSV to Date/Description/Amount(/Category). Returns None
    if the required columns are missing."""
    cols = {c.lower().strip(): c for c in df.columns}
    need = {"date", "description", "amount"}
    if not need.issubset(cols):
        return None
    out = pd.DataFrame({
        "Date": pd.to_datetime(df[cols["date"]], errors="coerce"),
        "Description": df[cols["description"]].astype(str),
        "Amount": pd.to_numeric(df[cols["amount"]], errors="coerce"),
    })
    if "category" in cols:
        out["Category"] = df[cols["category"]].astype(str)
    out = out.dropna(subset=["Date", "Amount"]).reset_index(drop=True)
    if "Category" not in out.columns:
        out["Category"] = _auto_categorize(out)
    return out


def _auto_categorize(df: pd.DataFrame) -> list[str]:
    """Categorize uploaded rows that have no category, via the structured-output
    tool. ponytail: caps at 80 unique merchants to bound LLM calls/cost;
    bigger files stay 'Uncategorized'."""
    uniq = df["Description"].unique()
    if len(uniq) > 80:
        return ["Uncategorized"] * len(df)
    mapping = {}
    for desc in uniq:
        amt = float(df.loc[df.Description == desc, "Amount"].iloc[0])
        try:
            mapping[desc] = categorize_transaction(desc, amt).category
        except Exception:  # noqa: BLE001 - offline/blocked -> leave uncategorized
            mapping[desc] = "Uncategorized"
    return df["Description"].map(mapping).tolist()


@app.get("/api/data")
def api_data() -> dict:
    """Real KPIs / categories / budget / cash flow from uploaded or sample data."""
    return dashboard_snapshot(_uploaded["df"])


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    """Upload a transactions/statement CSV (Date, Description, Amount[, Category])."""
    try:
        df = _normalize(pd.read_csv(io.BytesIO(await file.read())))
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(status_code=400, content={"error": f"Could not read CSV: {exc}"})
    if df is None or df.empty:
        return JSONResponse(status_code=400, content={"error": "CSV needs Date, Description and Amount columns."})
    _uploaded["df"] = df
    return {"ok": True, "rows": len(df)}


@app.post("/api/reset")
def api_reset() -> dict:
    """Switch back to the built-in sample data."""
    _uploaded["df"] = None
    return {"ok": True}


@app.post("/api/chat")
def api_chat(body: ChatIn) -> dict:
    try:
        # Ground the advisor in the data currently shown on the dashboard.
        grounded = f"{snapshot_summary(_uploaded['df'])}\n\nUser question: {body.message}"
        return {"reply": agent_chat(grounded, body.thread_id)}
    except Exception as exc:  # noqa: BLE001 - surface a friendly message
        if _is_connection_error(exc):
            return {"reply": CONN_HINT}
        return {"reply": f"Error: {exc}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
