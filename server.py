"""FinGenius dashboard web server (FastAPI).

Serves the pixel-perfect dashboard (web/index.html) and exposes a /api/chat
endpoint that drives the real LangGraph agent.

    uvicorn server:app --reload --port 8000
    # then open http://localhost:8000
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

import fingenius  # noqa: F401  (imports inject truststore for TLS)
from fingenius.agent import chat as agent_chat
from fingenius.dashboard import dashboard_snapshot

WEB_DIR = Path(__file__).parent / "web"

app = FastAPI(title="FinGenius Dashboard")

CONN_HINT = (
    "Can't reach OpenAI — your machine is blocking the connection (the API key "
    "is fine). Allow python.exe through NetLimiter/your firewall, disable "
    "antivirus HTTPS scanning, or try a phone hotspot, then ask again."
)


def _is_connection_error(exc: Exception) -> bool:
    text = f"{type(exc).__name__} {exc}".lower()
    return any(
        s in text
        for s in ("connection error", "apiconnection", "connecterror",
                  "certificate_verify", "max retries", "failed to establish",
                  "getaddrinfo")
    )


class ChatIn(BaseModel):
    message: str
    thread_id: str = "default"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/data")
def api_data() -> dict:
    """Real KPIs / categories / budget / cash flow from the sample data."""
    return dashboard_snapshot()


@app.post("/api/chat")
def api_chat(body: ChatIn) -> dict:
    try:
        return {"reply": agent_chat(body.message, body.thread_id)}
    except Exception as exc:  # noqa: BLE001 - surface a friendly message
        if _is_connection_error(exc):
            return {"reply": CONN_HINT}
        return {"reply": f"Error: {exc}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
