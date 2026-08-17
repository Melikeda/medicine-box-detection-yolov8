# 🗺️ Project Roadmap

This document describes the complete development roadmap of **Yolocilin** (Medicine Box Detection, Identification and Information System).

The project follows a **Git Feature Branch Workflow**, where each major development stage is implemented in its own feature branch, reviewed through a Pull Request, and merged into the **main** branch after successful validation.

---

# Phase 1 — Project Setup

**Branch:** `feature/project-setup`

## Objectives

- [x] Create GitHub repository
- [x] Initialize Git repository
- [x] Create project folder structure
- [x] Prepare README.md
- [x] Create project roadmap
- [x] Create documentation structure

---

# Phase 2 — Project Documentation

**Branch:** `feature/project-documentation`

## Objectives

- [x] Improve README.md
- [x] Define project goals
- [x] Document technologies
- [x] Create project architecture
- [x] Improve project roadmap
- [x] Define Git branching strategy

---

# Phase 3 — Development Environment

**Branch:** `feature/development-environment`

## Objectives

- [x] Install Python
- [x] Create virtual environment
- [x] Install required libraries
- [x] Configure Visual Studio Code
- [x] Update requirements.txt
- [x] Create setup guide
- [x] Verify development environment

---

# Phase 4 — Dataset Preparation

**Branch:** `feature/roboflow-dataset`

## Objectives

- [x] Collect medicine box images
- [x] Organize dataset
- [x] Upload images to Roboflow
- [x] Annotate medicine boxes
- [x] Export YOLOv8 dataset
- [x] Prepare data.yaml
- [x] Verify dataset structure
- [x] Verify YOLO label annotations

---

# Phase 5 — YOLOv8 Model Training

**Branch:** `feature/yolov8-detection`

## Objectives

- [x] Install YOLOv8
- [x] Train YOLOv8n model
- [x] Evaluate training results
- [x] Analyze model performance
- [x] Generate best.pt model
- [x] Perform prediction on test images
- [x] Evaluate prediction results

---

# Phase 6 — OpenCV Image Preprocessing

**Branch:** `feature/opencv-preprocessing`

## Objectives

- [x] Build modular preprocessing package
- [x] Implement image reading and saving
- [x] Implement image visualization
- [x] Analyze image shape and pixel information
- [x] Implement BGR ↔ RGB conversion
- [x] Implement image resizing
- [x] Implement image cropping
- [x] Implement grayscale conversion
- [x] Implement binary thresholding
- [x] Implement adaptive thresholding
- [x] Implement Gaussian Blur
- [x] Implement Median Blur
- [x] Implement Bilateral Filter
- [x] Compare filtering techniques
- [x] Implement Histogram Equalization
- [x] Implement CLAHE
- [x] Implement Erosion
- [x] Implement Dilation
- [x] Implement Opening
- [x] Implement Closing
- [x] Implement Canny Edge Detection
- [x] Implement Perspective Transform
- [x] Build reusable OCR preprocessing pipeline
- [x] Create step-by-step OpenCV examples

### Output

A reusable preprocessing module capable of preparing medicine-box images for OCR.

---

# Phase 7 — OCR Integration

**Branch:** `feature/ocr-integration`

## Objectives

- [x] Install EasyOCR
- [x] Create reusable OCR reader module
- [x] Build reusable OCR pipeline
- [x] Implement OCR preprocessing integration
- [x] Run OCR on original medicine-box images
- [x] Run OCR on preprocessed images
- [x] Compare OCR performance
- [x] Apply confidence filtering
- [x] Implement text cleaning
- [x] Generate combined OCR text
- [x] Build YOLO + OCR integration pipeline
- [x] Save OCR outputs
- [x] Create OCR example scripts
- [x] Evaluate PaddleOCR as an alternative engine (not adopted; [Report 26](reports/26-ocr-engine-comparison.md))

### Output

A reusable OCR package integrated with the YOLO detection pipeline and capable of extracting cleaned medicine text from detected medicine boxes.

---

# Phase 8 — Medicine Name Matching

**Branch:** `feature/medicine-matching` ✅  
**GitHub Issue:** #6 (closed)

## Objectives

- [x] Create medicine database (CSV)
- [x] Integrate RapidFuzz
- [x] Correct OCR spelling errors
- [x] Match OCR output with medicine database
- [x] Rank matching candidates
- [x] Evaluate matching accuracy

---

# Phase 9 — Pipeline Unification

**Branch:** `refactor/unify-pipeline`  
**GitHub Issue:** #23

## Objectives

- [x] Fix API mismatch between integration and OCR modules
- [x] Extract end-to-end logic from examples into `src/services/`
- [x] Create `analyze_medicine_box()` orchestration function
- [x] Centralize model paths and configuration

---

# Phase 10 — Pipeline Servicification

**Branch:** `feature/pipeline-services`  
**GitHub Issue:** #24

## Objectives

- [x] Split YOLO, OCR, and matching into dedicated services
- [x] Load models once at startup (singleton pattern)
- [x] Add `fast` and `accurate` OCR modes for CPU performance

---

# Phase 11 — FastAPI Backend Foundation

**Branch:** `feature/fastapi-foundation`  
**GitHub Issue:** #25

## Objectives

- [x] Set up FastAPI project structure
- [x] Add config, logging, and exception handling
- [x] Implement `GET /health` endpoint
- [x] Load pipeline via `PipelineManager` at startup

---

# Phase 12 — Image Upload & Analyze API

**Branch:** `feature/analyze-endpoint`  
**GitHub Issue:** #26

## Objectives

- [x] Implement `POST /api/v1/analyze` with multipart upload
- [x] Validate image type and file size
- [x] Return structured JSON response for mobile app
- [x] Add `GET /api/v1/analyze/info` and `mode` query parameter

### Real-world improvements (same release)

- [x] YOLO confidence fallback for blurry photos
- [x] Partial brand matching (e.g. `fen` → Nurofen) — historical; current policy rejects suffix fragments ([Report 27](reports/27-matching-reliability.md))
- [x] Dosage-only OCR filtering
- [x] OCR confusable normalization (`€` → `c` for Ibucold C)
- [x] Add Parafon to CSV (38 drugs total)

See [Report 10](reports/10-fastapi-analyze-api.md) and [Report 11](reports/11-real-world-matching-improvements.md).

---

# Phase 13 — SQLite Database Migration

**Branch:** `feature/sqlite-database`  
**GitHub Issue:** #27

## Objectives

- [x] Define SQLAlchemy Medicine model
- [x] Seed database from CSV
- [x] Add medicine query endpoints
- [x] Wire MatchingService to SQLite (CSV remains seed source)

See [Report 12](reports/12-sqlite-database.md).

---

# Phase 14 — Automated Testing

**Branch:** `feature/tests`  
**GitHub Issue:** #28

## Objectives

- [x] Set up pytest
- [x] Add unit, integration, and API tests

See [Report 13](reports/13-automated-testing.md).

---

# Phase 15 — Docker Containerization

**Branch:** `feature/docker`  
**GitHub Issue:** #29

## Objectives

- [x] Create Dockerfile and docker-compose
- [x] Document local deployment

See [Report 14](reports/14-docker-containerization.md).

---

# Phase 16 — Flutter Mobile App Foundation

**Branch:** `feature/flutter-foundation`  
**GitHub Issue:** #30

## Objectives

- [x] Initialize Flutter project
- [x] Build splash, home, and image preview screens
- [x] Integrate gallery image picker

See [Report 15](reports/15-flutter-foundation.md).

---

# Phase 17 — Mobile & Backend Integration (MVP)

**Branch:** `feature/mobile-integration`  
**GitHub Issue:** #31

## Objectives

- [x] Connect mobile app to analyze API
- [x] Display medicine name, match score, and basic info
- [x] Handle loading states and errors
- [x] Test on Android

See [Report 16](reports/16-mobile-integration.md).

---

# Phase 17.5 — CI/CD (GitHub Actions)

**Branch:** `feature/ci-cd`  
**GitHub Issue:** #39

## Objectives

- [x] Backend pytest workflow
- [x] Flutter analyze + test workflow
- [x] Docker build verification workflow
- [x] CONTRIBUTING.md, PR template, README badges

See [Report 17](reports/17-ci-cd-github-actions.md).

---

# Phase 17.6 — Medicine Database Expansion (TİTCK SKRS)

**Branch:** `feature/medicine-database-expansion`  
**GitHub Issue:** #41

## Objectives

- [x] Download and parse TİTCK SKRS E-Reçete XLSX
- [x] Enrich CSV placeholder fields (active ingredient, dosage, form)
- [x] Expand OTC catalog to 100+ records
- [x] Validation script, pytest, and data documentation

See [Report 18](reports/18-medicine-database-expansion.md).

---

# Phase 17.6b — Medicine Database Final Refresh

**Branch:** `feature/final-polish-2`  
**Date:** 2026-08-06

## Objectives

- [x] Re-download TİTCK SKRS (7948 active products)
- [x] Expand catalog to 131 records (popular OTC + SKRS picks)
- [x] Fix known bad dosage/form/category rows
- [x] Re-seed SQLite; update data README and Report 24

See [Report 24](reports/24-medicine-database-final-refresh.md).

---

# Phase 17.6c — Catalog Expansion (merged)

Later expansions on `main` (after Report 24). Historical sizes 131 and 153 stay in those phase notes; **current catalog is 1163**.

## Objectives

- [x] Controlled shelf-brand expand + matching tighten → 153 (`feature/catalog-expand-matching-tighten`)
- [x] Popular TR / ATC expansion → **1163** (PR [#59](https://github.com/Melikeda/medicine-box-detection-yolov8/pull/59))

---

# Phase 17.7 — Performance Optimization

**Branch:** `feature/performance-improvement`  
**GitHub Issue:** #43

## Objectives

- [x] Reduce fast-mode OCR variant count (rotations + scale)
- [x] Early-exit OCR on confident CSV match
- [x] Server-side image resize before pipeline
- [x] Per-stage timing in analyze API response
- [x] Benchmark script + Report 19

See [Report 19](reports/19-performance-optimization.md).

---

# Phase 17.8 — Production Hardening & Security

**Branch:** `feature/production-hardening`  
**GitHub Issue:** #45

## Objectives

- [x] Android debug vs release HTTP/HTTPS policy
- [x] CORS, rate limit, security headers
- [x] Production error masking + medical disclaimer
- [x] `.env.example` + Report 20

See [Report 20](reports/20-production-hardening.md).

---

# Phase 18–19 — Final Project Polish

**GitHub Issue:** [#50](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/50) (supersedes #32, #9)

**Branch workflow:** numbered improvement rounds — `feature/final-polish`, `feature/final-polish-2`, … Merge each round when done; open the next branch for the following slice.

**Status:** Feature polish merged to `main`. Next: Phase 21 (`feature/project-release`).

**Round 1 (merged PR #51):** matching fixes, multi-box OCR, garbage filter.

## Objectives (features, from former Phase 18)

- [x] LLM integration for medicine explanations (#8)
- [x] Mobile camera capture (Report 22, PR #48)
- [x] Mobile scan history — local SQLite (Report 23)
- [x] OCR mode UI toggle — preview screen Hızlı/Hassas; persists preference; calls `?mode=` (PR follow-up)
- [x] Fix active-ingredient-only false matches (ibuprofen → wrong brand, round 1)
- [x] Matching reliability: suffix OCR (`fen`, `alm`) → `not_found` (PR [#67](https://github.com/Melikeda/yolocilin/pull/67), [Report 27](reports/27-matching-reliability.md))
- [x] Multi-box OCR: supplemental deep retry + garbage OCR filter (round 1)
- [x] Medicine database final refresh — 131 rows, TİTCK re-sync (Report 24, round 2); later expanded to **1163**
- [x] User scan history (server sync) — `POST/GET/DELETE /api/v1/scans` + mobile best-effort sync (final-polish-4)

> **Moved to [Future Development](#-future-development):** PostgreSQL migration, Cloud deployment, iOS support. SQLite + Android MVP remain the supported product stage; barcode **API** is Phase 22 (`feature/barcode-reading`).

## Objectives (testing and docs, from former Phase 19)

- [x] Test complete mobile + backend system — pytest E2E + live `scripts/e2e_api_flow.py` + mobile checklist (Report 25)
- [x] Evaluate end-to-end performance — timing in e2e script + `benchmark_analyze.py --json-out` (Report 25)
- [x] GitHub [#9](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/9) (test and document final system) — **closed**; repo testing/docs wrap-up done

> Written internship report and final GitHub docs polish are **Phase 21** deliverables (not open GitHub issues).

---

# Phase 22 — Barcode Reading

**Branch:** `feature/barcode-reading`  
**Status:** Done (API + Flutter live/photo scanner)

## Objectives

- [x] Optional barcode decoder (`src/barcode/`, zxing-cpp)
- [x] `medicine_barcodes.csv` + SQLite `medicine_barcodes` (TİTCK GTIN → `medicine_id`)
- [x] `GET /api/v1/barcode/lookup` and `POST /api/v1/barcode/scan`
- [x] Analyze tries barcode before OCR; existing OCR path unchanged on miss
- [x] Explain unchanged (`medicine_id` → Gemini, catalog fallback if Gemini is busy)
- [x] Flutter barcode viewfinder / scan frame (live + photo → existing result screen)

## Objectives

- [x] Optional barcode decoder (`src/barcode/`, zxing-cpp)
- [x] `medicine_barcodes.csv` + SQLite `medicine_barcodes` (TİTCK GTIN → `medicine_id`)
- [x] `GET /api/v1/barcode/lookup` and `POST /api/v1/barcode/scan`
- [x] Analyze tries barcode before OCR; existing OCR path unchanged on miss
- [x] Explain unchanged (`medicine_id` → Gemini)
- [x] Flutter barcode viewfinder / scan frame (live + photo → existing result screen)

Details: [Report 28](reports/28-barcode-reading.md)

---

# 🔭 Future Development

Post-MVP / production-scale work. **Not required** to close the current internship deliverable or Phase 18–19 polish. Track here so the main roadmap stays honest about what ships now vs later.

| Item | Why later | When it becomes relevant |
|------|-----------|---------------------------|
| **PostgreSQL migration** | SQLite is enough for single-host demo, catalog matching (in-memory RapidFuzz), and low-traffic `scans`. Postgres adds concurrent writes, managed cloud DB, backups, and HA. | Multi-user cloud API, heavy scan-history write load, or ops requirements |
| **Cloud deployment** | Local API + Docker (+ optional HTTPS tunnel) already cover development and demos. Always-on public hosting adds cost, model/CPU sizing, and ops. | Public testers / production URL without a PC tunnel |
| **iOS support** | Android Flutter MVP is complete; iOS needs Apple toolchain, signing, and device testing. | App Store / iPhone users |
| Per-user auth for private scan lists | Scans are global / best-effort today | Multi-tenant production |
| YOLO retrain (blurry / negative samples) | Current model covers primary demos | Systematic false “kutu değil” / partial-box cases |
| Multilingual OCR | TR/EN pipeline is in place | Additional markets |

**Principle:** keep CSV → SQLite and Android as the current delivery path; treat Postgres, cloud hosting, and iOS as optional next-stage work.

---

# Phase 20 — Dataset Publishing

**Branch:** `feature/dataset-publishing`  
**Status:** Done (Aug 2026)

## Objectives

- [x] Review dataset image sources
- [x] Remove images with unclear copyright status (screenshots, third-party, handwritten personal notes)
- [x] Prepare final dataset (**395** images · train 363 / valid 15 / test 17)
- [x] Write dataset documentation (Kaggle card + `data.yaml`)
- [x] Publish dataset on Kaggle
- [x] Add Kaggle dataset link to README

**Dataset:** [melikeklahc/yolocilin-medicine-box-detection](https://www.kaggle.com/datasets/melikeklahc/yolocilin-medicine-box-detection)  
**License:** CC BY 4.0 · single class `medicine-box` · YOLOv8 format

---

# Phase 21 — Project Release

**Branch:** `feature/project-release`

## Objectives

- [ ] Final project review
- [x] Align living docs with matching reliability gates ([Report 27](reports/27-matching-reliability.md))
- [ ] Complete written internship report
- [ ] Finalize GitHub documentation (README / roadmap / changelog sync)
- [ ] Prepare Release v1.0.0
- [ ] Update repository badges
- [ ] Publish GitHub Release
- [ ] Archive final deliverables

---

# 📊 Project Status

| Phase | Status | GitHub Issue |
|--------|--------|--------------|
| ✅ Project Setup | Completed | — |
| ✅ Project Documentation | Completed | — |
| ✅ Development Environment | Completed | — |
| ✅ Dataset Preparation | Completed | — |
| ✅ YOLOv8 Model Training | Completed | — |
| ✅ OpenCV Image Preprocessing | Completed | — |
| ✅ OCR Integration | Completed | — |
| ✅ OCR engine comparison (PaddleOCR trial) | EasyOCR kept | [Report 26](reports/26-ocr-engine-comparison.md) |
| ✅ Matching reliability gates | Suffix fragments → not_found | [PR #67](https://github.com/Melikeda/yolocilin/pull/67) / [Report 27](reports/27-matching-reliability.md) |
| ✅ Medicine Name Matching | Completed | #6 |
| ✅ Pipeline Unification | Completed | #23 |
| ✅ Pipeline Servicification | Completed | #24 |
| ✅ FastAPI Backend | Completed | #25 |
| ✅ Analyze API | Completed | #26 |
| ✅ SQLite Database | Completed | #27 |
| ✅ Catalog expansion (TİTCK → 1163) | Done | #41 / PR #59 |
| ✅ Automated Testing | Completed | #28 |
| ✅ Docker | Done | #29 |
| ✅ Flutter Mobile App Foundation | Done | #30 |
| ✅ Mobile MVP Integration | Done | #31 |
| ✅ CI/CD (GitHub Actions) | Done | #39 |
| ✅ LLM explanations (Gemini) | Done | #8 |
| ✅ Server scan history + E2E tooling | Done (final-polish-4) | #50 / Report 23–25 |
| 🔭 Future Development | PostgreSQL, cloud, iOS (post-MVP) | #32 / #50 |
| ✅ Barcode reading | API + Flutter scanner | [Report 28](reports/28-barcode-reading.md) |
| ⏳ End-of-project docs | Written internship report + GitHub docs polish | Phase 21 (#9 closed) |
| ✅ Dataset Publishing (Kaggle) | Done | [Kaggle dataset](https://www.kaggle.com/datasets/melikeklahc/yolocilin-medicine-box-detection) |
| ⏳ Project Release | Planned | — |

---

# 🎯 Target System Architecture

```text
Flutter Mobile App
   │
   ▼
POST /api/v1/analyze (FastAPI)
   │
   ▼
YOLOv8 Detection
   │
   ▼
Crop Medicine Box
   │
   ▼
OpenCV Preprocessing
   │
   ▼
EasyOCR
   │
   ▼
RapidFuzz Matching
   │
   ▼
Medicine Database (SQLite)
   │
   ▼
JSON Response → Mobile Result Screen
   │
   ▼
(Optional) LLM Explanation
```

---

# 📌 Git Development Workflow

```text
Issue
   │
   ▼
Feature Branch
   │
   ▼
Development
   │
   ▼
Testing
   │
   ▼
Documentation
   │
   ▼
Commit
   │
   ▼
Push
   │
   ▼
Pull Request
   │
   ▼
Code Review
   │
   ▼
Merge into Main
   │
   ▼
Next Feature Branch
```