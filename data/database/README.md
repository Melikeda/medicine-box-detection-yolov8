# Medicine Database

<p align="center">
  <strong>Yolocilin seed catalog — OCR fuzzy matching &amp; runtime API</strong>
</p>

<p align="center">
  CSV source of truth · SQLite runtime (`medicines` + `scans`) · TİTCK SKRS enrichment
</p>

---

## Overview

This directory holds the **medicine catalog** used by the analyze pipeline and the FastAPI `/api/v1/medicines` endpoints. OCR text from detected boxes is matched against `medicine_name` and `brand_name` fields using RapidFuzz.

| Metric | Value |
|--------|-------|
| **Catalog size** | 131 medicines |
| **Source file** | `medicines.csv` (committed) |
| **Runtime DB** | `medicines.db` (generated, gitignored) |
| **Placeholder rate** | ~7% of dosage/form/ingredient fields |
| **Last TİTCK sync** | See `titck/skrs_manifest.json` |

> **Design rule:** Edit `medicines.csv`, then seed SQLite. Do not edit `medicines.db` by hand.

---

## Table of contents

- [Architecture](#architecture)
- [Directory layout](#directory-layout)
- [CSV schema](#csv-schema)
- [Quick start](#quick-start)
- [TİTCK enrichment pipeline](#titk-enrichment-pipeline)
- [Manual curation layers](#manual-curation-layers)
- [Editing the catalog](#editing-the-catalog)
- [Validation & tests](#validation--tests)
- [Troubleshooting](#troubleshooting)
- [Related documentation](#related-documentation)

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                     data/database/                              │
│  medicines.csv  ──►  seed / upsert  ──►  medicines.db (SQLite)  │
│       ▲                                        │                │
│       │                                        ▼                │
│  TİTCK SKRS XLSX                    MatchingService + API       │
│  + manual overrides                     (OCR fuzzy match)       │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | File | Role |
|-------|------|------|
| **Source of truth** | `medicines.csv` | Human-editable seed list; version-controlled |
| **Runtime store** | `medicines.db` | Fast queries for API and pipeline; regenerated from CSV |
| **Official reference** | `titck/skrs_latest.xlsx` | TİTCK E-Reçete export (local cache, gitignored) |
| **Sync metadata** | `titck/skrs_manifest.json` | Download date, URL, active row count |

The backend loads SQLite on startup (`PipelineConfig.use_sqlite=True`) and upserts from CSV when needed via `ensure_database_seeded()`.

---

## Directory layout

```text
data/database/
├── README.md                 # This file
├── medicines.csv             # Seed catalog (edit this)
├── medicines.db              # Generated SQLite (do not commit)
└── titck/
    ├── skrs_manifest.json    # Last SKRS download metadata
    └── skrs_latest.xlsx      # Cached TİTCK export (gitignored)
```

---

## CSV schema

| Column | Type | Description |
|--------|------|-------------|
| `medicine_id` | string | Unique ID (`MED001`, `MED002`, …) |
| `medicine_name` | string | Primary display name and main OCR match target |
| `brand_name` | string | Brand token for partial / fuzzy matching |
| `active_ingredient` | string | ATC active substance (title case) |
| `dosage` | string | Strength when known (e.g. `500 mg`, `200 mg / 30 mg`) |
| `form` | string | Pharmaceutical form (Tablet, Şurup, Kapsül, …) |
| `category` | string | Therapeutic group for UI (Ağrı Kesici, Antibiyotik, …) |

### Placeholder values

When dosage, form, or ingredient cannot be reliably parsed from TİTCK SKRS (topicals, complex combinations, supplements), the catalog uses:

```text
VERIFY_FROM_OFFICIAL_LEAFLET
```

These rows remain matchable by brand/name; only structured fields are deferred for manual review.

### Example row

```csv
medicine_id,medicine_name,brand_name,active_ingredient,dosage,form,category
MED011,Nurofen,Nurofen,Ibuprofen,200 mg,Tablet,Ağrı Kesici
```

---

## Quick start

From the repository root:

```bash
# Sync SQLite from the committed CSV
python scripts/seed_sqlite.py

# Restart the backend so the pipeline picks up changes
# Windows: .\scripts\stop-backend.ps1 && .\scripts\start-backend.ps1
```

Verify:

```bash
python scripts/validate_medicines_csv.py
python -m pytest tests/test_medicines_csv_validation.py -q
```

---

## TİTCK enrichment pipeline

Official source: [TİTCK SKRS E-Reçete İlaç Listesi](https://www.titck.gov.tr/dinamikmodul/43)

Full refresh (recommended after TİTCK publishes an update):

```bash
python scripts/fetch_titck_skrs.py
python scripts/enrich_medicines_from_titck.py
python scripts/validate_medicines_csv.py
python scripts/seed_sqlite.py
```

Use cached SKRS file (offline / faster):

```bash
python scripts/enrich_medicines_from_titck.py --no-download
```

### Script reference

| Script | Purpose |
|--------|---------|
| `scripts/fetch_titck_skrs.py` | Download latest SKRS XLSX; write manifest |
| `scripts/enrich_medicines_from_titck.py` | Enrich placeholders, expand brands, append popular OTC rows |
| `scripts/validate_medicines_csv.py` | Schema, duplicates, placeholder statistics |
| `scripts/seed_sqlite.py` | CSV → SQLite upsert |

### Enrichment flags

| Flag | Effect |
|------|--------|
| `--no-download` | Use existing `titck/skrs_latest.xlsx` |
| `--no-expand` | Enrich existing rows only; do not append new medicines |
| `--dry-run` | Print summary without writing CSV |

### What enrichment does

1. **Match** each CSV row to the best TİTCK SKRS product (scored fuzzy match).
2. **Fill** `active_ingredient`, `dosage`, and `form` from SKRS where confidence is sufficient.
3. **Expand** common OTC brand variants (Parol, Augmentin, Voltaren, …).
4. **Append** popular shelf medicines missing from SKRS under brand name (see manual layer below).
5. **Apply** persistent corrections and overrides.

---

## Manual curation layers

Some products are not listed under their consumer brand in SKRS, or require domain fixes after automated enrichment.

| Module | Path | Purpose |
|--------|------|---------|
| Manual overrides | `scripts/titck/manual_overrides.py` | Nurofen base tablet, supplements; `ROW_CORRECTIONS` for known bad fields |
| Popular OTC rows | `scripts/titck/popular_manual_rows.py` | Mucosolvan, Redoxon, Mesulid, Sinutab, … |
| Brand mapper | `scripts/titck/medicine_mapper.py` | SKRS scoring, dosage/form parsing, expansion queries |

To add a medicine that SKRS cannot resolve by brand:

1. Add an entry to `POPULAR_MANUAL_ROWS` in `popular_manual_rows.py`, **or**
2. Add a row directly to `medicines.csv` with the next `MED###` ID.
3. Run validate → seed → restart backend.

---

## Editing the catalog

### Add or update a medicine

1. Edit `medicines.csv` (unique `medicine_id`, no duplicate names if avoidable).
2. Run `python scripts/validate_medicines_csv.py`.
3. Run `python scripts/seed_sqlite.py`.
4. Restart the API.

### ID convention

- Format: `MED` + three-digit number (`MED001` … `MED131`).
- New rows: use the next free ID (check the last row in CSV or run enrichment with `--dry-run`).

### Do not

- Commit `medicines.db` or `titck/skrs_latest.xlsx` (gitignored).
- Edit SQLite directly for permanent changes — changes will be overwritten on seed.

---

## Validation & tests

```bash
# Standalone CSV check
python scripts/validate_medicines_csv.py

# Automated tests
python -m pytest tests/test_medicines_csv_validation.py tests/test_titck_mapper.py tests/test_database.py -q
```

Quality gates (enforced in CI via pytest):

| Check | Threshold |
|-------|-----------|
| Minimum catalog size | ≥ 130 rows |
| Duplicate `medicine_id` | 0 |
| Placeholder field rate | < 15% of dosage/form/ingredient fields |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| API still shows old medicine count | Stale SQLite or backend not restarted | `seed_sqlite.py` + restart backend |
| New CSV row not matched in scans | SQLite not seeded | Run `python scripts/seed_sqlite.py` |
| Enrichment adds wrong dosage | Ambiguous SKRS product name | Fix via `ROW_CORRECTIONS` or edit CSV manually |
| `fetch_titck_skrs.py` fails | Network or TİTCK site change | Use `--no-download` with cached XLSX; check manifest URL |
| Validation fails on placeholders | Too many `VERIFY_*` fields | Enrich from SKRS or fill fields manually |

---

## Related documentation

| Document | Description |
|----------|-------------|
| [Report 12 — SQLite database](../../docs/reports/12-sqlite-database.md) | Initial SQLite integration |
| [Report 18 — TİTCK expansion](../../docs/reports/18-medicine-database-expansion.md) | First SKRS pipeline (38 → 107 rows) |
| [Report 24 — Final refresh](../../docs/reports/24-medicine-database-final-refresh.md) | Latest catalog refresh (131 rows) |
| [Project roadmap — Phase 17.6](../../docs/roadmap.md) | Database phase tracking |

---

## License & data attribution

Medicine product data enriched from **T.C. Sağlık Bakanlığı — TİTCK SKRS E-Reçete list**. Manual OTC entries and corrections are maintained in this repository for OCR matching purposes. This catalog is **not** a substitute for official prescribing information or patient leaflets.
