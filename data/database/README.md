# Medicine database

Seed catalog for OCR fuzzy matching (`medicines.csv`) and SQLite runtime storage.

## Source of truth

| File | Role |
|------|------|
| `medicines.csv` | Editable seed list (committed) |
| `medicines.db` | Generated SQLite DB (gitignored) |
| `titck/skrs_manifest.json` | Last TİTCK SKRS download metadata |
| `titck/skrs_latest.xlsx` | Downloaded SKRS export (gitignored; regenerate locally) |

## TİTCK enrichment pipeline

Official data: [TİTCK SKRS E-Reçete list](https://www.titck.gov.tr/dinamikmodul/43)

```bash
# 1) Download latest SKRS XLSX + manifest
python scripts/fetch_titck_skrs.py

# 2) Enrich placeholders and expand OTC catalog
python scripts/enrich_medicines_from_titck.py

# 3) Validate CSV
python scripts/validate_medicines_csv.py
```

Options:

- `--no-download` — use cached `titck/skrs_latest.xlsx`
- `--no-expand` — only enrich existing rows
- `--dry-run` — print row count without writing

Manual corrections for supplements or missing SKRS rows live in `scripts/titck/manual_overrides.py`.

## CSV schema

| Column | Description |
|--------|-------------|
| `medicine_id` | Unique ID (`MED001` …) |
| `medicine_name` | Display / OCR match name |
| `brand_name` | Brand token for partial matching |
| `active_ingredient` | ATC active substance (title case) |
| `dosage` | Parsed strength when available |
| `form` | Tablet, şurup, kapsül, … |
| `category` | Therapeutic category for UI grouping |

Placeholder values (`VERIFY_FROM_OFFICIAL_LEAFLET`) remain where SKRS does not provide reliable dosage/form (e.g. topicals, combinations).

## After editing CSV

Restart the API or run:

```bash
python scripts/seed_sqlite.py
```

See also [Report 18](../../docs/reports/18-medicine-database-expansion.md).
