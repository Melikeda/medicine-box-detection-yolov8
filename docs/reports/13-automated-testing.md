# Report 13 — Automated Testing


> **Historical phase report.** Written for that phase; some numbers or “next steps” may be outdated.
> Living docs: [README](../../README.md) · [Architecture](../architecture.md) · [Roadmap](../roadmap.md) · [Reports index](README.md).
> Current product: **Yolocilin** · catalog **131** medicines · APIs: analyze · medicines · explain · scans.

## Overview

Phase 14 adds a `pytest` suite for matching, SQLite, and FastAPI endpoints without loading YOLO/EasyOCR on every run.

**Branch:** `feature/tests`  
**GitHub Issue:** #28

---

## Objectives

- [x] Set up pytest (`pytest.ini`, fixtures, dependencies)
- [x] Add unit tests for matching / OCR normalization
- [x] Add SQLite seed and repository tests
- [x] Add API tests (medicines, health, analyze/info, upload validation)

---

## Test Modules

| Module | What it verifies |
|--------|------------------|
| `tests/test_matching.py` | `fen`→Nurofen, `ibucold €`→Ibucold C, dosage false-positive block |
| `tests/test_database.py` | CSV→SQLite seed/upsert, search, categories |
| `tests/test_api.py` | `/api/v1/medicines`, `/health`, `/analyze/info`, upload rules |

---

## How to run

```bash
pip install -r requirements.txt
pytest
```

---

## Design choices

- Temporary SQLite + small CSV fixture (fast, isolated)
- No full pipeline analyze in CI unit suite (would need model weights + long CPU time)
- FastAPI `TestClient` with dependency overrides for medicine routes

---

## Next Phase

Issue #39 — CI/CD pipeline (GitHub Actions). Completed in [Report 17](17-ci-cd-github-actions.md).
