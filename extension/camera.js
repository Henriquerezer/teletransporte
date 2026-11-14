// Intercepta a câmera que o Meet abre, envia frames reduzidos ao backend e
// devolve ao Meet um vídeo processado no lugar do original.

(() => {
  const SEND_INTERVAL_MS = 100;
  const RESPONSE_TIMEOUT_MS = 1000;
  const ANALYSIS_WIDTH = 320;

  let state = { visible: true, changed: false, gesture: false, person: false };
  let lastSentAt = 0;
  let awaitingResponse = false;

  window.addEventListener("message", (event) => {
    if (event.source !== window || event.data?.source !== "teleport-bridge") {
      return;
    }
    state = event.data.state;
    awaitingResponse = false;
  });

  const getUserMedia = navigator.mediaDevices.getUserMedia.bind(
    navigator.mediaDevices,
  );

  navigator.mediaDevices.getUserMedia = async (constraints) => {
    const stream = await getUserMedia(constraints);
    if (!constraints?.video) {
      return stream;
    }
    const [cameraTrack] = stream.getVideoTracks();
    return new MediaStream([processTrack(cameraTrack), ...stream.getAudioTracks()]);
  };

  function processTrack(cameraTrack) {
    const processor = new MediaStreamTrackProcessor({ track: cameraTrack });
    const generator = new MediaStreamTrackGenerator({ kind: "video" });

    processor.readable
      .pipeThrough(new TransformStream({ transform: processFrame }))
      .pipeTo(generator.writable)
      .catch(() => cameraTrack.stop());

    // Quando o Meet desliga a câmera, desligamos também a câmera real.
    const stopGenerator = generator.stop.bind(generator);
    generator.stop = () => {
      stopGenerator();
      cameraTrack.stop();
    };
    return generator;
  }

  function processFrame(frame, controller) {
    sendForAnalysis(frame);
    controller.enqueue(frame);
  }

  function sendForAnalysis(frame) {
    const now = performance.now();
    const timedOut = now - lastSentAt > RESPONSE_TIMEOUT_MS;
    if ((awaitingResponse && !timedOut) || now - lastSentAt < SEND_INTERVAL_MS) {
      return;
    }
    lastSentAt = now;
    awaitingResponse = true;

    const scale = ANALYSIS_WIDTH / frame.displayWidth;
    const canvas = new OffscreenCanvas(
      ANALYSIS_WIDTH,
      Math.round(frame.displayHeight * scale),
    );
    canvas.getContext("2d").drawImage(frame, 0, 0, canvas.width, canvas.height);
    canvas
      .convertToBlob({ type: "image/jpeg", quality: 0.7 })
      .then((blob) =>
        window.postMessage({ source: "teleport-camera", frame: blob }, location.origin),
      );
  }
})();
