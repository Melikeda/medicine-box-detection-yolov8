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
POST /api/v1/analyze (FastAPI)
 │
 ▼
YOLOv8 Detection
 │
 ▼
Crop Detected Medicine Box
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
Medicine Database (CSV → SQLite)
 │
 ▼
JSON Response
 │
 ▼
Mobile Result Screen
 │
 ▼
(Optional) LLM Explanation
```

---

# 🧩 System Components

## 1. Mobile Client (Flutter)

The user selects a medicine box photo from the gallery (MVP) or captures one with the camera (later version).

### Responsibilities

- Image selection and preview
- API communication
- Loading and error states
- Display medicine name, match score, and basic drug info

### Output

- User-facing scan result

---

## 2. Backend API (FastAPI)

Receives uploaded images and orchestrates the AI pipeline.

### Responsibilities

- Image validation (type, size)
- Temporary file handling
- Pipeline orchestration
- Structured JSON responses
- Health checks and logging

### Key Endpoint

- `POST /api/v1/analyze`

---

## 3. Object Detection (YOLOv8)

YOLOv8 detects medicine boxes within the uploaded image.

### Output

- Bounding box coordinates
- Detection confidence score
- Cropped medicine box image

---

## 4. Image Preprocessing (OpenCV)

The cropped image is enhanced before OCR using multi-variant preprocessing.

### Output

- Enhanced images optimized for OCR accuracy

---

## 5. OCR (EasyOCR)

EasyOCR extracts text from processed medicine box images.

### Output

- OCR text candidates with confidence scores

---

## 6. Medicine Name Matching (RapidFuzz)

OCR output is compared with the medicine database to correct recognition errors.

### Example

```text
OCR Output: afern frte
      ↓
RapidFuzz
      ↓
Matched: A-Ferin Forte
```

### Output

- Best matching medicine record and match score

---

## 7. Medicine Database

Medicine information is stored in a structured database.

| Stage | Technology |
|-------|------------|
| Current | CSV file |
| MVP target | SQLite + SQLAlchemy |
| Production | PostgreSQL |

Example fields:

- medicine_id, medicine_name, brand_name
- active_ingredient, dosage, form, category

---

## 8. Large Language Model (LLM) — Post-MVP

The matched medicine information can be passed to an LLM for natural-language explanations.

### Output

- Usage information, warnings, and general description

---

# 🔁 Data Flow

```text
Flutter App
   │
   ▼
FastAPI
   │
   ▼
YOLOv8 → Crop → OpenCV → EasyOCR → RapidFuzz → Database
   │
   ▼
JSON Response → Flutter Result Screen
```

---

# 🎯 Design Principles

- Modular architecture with single-responsibility services
- AI models loaded once at backend startup
- REST + JSON for mobile communication
- Git Feature Branch Workflow with GitHub Issues
- Incremental delivery: AI pipeline → API → mobile MVP → advanced features

---

# 🚀 Future Improvements

- Fast and accurate OCR modes for CPU performance
- Multiple medicine boxes per image
- Barcode / QR code support
- User scan history and authentication
- Cloud deployment with Docker
- iOS support
- Multilingual OCR
