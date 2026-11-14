"""Converte detecções frame a frame em alternâncias de visibilidade."""

from dataclasses import dataclass, field


@dataclass
class TeleportToggle:
    """Alterna a visibilidade quando o gesto é mantido por tempo suficiente.

    É preciso soltar o gesto antes de disparar de novo, e há um intervalo
    mínimo entre disparos para evitar alternâncias acidentais.
    """

    hold_seconds: float = 0.4
    cooldown_seconds: float = 1.5
    visible: bool = True
    _held_since: float | None = field(default=None, init=False, repr=False)
    _fired: bool = field(default=False, init=False, repr=False)
    _last_fired: float = field(default=float("-inf"), init=False, repr=False)

    def update(self, gesture: bool, now: float) -> bool:
        """Registra o gesto no instante `now` e indica se a visibilidade mudou."""
        if not gesture:
            self._held_since = None
            self._fired = False
            return False

        if self._held_since is None:
            self._held_since = now

        held = now - self._held_since >= self.hold_seconds
        rested = now - self._last_fired >= self.cooldown_seconds
        if self._fired or not (held and rested):
            return False

        self._fired = True
        self._last_fired = now
        self.visible = not self.visible
        return True
