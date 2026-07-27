# Report 09 — Pipeline Servicification

## Overview

Phase 10 refactors the unified pipeline into dedicated services with singleton resource management and configurable OCR modes. This prepares the codebase for FastAPI startup loading (Issue #25).

**Branch:** `feature/pipeline-services`  
**GitHub Issue:** #24

---

## Objectives

- [x] Split YOLO, OCR, and matching into dedicated services
- [x] Load models once at startup (singleton pattern)
- [x] Add `fast` and `accurate` OCR modes for CPU performance

---

## New Modules

| Module | Responsibility |
|--------|----------------|
| `detection_service.py` | YOLO detection and crop |
| `ocr_service.py` | Multi-variant OCR with mode support |
| `matching_service.py` | CSV load, candidate processing, RapidFuzz |
| `pipeline_manager.py` | Singleton — load once, analyze many |

---

## OCR Modes

| Mode | Rotations | Blurry extras | Typical variants |
|------|-----------|---------------|------------------|
| `fast` | 0° only | Disabled | ~6 |
| `accurate` | 0°, 90°, 180°, 270° | Enabled | ~52 |

---

## Usage

```python
from src.services import PipelineManager, PipelineConfig

manager = PipelineManager.get_instance(PipelineConfig(ocr_mode="fast"))
manager.load()
result = manager.analyze("data/samples/samples3.jpg")
```

CLI:

```bash
python run_analyze.py data/samples/samples3.jpg --mode fast
python run_analyze.py data/samples/samples3.jpg --mode accurate --preload
```

---

## Next Phase

Issue #25 — FastAPI backend foundation. The API will call `PipelineManager.load()` on startup and `manager.analyze()` per request.
