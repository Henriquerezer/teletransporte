from teleport.toggle import TeleportToggle


def hold(toggle, start, end, step=0.1):
    """Mantém o gesto de `start` a `end` e devolve quantas vezes alternou."""
    changes = 0
    now = start
    while now <= end + 1e-9:
        changes += toggle.update(True, now)
        now += step
    return changes


def test_starts_visible():
    assert TeleportToggle().visible


def test_short_gesture_is_ignored():
    toggle = TeleportToggle(hold_seconds=0.4)

    assert hold(toggle, 0.0, 0.2) == 0
    assert toggle.visible


def test_held_gesture_toggles_once():
    toggle = TeleportToggle(hold_seconds=0.4)

    assert hold(toggle, 0.0, 3.0) == 1
    assert not toggle.visible


def test_repeating_gesture_toggles_back():
    toggle = TeleportToggle(hold_seconds=0.4, cooldown_seconds=1.0)
    hold(toggle, 0.0, 0.5)
    toggle.update(False, 0.6)

    assert hold(toggle, 2.0, 2.5) == 1
    assert toggle.visible


def test_cooldown_blocks_quick_repeat():
    toggle = TeleportToggle(hold_seconds=0.4, cooldown_seconds=1.5)
    hold(toggle, 0.0, 0.4)
    toggle.update(False, 0.5)

    assert hold(toggle, 0.6, 1.0) == 0
    assert not toggle.visible
