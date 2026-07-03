# Technology Selection

This document describes the technologies used in the project and explains why each technology was selected.

---

# Python

**Purpose**

Main programming language of the project.

**Reason for Selection**

- Easy to learn and maintain
- Rich AI and Computer Vision ecosystem
- Excellent library support

---

# YOLOv8n

**Purpose**

Detect medicine boxes in images.

**Reason for Selection**

- Fast object detection
- Lightweight model
- Suitable for real-time applications
- Good performance on mid-range computers

---

# OpenCV

**Purpose**

Image preprocessing before OCR.

**Reason for Selection**

- Image processing
- Cropping detected medicine boxes
- Preparing images for OCR

---

# Roboflow

**Purpose**

Dataset management and annotation.

**Reason for Selection**

- Easy image annotation
- Dataset versioning
- Preprocessing
- Data augmentation
- Direct YOLO export

---

# EasyOCR

**Purpose**

Read medicine names from detected medicine boxes.

**Reason for Selection**

- Supports Turkish language
- Easy integration
- Suitable for printed text recognition

> **Note:** PaddleOCR may also be evaluated during development if it provides better performance.

---

# RapidFuzz

**Purpose**

Correct OCR recognition errors.

**Reason for Selection**

- Fast fuzzy matching
- High accuracy
- Lightweight

---

# Streamlit

**Purpose**

Build the user interface.

**Reason for Selection**

- Rapid development
- Interactive web interface
- Easy deployment

---

# Pandas

**Purpose**

Manage medicine information stored in CSV files.

**Reason for Selection**

- Easy data manipulation
- Simple CSV integration

---

# Large Language Model (LLM)

**Purpose**

Provide explanations about detected medicines.

**Reason for Selection**

- Generate natural language responses
- Improve user experience
- Support future intelligent features