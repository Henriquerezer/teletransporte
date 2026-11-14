"""API HTTP/WebSocket do backend de teletransporte."""

import asyncio
import time
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect

from teleport.detector import GestureDetector
from teleport.toggle import TeleportToggle

app = FastAPI(title="Teletransporte")


def detector_session() -> Iterator[GestureDetector]:
    detector = GestureDetector()
    try:
        yield detector
    finally:
        detector.close()


def new_toggle() -> TeleportToggle:
    return TeleportToggle()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws")
async def frames(
    websocket: WebSocket,
    detector: Annotated[GestureDetector, Depends(detector_session)],
    toggle: Annotated[TeleportToggle, Depends(new_toggle)],
) -> None:
    """Recebe frames JPEG e responde a cada um com o estado do teletransporte.

    Como cada frame tem exatamente uma resposta, o cliente controla o ritmo:
    só envia o próximo frame depois de receber a resposta do anterior.
    """
    await websocket.accept()
    try:
        while True:
            jpeg = await websocket.receive_bytes()
            detection = await asyncio.to_thread(detector.detect, jpeg)
            changed = toggle.update(detection.gesture, time.monotonic())
            await websocket.send_json(
                {
                    "visible": toggle.visible,
                    "changed": changed,
                    "gesture": detection.gesture,
                    "person": detection.person,
                }
            )
    except WebSocketDisconnect:
        pass
