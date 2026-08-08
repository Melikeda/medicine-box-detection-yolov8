#!/bin/sh
set -eu

MODEL_PATH="${YOLO_MODEL_PATH:-runs/detect/runs/detect/medicine_box_yolov8n-2/weights/best.pt}"

if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: YOLO model not found at: $MODEL_PATH"
    echo ""
    echo "Also accepted locally (host) by the Python resolver:"
    echo "  - runs/detect/medicine_box_yolov8n/weights/best.pt  (python src/train.py)"
    echo "  - models/best.pt"
    echo ""
    echo "For Docker, mount your best.pt via YOLO_MODEL_HOST_PATH / YOLO_MODEL_PATH"
    echo "(see docker-compose.yml and models/README.md)."
    echo "Docs: docs/reports/14-docker-containerization.md"
    exit 1
fi

echo "Docker entrypoint: seeding SQLite from CSV (if needed)..."
python scripts/seed_sqlite.py

echo "Docker entrypoint: starting API..."
exec "$@"
