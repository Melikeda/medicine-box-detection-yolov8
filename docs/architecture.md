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
Medicine Database (CSV seed → SQLite)
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

## 1. Mobile Client (Flutter) — MVP ✅

The user captures a medicine box photo with the device camera or selects one from the gallery.

**Phase 16 (Issue #30):** Splash, home, gallery picker, and image preview screens under `mobile/`.

**Phase 17 (Issue #31):** Connected to `POST /api/v1/analyze` with result screen, loading overlay, and error handling.

Also: local scan history, best-effort `POST /api/v1/scans` sync, and optional `POST /api/v1/explain` (“İlaç hakkında”).

### Responsibilities

- Image selection and preview
- Multipart upload to FastAPI (`AnalyzeApiService`)
- Loading and error states
- Display medicine name, match score, and basic drug info
- Local history + server scan sync (`ScanHistoryService`, `ScanApiService`)

### Key modules

| Module | Role |
|--------|------|
| `config/app_config.dart` | API base URL, timeouts, endpoints |
| `services/analyze_api_service.dart` | Analyze HTTP client |
| `services/explain_api_service.dart` | Explain HTTP client |
| `services/scan_api_service.dart` | Server scan-history client |
| `services/scan_history_service.dart` | Local SQLite history |
| `models/analyze_response.dart` | Response parsing |
| `utils/medicine_display.dart` | Placeholder + box label formatting |
| `screens/result_screen.dart` | Result UI |

See [Report 16](reports/16-mobile-integration.md) and [Report 23](reports/23-scan-history.md).

## 2. Backend API (FastAPI) ✅

Receives uploaded images and orchestrates the AI pipeline.

### Responsibilities

- Image validation (magic bytes, type, size)
- Temporary file handling
- Async pipeline orchestration (`asyncio.to_thread`)
- Structured JSON responses with summary counts
- Health checks and logging
- Optional LLM explanations and server scan history

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Model readiness |
| GET | `/api/v1/analyze/info` | Upload limits and formats |
| POST | `/api/v1/analyze` | Multi-box analyze |
| GET | `/api/v1/medicines` | List / search medicines |
| GET | `/api/v1/medicines/categories` | Medicine categories |
| GET | `/api/v1/medicines/{id}` | Medicine detail |
| GET | `/api/v1/explain/info` | LLM readiness (`ready`) |
| POST | `/api/v1/explain` | Gemini short explanation |
| GET | `/api/v1/scans/info` | Server scan-history info |
| GET | `/api/v1/scans` | List saved scans |
| POST | `/api/v1/scans` | Persist successful analyze JSON |
| GET | `/api/v1/scans/{id}` | Scan detail |
| DELETE | `/api/v1/scans/{id}` | Delete scan |

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
| `fast` | ~4 (2 angles × 2; early exit) | API default, CPU-friendly |
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
| Current | CSV (seed) + SQLite (runtime) | **131** drugs |
| Production (later) | PostgreSQL | — |

Fields: `medicine_id`, `medicine_name`, `brand_name`, `active_ingredient`, `dosage`, `form`, `category`

Same SQLite file also stores the server `scans` table for analyze-history sync.

See [Report 24](reports/24-medicine-database-final-refresh.md).

---

## 8. Large Language Model (LLM) ✅

Issue [#8](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/8) — natural-language explanations after a successful match.

| Component | Technology |
|-----------|------------|
| Provider | Google Gemini API (free tier) |
| Primary model | `gemini-flash-latest` |
| Fallback | `gemini-flash-lite-latest` |
| Endpoint | `POST /api/v1/explain` |
| Mobile UI | Expandable “İlaç hakkında” card |

See [Report 21](reports/21-llm-integration.md).

---

## 9. Server Scan History ✅

| Component | Detail |
|-----------|--------|
| Storage | SQLite `scans` table (analyze JSON; images stay on device) |
| API | `POST/GET/DELETE /api/v1/scans` |
| Mobile | Local history first; best-effort server sync |
| Auth | Not yet — scans are global until user accounts exist |

See [Report 23](reports/23-scan-history.md).

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
YOLOv8 → Crop → OpenCV → EasyOCR → Normalize → RapidFuzz → SQLite (131)
   │
   ▼
JSON Response → Flutter Result Screen
   │
   ├─► local history + POST /api/v1/scans
   ▼ (optional, on demand)
POST /api/v1/explain → Gemini → "İlaç hakkında" card
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

- SQLite migration (#27) ✅
- Automated tests (#28) ✅
- Docker deployment (#29) ✅
- Flutter mobile MVP (#30–#31) ✅
- LLM explain (#8) ✅
- Server scan history ✅
- PostgreSQL migration
- Cloud deployment / HTTPS reverse proxy
- Per-user auth for private scan lists
- Barcode / QR code support
- YOLO retrain with blurry and negative samples
- Multilingual OCR
