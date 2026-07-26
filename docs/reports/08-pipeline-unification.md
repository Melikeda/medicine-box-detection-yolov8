# Report 08 — Pipeline Unification

## Overview

This report documents Phase 9 of the AI-Powered Medicine Box Detection System: unifying the end-to-end AI pipeline under a single service layer in `src/services/`.

Before this phase, the full YOLO → OCR → RapidFuzz workflow lived inside `examples/rapidfuzz/step_10_multi_ocr_medicine_matching.py` (~900 lines). The integration module in `src/integration/yolo_ocr_pipeline.py` was outdated and incompatible with the current OCR API. There was no single function that FastAPI or other callers could invoke.

The objective of this phase was to extract production-ready orchestration logic into `src/services/` and expose one entry point: `analyze_medicine_box()`.

**Branch:** `refactor/unify-pipeline`  
**GitHub Issue:** #23

---

## Objectives

The goals of this phase were:

- [x] Fix API mismatch between integration and OCR modules
- [x] Extract end-to-end logic from examples into `src/services/`
- [x] Create `analyze_medicine_box()` orchestration function
- [x] Centralize model paths and configuration
- [x] Simplify the step_10 demo script to use the service layer

---

## Problem Statement

### Scattered pipeline logic

The working pipeline was implemented as a demo script with embedded helper functions for:

- OCR candidate normalization
- Medicine name candidate generation
- Candidate filtering
- RapidFuzz ranking

This made the pipeline difficult to reuse from a backend API.

### Outdated integration module

`src/integration/yolo_ocr_pipeline.py` called `run_ocr_pipeline()` with deprecated parameters:

- `image_path` instead of `image_input`
- `save_preprocessed_image` instead of `save_preprocessed_images`
- `output_path` instead of `output_directory`

It also used `extract_texts()` on raw OCR results instead of `get_candidate_texts()` with `OCRPipelineResult`.

### No unified configuration

Model paths, CSV paths, confidence thresholds, and match score cutoffs were duplicated across example scripts and `src/predict.py`.

---

## Technologies

- Python 3.10+
- YOLOv8 (Ultralytics)
- EasyOCR
- OpenCV
- RapidFuzz
- dataclasses (configuration and result types)

---

## Project Structure

New service layer:

```text
src/services/
├── __init__.py
├── config.py              # PipelineConfig, default paths
├── detection.py           # crop_best_detection()
├── candidate_processor.py # OCR candidate logic + ranking
└── medicine_analyzer.py   # analyze_medicine_box()
```

Updated modules:

```text
src/integration/
└── yolo_ocr_pipeline.py   # Updated OCR API usage

examples/rapidfuzz/
└── step_10_multi_ocr_medicine_matching.py  # Thin demo wrapper
```

---

## Implemented Components

### PipelineConfig

Central configuration dataclass in `src/services/config.py`.

Responsibilities:

- YOLO model path
- Medicine CSV path
- Detection and OCR thresholds
- Match score cutoff and top match count
- Output directories for debug artifacts

Default paths are resolved relative to the project root.

---

### Detection Service

`crop_best_detection()` in `src/services/detection.py`.

Responsibilities:

- Select the highest-confidence YOLO bounding box
- Crop the medicine box region from the original image
- Return cropped image and YOLO confidence score

Previously duplicated in `examples/rapidfuzz/step_07_yolo_crop_ocr.py`.

---

### Candidate Processor

Logic extracted from step_10 into `src/services/candidate_processor.py`.

Responsibilities:

- Normalize OCR text for filtering
- Generate full medicine name candidates (e.g. `aferin` + `forte` → `aferin forte`)
- Filter dosage, form, and generic OCR noise
- Rank medicine matches with RapidFuzz

---

### Medicine Analyzer

Main orchestrator in `src/services/medicine_analyzer.py`.

Entry point:

```python
from src.services import analyze_medicine_box, PipelineConfig

result = analyze_medicine_box("data/samples/samples3.jpg")
```

Returns `MedicineAnalysisResult` with:

| Field | Description |
|-------|-------------|
| `success` | Whether a confident match was found |
| `yolo_confidence` | YOLO detection score |
| `medicine` | Best matching medicine record |
| `match_score` | RapidFuzz score (0–100) |
| `best_ocr_text` | OCR text used for the best match |
| `ranked_matches` | Top N matches |
| `ocr_candidates` | Raw OCR candidate texts |
| `filtered_candidates` | Candidates sent to RapidFuzz |
| `error` | Error message when `success` is False |

---

### Updated YOLO + OCR Integration

`src/integration/yolo_ocr_pipeline.py` was updated to use the current OCR pipeline API.

Changes:

- `run_ocr_pipeline()` with `image_input`, `save_preprocessed_images`, `output_directory`
- `get_candidate_texts()` instead of legacy `extract_texts()` / `combine_texts()`
- Docstring note directing callers to `analyze_medicine_box()` for full matching

---

## Workflow

```text
Image Path
    │
    ▼
analyze_medicine_box()
    │
    ├── YOLO Detection
    ├── Crop Best Box
    ├── Multi-variant OCR
    ├── Candidate Generation
    ├── Candidate Filtering
    └── RapidFuzz Matching
    │
    ▼
MedicineAnalysisResult
```

FastAPI (Phase 11+) will call `analyze_medicine_box()` from `POST /api/v1/analyze`.

---

## Usage

### Programmatic

```python
from src.services import analyze_medicine_box, PipelineConfig

config = PipelineConfig(
    confidence_threshold=0.60,
    match_score_cutoff=80.0,
)

result = analyze_medicine_box(
    "data/samples/samples3.jpg",
    config=config,
    save_debug_outputs=True,
)

if result.success:
    print(result.medicine["medicine_name"])
    print(result.match_score)
else:
    print(result.error)
```

### Demo script

```bash
python -m examples.rapidfuzz.step_10_multi_ocr_medicine_matching
```

---

## Results

This phase successfully:

- Unified the end-to-end pipeline under `src/services/`
- Fixed the integration module OCR API mismatch
- Reduced step_10 from ~900 lines to ~220 lines (display only)
- Provided a structured result type ready for JSON serialization
- Centralized configuration for upcoming FastAPI integration

---

## Current Limitations

- Models are loaded on each call (singleton loading planned in Phase 10, Issue #24)
- No REST API yet — service is Python-only
- Debug output saving is optional via `save_debug_outputs`
- `src/integration/yolo_ocr_pipeline.py` handles YOLO + OCR only; full matching requires `analyze_medicine_box()`

---

## Deliverables

Completed modules:

- `PipelineConfig`
- `crop_best_detection()`
- Candidate processor functions
- `analyze_medicine_box()`
- `MedicineAnalysisResult`

Updated files:

- `src/integration/yolo_ocr_pipeline.py`
- `examples/rapidfuzz/step_10_multi_ocr_medicine_matching.py`

---

## Conclusion

Pipeline Unification closes the gap between working demo scripts and production-ready code. The AI pipeline now has a single orchestration entry point that FastAPI can consume in the next development phase.

**Next phase:** Pipeline Servicification ([#24](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/24)) — split services further, load models once at startup, add fast/accurate OCR modes.
