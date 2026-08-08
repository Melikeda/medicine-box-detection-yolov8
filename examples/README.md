# Examples

Step-by-step learning scripts from the **Yolocilin** / medicine box detection internship project. They show how YOLOv8, OpenCV, OCR, RapidFuzz, CSV access, and pipeline integration were built incrementally.

**Production logic lives under `src/`** (and the FastAPI app under `backend/`). Prefer importing from `src/` instead of copying implementations.

Product docs: [root README](../README.md) · current catalog size **131** medicines.

---

## Directory layout

| Folder | Purpose |
|--------|---------|
| `preprocessing/` | OpenCV image processing tutorials (22 steps) |
| `ocr/` | EasyOCR learning and OCR pipeline usage |
| `database/` | Medicine CSV database reading |
| `matching/` | RapidFuzz fuzzy string matching |
| `integration/` | Step-by-step YOLO + OCR + matching integration (legacy demos) |
| `pipeline/` | **Current** unified pipeline demo (`analyze_medicine_box`) |

---

## Recommended learning order

Follow this sequence to mirror the project's development phases:

1. **Preprocessing** — `preprocessing/step_01` … `step_22`
2. **OCR** — `ocr/step_01` … `step_05`
3. **Database** — `database/step_01_read_medicine_csv`
4. **Matching** — `matching/step_01` … `step_03`
5. **Integration (legacy)** — `integration/step_01` … `step_03`
6. **Pipeline (current)** — `pipeline/analyze_medicine_box_demo`

---

## Running examples

Run any script as a module from the **project root**:

```bash
# Preprocessing
python -m examples.preprocessing.step_01_image_reading
python -m examples.preprocessing.step_22_preprocessing_pipeline

# OCR
python -m examples.ocr.step_01_basic_ocr

# Database
python -m examples.database.step_01_read_medicine_csv

# Matching
python -m examples.matching.step_01_rapidfuzz_basics

# Integration (legacy step-by-step demos)
python -m examples.integration.step_01_yolo_crop_ocr
python -m examples.integration.legacy_multi_ocr_medicine_matching

# Pipeline (recommended — uses src/services/)
python -m examples.pipeline.analyze_medicine_box_demo
```

---

## Prerequisites

Most examples require:

| Resource | Location |
|----------|----------|
| Sample images | `data/samples/` |
| Medicine database | `data/database/medicines.csv` |
| YOLO weights | Auto-resolved — see [models/README.md](../models/README.md) (not in Git) |

Install dependencies first:

```bash
pip install -r requirements.txt
```

See [docs/setup-guide.md](../docs/setup-guide.md) for full environment setup.

---

## Current vs legacy examples

| Type | Location | Description |
|------|----------|-------------|
| **Current** | `pipeline/analyze_medicine_box_demo.py` | Calls `analyze_medicine_box()` from `src/services/` |
| **Legacy** | `integration/step_01` … `step_03` | Early integration demos built before Phase 9 |
| **Legacy** | `integration/legacy_multi_ocr_medicine_matching.py` | Verbose integration demo with detailed terminal output |

Legacy examples are kept for learning history. They import from `src/` where possible and do not replace the production service layer.

---

## Relationship to `src/`

```text
src/      → reusable application logic (production-ready)
examples/ → learning scripts and usage demonstrations
tests/    → automated pytest suite (see tests/README.md)
docs/     → project documentation and technical reports
```

When adding new functionality:

- Put reusable logic in `src/`
- Add a thin demo under `examples/` if it helps learning or documents usage
- Do not copy pipeline orchestration into example files

---

## Related documentation

- [README.md](../README.md) — project overview
- [docs/architecture.md](../docs/architecture.md) — system design
- [docs/reports/](../docs/reports/) — phase-by-phase technical reports
