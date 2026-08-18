# Yolocilin — Technical Report

CV-facing product summary for the Computer Engineering internship.  
Phase diaries (01–29) stay in [`docs/reports/`](reports/README.md). This file is the current snapshot.

**Author:** Melike Eda Külahcı  
**Repo:** [github.com/Melikeda/yolocilin](https://github.com/Melikeda/yolocilin)  
**API / app version:** `1.0.0` · [GitHub Release](https://github.com/Melikeda/yolocilin/releases/tag/v1.0.0)  
**License:** MIT

---

## 1. Problem

Pharmacy-shelf photos are hard to identify by eye when print is small, rotated, or several boxes share a frame. A guessed brand is worse than no answer.

Yolocilin turns a phone photo into a **catalog identity** (or an explicit `not_found`), then optionally a short explanation. It is **not medical advice**.

---

## 2. What shipped

| Layer | Deliverable |
|-------|-------------|
| Vision | Single-class YOLOv8n box detection → crop |
| OCR | OpenCV variants + **EasyOCR** (CPU; Fast / Accurate) |
| Identity | RapidFuzz against SQLite (**1163** TİTCK-enriched drugs) |
| Barcode | Optional EAN-13 / DataMatrix (zxing-cpp) before OCR |
| API | FastAPI: analyze, medicines, barcode, explain, scans |
| Client | Flutter Android app **Yolocilin** (`applicationId` `com.yolocilin.app`) |
| Ops | Docker, GitHub Actions, production CORS / docs hardening |

Kaggle set: **395** privacy-cleaned `medicine-box` images (CC BY 4.0) — [melikeklahc/yolocilin-medicine-box-detection](https://www.kaggle.com/datasets/melikeklahc/yolocilin-medicine-box-detection).

---

## 3. Architecture

```text
Yolocilin (Flutter, TR/EN UI)
        │
        ▼
POST /api/v1/analyze
        │
        ▼
YOLOv8 → crop → (optional GTIN) → OpenCV → EasyOCR → RapidFuzz → SQLite
        │
        ├─► local history + POST /api/v1/scans
        ▼
JSON → result screen
        │
        ▼ (optional)
POST /api/v1/explain → Gemini (locale-aware) or catalog fallback
```

Production code lives in `src/` and `backend/`. `examples/` is the learnable path. Design notes: [architecture.md](architecture.md) · [technology-selection.md](technology-selection.md).

---

## 4. Pipeline decisions

**Detection.** YOLOv8n, one class. Confidence fallback if the primary pass misses a box.

**OCR.** EasyOCR stayed after a PaddleOCR trial on the same crops and matcher ([Report 26](reports/26-ocr-engine-comparison.md)). Fast mode runs a short variant list; a deep retry runs only if unmatched. Typical CPU wait is **tens of seconds to a few minutes** per photo ([Report 25](reports/25-e2e-performance.md)).

**Matching.** Prefer **no card** over a **wrong drug**. Three-letter suffix OCR (`fen`, `alm`, `pal`) is `not_found`. Fast-mode early-exit requires score ≥ 95. Exact short brands (Etol) still match ([Report 27](reports/27-matching-reliability.md)).

**Barcode.** Parallel path, not a replacement. Analyze tries the crop (then full frame) before OCR. Unknown / missing codes continue to EasyOCR ([Report 28](reports/28-barcode-reading.md)). Map: 2043 GTINs → 1041 of 1163 catalog rows.

**Explain.** Gemini is optional (`LLM_ENABLED`). Prompts are English; JSON string values follow `locale=tr|en`. On 503 / missing key, the UI fills from catalog text.

---

## 5. Data

- Seed CSV → SQLite `medicines` (display names stay **Turkish**).
- `medicine_barcodes` is 1:N (package GTIN → `medicine_id`).
- `scans` stores server history (global until auth; out of this internship round).
- Catalog growth: 38 → 107 → 131 → 153 → **1163** (TİTCK SKRS queries). Historical counts in older reports are outdated.

---

## 6. API and mobile

| Endpoint family | Role |
|-----------------|------|
| `POST /api/v1/analyze` | Box photo → per-box match + timings |
| `GET /api/v1/medicines` | Catalog list / search |
| `GET/POST /api/v1/barcode/*` | GTIN lookup / image decode |
| `POST /api/v1/explain` | Short usage / warnings (Gemini or catalog) |
| `POST/GET/DELETE /api/v1/scans` | Server history (`DELETE` needs `SCANS_API_KEY` in production) |

Android: gallery + camera, bilingual UI, local SQLite history, best-effort scan sync, live **Barkod tara**. iOS is future work.

---

## 7. Quality and operations

- Backend: `ruff check` + `pytest` (Python 3.11 CI). Analyze OCR is mocked in CI.
- Mobile: `flutter analyze` + `flutter test`.
- Live smoke: `scripts/e2e_api_flow.py`; timings: `scripts/benchmark_analyze.py`.
- Docker CPU image; GitHub Actions for tests and image build.
- Production: explicit `CORS_ORIGINS`, `/docs` off, upload size + magic-byte checks, per-IP rate limits, Firebase config gitignored.

---

## 8. Limits (honest)

| Constraint | Reality |
|------------|---------|
| Hardware | EasyOCR on **CPU** — slow, sequential variants |
| Photos | Blur, distance, multi-box carpet shots → `not_found` is expected |
| Catalog | 1163 rows is a seed, not the full Turkish market |
| Scans | No per-user auth (global table) |
| Rate limit | In-memory, single process |
| Explain | Gemini quota / missing key → catalog fallback, not a clinical leaflet |

---

## 9. Out of scope this round

PostgreSQL, cloud HTTPS deploy, per-user auth, iOS.

---

## 10. Where to go next

| Need | Doc |
|------|-----|
| Clone and run | [README](../README.md) · [setup-guide.md](setup-guide.md) |
| Phase history | [reports/](reports/README.md) |
| Remaining work | [roadmap.md](roadmap.md) |
| Security | [SECURITY.md](../SECURITY.md) |
| Changes | [CHANGELOG.md](../CHANGELOG.md) |
