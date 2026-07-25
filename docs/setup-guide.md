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

OpenCV tutorial:

```bash
python -m examples.opencv.step_22_preprocessing_pipeline
```

Full YOLO + OCR + RapidFuzz demo:

```bash
python -m examples.rapidfuzz.step_10_multi_ocr_medicine_matching
```

---

## Project Layout (summary)

```text
medicine-box-detection-yolov8/
├── data/          samples, database, dataset config
├── docs/          architecture, roadmap, reports
├── examples/      learning scripts
├── src/           production AI modules
├── requirements.txt
└── README.md
```

---

## Next Steps

1. Review [architecture.md](architecture.md) and [roadmap.md](roadmap.md)
2. Pick a GitHub Issue (start with [#23](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/23))
3. Create the corresponding feature branch
