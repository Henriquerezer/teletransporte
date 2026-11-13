from teleport.gesture import (
    FACE_LEFT,
    FACE_RIGHT,
    FOREHEAD,
    INDEX_TIP,
    MIDDLE_TIP,
    PINKY_PIP,
    PINKY_TIP,
    RING_PIP,
    RING_TIP,
    WRIST,
    is_teleport_gesture,
)

FOREHEAD_POINT = (300.0, 100.0)


def make_face():
    face = [(0.0, 0.0)] * 478
    face[FOREHEAD] = FOREHEAD_POINT
    face[FACE_LEFT] = (200.0, 200.0)
    face[FACE_RIGHT] = (400.0, 200.0)  # largura do rosto: 200 px
    return face


def make_hand(tips_at, ring_folded=True, pinky_folded=True):
    hand = [(0.0, 0.0)] * 21
    hand[WRIST] = (300.0, 400.0)
    hand[INDEX_TIP] = tips_at
    hand[MIDDLE_TIP] = (tips_at[0] + 15, tips_at[1])
    hand[RING_PIP] = (320.0, 300.0)
    hand[RING_TIP] = (320.0, 340.0) if ring_folded else (320.0, 150.0)
    hand[PINKY_PIP] = (340.0, 310.0)
    hand[PINKY_TIP] = (340.0, 350.0) if pinky_folded else (340.0, 160.0)
    return hand


def test_two_fingers_on_forehead():
    assert is_teleport_gesture(make_hand(FOREHEAD_POINT), make_face())


def test_fingers_far_from_forehead():
    assert not is_teleport_gesture(make_hand((300.0, 350.0)), make_face())


def test_open_hand_on_forehead():
    hand = make_hand(FOREHEAD_POINT, ring_folded=False, pinky_folded=False)

    assert not is_teleport_gesture(hand, make_face())
