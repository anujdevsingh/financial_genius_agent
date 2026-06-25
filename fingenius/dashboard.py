"""Builds a real dashboard snapshot from the sample transaction data, so the
web dashboard shows actual computed figures instead of hard-coded demo values.
"""

from fingenius.data import generate_transactions

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
}
_DEFAULT_STYLE = ("💳", ["#10b981", "#34d399"])

# 50/30/20 buckets.
NEEDS = {"Housing", "Utilities", "Groceries", "Healthcare", "Transportation", "Education"}
WANTS = {"Dining", "Shopping", "Entertainment"}


def dashboard_snapshot() -> dict:
    """Compute KPIs, category breakdown, budget, cash flow and recent
    transactions from the real sample data."""
    df = generate_transactions().sort_values("Date").reset_index(drop=True)

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
    recent = df.sort_values("Date", ascending=False).head(8)
    transactions = []
    for r in recent.itertuples():
        icon = CATEGORY_STYLE.get(r.Category, _DEFAULT_STYLE)[0]
        sign = "+" if r.Amount > 0 else "-"
        transactions.append(
            {
                "name": r.Description,
                "category": r.Category,
                "date": r.Date.strftime("%b %d"),
                "amount": f"{sign}${abs(r.Amount):,.2f}",
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
        "days": 90,
    }
