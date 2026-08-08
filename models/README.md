# Models directory

Optional place to drop a trained YOLO weight file for local development.

## Important

- **Weights are not committed to Git** (`.gitignore` excludes `*.pt`).
- The pipeline does **not** require this folder. It auto-resolves weights in this order:

  1. `runs/detect/runs/detect/medicine_box_yolov8n-2/weights/best.pt`  
     (legacy nested Ultralytics run — Docker Compose default)
  2. `runs/detect/medicine_box_yolov8n/weights/best.pt`  
     (output of `python src/train.py`)
  3. `runs/detect/medicine_box_yolov8n-2/weights/best.pt`
  4. **`models/best.pt`** ← optional manual copy here

Override anytime with `YOLO_MODEL_PATH` in `.env` / Compose.

## Quick options

```powershell
# A) Train (writes under runs/detect/medicine_box_yolov8n/)
python src/train.py

# B) Copy an existing best.pt into this folder
copy path\to\best.pt models\best.pt

# C) Point env at any file
# YOLO_MODEL_PATH=D:\weights\best.pt
```

Resolver implementation: `src/services/model_paths.py`.
