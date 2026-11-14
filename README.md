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

## O gesto

Indicador e médio encostados na testa, anelar e mindinho dobrados, mantidos
por cerca de 0,4 s. O primeiro gesto faz você sumir; o seguinte, reaparecer.

## Backend

```bash
docker compose up --build
```

Verifique em <http://localhost:8000/health>.

### Protocolo

`ws://localhost:8000/ws`: o cliente envia um frame JPEG (binário) e espera a
resposta antes de enviar o próximo.

```json
{"visible": false, "changed": true, "gesture": true, "person": true}
```

- `visible`: se você deve aparecer no vídeo.
- `changed`: a visibilidade mudou neste frame (hora de tocar o efeito).
- `gesture`: o gesto foi visto neste frame.
- `person`: há rosto ou mão no frame (usado para aprender o fundo vazio).

### Desenvolvimento local

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"

# Modelos do MediaPipe (o Docker baixa sozinho)
mkdir -p models
curl -Lo models/hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
curl -Lo models/face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task

ruff check . && ruff format --check .
pytest
```

## Extensão do Chrome

1. Abra `chrome://extensions` e ative o **Modo do desenvolvedor**.
2. Clique em **Carregar sem compactação** e selecione a pasta `extension/`.
3. Com o backend rodando, entre em uma chamada do Meet. Se o Chrome pedir
   permissão para acessar a rede local/dispositivos, permita: é a conexão
   com `localhost:8000`.

A extensão envolve o `getUserMedia` da página: o Meet continua escolhendo a
câmera normalmente, e recebe de volta o vídeo processado.

### Fundo vazio

Para sumir de verdade, a extensão precisa saber como é o fundo sem você.
Antes da primeira vez, saia do quadro por uns 2 segundos: o fundo é
aprendido sozinho (e atualizado sempre que o quadro fica vazio). Sem isso,
o vídeo fica preto enquanto você está "teletransportado".
