import pytest
from fastapi.testclient import TestClient

from teleport.app import app, detector_session, new_toggle
from teleport.detector import Detection
from teleport.toggle import TeleportToggle

GESTURE = b"gesture"
NOTHING = b"nothing"


class FakeDetector:
    """Interpreta o conteúdo do frame como o resultado da detecção."""

    def detect(self, jpeg):
        return Detection(gesture=jpeg == GESTURE, person=jpeg == GESTURE)


@pytest.fixture
def client():
    app.dependency_overrides[detector_session] = FakeDetector
    app.dependency_overrides[new_toggle] = lambda: TeleportToggle(
        hold_seconds=0, cooldown_seconds=0
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_gesture_toggles_visibility(client):
    with client.websocket_connect("/ws") as ws:
        ws.send_bytes(NOTHING)
        assert ws.receive_json() == {
            "visible": True,
            "changed": False,
            "gesture": False,
            "person": False,
        }

        ws.send_bytes(GESTURE)
        assert ws.receive_json()["visible"] is False

        ws.send_bytes(NOTHING)
        ws.receive_json()
        ws.send_bytes(GESTURE)
        response = ws.receive_json()
        assert response["visible"] is True
        assert response["changed"] is True
