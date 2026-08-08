# Report 09 — Pipeline Servicification


> **Historical phase report.** Written for that phase; some numbers or “next steps” may be outdated.
> Living docs: [README](../../README.md) · [Architecture](../architecture.md) · [Roadmap](../roadmap.md) · [Reports index](README.md).
> Current product: **Yolocilin** · catalog **131** medicines · APIs: analyze · medicines · explain · scans.

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

| Mode | Rotations | Variants per box | Notes |
|------|-----------|------------------|-------|
| `fast` | 0°, 90°, 180°, 270° | ~8 (2 per angle) | API default |
| `accurate` | 0°, 90°, 180°, 270° | ~52 | Full variant set |

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

Issues #25–#26 — FastAPI backend and analyze API. See [Report 10](10-fastapi-analyze-api.md).

Matching and detection improvements for real-world photos: [Report 11](11-real-world-matching-improvements.md).
