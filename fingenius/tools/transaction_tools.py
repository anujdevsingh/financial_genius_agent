"""Transaction tools that expose the remaining Gen AI capabilities to the agent:

- Structured output: categorize a transaction (category + confidence + reasoning)
- Embeddings: semantic search over the user's sample transaction history

These let the conversational agent reach capabilities that previously only
existed as standalone modules.
"""

from contextvars import ContextVar
from functools import lru_cache

import pandas as pd
from langchain_core.tools import tool

from fingenius.analysis.categorize import categorize_transaction as _categorize
from fingenius.analysis.embeddings import (
    embed_transactions,
    find_similar_transactions as _find_similar,
)
from fingenius.data import generate_transactions
from fingenius.privacy import redact


@lru_cache(maxsize=1)
def _sample_with_embeddings():
    """Sample transactions + their embeddings, computed once and reused."""
    df = generate_transactions().sample(60, random_state=42).reset_index(drop=True)
    return df, embed_transactions(df)


# Per-session search corpus, so concurrent users never see each other's data.
# Description here is the REDACTED merchant name, so embeddings/results sent to
# OpenAI never contain account or reference numbers. Embeddings are built lazily
# on first search (one batched call) and cached until that session re-uploads.
# A ContextVar carries the current session id into the (shared) tool call.
_active_by_sid: dict[str, dict] = {}
_current_sid: ContextVar[str] = ContextVar("fingenius_sid", default="")


def set_active_transactions(df, sid: str = "") -> None:
    """Point this session's semantic search at its uploaded statement (or sample
    when df is None). Must be called in the same request that runs the agent."""
    _current_sid.set(sid)
    if df is None or len(df) == 0:
        _active_by_sid.pop(sid, None)
        return
    names = df["Merchant"] if "Merchant" in df.columns else df["Description"]
    _active_by_sid[sid] = {
        "df": pd.DataFrame({
            "Description": [redact(n) for n in names],   # redacted before any LLM call
            "Amount": df["Amount"].to_numpy(),
            "Category": df.get("Category", pd.Series(["Uncategorized"] * len(df))).to_numpy(),
            "Date": df["Date"].to_numpy(),
        }),
        "emb": None,  # rebuilt lazily on first search
    }


@tool
def categorize_transaction(description: str, amount: float) -> dict:
    """Categorize a single financial transaction into a spending category.

    Use when the user wants a transaction labelled (e.g. "what category is
    Netflix -15.99?"). `amount` is negative for spending, positive for income.
    Returns the category, a confidence score (0-1) and a short reasoning.
    """
    result = _categorize(description, amount)
    return {
        "category": result.category,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
    }


@tool
def find_similar_transactions(query: str, top_n: int = 5) -> list:
    """Semantically search the user's transaction history.

    Searches the uploaded statement when one is loaded (otherwise the sample
    data). Use when the user asks to find spending similar to something (e.g.
    "show me transactions like coffee" or "what did I spend on transport?").
    Returns the most similar transactions with a similarity score.
    """
    active = _active_by_sid.get(_current_sid.get())
    if active is not None:
        df = active["df"]
        if active["emb"] is None:
            active["emb"] = embed_transactions(df)  # df.Description already redacted
        embeddings = active["emb"]
    else:
        df, embeddings = _sample_with_embeddings()
    results = _find_similar(query, df, top_n=top_n, embeddings=embeddings)
    return [
        {
            "description": r["Description"],
            "amount": round(r["Amount"], 2),
            "category": r["Category"],
            "similarity": round(r["Similarity"], 3),
        }
        for r in results
    ]
