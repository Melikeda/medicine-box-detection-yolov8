# 🖼️ OpenCV Image Preprocessing

## 📌 Overview

This report documents the implementation of the OpenCV image preprocessing module developed for the **AI-Powered Medicine Box Detection System**.

The purpose of this phase was to build a reusable and modular image preprocessing package capable of preparing detected medicine-box images before Optical Character Recognition (OCR).

Rather than using isolated OpenCV functions, this phase focused on designing a complete preprocessing workflow composed of reusable modules. Each image processing technique was first implemented and tested independently before being integrated into a unified OCR preprocessing pipeline.

This modular approach improves maintainability, reusability, and future optimization of the project.

---

# 🎯 Objectives

The objectives of this phase were:

- Build a reusable OpenCV preprocessing package
- Learn the fundamentals of digital image processing
- Implement commonly used preprocessing techniques
- Improve medicine-box image quality before OCR
- Design a configurable preprocessing pipeline
- Create educational step-by-step OpenCV examples
- Prepare the project for the OCR integration phase

---

# 📂 Project Structure

The preprocessing package was implemented under:

```text
src/preprocessing/
```

Implemented modules:

```text
basic_operations.py
geometric_operations.py
color_operations.py
filter_operations.py
threshold_operations.py
morphological_operations.py
edge_operations.py
perspective_operations.py
pipeline.py
```

Each module is responsible for a specific category of image processing operations.

Additionally, a separate **examples/** directory was created to demonstrate every implemented technique independently.

---

# ⚙️ Implementation Summary

During this phase, the preprocessing system evolved from simple image manipulation functions into a complete OCR-ready preprocessing pipeline.

The implementation followed these principles:

- Modular architecture
- Reusable functions
- Small independent modules
- Step-by-step validation
- Easy integration with future OCR modules

This approach allows preprocessing functions to be reused individually or combined into larger workflows.

---

# 🧪 Implemented Techniques

## Basic Image Operations

Implemented:

- Image Reading
- Image Saving
- Image Display
- Image Shape Analysis
- Pixel Information
- BGR ↔ RGB Conversion

Purpose:

Understand how OpenCV stores, loads, displays, and manipulates digital images.

---

## Geometric Transformations

Implemented:

- Resize
- Crop

Purpose:

Resize images for faster processing and crop detected medicine-box regions before OCR.

---

## Color Processing

Implemented:

- Grayscale Conversion

Purpose:

Remove unnecessary color information while preserving text structure.

---

## Thresholding

Implemented:

- Binary Threshold
- Adaptive Threshold

Purpose:

Convert grayscale images into binary images to improve OCR readability.

---

## Image Filtering

Implemented:

- Gaussian Blur
- Median Blur
- Bilateral Filter

Additional comparison:

- Salt-and-Pepper Noise Simulation
- Filter Comparison

Purpose:

Reduce image noise while preserving useful visual information.

---

## Contrast Enhancement

Implemented:

- Histogram Equalization
- CLAHE (Contrast Limited Adaptive Histogram Equalization)

Purpose:

Improve local image contrast and increase text visibility.

---

## Morphological Operations

Implemented:

- Erosion
- Dilation
- Opening
- Closing

Purpose:

Remove unwanted artifacts and strengthen text regions before OCR.

---

## Edge Detection

Implemented:

- Canny Edge Detection

Purpose:

Detect significant image boundaries and visualize object structure.

---

## Perspective Transformation

Implemented:

- Perspective Warp

Purpose:

Correct perspective distortion caused by photographs captured from different viewing angles.

---

# 🔄 OCR Preprocessing Pipeline

After implementing each technique individually, they were combined into a reusable preprocessing pipeline.

Pipeline flow:

```text
Image
    │
    ▼
Resize
    │
    ▼
Crop
    │
    ▼
Grayscale
    │
    ▼
Median Blur
    │
    ▼
CLAHE
    │
    ▼
Adaptive Threshold
    │
    ▼
Opening
    │
    ▼
Closing
    │
    ▼
OCR Ready Image
```

The entire preprocessing workflow is implemented inside:

```text
src/preprocessing/pipeline.py
```

This pipeline generates a clean binary image optimized for OCR.

---

# 📚 Learning Examples

To better understand each OpenCV technique, every preprocessing stage was implemented as an independent example script.

Examples include:

- step_01_image_reading.py
- step_02_image_saving.py
- step_03_image_display.py
- step_04_bgr_vs_rgb.py
- step_05_image_shape.py
- step_06_resize.py
- step_07_crop.py
- step_08_grayscale.py
- step_09_threshold.py
- step_10_adaptive_threshold.py
- step_11_gaussian_blur.py
- step_12_median_blur.py
- step_13_filter_comparison.py
- step_14_histogram_equalization.py
- step_15_clahe.py
- step_16_erosion.py
- step_17_dilation.py
- step_18_opening.py
- step_19_closing.py
- step_20_edge_detection.py
- step_21_perspective_transform.py
- step_22_preprocessing_pipeline.py

These examples provide a practical learning resource while also serving as test cases for each preprocessing technique.

---

# 📊 Results

The OpenCV preprocessing phase produced a reusable preprocessing package specifically designed for OCR.

Achievements include:

- Modular preprocessing architecture
- Reusable OCR preprocessing pipeline
- Twenty-two educational OpenCV examples
- Improved image quality before OCR
- Cleaner project organization
- Better maintainability
- Fully documented preprocessing workflow

---

# 🎯 Key Outcomes

At the end of this phase, the project successfully achieved:

- A reusable preprocessing library
- Configurable preprocessing pipeline
- OCR-ready binary image generation
- Independent image processing modules
- Comprehensive OpenCV documentation
- Practical learning examples for every implemented technique

This preprocessing module now serves as the foundation for all OCR-related stages of the project.

---

# 📌 Conclusion

The OpenCV preprocessing phase established one of the project's most important components.

Instead of applying isolated image processing functions, a complete and reusable preprocessing system was developed.

The modular architecture makes future improvements straightforward while allowing individual preprocessing techniques to be tested independently.

The resulting OCR preprocessing pipeline significantly improves image quality before text recognition and provides a strong foundation for the remaining stages of the project.

---

# 🚀 Next Phase

The next development stage is:

## OCR Integration

Upcoming tasks:

- Install EasyOCR
- Build reusable OCR module
- Integrate OCR with the preprocessing pipeline
- Compare OCR performance before and after preprocessing
- Extract medicine names
- Evaluate OCR accuracy
- Prepare data for RapidFuzz matching