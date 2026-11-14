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

## Próximos passos

O backend e a extensão estão prontos, mas **o fluxo completo ainda não foi
testado no Meet** com uma webcam real. Já foi verificado: testes do backend,
container carregando os modelos e respondendo pelo WebSocket, e a sintaxe do
JavaScript da extensão.

### Checklist do primeiro teste

- [ ] Clonar o repositório e rodar `docker compose up --build`.
- [ ] Abrir <http://localhost:8000/health> e ver `{"status": "ok"}`.
- [ ] Confirmar que a webcam funciona fora do Chrome (app **Câmera** do
      Windows), antes de carregar a extensão.
- [ ] Carregar a pasta `extension/` em `chrome://extensions`.
- [ ] Entrar em uma chamada do Meet (dá para testar sozinho em
      <https://meet.google.com/new>) e permitir o acesso à rede local se o
      Chrome pedir.
- [ ] Ver o próprio vídeo normalmente no Meet, com a extensão ativa.
- [ ] Sair do quadro por uns 2 segundos para a extensão aprender o fundo.
- [ ] Fazer o gesto e segurar por cerca de 0,4 s: você deve sumir.
- [ ] Soltar, esperar 1,5 s e repetir o gesto: você deve reaparecer.

### Se algo der errado

| Sintoma | O que verificar |
| --- | --- |
| Câmera preta ou ausente no Meet | Desative a extensão e recarregue a página. Se a câmera voltar, o problema está no `camera.js`: abra o DevTools (F12) na aba do Meet e veja os erros no **Console**. |
| Vídeo normal, mas o gesto não faz nada | No Console, procure erros de WebSocket. Veja os logs do container com `docker compose logs -f`. Confirme se o Chrome bloqueou o acesso à rede local (ícone na barra de endereço). |
| O gesto não é reconhecido | Aumente `FOREHEAD_RADIUS` em `backend/src/teleport/gesture.py`. Iluminação ruim e mão cobrindo todo o rosto atrapalham. |
| Dispara sem querer | Aumente `hold_seconds` e `cooldown_seconds` em `backend/src/teleport/toggle.py`. |
| Tela preta quando some | O fundo ainda não foi aprendido: saia do quadro por uns 2 segundos. |

Depois de mudar o backend, rode `docker compose up --build` de novo. Depois
de mudar a extensão, clique em recarregar no card dela em
`chrome://extensions` e recarregue a aba do Meet.

### Pendências conhecidas

- Não foi confirmado se o Meet aceita sem problemas o vídeo gerado pela
  extensão (`MediaStreamTrackGenerator`), inclusive com os efeitos nativos do
  Meet (desfoque de fundo) ligados.
- Se você se mexer enquanto está sumido, isso não aparece. Mas se a câmera
  mudar de posição, o fundo aprendido fica desatualizado até o quadro ficar
  vazio de novo.
