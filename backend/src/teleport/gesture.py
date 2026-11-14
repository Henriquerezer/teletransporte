"""Regra geométrica do gesto de teletransporte: dois dedos na testa."""

from collections.abc import Sequence
from math import dist

Point = tuple[float, float]

# Landmarks da mão (MediaPipe Hand Landmarker).
WRIST = 0
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_PIP, RING_TIP = 14, 16
PINKY_PIP, PINKY_TIP = 18, 20

# Landmarks do rosto (MediaPipe Face Landmarker).
FOREHEAD = 151
FACE_LEFT, FACE_RIGHT = 234, 454

# Distância máxima entre a ponta do dedo e a testa, em larguras de rosto.
FOREHEAD_RADIUS = 0.35


def is_finger_folded(hand: Sequence[Point], pip: int, tip: int) -> bool:
    """Um dedo está dobrado quando a ponta fica mais perto do pulso que a junta."""
    return dist(hand[tip], hand[WRIST]) < dist(hand[pip], hand[WRIST])


def is_teleport_gesture(hand: Sequence[Point], face: Sequence[Point]) -> bool:
    """Indicador e médio na testa, com anelar e mindinho dobrados.

    Os pontos devem estar em pixels para que as distâncias não sejam
    distorcidas pela proporção da imagem.
    """
    radius = FOREHEAD_RADIUS * dist(face[FACE_LEFT], face[FACE_RIGHT])
    fingers_on_forehead = all(
        dist(hand[tip], face[FOREHEAD]) < radius for tip in (INDEX_TIP, MIDDLE_TIP)
    )
    others_folded = is_finger_folded(hand, RING_PIP, RING_TIP) and is_finger_folded(
        hand, PINKY_PIP, PINKY_TIP
    )
    return fingers_on_forehead and others_folded
