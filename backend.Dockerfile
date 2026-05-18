FROM python:3.12-slim

LABEL org.opencontainers.image.title="Videoflix Backend"
LABEL org.opencontainers.image.description="Django REST API backend for a video streaming platform with JWT authentication, Redis queue processing and HLS video streaming"
LABEL org.opencontainers.image.authors="René Theis <contact@rene-theis.de>"
LABEL org.opencontainers.image.source="https://github.com/DrPinselbecher/Videoflix_Backend"
LABEL org.opencontainers.image.version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ffmpeg \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN chmod +x backend.entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./backend.entrypoint.sh"]