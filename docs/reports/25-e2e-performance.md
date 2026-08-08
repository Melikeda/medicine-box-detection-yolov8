# Report 25 — Mobile + Backend E2E & Performance

## Overview

Defines a repeatable end-to-end API smoke path (health → medicines → explain → analyze → scans) and performance measurement tooling for the final polish round.

**Branch:** `feature/final-polish-4`  
**Roadmap:** Phase 18–19 testing objectives

---

## What was added

| Artifact | Purpose |
|----------|---------|
| `tests/test_e2e_api_flow.py` | CI-friendly E2E (analyze mocked; real medicines/explain/scans) |
| `scripts/e2e_api_flow.py` | Live backend E2E + per-step timings (optional real OCR) |
| `scripts/benchmark_analyze.py --json-out` | Local pipeline benchmark JSON export |

---

## CI E2E (always runs with pytest)

```bash
pytest tests/test_e2e_api_flow.py -q
```

Covers:

1. `GET /health`
2. `GET /api/v1/medicines`
3. `GET/POST /api/v1/explain` (mock LLM + cache hit)
4. `POST /api/v1/analyze` (pipeline mocked; real upload validation)
5. `POST/GET/DELETE /api/v1/scans`

Asserts non-OCR steps complete under 5s each in CI.

---

## Live API E2E (local / emulator day)

Start backend, then:

```bash
# Fast smoke (no OCR)
python scripts/e2e_api_flow.py --skip-analyze --json-out artifacts/e2e-smoke.json

# Full path including analyze (CPU: often 1–3+ minutes)
python scripts/e2e_api_flow.py --image data/samples/parol_plus.jpg --json-out artifacts/e2e-full.json
```

### Mobile manual checklist

1. Backend healthy: `curl http://127.0.0.1:8000/health`
2. Run live API smoke: `python scripts/e2e_api_flow.py --skip-analyze`
3. `flutter run` (emulator) → Gallery → **Analiz Et**
4. Result screen shows match / not_found correctly
5. History icon → entry appears (local)
6. Optional: `GET /api/v1/scans` shows synced server row
7. Expand **İlaç hakkında** if `LLM_ENABLED=true` and key configured
8. Stop backend → analyze shows connection error SnackBar

---

## Performance measurement

### API/pipeline timings

```bash
python scripts/benchmark_analyze.py --image data/samples/parol_plus.jpg --mode fast --json-out artifacts/bench-parol.json
```

Response field `timing` from `POST /api/v1/analyze` also exposes `yolo_ms`, `ocr_ms`, `matching_ms`, `total_ms`.

### Baseline (documented from prior runs)

| Scenario | Environment | Approx. wall time | Source |
|----------|-------------|-------------------|--------|
| Analyze 1 box (fast, CPU) | Android emulator + local API | ~255 s | Report 16 |
| Analyze fast mode | Local CPU (typical) | ~1–3 min / photo | README / Report 19 |
| Explain (mock / cached) | API process | tens of ms | E2E pytest |
| Medicines / scans CRUD | API + SQLite | < 2 s | E2E pytest |

Re-run benchmarks on your machine after major OCR/model changes and attach JSON under `artifacts/` (gitignored if desired).

---

## Success criteria

- [x] Automated API E2E in pytest
- [x] Live E2E script with timing summary
- [x] Pipeline benchmark JSON export
- [x] Mobile manual checklist documented
- [x] Roadmap testing items updated

---

## Out of scope

- Full Flutter `integration_test` driver in CI (requires emulator + GPU/CPU budget)
- Load / multi-user stress testing
- GPU production SLA targets
