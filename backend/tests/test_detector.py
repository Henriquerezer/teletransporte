import io

import pytest
from PIL import Image

from teleport.detector import MODELS_DIR, GestureDetector

pytestmark = pytest.mark.skipif(
    not (MODELS_DIR / "hand_landmarker.task").exists(),
    reason="modelos do MediaPipe não baixados",
)


def test_empty_frame_has_no_person():
    buffer = io.BytesIO()
    Image.new("RGB", (320, 240), "gray").save(buffer, format="JPEG")
    detector = GestureDetector()

    detection = detector.detect(buffer.getvalue())
    detector.close()

    assert not detection.gesture
    assert not detection.person
