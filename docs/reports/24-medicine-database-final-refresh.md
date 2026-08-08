# Report 24 — Medicine Database Final Refresh

## Overview

Final catalog refresh on **`feature/final-polish-2`**: re-sync with latest TİTCK SKRS, add popular OTC brands missing from the e-reçete list, fix known bad rows, and re-seed SQLite.

**Branch:** `feature/final-polish-2`  
**Date:** 2026-08-06

---

## Objectives

- [x] Download latest TİTCK SKRS (7948 active rows, Aug 2026)
- [x] Re-run enrichment + brand expansion pipeline
- [x] Append popular manual OTC rows (Mucosolvan, Mesulid, Redoxon, …)
- [x] Append selected SKRS single-product brands (Advil, Dolgit, Klacid, Differin)
- [x] Fix incorrect dosage/form/category on existing rows
- [x] Seed `medicines.db` (131 records)
- [x] Validate CSV + pytest

---

## Results

| Metric | Before (round 1) | After |
|--------|------------------|-------|
| CSV / SQLite rows | 107 | **131** |
| Placeholder fields (dosage/form/ingredient) | 30 | **29** (~7.4%) |
| TİTCK SKRS rows (active) | ~7900 | **7948** |
| SKRS manifest date | — | **2026-08-04** |

### New popular additions (manual + SKRS)

| ID | Name | Source |
|----|------|--------|
| MED115–116 | Mucosolvan (şurup + tablet) | Manual OTC |
| MED117 | Bisolvon | Manual OTC |
| MED118 | Mydocalm | Manual OTC |
| MED119 | Mesulid | Manual OTC |
| MED120 | Redoxon | Manual OTC |
| MED121 | Berocca | Manual OTC |
| MED122 | Sinutab | Manual OTC |
| MED123 | Minol | Manual OTC |
| MED124 | Strepsils | Manual OTC |
| MED125 | Deflamax | Manual OTC |
| MED126 | Mobilat | Manual OTC |
| MED127 | Pharmaton | Manual OTC |
| MED128 | Advil Liqui-Gels | TİTCK SKRS |
| MED129 | Dolgit %5 Krem | TİTCK SKRS |
| MED130 | Klacid | TİTCK SKRS |
| MED131 | Differin | TİTCK SKRS |

### Corrections

| ID | Fix |
|----|-----|
| MED022 Diclomec | Dosage `50 G` → `50 mg`, form corrected |
| MED023 Rennie | Dosage `100 ML` → `680 mg`, form → Çiğnenebilir Tablet |
| MED084–086 Tegretol | Category → Nöroloji |
| MED105–106 Bepanthen | Category → Genel |

---

## Pipeline (unchanged flow, new modules)

```text
python scripts/fetch_titck_skrs.py
python scripts/enrich_medicines_from_titck.py
python scripts/validate_medicines_csv.py
python scripts/seed_sqlite.py
```

New code:

| File | Role |
|------|------|
| `scripts/titck/popular_manual_rows.py` | OTC brands not found under brand name in SKRS |
| `scripts/titck/manual_overrides.py` | `ROW_CORRECTIONS` for persistent fixes |

---

## Tests

- `tests/test_medicines_csv_validation.py` — ≥100 rows, placeholder rate <15%
- `tests/test_titck_mapper.py` — mapper + overrides
- `tests/test_database.py` — seed / list (fixture CSV unchanged)

---

## Operational notes

1. After any CSV edit: `python scripts/seed_sqlite.py` then restart backend.
2. SKRS XLSX remains gitignored; manifest `data/database/titck/skrs_manifest.json` is committed.
3. Re-run `fetch_titck_skrs.py` periodically when TİTCK publishes updates.

---

## Follow-up (post-MVP)

- PostgreSQL migration (server scan history already on SQLite — [Report 23](23-scan-history.md))
- Reduce topical placeholders (gel/cream form parsers)
- Optional CI job on `data/database/medicines.csv` changes
