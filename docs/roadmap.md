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

- [ ] Fix API mismatch between integration and OCR modules
- [ ] Extract end-to-end logic from examples into `src/services/`
- [ ] Create `analyze_medicine_box()` orchestration function
- [ ] Centralize model paths and configuration

---

# Phase 10 — Pipeline Servicification

**Branch:** `feature/pipeline-services`  
**GitHub Issue:** #24

## Objectives

- [ ] Split YOLO, OCR, and matching into dedicated services
- [ ] Load models once at startup (singleton pattern)
- [ ] Add `fast` and `accurate` OCR modes for CPU performance

---

# Phase 11 — FastAPI Backend Foundation

**Branch:** `feature/fastapi-foundation`  
**GitHub Issue:** #25

## Objectives

- [ ] Set up FastAPI project structure
- [ ] Add config, logging, and exception handling
- [ ] Implement `GET /health` endpoint

---

# Phase 12 — Image Upload & Analyze API

**Branch:** `feature/analyze-endpoint`  
**GitHub Issue:** #26

## Objectives

- [ ] Implement `POST /api/v1/analyze` with multipart upload
- [ ] Validate image type and file size
- [ ] Return structured JSON response for mobile app

---

# Phase 13 — SQLite Database Migration

**Branch:** `feature/sqlite-database`  
**GitHub Issue:** #27

## Objectives

- [ ] Define SQLAlchemy Medicine model
- [ ] Seed database from CSV
- [ ] Add medicine query endpoints

---

# Phase 14 — Automated Testing

**Branch:** `feature/tests`  
**GitHub Issue:** #28

## Objectives

- [ ] Set up pytest
- [ ] Add unit, integration, and API tests

---

# Phase 15 — Docker Containerization

**Branch:** `feature/docker`  
**GitHub Issue:** #29

## Objectives

- [ ] Create Dockerfile and docker-compose
- [ ] Document local deployment

---

# Phase 16 — Flutter Mobile App Foundation

**Branch:** `feature/flutter-foundation`  
**GitHub Issue:** #30

## Objectives

- [ ] Initialize Flutter project
- [ ] Build splash, home, and image preview screens
- [ ] Integrate gallery image picker

---

# Phase 17 — Mobile & Backend Integration (MVP)

**Branch:** `feature/mobile-integration`  
**GitHub Issue:** #31

## Objectives

- [ ] Connect mobile app to analyze API
- [ ] Display medicine name, match score, and basic info
- [ ] Handle loading states and errors
- [ ] Test on Android

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
| ⏳ Pipeline Unification | Next | #23 |
| ⏳ Pipeline Servicification | Planned | #24 |
| ⏳ FastAPI Backend | Planned | #25 |
| ⏳ Analyze API | Planned | #26 |
| ⏳ SQLite Database | Planned | #27 |
| ⏳ Automated Testing | Planned | #28 |
| ⏳ Docker | Planned | #29 |
| ⏳ Flutter Mobile App | Planned | #30 |
| ⏳ Mobile MVP Integration | Planned | #31 |
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