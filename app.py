"""FinGenius Streamlit web app.

A polished browser chat UI for the financial advisor agent, with a sidebar
dashboard showing sample spending data and charts.

    streamlit run app.py
"""

import uuid

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fingenius.agent import chat
from fingenius.data import generate_transactions

st.set_page_config(page_title="FinGenius", page_icon="💰", layout="wide")

# --- Theme / custom styling ---------------------------------------------
ACCENT = "#10b981"        # emerald
ACCENT_DARK = "#059669"
BG_CARD = "#161b22"
BORDER = "#262d3a"

st.markdown(
    f"""
    <style>
    /* Base */
    .stApp {{ background: #0d1117; }}
    #MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; }}
    .block-container {{ padding-top: 2.2rem; max-width: 900px; }}

    /* Hero header */
    .fg-hero {{ margin-bottom: 1.4rem; }}
    .fg-title {{
        font-size: 2.4rem; font-weight: 800; letter-spacing: -0.02em;
        background: linear-gradient(90deg, {ACCENT}, #38bdf8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0;
    }}
    .fg-sub {{ color: #8b949e; font-size: 0.95rem; margin-top: 0.2rem; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{ background: #0b0e14; border-right: 1px solid {BORDER}; }}
    section[data-testid="stSidebar"] h2 {{ font-size: 1.05rem; color: #e6edf3; }}

    /* Metric cards */
    div[data-testid="stMetric"] {{
        background: {BG_CARD}; border: 1px solid {BORDER};
        border-radius: 14px; padding: 14px 16px;
    }}
    div[data-testid="stMetricValue"] {{ font-size: 1.5rem; font-weight: 700; }}
    div[data-testid="stMetricLabel"] {{ color: #8b949e; }}

    /* Chat bubbles */
    div[data-testid="stChatMessage"] {{
        background: {BG_CARD}; border: 1px solid {BORDER};
        border-radius: 16px; padding: 6px 14px; margin-bottom: 8px;
    }}

    /* Example-question chips */
    div[data-testid="stButton"] > button {{
        background: {BG_CARD}; color: #c9d1d9;
        border: 1px solid {BORDER}; border-radius: 12px;
        padding: 12px 14px; text-align: left; font-size: 0.9rem;
        transition: all 0.15s ease; width: 100%;
    }}
    div[data-testid="stButton"] > button:hover {{
        border-color: {ACCENT}; color: #fff;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(16,185,129,0.15);
    }}

    /* Chat input */
    div[data-testid="stChatInput"] textarea {{ font-size: 0.95rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def _sample_data() -> pd.DataFrame:
    return generate_transactions()


def _spending_chart(spending: pd.Series) -> go.Figure:
    """A smooth horizontal bar chart of spending by category."""
    s = spending.sort_values()
    fig = go.Figure(
        go.Bar(
            x=s.values, y=s.index, orientation="h",
            marker=dict(color=s.values, colorscale=[[0, ACCENT_DARK], [1, ACCENT]]),
            hovertemplate="%{y}: $%{x:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=300, margin=dict(l=0, r=10, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e", size=11),
        xaxis=dict(showgrid=True, gridcolor=BORDER, tickprefix="$"),
        yaxis=dict(showgrid=False),
    )
    return fig


EXAMPLES = [
    "How should I budget my $5000 monthly income?",
    "How much emergency fund do I need if my expenses are $3000?",
    "Should I pay off debt or invest first?",
    "Monthly payment on a $300,000 mortgage at 4.5% for 30 years?",
]

# --- State ---------------------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None
if "conn_error" not in st.session_state:
    st.session_state.conn_error = False


def _is_connection_error(exc: Exception) -> bool:
    """True when the failure is the agent not being able to reach OpenAI."""
    text = f"{type(exc).__name__} {exc}".lower()
    return any(s in text for s in ("connection error", "apiconnection", "connecterror",
                                   "max retries", "failed to establish", "getaddrinfo"))


CONN_HINT = (
    "**Can't reach OpenAI — your machine is blocking the connection.**\n\n"
    "Your API key is fine; `python.exe` just can't get online. Fix one of these, "
    "then ask again:\n"
    "- **NetLimiter / firewall** → allow `python.exe` (and `venv\\Scripts\\python.exe`) internet access\n"
    "- **Antivirus HTTPS/SSL scanning** → disable it or whitelist `api.openai.com`\n"
    "- **Quick test** → switch to a phone hotspot; if it works there, it's your local firewall"
)

# --- Sidebar dashboard ---------------------------------------------------
df = _sample_data()
spending = df[df["Amount"] < 0].groupby("Category")["Amount"].sum().abs()
income = df[df["Amount"] > 0]["Amount"].sum()

with st.sidebar:
    st.markdown("## 💰 Dashboard")
    st.caption("Synthetic demo data · last 90 days")
    c1, c2 = st.columns(2)
    c1.metric("Spend", f"${spending.sum():,.0f}")
    c2.metric("Income", f"${income:,.0f}")
    st.markdown("###### Spending by category")
    st.plotly_chart(_spending_chart(spending), width="stretch",
                    config={"displayModeBar": False})
    if st.session_state.messages:
        if st.button("🗑️  Clear conversation", width="stretch"):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()

# --- Header --------------------------------------------------------------
st.markdown(
    '<div class="fg-hero">'
    '<p class="fg-title">FinGenius</p>'
    '<p class="fg-sub">AI personal finance advisor — budgeting, saving, debt, loans & investing.</p>'
    '</div>',
    unsafe_allow_html=True,
)

# Persistent banner while the connection is broken.
if st.session_state.conn_error:
    st.error(CONN_HINT, icon="🚫")

# --- Welcome + example chips (only before first message) -----------------
if not st.session_state.messages:
    st.markdown("##### Try asking")
    cols = st.columns(2)
    for i, ex in enumerate(EXAMPLES):
        if cols[i % 2].button(ex, key=f"ex_{i}"):
            st.session_state.pending = ex
            st.rerun()

# --- Render history ------------------------------------------------------
for role, content in st.session_state.messages:
    avatar = "🧑" if role == "user" else "💰"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)

# --- Handle input --------------------------------------------------------
prompt = st.chat_input("Ask a financial question...")
if st.session_state.pending:
    prompt = st.session_state.pending
    st.session_state.pending = None

if prompt:
    st.session_state.messages.append(("user", prompt))
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="💰"):
        with st.spinner("Thinking..."):
            try:
                reply = chat(prompt, thread_id=st.session_state.thread_id)
                st.session_state.conn_error = False
            except Exception as exc:
                if _is_connection_error(exc):
                    st.session_state.conn_error = True
                    reply = CONN_HINT
                else:
                    reply = f"⚠️ **Error:** {exc}"
        st.markdown(reply)
    st.session_state.messages.append(("assistant", reply))
    st.rerun()
