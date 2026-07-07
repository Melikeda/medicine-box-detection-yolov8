# 📦 Dataset Preparation Report

## 📌 Purpose

The purpose of this phase is to prepare, organize, and validate a high-quality dataset for training the YOLOv8 object detection model.

A well-structured and accurately annotated dataset is essential for achieving reliable and accurate object detection performance.

---

# 🎯 Objectives

- Collect medicine box images
- Organize the dataset
- Export the dataset in YOLOv8 format
- Verify the dataset structure
- Validate dataset annotations
- Prepare the project for model training

---

# 📊 Dataset Overview

The dataset consists of **478 annotated medicine box images** prepared for object detection.

The images are divided into training, validation, and test subsets following the standard YOLOv8 dataset structure.

| Subset | Number of Images |
|---------|-----------------:|
| Train | 441 |
| Validation | 18 |
| Test | 19 |

---

# 📈 Dataset Statistics

| Property | Value |
|----------|------:|
| Total Images | 478 |
| Classes | 1 |
| Image Size | 640 × 640 |
| Annotation Format | YOLOv8 |
| Annotation Tool | Roboflow |

---

# 📂 Dataset Structure

```text
data/dataset/
│
├── train/
│   ├── images/
│   └── labels/
│
├── valid/
│   ├── images/
│   └── labels/
│
├── test/
│   ├── images/
│   └── labels/
│
└── data.yaml
```

Each subset contains an **images** directory for the original images and a **labels** directory containing the corresponding YOLO annotation files.

---

# 📝 YOLO Label Format

Each image has a corresponding annotation file with the same filename.

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

Where:

- **class_id** → Object class identifier
- **x_center** → Normalized horizontal center of the bounding box
- **y_center** → Normalized vertical center of the bounding box
- **width** → Normalized bounding box width
- **height** → Normalized bounding box height

All coordinate values are normalized between **0** and **1**, making the annotations independent of image resolution.

---

# ⚙️ data.yaml Configuration

The `data.yaml` file defines the dataset structure used by YOLOv8 during training.

Current configuration:

```yaml
path: data/dataset

train: train/images
val: valid/images
test: test/images

nc: 1

names:
  0: medicine-box
```

This configuration specifies:

- Dataset location
- Training images
- Validation images
- Test images
- Number of classes
- Class names

---

# ✅ Dataset Verification

Before starting model training, the dataset structure and annotations were verified.

A custom visualization tool (`src/tools/visualize_yolo_labels.py`) was developed to validate the exported YOLO annotations.

The tool performs the following operations:

- Reads the original image.
- Reads the corresponding YOLO annotation file.
- Converts normalized coordinates into pixel coordinates.
- Draws bounding boxes on the image.
- Saves the visualization for manual inspection.

The verification confirmed that:

- Labels correctly match their corresponding images.
- Bounding boxes accurately surround the medicine boxes.
- YOLO annotation files are correctly formatted.
- The dataset is ready for model training.

---

# 📌 Outcome

At the end of this phase:

- Dataset organization was completed.
- The YOLOv8 dataset structure was verified.
- The dataset configuration was validated.
- Label annotations were successfully verified.
- A custom annotation visualization tool was developed.
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