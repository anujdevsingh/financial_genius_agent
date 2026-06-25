"""Transaction tools that expose the remaining Gen AI capabilities to the agent:

- Structured output: categorize a transaction (category + confidence + reasoning)
- Embeddings: semantic search over the user's sample transaction history

These let the conversational agent reach capabilities that previously only
existed as standalone modules.
"""

from functools import lru_cache

from langchain_core.tools import tool

from fingenius.analysis.categorize import categorize_transaction as _categorize
from fingenius.analysis.embeddings import (
    embed_transactions,
    find_similar_transactions as _find_similar,
)
from fingenius.data import generate_transactions


@lru_cache(maxsize=1)
def _sample_with_embeddings():
    """Sample transactions + their embeddings, computed once and reused."""
    df = generate_transactions().sample(60, random_state=42).reset_index(drop=True)
    return df, embed_transactions(df)


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
    """Semantically search the user's sample transaction history.

    Use when the user asks to find spending similar to something (e.g. "show me
    transactions like coffee" or "what did I spend on transport?"). Returns the
    most similar transactions with a similarity score.
    """
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
