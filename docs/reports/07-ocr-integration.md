# 📄 Report 07 — OCR Integration

## Overview

This report documents the implementation of the Optical Character Recognition (OCR) module for the AI-Powered Medicine Box Detection System.

The objective of this phase was to build a reusable OCR package capable of extracting medicine names from images detected by the YOLOv8 model.

Rather than simply reading text from an image, the OCR module was designed as an independent and modular component that can be integrated into different computer vision pipelines.

---

# Objectives

The goals of this phase were:

- Integrate EasyOCR into the project
- Build reusable OCR modules
- Improve OCR accuracy using OpenCV preprocessing
- Compare OCR performance before and after preprocessing
- Filter low-confidence OCR results
- Clean OCR output
- Integrate YOLO detection with OCR
- Produce reusable OCR examples

---

# Technologies

- Python
- EasyOCR
- OpenCV
- NumPy
- YOLOv8
- PyTorch

---

# Project Structure

The OCR implementation introduced the following modules:

```text
src/
├── ocr/
│   ├── ocr_reader.py
│   ├── ocr_pipeline.py
│   └── text_cleaner.py
│
├── integration/
│   └── yolo_ocr_pipeline.py
```

Example scripts:

```text
examples/
└── ocr/
    ├── step_01_basic_ocr.py
    ├── step_02_ocr_with_preprocessing.py
    ├── step_03_ocr_pipeline.py
    ├── step_04_text_cleaning.py
    └── step_05_yolo_ocr_integration.py
```

---

# Implemented Components

## OCR Reader

A reusable EasyOCR reader was implemented.

Responsibilities:

- Load EasyOCR
- Configure language support
- Initialize OCR engine

---

## OCR Pipeline

A reusable OCR pipeline was developed.

Pipeline steps:

1. Read image
2. Apply OpenCV preprocessing
3. Run EasyOCR
4. Filter low-confidence detections
5. Extract recognized text
6. Combine OCR outputs

---

## Confidence Filtering

Low-confidence OCR detections are automatically removed before further processing.

This reduces false-positive recognitions and improves overall OCR quality.

---

## Text Cleaning

A dedicated text cleaning module was implemented.

The module performs:

- Remove unnecessary whitespace
- Remove empty strings
- Normalize OCR outputs
- Generate combined text

Example:

```text
["NUROFCN", "", "200 mg"]

↓

["NUROFCN", "200 mg"]

↓

NUROFCN 200 mg
```

---

## YOLO + OCR Integration

A complete integration pipeline was developed.

Workflow:

```text
Image
    │
    ▼
YOLO Detection
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
Confidence Filtering
    │
    ▼
Text Cleaning
    │
    ▼
Combined OCR Text
```

This integration enables automatic text extraction directly from detected medicine boxes.

---

# Example Output

Example OCR output:

```text
Detected Medicine Box

↓

NUROFCN
COLD
&
FLU
200 mg
30 mg
Film Kaplı Tablet
Ibuprofen

↓

Combined Text

NUROFCN COLD & FLU 200 mg 30 mg Film Kaplı Tablet Ibuprofen
```

---

# Results

The OCR module successfully:

- Extracted medicine names
- Read dosage information
- Read package descriptions
- Improved OCR quality using preprocessing
- Produced reusable OCR outputs

The preprocessing pipeline noticeably improved OCR accuracy compared to running OCR directly on the original image.

---

# Current Limitations

Some OCR mistakes still occur.

Example:

```text
NUROFCN
```

Expected result:

```text
NUROFEN
```

These spelling errors will be corrected in the next development phase using RapidFuzz.

---

# Deliverables

Completed modules:

- OCR Reader
- OCR Pipeline
- Text Cleaner
- YOLO + OCR Integration

Completed example scripts:

- Basic OCR
- OCR with preprocessing
- OCR pipeline
- Text cleaning
- YOLO + OCR integration

---

# Conclusion

The OCR Integration phase successfully introduced a reusable and modular OCR system into the project.

The system is capable of extracting medicine-related text from YOLO-detected medicine boxes while improving recognition quality through OpenCV preprocessing and confidence filtering.

The next phase of the project will focus on RapidFuzz-based medicine name matching to correct OCR spelling errors and improve overall recognition accuracy.