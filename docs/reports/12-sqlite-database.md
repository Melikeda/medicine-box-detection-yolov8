# Report 12 — SQLite Database Migration

## Overview

Phase 13 migrates the medicine data layer from CSV-only reads to **SQLite + SQLAlchemy**, while keeping `medicines.csv` as the seed source of truth.

**Branch:** `feature/sqlite-database`  
**GitHub Issue:** #27

---

## Objectives

- [x] Define SQLAlchemy `Medicine` model
- [x] Seed database from CSV (upsert by `medicine_id`)
- [x] Load RapidFuzz matching from SQLite
- [x] Add medicine query endpoints
- [x] Add seed CLI script and configuration

---

## Architecture

```text
medicines.csv  ──seed/upsert──►  medicines.db (SQLite)
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
           MatchingService                      GET /api/v1/medicines
           (RapidFuzz in-memory)                GET /api/v1/medicines/{id}
```

- **CSV:** editable source for adding drugs
- **SQLite:** runtime database for API queries and pipeline matching
- On startup, CSV is upserted into SQLite so both stay in sync

---

## New Modules

| Path | Role |
|------|------|
| `src/database/models.py` | SQLAlchemy `Medicine` model |
| `src/database/session.py` | Engine / session factory |
| `src/database/repository.py` | Seed, list, get, load helpers |
| `backend/app/routers/medicines.py` | REST endpoints |
| `backend/app/services/medicine_service.py` | Query service |
| `backend/app/schemas/medicines.py` | Pydantic schemas |
| `scripts/seed_sqlite.py` | Manual seed CLI |

---

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `USE_SQLITE` | `true` | Prefer SQLite over CSV for matching |
| `SQLITE_PATH` | `data/database/medicines.db` | Database file path |
| `PipelineConfig.use_sqlite` | `True` | Same flag in pipeline |
| `PipelineConfig.sqlite_path` | `data/database/medicines.db` | Same path |

Generated `.db` files are gitignored.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/medicines` | List / search medicines |
| GET | `/api/v1/medicines/categories` | Distinct categories |
| GET | `/api/v1/medicines/{medicine_id}` | Single medicine detail |

Query parameters for list:

- `search` — name, brand, or ingredient
- `category` — category filter
- `limit` / `offset` — pagination

---

## Usage

```bash
pip install -r requirements.txt

# Optional manual seed
python scripts/seed_sqlite.py

# API (auto-seeds on pipeline load)
python run_api.py
```

```bash
curl "http://127.0.0.1:8000/api/v1/medicines?search=nurofen"
curl "http://127.0.0.1:8000/api/v1/medicines/MED038"
```

---

## Matching Integration

`MatchingService.from_config()`:

1. If `use_sqlite=True` → seed CSV → load all rows from SQLite into memory
2. Else → load CSV directly (legacy fallback)

RapidFuzz still runs in-memory for speed; SQLite is the durable store.

---

## Next Phase

Issue #28 — Automated tests (include SQLite seed + medicine endpoints) — see [Report 13](13-automated-testing.md).
Next: Issue #30 — Flutter mobile app foundation.
