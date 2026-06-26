"""Chroma-backed financial knowledge base for RAG."""

from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document

from fingenius.config import CHROMA_DIR, get_embeddings
from fingenius.data import FINANCIAL_KNOWLEDGE

_COLLECTION = "financial_knowledge"


@lru_cache(maxsize=1)
def _get_vectorstore() -> Chroma:
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
    return _get_vectorstore().as_retriever(search_kwargs={"k": k})
