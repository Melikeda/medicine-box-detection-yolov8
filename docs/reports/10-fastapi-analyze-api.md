# Report 10 — FastAPI Backend & Analyze API

## Overview

Phases 11–12 add a production FastAPI backend with health checks, image upload validation, and a mobile-ready analyze endpoint that runs the full multi-box pipeline.

**Branches:** `feature/fastapi-foundation`, `feature/analyze-endpoint`  
**GitHub Issues:** #25, #26  
**Merged to:** `main` (commit `57789fe`)

---

## Objectives

### Phase 11 — FastAPI foundation (#25)

- [x] Set up FastAPI project structure under `backend/app/`
- [x] Add config, logging, and exception handling
- [x] Implement `GET /health` endpoint
- [x] Load YOLO + EasyOCR + CSV once at startup via `PipelineManager`

### Phase 12 — Analyze API (#26)

- [x] Implement `POST /api/v1/analyze` with multipart upload
- [x] Validate image type (magic bytes) and file size
- [x] Return structured JSON response for mobile app
- [x] Add `GET /api/v1/analyze/info` and `mode` query parameter (`fast` | `accurate`)
- [x] Include per-box status, summary counts, and `processing_time_ms`

---

## Backend Structure

```text
backend/app/
├── main.py              # App factory + lifespan
├── config.py            # ApiSettings (upload limits, OCR mode)
├── exceptions.py        # HTTP error types
├── routers/
│   ├── health.py        # GET /health
│   └── analyze.py       # GET/POST /api/v1/analyze
├── schemas/
│   └── analyze.py       # Pydantic request/response models
└── services/
    ├── analyze_service.py    # Upload + async pipeline orchestration
    └── upload_validator.py   # Magic-byte and metadata validation
```

Entry point: `run_api.py`

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | API readiness, model load status, medicine count |
| GET | `/api/v1/analyze/info` | Upload limits, allowed formats, OCR modes |
| POST | `/api/v1/analyze?mode=fast` | Upload image (`file` field), analyze all boxes |

### Analyze response (per box)

| Field | Description |
|-------|-------------|
| `box_index` | 1-based box order |
| `bounding_box` | YOLO crop coordinates |
| `yolo_confidence` | Detection score |
| `ocr_text` | Best OCR text used for matching |
| `medicine_name` | Matched drug name (if any) |
| `matching_score` | RapidFuzz score (0–100) |
| `status` | `matched` \| `not_found` \| `not_medicine_box` \| `error` |
| `medicine` | Full CSV row when matched |

### Summary block

`summary.matched_count`, `not_found_count`, `not_medicine_box_count`, `error_count`

---

## Usage

```bash
pip install -r requirements.txt
python run_api.py
```

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/v1/analyze/info
curl -X POST "http://127.0.0.1:8000/api/v1/analyze?mode=fast" \
  -F "file=@data/samples/coklu_resim.jpg"
```

Interactive docs: http://127.0.0.1:8000/docs

---

## Design Decisions

- **Async thread pool:** `asyncio.to_thread()` runs CPU-heavy pipeline without blocking the event loop
- **Temporary files:** Uploaded bytes saved to a temp file, deleted after analysis
- **Singleton pipeline:** Models loaded once in FastAPI lifespan — not per request
- **Mobile-first JSON:** Filename, summary, timing, and per-box status for Flutter UI

---

## Next Phase

Issue #27 — SQLite migration — completed; see [Report 12](12-sqlite-database.md).  
Issue #28 — Automated tests — completed; see [Report 13](13-automated-testing.md).  
Next: Issue #29 — Docker containerization.
