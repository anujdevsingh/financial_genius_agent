"""Central configuration: API keys, model selection, and shared LLM/embedding
factories. Everything reads the OpenAI key from the environment (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()

# --- Model configuration -------------------------------------------------
# Override any of these via environment variables / .env without code changes.
CHAT_MODEL = os.getenv("FINGENIUS_CHAT_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("FINGENIUS_EMBEDDING_MODEL", "text-embedding-3-small")
TEMPERATURE = float(os.getenv("FINGENIUS_TEMPERATURE", "0.2"))

# Where the persistent Chroma vector store lives.
CHROMA_DIR = os.getenv("FINGENIUS_CHROMA_DIR", ".chroma")


def _require_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your "
            "OpenAI key, or export OPENAI_API_KEY in your shell."
        )
    return key


def get_llm(temperature: float | None = None):
    """Return a configured ChatOpenAI instance."""
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=CHAT_MODEL,
        temperature=TEMPERATURE if temperature is None else temperature,
        api_key=_require_api_key(),
    )


def get_embeddings():
    """Return a configured OpenAIEmbeddings instance."""
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=_require_api_key())
