# Data Directory

This folder contains dataset configuration, sample images, and the medicine database.

## Contents

| Path | Description |
|------|-------------|
| `database/medicines.csv` | Medicine records (131 drugs, TİTCK-enriched) |
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

`database/medicines.csv` is the **seed source of truth** (editable).  
`database/medicines.db` is the **runtime SQLite database** (generated locally, gitignored).

| Field | Description |
|-------|-------------|
| `medicine_id` | Unique ID (e.g. MED038) |
| `medicine_name` | Full product name |
| `brand_name` | Brand for partial matching |
| `active_ingredient` | Used for fuzzy match (with guards) |
| `dosage` | Strength information |
| `form` | Tablet, capsule, etc. |
| `category` | Therapeutic category |

### Adding a new drug

1. Add a row to `medicines.csv` with the next `medicine_id`
2. Restart the API (`python run_api.py`) — CSV is upserted into SQLite on startup  
   Or run: `python scripts/seed_sqlite.py`
3. Test with `python run_analyze.py --image your_photo.jpg --mode fast`

Catalog size: **131** seed records (TİTCK SKRS–enriched) — see [Report 24](../docs/reports/24-medicine-database-final-refresh.md), [Report 18](../docs/reports/18-medicine-database-expansion.md), and [database/README.md](database/README.md).

SQLite migration: Issue [#27](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/27) / [Report 12](../docs/reports/12-sqlite-database.md).

### Query API

| Method | Path |
|--------|------|
| GET | `/api/v1/medicines` |
| GET | `/api/v1/medicines/categories` |
| GET | `/api/v1/medicines/{medicine_id}` |

## Sample images

| File | Use case |
|------|----------|
| `coklu_resim.jpg` | Multi-box detection test |
| `samples3.jpg` | Standard pipeline test |
| `nurofen_calpol.jpg` | Brand matching |
| `2li_ornek.png` | Two-box sample |

Large personal test photos are kept locally and not committed to Git.
