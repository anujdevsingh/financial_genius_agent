"""Builds a real dashboard snapshot from the sample transaction data, so the
web dashboard shows actual computed figures instead of hard-coded demo values.
"""

from fingenius.data import generate_transactions
from fingenius.privacy import redact

# Visual mapping per category (icon + 2-stop bar gradient), matching the design.
CATEGORY_STYLE = {
    "Income": ("💰", ["#10b981", "#34d399"]),
    "Housing": ("🏠", ["#10b981", "#34d399"]),
    "Shopping": ("🛍️", ["#6366f1", "#818cf8"]),
    "Groceries": ("🥑", ["#0891b2", "#22d3ee"]),
    "Dining": ("🍽️", ["#db2777", "#f472b6"]),
    "Education": ("🎓", ["#d97706", "#fbbf24"]),
    "Transportation": ("🚗", ["#0d9488", "#2dd4bf"]),
    "Utilities": ("⚡", ["#7c3aed", "#a78bfa"]),
    "Healthcare": ("💊", ["#e11d48", "#fb7185"]),
    "Entertainment": ("🎬", ["#60a5fa", "#93c5fd"]),
    "Transfers": ("🔁", ["#64748b", "#94a3b8"]),
}
_DEFAULT_STYLE = ("💳", ["#10b981", "#34d399"])

# 50/30/20 buckets (Transfers / Income sit outside needs & wants).
NEEDS = {"Housing", "Utilities", "Groceries", "Healthcare", "Transportation", "Education"}
WANTS = {"Dining", "Shopping", "Entertainment"}


def dashboard_snapshot(df=None, symbol="$") -> dict:
    """Compute KPIs, category breakdown, budget, cash flow and recent
    transactions. Uses the sample data unless an uploaded DataFrame is passed.
    `symbol` is the currency symbol used for preformatted strings."""
    if df is None:
        df = generate_transactions()
    df = df.sort_values("Date").reset_index(drop=True)
    if "Category" not in df.columns:
        df["Category"] = "Uncategorized"
    days = max(int((df["Date"].max() - df["Date"].min()).days), 1)

    income = float(df.loc[df.Amount > 0, "Amount"].sum())
    spend = float(-df.loc[df.Amount < 0, "Amount"].sum())
    net = income - spend
    rate = (net / income * 100) if income else 0.0

    # Spending by category (descending).
    cats = (
        df[df.Amount < 0].groupby("Category")["Amount"].sum().abs().sort_values(ascending=False)
    )
    categories = [
        {"name": name, "amount": float(amt), "colors": CATEGORY_STYLE.get(name, _DEFAULT_STYLE)[1]}
        for name, amt in cats.items()
    ]

    # 50/30/20 actuals vs. recommended.
    needs = float(sum(v for k, v in cats.items() if k in NEEDS))
    wants = float(sum(v for k, v in cats.items() if k in WANTS))
    savings = max(net, 0.0)
    budget = [
        {"name": "Needs", "actual": needs, "target": income * 0.5, "colors": ["#10b981", "#34d399"]},
        {"name": "Wants", "actual": wants, "target": income * 0.3, "colors": ["#6366f1", "#818cf8"]},
        {"name": "Savings", "actual": savings, "target": income * 0.2, "colors": ["#059669", "#34d399"], "isSavings": True},
    ]

    # Net cash flow per calendar month.
    monthly = df.assign(M=df.Date.dt.to_period("M")).groupby("M")["Amount"].sum()
    cashflow = [
        {"label": period.start_time.strftime("%b"), "net": float(val)}
        for period, val in monthly.items()
    ]

    # Most recent transactions.
    recent = df.sort_values("Date", ascending=False)
    has_merchant = "Merchant" in df.columns
    transactions = []
    for r in recent.itertuples():
        icon = CATEGORY_STYLE.get(r.Category, _DEFAULT_STYLE)[0]
        sign = "+" if r.Amount > 0 else "-"
        name = r.Merchant if has_merchant and r.Merchant else r.Description
        transactions.append(
            {
                "name": name,
                "category": r.Category,
                "date": r.Date.strftime("%b %d"),
                "amount": f"{sign}{symbol}{abs(r.Amount):,.2f}",
                "positive": bool(r.Amount > 0),
                "icon": icon,
            }
        )

    return {
        "income": income,
        "spend": spend,
        "net": net,
        "rate": rate,
        "categories": categories,
        "budget": budget,
        "cashflow": cashflow,
        "transactions": transactions,
        "days": days,
        "symbol": symbol,
    }


def snapshot_summary(df=None, symbol="$") -> str:
    """Grounding for the AI advisor: a compact but complete picture of the
    user's actual data (totals, every category, top payees, monthly flow,
    biggest transactions) so it answers from real numbers, not generics."""
    if df is None:
        df = generate_transactions()
    if "Category" not in df.columns:
        df = df.assign(Category="Uncategorized")
    d = dashboard_snapshot(df, symbol=symbol)
    s = symbol
    name_col = "Merchant" if "Merchant" in df.columns else "Description"

    lines = [
        f"User's finances (last {d['days']} days): income {s}{d['income']:,.0f}, "
        f"spending {s}{d['spend']:,.0f}, net {s}{d['net']:,.0f}, savings rate {d['rate']:.1f}%."
    ]
    if d["categories"]:
        lines.append("Spending by category: "
                     + "; ".join(f"{c['name']} {s}{c['amount']:,.0f}" for c in d["categories"]) + ".")
    spend = df[df.Amount < 0]
    if not spend.empty:
        top_m = spend.groupby(name_col)["Amount"].sum().abs().sort_values(ascending=False).head(8)
        lines.append("Top payees/merchants by spend: "
                     + "; ".join(f"{redact(n)} {s}{a:,.0f}" for n, a in top_m.items()) + ".")
    if d["cashflow"]:
        lines.append("Monthly net cash flow: "
                     + "; ".join(f"{c['label']} {s}{c['net']:,.0f}" for c in d["cashflow"]) + ".")
    big = df.loc[df.Amount.abs().sort_values(ascending=False).index].head(6)
    lines.append("Largest transactions: " + "; ".join(
        f"{r.Date:%b %d} {redact(getattr(r, name_col))} {s}{r.Amount:,.0f} ({r.Category})"
        for r in big.itertuples()) + ".")
    return "\n".join(lines)
