# Tests

Automated tests for **Yolocilin** / the medicine box detection backend (pytest).

## Layout

| File | Coverage |
|------|----------|
| `conftest.py` | Temp CSV/SQLite seed, singleton resets |
| `test_matching.py` | RapidFuzz, OCR normalize, dosage filters |
| `test_database.py` | SQLite seed, list, search, categories |
| `test_api.py` | Medicines API, health, analyze/info, upload validation |
| `test_explain.py` | Explain endpoint, cache, rate limit, missing key |
| `test_llm_config.py` | LLM key / production fail-fast |
| `test_llm_models.py` | Gemini model fallback chain |
| `test_scans.py` | Server scan history CRUD + trim |
| `test_security.py` | CORS, docs-off in prod, headers, analyze 429 |
| `test_e2e_api_flow.py` | Health → medicines → explain → analyze (mock) → scans |
| `test_performance.py` | Fast/accurate OCR config, early exit, resize |
| `test_model_paths.py` | YOLO weight auto-resolve candidates |
| `test_medicines_csv_validation.py` | Catalog CSV sanity |
| `test_titck_mapper.py` | TİTCK mapping helpers |

## Run

```bash
pip install -r requirements.txt
pytest
pytest tests/test_e2e_api_flow.py -q
pytest -v tests/test_scans.py
```

## Notes

- Fixtures use a **temporary SQLite DB** — production `medicines.db` is not modified.
- Full YOLO + EasyOCR analyze is **not** run in CI (slow). Use `scripts/e2e_api_flow.py` or `scripts/benchmark_analyze.py` locally with weights loaded.
- Mobile tests: `cd mobile && flutter test` (see [mobile/README.md](../mobile/README.md)).

Live E2E / timing: [Report 25](../docs/reports/25-e2e-performance.md).
