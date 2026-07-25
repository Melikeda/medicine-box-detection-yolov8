# Data Directory

This folder contains dataset configuration, sample images, and the medicine database.

## Contents

| Path | Description |
|------|-------------|
| `database/medicines.csv` | Medicine records (name, brand, ingredient, dosage, form, category) |
| `dataset/data.yaml` | YOLOv8 training configuration |
| `dataset/README.*.txt` | Roboflow export metadata |
| `samples/` | Test images for detection, OCR, and matching demos |

## Dataset images (not in repo)

Training images and YOLO labels are excluded from Git to keep the repository lightweight. Download from Roboflow and place them here:

```text
dataset/
├── train/
├── valid/
├── test/
└── data.yaml
```

See [docs/reports/03-dataset-preparation.md](../docs/reports/03-dataset-preparation.md) for details.

## Medicine database

`database/medicines.csv` is the current source of truth for RapidFuzz matching. A SQLite migration is planned in issue [#27](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/27).
