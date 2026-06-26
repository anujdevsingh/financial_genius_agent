"""Capability 3 - Embeddings: similarity search and clustering of transactions.

Uses OpenAI embeddings via LangChain instead of the notebook's Gemini
embeddings, plus scikit-learn for clustering / PCA.
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from fingenius.config import get_embeddings


def _transaction_text(description: str, amount: float) -> str:
    direction = "spent" if amount < 0 else "received"
    return f"{description} - ${abs(amount):.2f} {direction}"


def embed_transactions(df: pd.DataFrame) -> np.ndarray:
    """Return an (n, d) embedding matrix for the transactions in `df`."""
    texts = [_transaction_text(r.Description, r.Amount) for r in df.itertuples()]
    vectors = get_embeddings().embed_documents(texts)
    return np.array(vectors)


def find_similar_transactions(query_text: str, df: pd.DataFrame, top_n: int = 5,
                              embeddings: np.ndarray | None = None) -> list[dict]:
    """Find the `top_n` transactions most similar to `query_text`."""
    if embeddings is None:
        embeddings = embed_transactions(df)

    query_vec = np.array(get_embeddings().embed_query(query_text)).reshape(1, -1)
    scores = cosine_similarity(query_vec, embeddings)[0]

    order = np.argsort(scores)[::-1][:top_n]
    results = []
    for pos in order:
        row = df.iloc[pos]
        results.append(
            {
                "Description": row["Description"],
                "Amount": row["Amount"],
                "Category": row["Category"],
                "Date": row["Date"],
                "Similarity": float(scores[pos]),
            }
        )
    return results


