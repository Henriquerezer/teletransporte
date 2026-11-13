"""Detecção de mãos e rosto com MediaPipe."""

import io
import os
from dataclasses import dataclass
from pathlib import Path

import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision
from PIL import Image

from teleport.gesture import Point, is_teleport_gesture

MODELS_DIR = Path(os.environ.get("TELEPORT_MODELS_DIR", "models"))


@dataclass(frozen=True)
class Detection:
    gesture: bool
    person: bool


class GestureDetector:
    """Procura o gesto de teletransporte em frames JPEG."""

    def __init__(self, models_dir: Path = MODELS_DIR) -> None:
        self._hands = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=_model(models_dir / "hand_landmarker.task"),
                num_hands=2,
            )
        )
        self._faces = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                base_options=_model(models_dir / "face_landmarker.task"),
            )
        )
        # A mão sobre a testa pode esconder o rosto; reaproveitamos o último.
        self._last_face: list[Point] | None = None

    def detect(self, jpeg: bytes) -> Detection:
        pixels = np.asarray(Image.open(io.BytesIO(jpeg)).convert("RGB"))
        height, width = pixels.shape[:2]
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=pixels)

        faces = self._faces.detect(image).face_landmarks
        hands = [
            _to_pixels(hand, width, height)
            for hand in self._hands.detect(image).hand_landmarks
        ]
        if faces:
            self._last_face = _to_pixels(faces[0], width, height)

        gesture = self._last_face is not None and any(
            is_teleport_gesture(hand, self._last_face) for hand in hands
        )
        return Detection(gesture=gesture, person=bool(faces or hands))

    def close(self) -> None:
        self._hands.close()
        self._faces.close()


def _model(path: Path) -> BaseOptions:
    return BaseOptions(model_asset_path=str(path))


def _to_pixels(landmarks, width: int, height: int) -> list[Point]:
    return [(point.x * width, point.y * height) for point in landmarks]
