# Kaggle Dataset — Yolocilin Medicine Box Detection

Published dataset for the YOLOv8 **medicine-box** detector used by Yolocilin.

| | |
|---|---|
| **Kaggle** | [melikeklahc/yolocilin-medicine-box-detection](https://www.kaggle.com/datasets/melikeklahc/yolocilin-medicine-box-detection) |
| **Images** | 395 (train 363 · valid 15 · test 17) |
| **Class** | `medicine-box` (1) |
| **Format** | YOLOv8 images + labels + `data.yaml` |
| **License** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

## What was published

Privacy-cleaned phone photos of medicine packaging, annotated in Roboflow and exported for Ultralytics YOLO.

Removed before publish:

- Third-party / screenshot sources with unclear rights
- Frames with handwritten personal dosage notes

## Local packaging (maintainers)

Staging folder (gitignored images): `data/kaggle_publish/`

```powershell
# Rebuild cover (560x280) for Kaggle header + thumbnail crops
python scripts/build_kaggle_cover.py

# Create first version
python -m kaggle datasets create -p data/kaggle_publish --dir-mode zip

# New version
python -m kaggle datasets version -p data/kaggle_publish --dir-mode zip -m "release notes"

# Metadata / cover / tags only
python -m kaggle datasets metadata melikeklahc/yolocilin-medicine-box-detection --update -p data/kaggle_publish
```

Requires `kaggle.json` in `%USERPROFILE%\.kaggle\` (Legacy API key from Kaggle Settings).

License name for metadata updates must be exactly:

`Attribution 4.0 International (CC BY 4.0)`

## Related

- Phase 20: [docs/roadmap.md](../roadmap.md)
- Dataset prep report: [docs/reports/03-dataset-preparation.md](../reports/03-dataset-preparation.md)
- Roboflow: [Medicine Detection](https://universe.roboflow.com/melikes-workspace-jkw9f/medicine-detection-cfvfd)
