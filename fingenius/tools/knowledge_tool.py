"""RAG exposed as a tool so the agent can pull evidence-based financial
knowledge on demand during a conversation."""

from langchain_core.tools import tool

from fingenius.rag import get_retriever


@tool
def financial_knowledge_lookup(query: str) -> str:
    """Look up evidence-based personal-finance knowledge (budgeting, saving,
    investing, debt, retirement) relevant to the user's question. Use this
    whenever the user asks for financial advice or concepts."""
    docs = get_retriever(k=3).invoke(query)
    if not docs:
        return "No relevant financial knowledge found."
    return "\n".join(f"- {d.page_content}" for d in docs)
