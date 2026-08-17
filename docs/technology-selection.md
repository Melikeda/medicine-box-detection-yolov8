# Technology Selection

Technologies behind **Yolocilin** (Medicine Box Detection, Identification and Information System) and why they were chosen.

Product name across GitHub, Kaggle, Medium notes and the Android app: **Yolocilin**.

---

## Python

**Role:** Main programming language for the AI pipeline and backend.

**Why:** Strong ecosystem for computer vision (OpenCV, PyTorch, Ultralytics), rapid prototyping, and easy integration with FastAPI.

---

## YOLOv8n

**Role:** Detect medicine boxes in photos.

**Why:** Lightweight enough for CPU inference on a development machine; good accuracy for a single-class detection task; well documented via Ultralytics.

---

## OpenCV

**Role:** Image preprocessing before OCR (resize, CLAHE, thresholding, sharpening, rotation).

**Why:** Industry standard for image processing; modular functions reusable across the project.

---

## EasyOCR

**Role:** Engine to read medicine names from cropped box images.

**Why:** Supports Turkish and English; simple API; works with the OpenCV variant pipeline; already in the production venv and Docker image.

A PaddleOCR trial (same YOLO crops + matcher) did not improve identity accuracy enough to justify the extra install or CPU cost. **Not adopted.** See [Report 26](reports/26-ocr-engine-comparison.md).

---

## RapidFuzz

**Role:** Match noisy OCR output to medicine names in the database.

**Why:** Fast fuzzy string matching; handles OCR typos (e.g. `afern` → `A-Ferin`); no heavy ML dependency.

---

## zxing-cpp

**Role:** Optional barcode / GTIN reader (EAN-13, DataMatrix) as a parallel identity path.

**Why:** Exact lookup is faster than OCR when the code is in frame; official wheels on Windows and Linux (no libzbar). OCR remains the fallback. See [Report 28](reports/28-barcode-reading.md).

---

## CSV / SQLite / PostgreSQL

| Stage | Technology | Why |
|-------|------------|-----|
| Current | CSV + SQLite | Catalog (**1163**) + barcode map + `scans` history table |
| Production (later) | PostgreSQL | Concurrent users; optional when scaling cloud |

---

## FastAPI ✅

**Role:** REST API backend for the mobile app.

**Status:** Implemented — health, analyze, medicines, barcode, explain, scans; upload validation; async pipeline.

**Why:** Native async support, automatic OpenAPI docs, Pydantic validation, straightforward file upload handling, excellent Python AI ecosystem fit.

---

## Flutter (Yolocilin)

**Role:** Cross-platform mobile app (Android MVP first), branded **Yolocilin**.

**Why:** Single codebase for Android and future iOS; mature camera/gallery packages (`image_picker`); good UI tooling for internship-level development.

**Status:** Analyze + camera + bilingual UI + local/server history + explain client — see [mobile/README.md](../mobile/README.md), [Report 15](reports/15-flutter-foundation.md), [Report 16](reports/16-mobile-integration.md).

---

## Docker

**Role:** Package backend, models, and dependencies for consistent deployment.

**Why:** Eliminates "works on my machine" issues; simplifies sharing the backend across Windows/Linux.

**Status:** Implemented in Phase 15 ([#29](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/29)) — see [Report 14](reports/14-docker-containerization.md).

---

## Large Language Model — Post-MVP ✅

**Role:** Generate natural-language medicine explanations after a successful match.

**Why:** Adds user-friendly information beyond raw database fields; strengthens the AI-powered product story.

**Status:** Implemented in Phase 18 ([#8](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/8)) — Gemini free tier via `POST /api/v1/explain`. See [Report 21](reports/21-llm-integration.md).

---

## Deprecated Direction: Streamlit

Streamlit was considered for a web UI early in the project. The direction changed to **Flutter + FastAPI** for a real mobile product. Issue [#7](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/7) was closed accordingly.

---

## Roboflow

**Role:** Dataset annotation, augmentation, and YOLO export.

**Why:** Simplified labeling workflow and reproducible dataset versioning for training.
