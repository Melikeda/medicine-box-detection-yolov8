# Report 28 — Barcode Reading Path

> Living decision record. Barcode is an **optional parallel identity path**; YOLO → OCR → RapidFuzz stays the default.  
> Branch: `feature/barcode-reading`  
> Code: `src/barcode/`, `src/database/` (`medicine_barcodes`), `backend/app/routers/barcode.py`, `src/services/pipeline_manager.py`

**Product:** Yolocilin · catalog **1163** · OCR **EasyOCR** · barcode **zxing-cpp**

---

## Purpose

Box-text OCR is slow on CPU and brittle on blurry photos. Turkish packs already carry EAN-13 (and often an İTS DataMatrix). Reading that code and looking it up in the TİTCK-linked catalog is faster and more exact **when the code is in frame**.

This path must not replace the current analyze flow. If the barcode is missing, damaged, unknown, or the decoder library is absent, the existing OCR matcher still runs.

---

## Decision

| Situation | Product behaviour |
|-----------|-------------------|
| Dedicated live code / photo | Scan-tab **Barkod tara** → `GET /api/v1/barcode/lookup` or `POST /api/v1/barcode/scan` |
| Box photo with a readable code | Analyze tries barcode on the YOLO crop (and full frame if no box) **before** OCR |
| No barcode / decoder miss / unknown GTIN | Unchanged OCR + RapidFuzz path |
| GTIN not in the 1163-row map | TİTCK SKRS index lookup, then fuzzy map onto the catalog when possible |
| Medicine found | Same `medicine_id` → existing `POST /api/v1/explain` |

Mobile: **Barkod tara** opens a live overlay; **Fotoğraftan oku** posts to `/barcode/scan`. Matches reuse the existing result screen and explain card.

Phone scanners often prefix AIM identifiers (`]C1…`). Lookup strips those so EAN-13 `869…` reaches the catalog (not `1869…`).

---

## Catalog

Medicines stay one row per display name in `medicines.csv`. Barcodes are **1:N** in `medicine_barcodes.csv` (`barcode`, `medicine_id`) because SKRS lists package GTINs, not brand-level IDs.

Populate from TİTCK without rewriting the seed catalog:

```bash
python scripts/attach_titck_barcodes.py --no-download
python scripts/seed_sqlite.py
```

Current mapping (this branch): **2043** GTINs covering **1041** of **1163** catalog rows. Seed also stores GTIN-13/14 lookup aliases. Unknown `medicine_id` rows are skipped at seed time.

A local SKRS barcode index (`data/database/titck/skrs_barcode_index.csv`, gitignored) backs lookup when the compact CSV map misses.

---

## API

| Method | Path | Role |
|--------|------|------|
| GET | `/api/v1/barcode/info` | Limits / formats |
| GET | `/api/v1/barcode/lookup?code=` | Exact GTIN lookup (live camera clients) |
| POST | `/api/v1/barcode/scan` | Decode image + lookup |

Analyze responses may include `match_source=barcode` and `barcode` when the fast path hits. OCR-only clients can ignore those fields.

---

## Libraries

| Library | Why |
|---------|-----|
| **zxing-cpp** | EAN/UPC/QR/DataMatrix wheels on Windows and Linux; no libzbar |
| **python-barcode** | Synthetic EAN-13 fixtures in tests / examples |
| **mobile_scanner** | On-device live decode; the phone sends the raw code to lookup |

OpenCV is already in the stack (image decode + optional upscale). If `zxing-cpp` is not installed in the API venv, analyze skips image barcode decode and continues to OCR.

---

## Tests

`tests/test_barcode.py` — normalize GS1 and AIM prefixes, decode a generated EAN-13, SQLite lookup, matching service, lookup/scan endpoints, SKRS CSV fallback.

---

## What did not change

- YOLOv8 weights, EasyOCR as the only OCR engine, RapidFuzz gates (Report 27)
- Gemini explain contract (`medicine_id`); busy Gemini falls back to catalog text (Report 21)
- Camera / OCR scan tab remains the default box-photo path
