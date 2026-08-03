# 🗺️ Project Roadmap

This document describes the complete development roadmap of the **AI-Powered Medicine Box Detection System**.

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
- [x] Partial brand matching (e.g. `fen` → Nurofen)
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

# Phase 18 — Advanced Features

**Branch:** `feature/advanced-features`  
**GitHub Issue:** #32

## Objectives

- [ ] LLM integration for medicine explanations (#8)
- [ ] PostgreSQL migration
- [ ] User scan history
- [ ] Barcode/QR reading
- [ ] Cloud deployment
- [ ] iOS support

---

# Phase 19 — Final Testing & Documentation

**Branch:** `feature/final-testing`  
**GitHub Issue:** #9

## Objectives

- [ ] Test complete mobile + backend system
- [ ] Evaluate end-to-end performance
- [ ] Complete internship report
- [ ] Finalize GitHub documentation

---

# Phase 20 — Dataset Publishing

**Branch:** `feature/dataset-publishing`

## Objectives

- [ ] Review dataset image sources
- [ ] Remove images with unclear copyright status
- [ ] Prepare final dataset
- [ ] Write dataset documentation
- [ ] Publish dataset on Kaggle
- [ ] Add Kaggle dataset link to README

---

# Phase 21 — Project Release

**Branch:** `feature/project-release`

## Objectives

- [ ] Final project review
- [ ] Prepare Release v1.0.0
- [ ] Update documentation
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
| ✅ Medicine Name Matching | Completed | #6 |
| ✅ Pipeline Unification | Completed | #23 |
| ✅ Pipeline Servicification | Completed | #24 |
| ✅ FastAPI Backend | Completed | #25 |
| ✅ Analyze API | Completed | #26 |
| ✅ SQLite Database | Completed | #27 |
| ✅ Automated Testing | Completed | #28 |
| ✅ Docker | Done | #29 |
| ✅ Flutter Mobile App Foundation | Done | #30 |
| ✅ Mobile MVP Integration | Done | #31 |
| ✅ CI/CD (GitHub Actions) | Done | #39 |
| ⏳ Advanced Features (LLM, etc.) | Planned | #32, #8 |
| ⏳ Final Testing & Documentation | Planned | #9 |
| ⏳ Dataset Publishing | Planned | — |
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