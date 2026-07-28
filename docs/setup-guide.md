# Setup Guide

Environment setup for the **Medicine Box Detection System**.

---

## Prerequisites

| Software | Purpose |
|----------|---------|
| Python 3.12+ | AI pipeline and backend |
| Git | Version control |
| VS Code (recommended) | Development IDE |

Future phases will also require Flutter SDK and Docker (not needed for the current AI pipeline work).

---

## 1. Clone the Repository

```bash
git clone https://github.com/Melikeda/medicine-box-detection-yolov8.git
cd medicine-box-detection-yolov8
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Activate — Windows (PowerShell)

```powershell
venv\Scripts\Activate.ps1
```

### Activate — Windows (CMD)

```cmd
venv\Scripts\activate
```

### Activate — Linux / macOS

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

First run downloads PyTorch and EasyOCR models — this may take several minutes.

---

## 4. Verify Installation

```bash
python --version
pip list
```

---

## 5. YOLO Model

Training produces weights under `runs/detect/`. For inference scripts, point to your trained `best.pt` file. Model files (`.pt`) are excluded from Git.

Train from scratch:

```bash
python src/train.py
```

Run detection on a sample image:

```bash
python src/predict.py
```

---

## 6. Run Pipeline (CLI)

See [examples/README.md](../examples/README.md) for the full learning path.

Unified pipeline (fast mode, recommended):

```bash
python run_analyze.py --image data/samples/samples3.jpg --mode fast
```

Multi-box sample:

```bash
python run_analyze.py --image data/samples/coklu_resim.jpg --mode fast
```

Accurate mode (slow on CPU):

```bash
python run_analyze.py --image data/samples/samples3.jpg --mode accurate
```

JSON output:

```bash
python run_analyze.py --image data/samples/parol_plus.jpg --mode fast --json
```

**New photo vs new drug**

| Goal | Action |
|------|--------|
| Try another photo | Pass `--image path/to/photo.jpg` — no code change |
| Recognize a new drug | Add a row to `data/database/medicines.csv` |

YOLO detects boxes; OCR reads text; RapidFuzz matches only drugs listed in the CSV (38 records).

---

## 7. Run FastAPI Backend

```bash
python run_api.py
```

Server starts at http://127.0.0.1:8000

| Endpoint | Description |
|----------|-------------|
| `GET /health` | API and model readiness |
| `GET /api/v1/analyze/info` | Upload limits, formats, OCR modes |
| `POST /api/v1/analyze?mode=fast` | Upload image (`file` field) |

Example:

```bash
curl http://127.0.0.1:8000/health
curl -X POST "http://127.0.0.1:8000/api/v1/analyze?mode=fast" \
  -F "file=@data/samples/coklu_resim.jpg"
```

Interactive docs: http://127.0.0.1:8000/docs

Restart the server after pulling code changes.

---

## 8. Troubleshooting

| Problem | Likely cause | What to do |
|---------|--------------|------------|
| YOLO count = 0 | Blurry photo, high confidence threshold | Retake photo; fallback runs automatically at conf 0.25 |
| `not_found` | Drug not in CSV or OCR unreadable | Add drug to CSV; use `mode=accurate` |
| Wrong drug match | Dosage text matched (fixed in latest) | Pull latest `main`; restart API |
| Ibucold vs Ibucold C | OCR read `€` instead of `C` | Fixed via text normalizer |
| Slow analyze | CPU + many boxes | Use `mode=fast`; reduce box count in photo |

---

## Project Layout (summary)

```text
medicine-box-detection-yolov8/
├── backend/app/   FastAPI application
├── data/          samples, database, dataset config
├── docs/          architecture, roadmap, reports
├── examples/      learning scripts and usage demos
├── src/           reusable production AI modules
├── tests/         automated tests (planned)
├── run_api.py     FastAPI entry point
├── run_analyze.py CLI pipeline runner
├── requirements.txt
└── README.md
```

| Directory | Role |
|-----------|------|
| `src/` | Production-ready application logic |
| `backend/` | REST API layer |
| `examples/` | Step-by-step learning demonstrations |
| `docs/` | Documentation and technical reports |

---

## Next Steps

1. Review [architecture.md](architecture.md) and [roadmap.md](roadmap.md)
2. Read [Report 10](reports/10-fastapi-analyze-api.md) and [Report 11](reports/11-real-world-matching-improvements.md)
3. Pick the next GitHub Issue — start with [#27](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/27) (SQLite)

### Run the unified pipeline from Python

```python
from src.services import analyze_medicine_boxes, PipelineConfig

result = analyze_medicine_boxes(
    "data/samples/coklu_resim.jpg",
    config=PipelineConfig(ocr_mode="fast"),
)
print(result.detection_count)
for box in result.medicines:
    print(box.status, box.medicine_name, box.matching_score)
```
