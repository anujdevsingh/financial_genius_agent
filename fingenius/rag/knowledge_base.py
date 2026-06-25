"""Capability 2 - RAG: a Chroma-backed financial knowledge base.

Builds (and persists) a vector store from the financial knowledge documents and
exposes a retriever plus a convenience `get_financial_advice` helper.
"""

from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document

from fingenius.config import CHROMA_DIR, get_embeddings, get_llm
from fingenius.data import FINANCIAL_KNOWLEDGE

_COLLECTION = "financial_knowledge"


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    """Return the financial-knowledge vector store, building it on first use.

    The store is persisted to disk (CHROMA_DIR). If it is already populated we
    reuse it instead of re-embedding the documents on every run.
    """
    store = Chroma(
        collection_name=_COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )
    if store._collection.count() == 0:
        docs = [
            Document(page_content=text, metadata={"id": f"doc_{i}"})
            for i, text in enumerate(FINANCIAL_KNOWLEDGE)
        ]
        store.add_documents(docs)
    return store


def get_retriever(k: int = 3):
    """Return a retriever over the financial knowledge base."""
    return get_vectorstore().as_retriever(search_kwargs={"k": k})


def get_financial_advice(query: str, num_results: int = 3) -> dict:
    """Answer a financial question using retrieved knowledge (RAG).

    Returns a dict with `response` (markdown text) and `sources` (the documents
    used), matching the original notebook's interface.
    """
    docs = get_retriever(k=num_results).invoke(query)
    sources = [d.page_content for d in docs]
    knowledge = "\n".join(f"- {s}" for s in sources)

    system = (
        "You are a financial advisor providing evidence-based advice. Use the "
        "provided financial knowledge to answer the question. Include specific "
        "advice from the knowledge and explain why it is relevant. Respond in "
        "markdown."
    )
    user = f"FINANCIAL KNOWLEDGE:\n{knowledge}\n\nUSER QUESTION: {query}"

    response = get_llm().invoke([("system", system), ("human", user)])
    return {"response": response.content, "sources": sources}
