# Medicine Box Detection API — CPU image (FastAPI + YOLOv8 + EasyOCR)
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

# OpenCV / EasyOCR runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend/ backend/
COPY src/ src/
COPY scripts/ scripts/
COPY data/database/medicines.csv data/database/medicines.csv
COPY run_api.py .

RUN chmod +x scripts/docker-entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

ENTRYPOINT ["scripts/docker-entrypoint.sh"]
CMD ["python", "run_api.py"]
