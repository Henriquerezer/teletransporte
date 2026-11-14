FROM python:3.12-slim

# Bibliotecas de sistema exigidas pelo OpenCV, dependência do MediaPipe.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libegl1 libgl1 libgles2 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ARG MODELS_URL=https://storage.googleapis.com/mediapipe-models
ADD ${MODELS_URL}/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task models/
ADD ${MODELS_URL}/face_landmarker/face_landmarker/float16/latest/face_landmarker.task models/

COPY pyproject.toml .
COPY src ./src
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "teleport.app:app", "--host", "0.0.0.0", "--port", "8000"]
