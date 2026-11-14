// Ponte entre a página e o backend.
//
// O camera.js roda no contexto da página e fica sujeito à CSP do Meet, que pode
// bloquear conexões para o localhost. Este script roda no contexto isolado da
// extensão, abre o WebSocket e repassa frames e respostas via postMessage.

const BACKEND_URL = "ws://localhost:8000/ws";
const RETRY_MS = 2000;

let socket = null;

function connect() {
  socket = new WebSocket(BACKEND_URL);
  socket.onmessage = (event) => {
    window.postMessage(
      { source: "teleport-bridge", state: JSON.parse(event.data) },
      location.origin,
    );
  };
  socket.onclose = () => setTimeout(connect, RETRY_MS);
}

window.addEventListener("message", (event) => {
  if (event.source !== window || event.data?.source !== "teleport-camera") {
    return;
  }
  if (socket === null) {
    connect();
  }
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(event.data.frame);
  }
});
