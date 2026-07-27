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

## 6. Run Pipeline Demos

See [examples/README.md](../examples/README.md) for the full learning path.

Preprocessing tutorial (final step):

```bash
python -m examples.preprocessing.step_22_preprocessing_pipeline
```

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

**New photo vs new drug**

| Goal | Action |
|------|--------|
| Try another photo | Pass `--image path/to/photo.jpg` — no code change |
| Recognize a new drug | Add a row to `data/database/medicines.csv` |

YOLO detects boxes; OCR reads text; RapidFuzz matches only drugs listed in the CSV.

Legacy integration demo (verbose step-by-step output):

```bash
python -m examples.integration.legacy_multi_ocr_medicine_matching
```

---

## Project Layout (summary)

```text
medicine-box-detection-yolov8/
├── data/          samples, database, dataset config
├── docs/          architecture, roadmap, reports
├── examples/      learning scripts and usage demos
├── src/           reusable production AI modules
├── tests/         automated tests (planned)
├── requirements.txt
└── README.md
```

| Directory | Role |
|-----------|------|
| `src/` | Production-ready application logic |
| `examples/` | Step-by-step learning demonstrations |
| `docs/` | Documentation and technical reports |

---

## Next Steps

1. Review [architecture.md](architecture.md) and [roadmap.md](roadmap.md)
2. Pick a GitHub Issue (start with [#25](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/25))
3. Create the corresponding feature branch

### Run the unified pipeline

```python
from src.services import analyze_medicine_boxes, PipelineConfig

result = analyze_medicine_boxes(
    "data/samples/coklu_resim.jpg",
    config=PipelineConfig(ocr_mode="fast"),
)
print(result.detection_count, [m.medicine_name for m in result.medicines])
```

Or use the demo script:

```bash
python run_analyze.py --image data/samples/samples3.jpg --mode fast
```
