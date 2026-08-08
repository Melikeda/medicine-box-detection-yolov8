# GitHub Project Board — Column Mapping

Use this file when organizing issues on the GitHub Project board.

## Done

| Issue | Title |
|-------|-------|
| [#6](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/6) | Medicine name matching (RapidFuzz + CSV) |
| [#23](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/23) | Unify AI pipeline under `src/services/` |
| [#24](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/24) | Service-layer pipeline architecture |
| [#25](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/25) | FastAPI backend foundation |
| [#26](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/26) | Analyze API + real-world matching improvements |
| [#27](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/27) | SQLite database + medicine query endpoints |
| [#28](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/28) | Automated testing (pytest) |
| [#29](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/29) | Docker containerization |
| [#30](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/30) | Flutter mobile app foundation |
| [#31](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/31) | Mobile & backend integration (MVP) |
| [#39](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/39) | CI/CD pipeline (GitHub Actions) |
| [#41](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/41) | Medicine database expansion (TİTCK SKRS) |
| [#43](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/43) | Pipeline performance optimization |
| [#45](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/45) | Production hardening & security |
| [#8](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/8) | LLM medicine explanations (Gemini) |

## In Progress

| Issue | Title | Branch |
|-------|-------|--------|
| — | — | — |

## Todo — Mobile

| Issue | Branch |
|-------|--------|
| — | — |

## Post-MVP

| Issue | Branch |
|-------|--------|
| [#32](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/32) | `feature/advanced-features` |
| [#9](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/9) | `feature/final-testing` |

## Closed / Superseded

| Issue | Reason |
|-------|--------|
| [#7](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/7) | Streamlit replaced by Flutter ([#30](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/30), [#31](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/31)) |

## Labels

| Label | Use |
|-------|-----|
| `ai-pipeline` | YOLO, OCR, matching |
| `backend` | FastAPI |
| `mobile` | Flutter |
| `database` | SQLite / PostgreSQL |
| `testing` | pytest |
| `infrastructure` | Docker, CI/CD |
| `mvp` | Minimum viable product scope |

## Technical reports (docs/reports/)

| Report | Phase |
|--------|-------|
| 01–09 | Setup through pipeline servicification |
| [10-fastapi-analyze-api.md](../docs/reports/10-fastapi-analyze-api.md) | FastAPI + analyze endpoint |
| [11-real-world-matching-improvements.md](../docs/reports/11-real-world-matching-improvements.md) | Detection fallback + matching fixes |
| [12-sqlite-database.md](../docs/reports/12-sqlite-database.md) | SQLite + medicine query API |
| [13-automated-testing.md](../docs/reports/13-automated-testing.md) | pytest suite |
| [14-docker-containerization.md](../docs/reports/14-docker-containerization.md) | Docker deployment |
| [15-flutter-foundation.md](../docs/reports/15-flutter-foundation.md) | Flutter foundation |
| [16-mobile-integration.md](../docs/reports/16-mobile-integration.md) | Mobile API integration |
| [17-ci-cd-github-actions.md](../docs/reports/17-ci-cd-github-actions.md) | GitHub Actions CI |
| [18-medicine-database-expansion.md](../docs/reports/18-medicine-database-expansion.md) | TİTCK SKRS database expansion |
| [19-performance-optimization.md](../docs/reports/19-performance-optimization.md) | Fast-mode latency optimization |
| [20-production-hardening.md](../docs/reports/20-production-hardening.md) | Security & production settings |
| [25-e2e-performance.md](../docs/reports/25-e2e-performance.md) | Mobile+backend E2E & performance tooling |

## CI status checks (required for merge — recommended)

| Check name | Workflow |
|------------|----------|
| `pytest (Python 3.11)` | Backend Tests |
| `flutter analyze & test` | Mobile Tests |

Enable in **Settings → Branches → Branch protection** after first green run on `main`.
