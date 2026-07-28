# Tests

Automated tests for the Medicine Box Detection System will be added in Phase 14 (GitHub Issue [#28](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/28)).

Planned coverage:

- `src/services/` — pipeline orchestration, detection fallback
- `src/matching/` — RapidFuzz scoring, dosage filter, text normalizer
- `src/database/` — CSV reader
- `backend/app/` — FastAPI health and analyze endpoints

Run tests (when available):

```bash
pytest
```
