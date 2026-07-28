# 🏗️ AI-Powered Medicine Box Detection System Architecture

## 📌 Overview

The **AI-Powered Medicine Box Detection System** is a modular Computer Vision application that combines Object Detection, Image Processing, Optical Character Recognition (OCR), Fuzzy String Matching, a REST API backend, and a mobile client.

The primary objective is to let a user photograph a medicine box with their phone, identify the drug through an AI pipeline, and receive structured medicine information on the result screen.

The project follows a **modular architecture**, allowing each component to be developed, tested, maintained, and improved independently.

---

# 🔄 High-Level Workflow

```text
User (Flutter Mobile App)
 │
 ▼
Select / Capture Image
 │
 ▼
POST /api/v1/analyze (FastAPI) ✅
 │
 ▼
YOLOv8 Detection (+ confidence fallback)
 │
 ▼
Crop Detected Medicine Box(es)
 │
 ▼
OpenCV Preprocessing
 │
 ▼
EasyOCR (fast / accurate mode)
 │
 ▼
OCR Normalization + Candidate Processing
 │
 ▼
RapidFuzz Matching
 │
 ▼
Medicine Database (CSV → SQLite planned)
 │
 ▼
JSON Response (per-box status + summary)
 │
 ▼
Mobile Result Screen
 │
 ▼
(Optional) LLM Explanation
```

---

# 🧩 System Components

## 1. Mobile Client (Flutter) — Planned

The user selects a medicine box photo from the gallery (MVP) or captures one with the camera (later version).

### Responsibilities

- Image selection and preview
- API communication
- Loading and error states
- Display medicine name, match score, and basic drug info

---

## 2. Backend API (FastAPI) ✅

Receives uploaded images and orchestrates the AI pipeline.

### Responsibilities

- Image validation (magic bytes, type, size)
- Temporary file handling
- Async pipeline orchestration (`asyncio.to_thread`)
- Structured JSON responses with summary counts
- Health checks and logging

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Model readiness |
| GET | `/api/v1/analyze/info` | Upload limits and formats |
| POST | `/api/v1/analyze` | Multi-box analyze |

Entry point: `run_api.py`

---

## 2.1 Pipeline Service Layer (`src/services/`) ✅

Unified orchestration for the AI pipeline.

### Key Entry Points

```python
from src.services import analyze_medicine_boxes, PipelineManager

# CLI / scripts
result = analyze_medicine_boxes("data/samples/coklu_resim.jpg")

# FastAPI startup
manager = PipelineManager.get_instance()
manager.load()
result = manager.analyze_all(image_path)
```

### Modules

| Module | Role |
|--------|------|
| `config.py` | `PipelineConfig` — thresholds, OCR modes |
| `pipeline_manager.py` | Singleton — load models once |
| `detection_service.py` | YOLO + adaptive confidence fallback |
| `ocr_service.py` | OCR with fast/accurate modes |
| `matching_service.py` | CSV + RapidFuzz + reliability checks |
| `candidate_processor.py` | OCR candidate expansion and filtering |
| `medicine_analyzer.py` | Public API and result dataclasses |

### Matching layer (`src/matching/`)

| Module | Role |
|--------|------|
| `medicine_matcher.py` | RapidFuzz scoring, dosage detection |
| `text_normalizer.py` | OCR confusable fixes (`€` → `c`) |

---

## 3. Object Detection (YOLOv8) ✅

YOLOv8 detects all medicine boxes within the uploaded image.

### Adaptive fallback

| Threshold | Value | Purpose |
|-----------|-------|---------|
| Primary | 0.40 | Standard detection |
| Fallback | 0.25 | Blurry / low-confidence photos |

If primary finds zero boxes, or weak detections with fewer boxes than fallback, the lower threshold is used.

### Output

- Bounding box coordinates per box
- Detection confidence score
- Cropped medicine box images

---

## 4. Image Preprocessing (OpenCV) ✅

The cropped image is enhanced before OCR using multi-variant preprocessing (scale, sharpen, rotation).

---

## 5. OCR (EasyOCR) ✅

| Mode | Variants per box | Use case |
|------|------------------|----------|
| `fast` | ~8 (4 angles × 2) | API default, CPU-friendly |
| `accurate` | ~52 | Difficult / rotated text |

---

## 6. Medicine Name Matching (RapidFuzz) ✅

OCR output is compared with CSV fields: `medicine_name`, `brand_name`, `active_ingredient`.

### Reliability guards

- Minimum match score (80)
- Name coverage ratio (prevents single-letter false positives)
- Partial brand matching for blurry reads (`fen` → Nurofen)
- Dosage-only text filtering (`250 mg / 300 mg tablet` patterns)
- `not_medicine_box` status for YOLO false positives (UNO cards, etc.)

### Per-box status

`matched` | `not_found` | `not_medicine_box` | `error`

---

## 7. Medicine Database ✅

| Stage | Technology | Records |
|-------|------------|---------|
| Current | CSV file | 38 drugs |
| MVP target | SQLite + SQLAlchemy (#27) | — |
| Production | PostgreSQL | — |

Fields: `medicine_id`, `medicine_name`, `brand_name`, `active_ingredient`, `dosage`, `form`, `category`

---

## 8. Large Language Model (LLM) — Post-MVP

Issue #8 — natural-language explanations after a successful match.

---

# 🔁 Data Flow

```text
Flutter App
   │
   ▼
FastAPI (analyze_service)
   │
   ▼
PipelineManager.analyze_all()
   │
   ▼
YOLOv8 → Crop → OpenCV → EasyOCR → Normalize → RapidFuzz → CSV
   │
   ▼
JSON Response → Flutter Result Screen
```

---

# 🎯 Design Principles

- Modular architecture with single-responsibility services
- Clear separation: `src/` (production) vs `examples/` (learning)
- AI models loaded once at backend startup
- REST + JSON for mobile communication
- Git Feature Branch Workflow with GitHub Issues
- Incremental delivery: AI pipeline → API → mobile MVP → advanced features

---

# 🚀 Future Improvements

- SQLite migration (#27)
- Automated tests (#28)
- Docker deployment (#29)
- Flutter mobile MVP (#30–#31)
- Barcode / QR code support
- User scan history
- YOLO retrain with blurry and negative samples
- Multilingual OCR
