"""API HTTP/WebSocket do backend de teletransporte."""

from fastapi import FastAPI

app = FastAPI(title="Teletransporte")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
