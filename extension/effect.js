// Efeito de teletransporte: o vídeo se fatia, tremula e some num clarão,
// revelando o fundo vazio. No reaparecimento, o caminho inverso.
//
// O fundo vazio é aprendido sozinho: sempre que o backend informa que não há
// ninguém no quadro por um tempo, o frame atual vira a "placa" de fundo.

class TeleportEffect {
  static DURATION_MS = 700;
  static EMPTY_DELAY_MS = 1000;
  static SLICES = 14;
  static MAX_SHIFT = 0.08; // deslocamento máximo das fatias, em larguras
  static FLASH_COLOR = "220, 240, 255";

  visible = true;
  transitionStart = -Infinity;
  emptySince = null;
  plate = null;
  canvas = null;

  // Recebe o frame da câmera e devolve o frame que o Meet deve transmitir.
  apply(frame, state, now) {
    this.track(state, now);
    this.learnBackground(frame, state, now);

    const progress = this.progress(now);
    if (this.visible && progress >= 1) {
      return frame;
    }

    const canvas = this.canvasFor(frame);
    this.draw(canvas.getContext("2d"), frame, progress);
    const output = new VideoFrame(canvas, { timestamp: frame.timestamp });
    frame.close();
    return output;
  }

  track(state, now) {
    if (state.visible !== this.visible) {
      this.visible = state.visible;
      this.transitionStart = now;
    }
  }

  learnBackground(frame, state, now) {
    if (state.person) {
      this.emptySince = null;
      return;
    }
    this.emptySince ??= now;
    if (now - this.emptySince < TeleportEffect.EMPTY_DELAY_MS) {
      return;
    }
    this.plate ??= new OffscreenCanvas(frame.displayWidth, frame.displayHeight);
    this.plate
      .getContext("2d")
      .drawImage(frame, 0, 0, this.plate.width, this.plate.height);
  }

  progress(now) {
    return Math.min((now - this.transitionStart) / TeleportEffect.DURATION_MS, 1);
  }

  canvasFor(frame) {
    const { displayWidth: width, displayHeight: height } = frame;
    if (this.canvas?.width !== width || this.canvas?.height !== height) {
      this.canvas = new OffscreenCanvas(width, height);
    }
    return this.canvas;
  }

  draw(ctx, frame, progress) {
    const { width, height } = ctx.canvas;
    // Quanto da pessoa aparece (0 a 1) e a força do efeito, máxima no meio.
    const presence = this.visible ? progress : 1 - progress;
    const intensity = Math.sin(Math.PI * progress);

    this.drawBackground(ctx, width, height);
    if (presence > 0) {
      ctx.globalAlpha = presence * (0.6 + 0.4 * Math.random());
      this.drawSlices(ctx, frame, width, height, intensity);
      ctx.globalAlpha = 1;
    }
    if (intensity > 0) {
      ctx.fillStyle = `rgba(${TeleportEffect.FLASH_COLOR}, ${0.8 * intensity})`;
      ctx.fillRect(0, 0, width, height);
    }
  }

  drawBackground(ctx, width, height) {
    if (this.plate) {
      ctx.drawImage(this.plate, 0, 0, width, height);
    } else {
      ctx.fillStyle = "black";
      ctx.fillRect(0, 0, width, height);
    }
  }

  drawSlices(ctx, frame, width, height, intensity) {
    const sliceHeight = Math.ceil(height / TeleportEffect.SLICES);
    const maxShift = TeleportEffect.MAX_SHIFT * width * intensity;
    for (let y = 0; y < height; y += sliceHeight) {
      const shift = (Math.random() * 2 - 1) * maxShift;
      ctx.drawImage(frame, 0, y, width, sliceHeight, shift, y, width, sliceHeight);
    }
  }
}
