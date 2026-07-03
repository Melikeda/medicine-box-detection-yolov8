# System Architecture

## Overview

The **Medicine Box Detection System** is designed as a modular Computer Vision application.

The system detects medicine boxes from an uploaded image, extracts the medicine name using OCR, corrects OCR errors using fuzzy matching, and finally provides medicine-related information through a Large Language Model (LLM).

The architecture is modular, allowing each component to be developed, tested, and improved independently.

---

## High-Level Workflow

```text
User
 │
 ▼
Upload Image
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
RapidFuzz
 │
 ▼
Medicine Database (CSV)
 │
 ▼
LLM
 │
 ▼
Streamlit Interface
 │
 ▼
Result to User
```

---

## Component Descriptions

## 1. Image Input

The user uploads an image containing one or more medicine boxes through the Streamlit interface.

Output:

- Input image

---

## 2. Object Detection (YOLOv8)

YOLOv8 detects the location of medicine boxes.

Output:

- Bounding Box
- Confidence Score

---

## 3. Image Cropping

The detected medicine box is cropped from the original image.

Output:

- Cropped medicine box image

---

## 4. Image Preprocessing (OpenCV)

The cropped image is prepared for OCR.

Possible operations include:

- Resize
- Contrast adjustment
- Noise reduction
- Sharpening

Output:

- Enhanced image

---

## 5. OCR (EasyOCR)

The enhanced image is processed using EasyOCR.

Output:

- Raw medicine name

Example:

```text
Paroi
```

---

## 6. Medicine Name Matching (RapidFuzz)

OCR output is compared with the medicine database.

Example:

```text
OCR Output
Paroi

↓

RapidFuzz

↓

Parol
```

Output:

- Correct medicine name

---

## 7. Medicine Database

Medicine information is stored in a CSV file.

Example fields:

- Medicine Name
- Active Ingredient
- Category
- Description

---

## 8. Large Language Model (LLM)

The detected medicine information is passed to an LLM.

The LLM generates a natural language explanation.

Example:

- What is this medicine?
- What is it generally used for?

---

## 9. User Interface (Streamlit)

The interface presents:

- Uploaded image
- Detected medicine boxes
- OCR result
- Corrected medicine name
- LLM explanation

---

## Data Flow

```text
Image
   │
   ▼
YOLOv8
   │
   ▼
Crop
   │
   ▼
OpenCV
   │
   ▼
EasyOCR
   │
   ▼
RapidFuzz
   │
   ▼
CSV Database
   │
   ▼
LLM
   │
   ▼
Streamlit
```

---

## Design Principles

The project is designed according to the following principles:

- Modular architecture
- Easy maintenance
- Independent components
- Scalable design
- Readable code structure

---

## Future Improvements

Future versions may include:

- Medicine bottle detection
- Blister package detection
- Barcode recognition
- QR code support
- Mobile application
- Cloud deployment
- Multi-language support