"""Capability 3 - Embeddings: similarity search and clustering of transactions.

Uses OpenAI embeddings via LangChain instead of the notebook's Gemini
embeddings, plus scikit-learn for clustering / PCA.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
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


def cluster_transactions(df: pd.DataFrame, n_clusters: int = 5,
                         embeddings: np.ndarray | None = None) -> pd.DataFrame:
    """Cluster transactions by embedding similarity.

    Returns a copy of `df` with Cluster, PCA1 and PCA2 columns added so callers
    can analyse or plot the clusters.
    """
    if embeddings is None:
        embeddings = embed_transactions(df)

    out = df.copy().reset_index(drop=True)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    out["Cluster"] = kmeans.fit_predict(embeddings)

    pca = PCA(n_components=2)
    coords = pca.fit_transform(embeddings)
    out["PCA1"] = coords[:, 0]
    out["PCA2"] = coords[:, 1]
    return out
