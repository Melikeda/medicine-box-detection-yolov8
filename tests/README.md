# Tests

Automated tests for the Medicine Box Detection System (Phase 14 / Issue [#28](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/28)).

## Layout

| File | Coverage |
|------|----------|
| `conftest.py` | Shared fixtures (temp CSV/SQLite seed) |
| `test_matching.py` | RapidFuzz matching, OCR normalize, dosage filter |
| `test_database.py` | SQLite seed, list, search, categories |
| `test_api.py` | Medicines API, health, analyze/info, upload validation |

## Run

```bash
pip install -r requirements.txt
pytest
```

Verbose:

```bash
pytest -v
```

Single module:

```bash
pytest tests/test_matching.py -v
```

## Notes

- Tests use an in-memory-style **temporary SQLite DB** seeded from a small CSV fixture — production `medicines.db` is not touched.
- Full YOLO + EasyOCR analyze runs are **not** included (slow / GPU). Upload validation and matching edge cases are covered instead.
