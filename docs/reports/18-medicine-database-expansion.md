# Report 18 — Medicine Database Expansion (TİTCK SKRS)

## Overview

Expands the seed medicine catalog from **38** to **107** records by enriching placeholder fields from the official TİTCK SKRS E-Reçete list and appending common OTC brand variants used in Turkish pharmacy shelves.

**Branch:** `feature/medicine-database-expansion`  
**GitHub Issue:** [#41](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/41)

---

## Objectives

- [x] Download and parse latest TİTCK SKRS XLSX (~7.9k active rows)
- [x] Reproducible scripts under `scripts/titck/` and `scripts/enrich_medicines_from_titck.py`
- [x] Reduce `VERIFY_FROM_OFFICIAL_*` placeholders via ATC + parsed dosage/form
- [x] Expand catalog with scored brand queries (Parol, Augmentin, Voltaren, …)
- [x] Manual overrides for supplements / missing SKRS rows (Nurofen, Supradyn, Imunol)
- [x] CSV validation script + pytest coverage
- [x] Data README and TİTCK source attribution

---

## Data source

| Item | Value |
|------|-------|
| Publisher | T.C. Sağlık Bakanlığı — TİTCK |
| Page | https://www.titck.gov.tr/dinamikmodul/43 |
| Format | SKRS E-Reçete İlaç ve Diğer Farmasötik Ürünler Listesi (XLSX) |
| Manifest | `data/database/titck/skrs_manifest.json` |

The raw XLSX is **not committed** (`.gitignore`); CI and fresh clones run enrichment locally or rely on the committed CSV output.

---

## Pipeline

```text
TİTCK SKRS XLSX
      │
      ▼
scripts/titck/skrs_client.py  ──►  pandas DataFrame (ilac_adi, atc_kodu, atc_adi, durumu)
      │
      ▼
scripts/titck/medicine_mapper.py
  • score_titck_row / find_best_titck_match
  • parse_dosage / parse_form / category_from_atc
  • discover_expansion_rows (brand queries + ATC exclusions)
      │
      ▼
scripts/titck/manual_overrides.py
      │
      ▼
data/database/medicines.csv  ──►  SQLite seed on API startup
```

---

## Results

| Metric | Before | After |
|--------|--------|-------|
| CSV rows | 38 | 107 |
| Placeholder fields (dosage/form/ingredient) | ~40+ | 30 (~9%) |
| Enrichment source | Manual / leaflet placeholders | TİTCK SKRS + overrides |

Notable fixes:

- **Apranax** → Naproxen 275 MG (was mismatched before scoring tweak)
- **Nurofen** base tablet → manual Ibuprofen 200 mg (no plain SKRS row)
- Expansion filtering excludes diagnostic ATC (e.g. V08 contrast media)

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/fetch_titck_skrs.py` | Download XLSX + write manifest |
| `scripts/enrich_medicines_from_titck.py` | Enrich + expand CSV |
| `scripts/validate_medicines_csv.py` | Schema / duplicate / placeholder stats |

---

## Tests

- `tests/test_titck_mapper.py` — scoring, parsing, enrichment, overrides
- `tests/test_medicines_csv_validation.py` — committed CSV ≥100 rows, placeholder rate <15%

---

## Follow-up

- Periodic re-run of `fetch_titck_skrs.py` when TİTCK publishes updates
- Further reduce placeholders for topicals (gel/cream) via form-specific parsers
- Optional CI job to validate CSV on `data/database/**` changes
