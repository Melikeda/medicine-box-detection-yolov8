# 🗺️ Project Roadmap

This document describes the complete development roadmap of the **AI-Powered Medicine Box Detection System**.

The project follows a **Git Feature Branch Workflow**, where each major development stage is implemented in its own feature branch, reviewed through a Pull Request, and merged into the **main** branch after completion.

---

# Phase 1 — Project Setup

**Branch:** `feature/project-setup`

## Objectives

* [x] Create GitHub repository
* [x] Initialize Git repository
* [x] Create project folder structure
* [x] Prepare README.md
* [x] Create project roadmap
* [x] Create documentation structure

---

# Phase 2 — Project Documentation

**Branch:** `feature/project-documentation`

## Objectives

* [x] Improve README.md
* [x] Define project goals
* [x] Document technologies
* [x] Create project architecture
* [x] Improve project roadmap
* [x] Define Git branching strategy

---

# Phase 3 — Development Environment

**Branch:** `feature/development-environment`

## Objectives

* [x] Install Python
* [x] Create virtual environment
* [x] Install required libraries
* [x] Configure Visual Studio Code
* [x] Update requirements.txt
* [x] Create setup guide
* [x] Verify development environment

---

# Phase 4 — Dataset Preparation

**Branch:** `feature/roboflow-dataset`

## Objectives

* [x] Collect medicine box images
* [x] Organize dataset
* [x] Upload images to Roboflow
* [x] Annotate medicine boxes
* [x] Export YOLOv8 dataset
* [x] Prepare data.yaml
* [x] Verify dataset structure
* [x] Verify YOLO label annotations

---

# Phase 5 — YOLOv8 Model Training

**Branch:** `feature/yolov8-detection`

## Objectives

* [x] Install YOLOv8
* [x] Train YOLOv8n model
* [x] Evaluate training results
* [x] Analyze model performance
* [x] Generate best.pt model
* [x] Perform prediction on test images
* [x] Evaluate prediction results

---

# Phase 6 — Image Preprocessing

**Branch:** `feature/opencv-preprocessing`

## Objectives

* [ ] Crop detected medicine boxes
* [ ] Resize images
* [ ] Improve image quality
* [ ] Remove unnecessary background
* [ ] Prepare images for OCR

---

# Phase 7 — OCR Integration

**Branch:** `feature/ocr-integration`

## Objectives

* [ ] Integrate EasyOCR
* [ ] Extract medicine names
* [ ] Evaluate OCR accuracy
* [ ] Improve OCR performance

---

# Phase 8 — Medicine Name Matching

**Branch:** `feature/medicine-matching`

## Objectives

* [ ] Create medicine database
* [ ] Integrate RapidFuzz
* [ ] Correct OCR mistakes
* [ ] Match medicine names

---

# Phase 9 — User Interface

**Branch:** `feature/streamlit-interface`

## Objectives

* [ ] Develop Streamlit interface
* [ ] Upload images
* [ ] Display detection results
* [ ] Display OCR output
* [ ] Display medicine information

---

# Phase 10 — LLM Integration

**Branch:** `feature/llm-integration`

## Objectives

* [ ] Integrate LLM
* [ ] Generate medicine explanations
* [ ] Improve prompts
* [ ] Produce user-friendly responses

---

# Phase 11 — Final Testing & Documentation

**Branch:** `feature/final-testing`

## Objectives

* [ ] Test the complete system
* [ ] Evaluate system performance
* [ ] Optimize the project
* [ ] Prepare Medium articles
* [ ] Complete internship report
* [ ] Finalize GitHub documentation

---

# Phase 12 — Dataset Publishing

**Branch:** `feature/dataset-publishing`

## Objectives

* [ ] Review dataset image sources
* [ ] Remove images with unclear copyright status
* [ ] Prepare the final dataset
* [ ] Write dataset documentation
* [ ] Publish the dataset on Kaggle
* [ ] Add the Kaggle dataset link to README.md

---

# Phase 13 — Project Release

**Branch:** `feature/project-release`

## Objectives

* [ ] Perform final project review
* [ ] Prepare Release v1.0.0
* [ ] Update repository badges and documentation
* [ ] Publish the final GitHub release
* [ ] Archive project deliverables

---

# 📊 Project Status

| Phase                         | Status      |
| ----------------------------- | ----------- |
| Project Setup                 | ✅ Completed |
| Project Documentation         | ✅ Completed |
| Development Environment       | ✅ Completed |
| Dataset Preparation           | ✅ Completed |
| YOLOv8 Model Training         | ✅ Completed |
| Image Preprocessing           | ⏳ Planned   |
| OCR Integration               | ⏳ Planned   |
| Medicine Name Matching        | ⏳ Planned   |
| User Interface                | ⏳ Planned   |
| LLM Integration               | ⏳ Planned   |
| Final Testing & Documentation | ⏳ Planned   |
| Dataset Publishing            | ⏳ Planned   |
| Project Release               | ⏳ Planned   |

---

# 🎯 Final Project Goal

```text
Image
   │
   ▼
YOLOv8 Detection
   │
   ▼
Bounding Box Detection
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
Medicine Database
   │
   ▼
Medicine Information
   │
   ▼
Large Language Model (LLM)
   │
   ▼
Streamlit Interface
   │
   ▼
Final Result
```

---

# 📌 Development Workflow

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
Merge
   │
   ▼
Done
```
