# Teletransporte

Faça o gesto de teletransporte (dois dedos na testa) durante uma chamada do
Google Meet e desapareça da câmera. Repita o gesto para reaparecer.

## Arquitetura

```
┌──────── Chrome (Google Meet) ────────┐         ┌──── Docker ────────────┐
│ Extensão intercepta a câmera         │ frames  │ FastAPI + WebSocket     │
│ (a mesma que o Meet usa), desenha    │ ──────► │ MediaPipe detecta o     │
│ o efeito e entrega o vídeo ao Meet   │ ◄────── │ gesto dos dedos na testa│
└──────────────────────────────────────┘ estado  └─────────────────────────┘
```

O Docker Desktop no Windows não dá acesso à webcam dentro do container, por
isso a câmera é lida pela extensão e os frames são enviados ao backend.

## Backend

```bash
docker compose up --build
```

Verifique em <http://localhost:8000/health>.

### Desenvolvimento local

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
ruff check . && ruff format --check .
pytest
```
