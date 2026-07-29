# Medicine Box Detection System

<p align="center">
  <strong>Scan a medicine box · Identify the drug · Get basic information</strong>
</p>

<p align="center">
  An AI-powered computer vision project that detects medicine boxes, reads package text with OCR,
  matches drug names with fuzzy search, and delivers results through a FastAPI backend and Flutter mobile app.
</p>

<p align="center">
  Computer Engineering internship project · Modular Python architecture · Git Feature Branch Workflow
</p>

---

## About

This repository contains an intelligent **medicine box recognition system**. It is not a single model but a multi-stage pipeline that combines object detection, image processing, OCR, and database matching.

### What works today

| Stage | Technology | Status |
|-------|------------|--------|
| Object detection | YOLOv8n | Done |
| Image preprocessing | OpenCV | Done |
| Text recognition | EasyOCR | Done |
| Name matching | RapidFuzz | Done |
| Medicine database | CSV seed + SQLite (38 records) | Done |
| End-to-end pipeline | `src/services/` + `PipelineManager` | Done |
| OCR modes (fast/accurate) | `PipelineConfig.ocr_mode` | Done |
| REST backend | FastAPI | Done |
| Analyze API | `POST /api/v1/analyze` | Done |
| Medicine DB | SQLite + SQLAlchemy | Done |
| Multi-box detection | `analyze_medicine_boxes()` | Done |
| Real-world matching | Fallback YOLO, partial brand, dosage filter | Done |

### What we are building next

| Stage | Technology | GitHub Issue |
|-------|------------|--------------|
| Automated tests | pytest | Done |
| Docker deployment | Docker Compose | [#29](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/29) |
| Mobile app | Flutter (Android MVP) | [#30](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/30) |
| Mobile integration | Gallery → API → result | [#31](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/31) |

Post-MVP: PostgreSQL, LLM explanations ([#32](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/32)).

---

## System Workflow

```text
Flutter Mobile App
        │
        ▼
POST /api/v1/analyze  (FastAPI)
        │
        ▼
YOLOv8 → Crop → OpenCV → EasyOCR → RapidFuzz → Medicine DB
        │
        ▼
JSON response → Mobile result screen
```

The AI pipeline itself is implemented in Python under `src/`. Learning scripts and demos live under `examples/`. The backend and mobile layers are the current development focus.

---

## Code layout

| Directory | Purpose |
|-----------|---------|
| `src/` | Reusable, production-ready application logic |
| `examples/` | Step-by-step learning scripts and usage demos |
| `docs/` | Architecture, roadmap, setup guide, technical reports |
| `tests/` | Automated tests (`pytest`) |

See [examples/README.md](examples/README.md) for the full learning path.

---

## Project Structure

```text
medicine-box-detection-yolov8/
├── data/
│   ├── database/          # medicines.csv
│   ├── dataset/           # YOLO training config (images not in repo)
│   └── samples/           # Test images
├── docs/                  # Architecture, roadmap, setup, reports
├── examples/              # Learning scripts (not production code)
│   ├── preprocessing/     # OpenCV tutorials (22 steps)
│   ├── ocr/               # OCR learning scripts
│   ├── database/          # CSV database examples
│   ├── matching/          # RapidFuzz examples
│   ├── integration/       # Legacy step-by-step integration demos
│   ├── pipeline/          # Current analyze_medicine_box demo
│   └── README.md
├── src/
│   ├── preprocessing/     # OpenCV modules
│   ├── ocr/               # EasyOCR pipeline
│   ├── matching/          # RapidFuzz matcher + OCR text normalizer
│   ├── database/          # CSV reader
│   ├── services/          # Unified pipeline (analyze_medicine_box)
│   └── integration/       # YOLO + OCR glue code
├── src/train.py           # YOLO training script
├── src/predict.py         # YOLO inference script
├── backend/               # FastAPI application
│   └── app/
│       ├── main.py        # App factory + lifespan
│       ├── config.py      # API settings
│       ├── routers/       # health, analyze
│       ├── services/      # analyze_service, upload_validator
│       └── schemas/       # Pydantic response models
├── run_api.py             # FastAPI / Uvicorn entry point
├── run_analyze.py         # CLI pipeline runner (analyze_medicine_boxes)
└── requirements.txt
```

Planned additions: `mobile/` (Flutter).

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Detection | YOLOv8n, Ultralytics, PyTorch |
| Preprocessing | OpenCV |
| OCR | EasyOCR |
| Matching | RapidFuzz |
| Data | CSV (seed) + SQLite (runtime) |
| Backend | FastAPI, Pydantic, Uvicorn |
| Mobile (planned) | Flutter, Dart |
| DevOps | pytest (Done), Docker (planned) |

See [docs/technology-selection.md](docs/technology-selection.md) for rationale.

---

## Quick Start

```bash
git clone https://github.com/Melikeda/medicine-box-detection-yolov8.git
cd medicine-box-detection-yolov8
python -m venv venv

# Windows
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Train YOLOv8

```bash
python src/train.py
```

### Run detection

```bash
python src/predict.py
```

### Run main pipeline (production entry point)

```bash
# Single or multi-box photo (fast mode, recommended)
python run_analyze.py --image data/samples/samples3.jpg --mode fast

# Multi-box sample
python run_analyze.py --image data/samples/coklu_resim.jpg --mode fast

# Accurate mode (slow on CPU)
python run_analyze.py --image data/samples/aferin_forte.jpg --mode accurate

# JSON output
python run_analyze.py --image data/samples/parol_plus.jpg --mode fast --json
```

### Image vs CSV — important

| Action | What to do |
|--------|------------|
| Test a **new photo** | Use `--image path/to/photo.jpg` — no code change needed |
| Support a **new drug** | Add a row to `data/database/medicines.csv` |
| Photo has a box detected | Does **not** mean the drug is in CSV |
| Pipeline stages | YOLO detects box → OCR reads text → RapidFuzz matches **CSV only** |

YOLO finds medicine **boxes**. OCR reads **text**. RapidFuzz matches only against drugs listed in `medicines.csv` (38 records today).

**Real-world tips:** Use steady, well-lit photos. Blurry images trigger YOLO fallback mode. Drugs not in CSV return `not_found`.

### Run FastAPI backend

```bash
# Install new backend dependencies first
pip install fastapi uvicorn[standard] python-multipart pydantic-settings

# Start API (loads YOLO + EasyOCR + CSV once at startup)
python run_api.py
```

Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | API and model readiness |
| GET | `/api/v1/analyze/info` | Upload limits and supported formats |
| POST | `/api/v1/analyze` | Upload image, analyze all boxes |
| GET | `/api/v1/medicines` | List / search medicines (SQLite) |
| GET | `/api/v1/medicines/categories` | Medicine categories |
| GET | `/api/v1/medicines/{id}` | Medicine detail |

Query parameter for analyze:

- `mode=fast` (default) — ~8 OCR variants per box
- `mode=accurate` — ~52 OCR variants per box (slow on CPU)

Example analyze request:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze?mode=fast" \
  -F "file=@data/samples/samples3.jpg"
```

Example info request:

```bash
curl http://127.0.0.1:8000/api/v1/analyze/info
```

Interactive docs: http://127.0.0.1:8000/docs

### Run pipeline demo (examples wrapper)

```bash
python -m examples.pipeline.analyze_medicine_box_demo
```

### Run legacy integration demo (verbose output)

```bash
python -m examples.integration.legacy_multi_ocr_medicine_matching
```

### Run pipeline from Python

```python
from src.services import analyze_medicine_box

result = analyze_medicine_box("data/samples/samples3.jpg")
print(result.medicine, result.match_score)
```

Full setup instructions: [docs/setup-guide.md](docs/setup-guide.md)

---

## Development Status

| Phase | Status |
|-------|--------|
| Project setup & documentation | Done |
| Dataset preparation (Roboflow) | Done |
| YOLOv8 training | Done |
| OpenCV preprocessing | Done |
| OCR integration | Done |
| Medicine matching (RapidFuzz) | Done |
| Pipeline unification | Done ([#23](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/23)) |
| Pipeline servicification | Done ([#24](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/24)) |
| FastAPI backend | Done ([#25](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/25)) |
| Analyze API + matching improvements | Done ([#26](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/26)) |
| SQLite database | Done ([#27](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/27)) |
| Automated tests | Done ([#28](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/28)) |
| Flutter mobile MVP | Planned ([#30](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/30)-[#31](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/31)) |
| LLM integration | Post-MVP ([#8](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/8)) |

Detailed roadmap: [docs/roadmap.md](docs/roadmap.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| [architecture.md](docs/architecture.md) | System design |
| [roadmap.md](docs/roadmap.md) | Development phases and GitHub issues |
| [setup-guide.md](docs/setup-guide.md) | Environment setup |
| [technology-selection.md](docs/technology-selection.md) | Why each tool was chosen |
| [reports/](docs/reports/) | Step-by-step technical reports (phases 1–13) |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`feature/your-feature`)
3. Commit with clear messages
4. Open a Pull Request

Follow the existing modular structure in `src/` and link PRs to GitHub Issues.

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Author

**Melike** — Computer Engineering Student

GitHub: [Melikeda](https://github.com/Melikeda)

---

<p align="center">
  If this project was useful to you, consider giving it a star.
</p>
