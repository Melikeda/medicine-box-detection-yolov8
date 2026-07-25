# GitHub Project Board — Issue Mapping

This file maps GitHub Issues to recommended Project board columns.

## Column: Done

| Issue | Title |
|-------|-------|
| #6 | Implement medicine name matching |

## Column: In Progress

| Issue | Title | Branch |
|-------|-------|--------|
| #23 | Unify AI pipeline under src/services | `refactor/unify-pipeline` |

## Column: Todo — AI Pipeline

| Issue | Title | Branch |
|-------|-------|--------|
| #24 | Service-layer pipeline architecture | `feature/pipeline-services` |

## Column: Todo — Backend

| Issue | Title | Branch |
|-------|-------|--------|
| #25 | FastAPI backend foundation | `feature/fastapi-foundation` |
| #26 | Image upload and analyze API endpoint | `feature/analyze-endpoint` |
| #27 | SQLite database migration | `feature/sqlite-database` |
| #28 | Automated test system (pytest) | `feature/tests` |
| #29 | Docker containerization for backend | `feature/docker` |

## Column: Todo — Mobile

| Issue | Title | Branch |
|-------|-------|--------|
| #30 | Flutter mobile app foundation | `feature/flutter-foundation` |
| #31 | Mobile and backend integration (MVP) | `feature/mobile-integration` |

## Column: Todo — Post-MVP

| Issue | Title | Branch |
|-------|-------|--------|
| #8 | Integrate LLM support | `feature/llm-integration` |
| #32 | Advanced features | `feature/advanced-features` |
| #9 | Test and document final system | `feature/final-testing` |

## Closed / Superseded

| Issue | Title | Reason |
|-------|-------|--------|
| #7 | Build Streamlit interface | Replaced by Flutter (#30, #31) |

## Labels

| Label | Purpose |
|-------|---------|
| `ai-pipeline` | YOLO, OCR, matching work |
| `backend` | FastAPI |
| `mobile` | Flutter |
| `database` | SQLite / PostgreSQL |
| `testing` | pytest |
| `infrastructure` | Docker, deployment |
| `mvp` | Minimum viable product scope |
