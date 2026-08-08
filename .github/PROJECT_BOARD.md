# GitHub Project Board — Column Mapping

Use this file when organizing issues on the GitHub Project board for **Yolocilin**.

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
| [#50](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/50) | Final polish rounds (partial — see open leftovers) |

## In Progress

| Item | Branch |
|------|--------|
| Final polish / docs refresh | `feature/final-polish-4` |

## Post-MVP / Todo

| Issue | Notes |
|-------|--------|
| [#32](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/32) | Advanced leftovers: PostgreSQL, cloud, barcode, iOS |
| [#9](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/9) | Internship report / final documentation wrap-up |

## Closed / Superseded

| Issue | Reason |
|-------|--------|
| [#7](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/7) | Streamlit replaced by Flutter ([#30](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/30), [#31](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/31)) |

## Labels

| Label | Use |
|-------|-----|
| `ai-pipeline` | YOLO, OCR, matching |
| `backend` | FastAPI |
| `mobile` | Flutter / Yolocilin |
| `database` | SQLite / PostgreSQL |
| `testing` | pytest |
| `infrastructure` | Docker, CI/CD |
| `mvp` | Minimum viable product scope |
| `docs` | README / reports |

## Technical reports

Full index: [docs/reports/README.md](../docs/reports/README.md)

| Report | Topic |
|--------|--------|
| 01–09 | Setup → pipeline servicification |
| [10](../docs/reports/10-fastapi-analyze-api.md)–[14](../docs/reports/14-docker-containerization.md) | API, matching, SQLite, tests, Docker |
| [15](../docs/reports/15-flutter-foundation.md)–[17](../docs/reports/17-ci-cd-github-actions.md) | Mobile + CI |
| [18](../docs/reports/18-medicine-database-expansion.md)–[19](../docs/reports/19-performance-optimization.md) | Catalog + performance |
| [20](../docs/reports/20-production-hardening.md) | Security |
| [21](../docs/reports/21-llm-integration.md) | Gemini explain |
| [22](../docs/reports/22-camera-capture.md) | Camera |
| [23](../docs/reports/23-scan-history.md) | Local + server history |
| [24](../docs/reports/24-medicine-database-final-refresh.md) | 131-row catalog |
| [25](../docs/reports/25-e2e-performance.md) | E2E & benchmarks |

## CI status checks (recommended for branch protection)

| Check name | Workflow |
|------------|----------|
| `pytest (Python 3.11)` | Backend Tests |
| `flutter analyze & test` | Mobile Tests |
