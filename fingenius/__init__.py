"""FinGenius: AI-powered personal finance advisor.

A LangChain + LangGraph agent that categorizes transactions, retrieves
evidence-based financial knowledge (RAG), runs financial calculations
(tool/function calling), and holds a stateful conversation.
"""

__version__ = "1.0.0"

# Use the operating system's trust store for TLS. This lets the app work behind
# corporate / antivirus / firewall SSL inspection (e.g. NetLimiter), where the
# intercepting proxy's root certificate is trusted by Windows but not by
# Python's bundled certificate list. Best-effort: never fail import if missing.
try:  # pragma: no cover - environment dependent
    import truststore

    truststore.inject_into_ssl()
except Exception:
    pass
