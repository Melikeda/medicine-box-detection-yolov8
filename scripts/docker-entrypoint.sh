#!/bin/sh
set -eu

MODEL_PATH="${YOLO_MODEL_PATH:-runs/detect/runs/detect/medicine_box_yolov8n-2/weights/best.pt}"

if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: YOLO model not found at: $MODEL_PATH"
    echo ""
    echo "Train the model locally (python src/train.py) or copy best.pt to the expected path,"
    echo "then mount it into the container via docker-compose volumes."
    echo "See docs/reports/14-docker-containerization.md for details."
    exit 1
fi

echo "Docker entrypoint: seeding SQLite from CSV (if needed)..."
python scripts/seed_sqlite.py

echo "Docker entrypoint: starting API..."
exec "$@"
