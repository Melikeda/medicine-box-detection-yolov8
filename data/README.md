# Dataset

This directory contains the dataset configuration and related documentation for the project.

The complete image dataset is **not included** in this repository to keep the repository lightweight.

Included files:

- `data.yaml` — YOLOv8 dataset configuration
- `README.dataset.txt` — Roboflow dataset information
- `README.roboflow.txt` — Roboflow export details

The dataset images and labels can be downloaded from the corresponding Roboflow project and placed in the following structure:

```text
dataset/
│
├── train/
├── valid/
├── test/
└── data.yaml
```

After downloading the dataset, the project will be ready for YOLOv8 training.