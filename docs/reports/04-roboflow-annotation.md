# 🤖 Roboflow Annotation Report

## 📌 Purpose

The purpose of this phase is to prepare a high-quality annotated dataset using Roboflow for training the YOLOv8 object detection model.

Roboflow provides an efficient workflow for image annotation, dataset management, preprocessing, augmentation, and exporting datasets in YOLOv8 format.

---

# 🎯 Objectives

- Upload medicine box images to Roboflow
- Annotate medicine boxes
- Organize the dataset
- Configure preprocessing
- Configure data augmentation
- Export the dataset in YOLOv8 format
- Verify exported annotations before training

---

# 🌐 Roboflow Project

**Project Name**

Medicine Detection

**Dataset Version**

Version 1

**Export Format**

YOLOv8

---

# 📊 Dataset Summary

The exported dataset contains **478 images**.

Dataset split:

| Subset | Images |
|---------|-------:|
| Train | 441 |
| Validation | 18 |
| Test | 19 |

The dataset is organized according to the standard YOLOv8 directory structure.

---

# 🏷️ Annotation Process

Each medicine box in the dataset was manually annotated using bounding boxes in Roboflow.

The project currently contains a single object class.

| Class ID | Class Name |
|----------|------------|
| 0 | medicine-box |

Roboflow automatically generated the corresponding YOLO label files for every annotated image.

---

# 📄 YOLO Annotation Format

Each image has a matching annotation file.

Example:

```text
10_png.rf....jpg
10_png.rf....txt
```

YOLO annotation format:

```text
class_id x_center y_center width height
```

Example:

```text
0 0.359375 0.49140625 0.5546875 0.703125
```

The coordinate values are normalized between **0** and **1**, making the annotations independent of image resolution.

---

# ⚙️ Dataset Preprocessing

The following preprocessing operations were applied before exporting the dataset:

- Auto-orientation (EXIF correction)
- Resize all images to **640 × 640**

These preprocessing steps ensure that all images have a consistent format suitable for YOLOv8 training.

---

# 🔄 Data Augmentation

The following augmentation techniques were applied:

- Random rotation (-15° to +15°)
- Random brightness adjustment (-15% to +15%)
- Random exposure adjustment (-10% to +10%)
- Random Gaussian blur (0–2.5 px)
- Salt-and-pepper noise

These augmentations increase dataset diversity and improve the model's ability to generalize to real-world images.

---

# 📦 Dataset Export

The dataset was exported directly from Roboflow in **YOLOv8 format**.

Exported files:

```text
train/
valid/
test/
data.yaml
README.dataset.txt
README.roboflow.txt
```

The `data.yaml` configuration defines:

- Dataset location
- Train images
- Validation images
- Test images
- Number of classes
- Class names

The exported dataset is fully compatible with the Ultralytics YOLOv8 training pipeline.

---

# ✅ Annotation Verification

Before training, the exported annotations were verified using a custom visualization tool:

```text
src/tools/visualize_yolo_labels.py
```

The tool performs the following steps:

- Reads a YOLO annotation file.
- Converts normalized coordinates into pixel coordinates.
- Draws bounding boxes on the corresponding image.
- Saves the visualization for manual inspection.

The verification confirmed that:

- Bounding boxes correctly surround the medicine boxes.
- Label files match the corresponding images.
- Normalized coordinates were exported correctly.
- The dataset is ready for YOLOv8 training.

---

# 📌 Outcome

At the end of this phase:

- The medicine box dataset was successfully annotated.
- Roboflow preprocessing was configured.
- Data augmentation was applied.
- The dataset was exported in YOLOv8 format.
- YOLO label files were verified using a custom visualization tool.
- The dataset is fully prepared for YOLOv8 model training.

---

# 📍 Next Phase

The next development stage is:

```text
feature/yolov8-detection
```

This phase will focus on:

- Training the YOLOv8 model
- Understanding the training pipeline
- Evaluating model performance
- Analyzing training metrics
- Generating prediction results