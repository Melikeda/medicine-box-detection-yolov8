# Technology Selection

This document explains which technologies are used in the project and why they were chosen.

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

**Role:** Read medicine names from cropped box images.

**Why:** Supports Turkish and English; simple API; works well with our preprocessing pipeline.

---

## RapidFuzz

**Role:** Match noisy OCR output to medicine names in the database.

**Why:** Fast fuzzy string matching; handles OCR typos (e.g. `afern` → `A-Ferin`); no heavy ML dependency.

---

## CSV / SQLite / PostgreSQL

| Stage | Technology | Why |
|-------|------------|-----|
| Current | CSV + SQLite | CSV seeds SQLite; matching/API use SQLite |
| Production (later) | PostgreSQL | Scalable; supports concurrent users and history |

---

## FastAPI ✅

**Role:** REST API backend for the mobile app.

**Status:** Implemented — `GET /health`, `GET/POST /api/v1/analyze`, upload validation, async pipeline.

**Why:** Native async support, automatic OpenAPI docs, Pydantic validation, straightforward file upload handling, excellent Python AI ecosystem fit.

---

## Flutter (planned)

**Role:** Cross-platform mobile app (Android MVP first).

**Why:** Single codebase for Android and future iOS; mature camera/gallery packages (`image_picker`); good UI tooling for internship-level development.

---

## Docker (planned)

**Role:** Package backend, models, and dependencies for consistent deployment.

**Why:** Eliminates "works on my machine" issues; simplifies sharing the backend across Windows/Linux.

---

## Large Language Model — Post-MVP

**Role:** Generate natural-language medicine explanations (usage, warnings).

**Why:** Adds user-friendly information beyond raw database fields. Planned after the mobile MVP is stable ([#8](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/8), [#32](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/32)).

---

## Deprecated Direction: Streamlit

Streamlit was considered for a web UI early in the project. The direction changed to **Flutter + FastAPI** for a real mobile product. Issue [#7](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/7) was closed accordingly.

---

## Roboflow

**Role:** Dataset annotation, augmentation, and YOLO export.

**Why:** Simplified labeling workflow and reproducible dataset versioning for training.
