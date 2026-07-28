# Report 11 — Real-World Detection & Matching Improvements

## Overview

After the analyze API was deployed, testing with real phone photos revealed edge cases: blurry images with zero YOLO detections, partial OCR brand reads, dosage-only text false matches, and OCR confusions (e.g. `€` instead of `C`). This report documents the fixes merged to `main` in commit `57789fe`.

---

## Problems Found in Testing

| Photo type | Symptom | Root cause |
|------------|---------|------------|
| Blurry multi-box | YOLO count = 0 | Default confidence threshold (0.60) too high |
| Blurry Nurofen box | OCR reads `fen`, no match | Short text rejected by coverage ratio check |
| Parafon box | Matched as Nurofen Cold & Flu | Dosage OCR matched `active_ingredient` field |
| Ibucold C box | Matched as Ibucold | OCR read `€` instead of `C` |
| Parafon | `not_found` | Drug missing from CSV |

---

## 1. YOLO Adaptive Fallback

**File:** `src/services/detection_service.py`, `src/services/config.py`

| Setting | Old | New |
|---------|-----|-----|
| `confidence_threshold` | 0.60 | 0.40 |
| `fallback_confidence_threshold` | — | 0.25 |

**Logic:**

1. Detect at primary threshold (0.40)
2. If zero boxes → retry at 0.25
3. If weak detections (max confidence < 0.55) and fallback finds more boxes → use fallback result

**Example:** Blurry photo went from 0 boxes → 3 boxes with fallback.

---

## 2. Partial Brand Matching

**File:** `src/services/matching_service.py`

Allows high-score matches when OCR reads only part of a brand name:

- Example: `fen` → brand `Nurofen` (score 90, coverage on brand ≥ 40%)
- Requires `minimum_partial_brand_match_score` ≥ 85
- Still rejects single-letter false positives (`s`, `u`)

---

## 3. Dosage / Form Text Filtering

**Files:** `src/matching/medicine_matcher.py`, `src/services/candidate_processor.py`

Rejects OCR that contains dosage markers without a brand word:

- Example: `250 mo / j0o mo tablot` → filtered out (was matching Nurofen via ingredient field)
- Markers: `mg`, `mo`, `tablet`, `tablot`, `kapli`, etc.
- Skips `active_ingredient` field comparison for dosage-like queries

When only dosage text is read → `status: not_found` (not a wrong drug name).

---

## 4. OCR Text Normalization

**File:** `src/matching/text_normalizer.py`

Common OCR confusions normalized before matching:

| OCR read | Normalized |
|----------|------------|
| `€` | `c` |
| `©` | `c` |
| `¢` | `c` |

**Example:** `ibucold €` → `ibucold c` → **Ibucold C** (100)

Single-letter suffix combination: separate OCR tokens `ibucold` + `€` → candidate `ibucold c`.

---

## 5. Database Update

**File:** `data/database/medicines.csv`

Added:

| ID | Name |
|----|------|
| MED038 | Parafon |

Total records: **38**

---

## Configuration Reference

```python
# src/services/config.py (selected)
confidence_threshold: float = 0.40
fallback_confidence_threshold: float = 0.25
minimum_name_coverage_ratio: float = 0.45
minimum_brand_coverage_ratio: float = 0.40
minimum_partial_brand_match_score: float = 85.0
minimum_match_score: float = 80.0
minimum_plausible_match_score: float = 55.0
```

---

## Box Status Values

| Status | Meaning |
|--------|---------|
| `matched` | OCR matched a CSV drug above threshold |
| `not_found` | Box detected, OCR ran, no reliable CSV match |
| `not_medicine_box` | Low-confidence OCR; likely non-medicine YOLO false positive |
| `error` | Pipeline exception for this box |

---

## Recommendations for Users

1. Use **well-lit, steady photos** — blur hurts both YOLO and OCR
2. Prefer **`mode=accurate`** for difficult boxes (slow on CPU)
3. Add new drugs to `medicines.csv` before expecting matches
4. Restart API after code changes: `python run_api.py`

---

## Next Steps

- Issue #27 — SQLite migration
- Issue #28 — Automated tests for matching edge cases
- Long-term — YOLO retrain with blurry/negative samples
