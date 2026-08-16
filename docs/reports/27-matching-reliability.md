# Report 27 — Matching Reliability Gates

> Living decision record. Prefer **no card** over a **wrong drug**.  
> Code: `src/services/matching_service.py`, `src/services/config.py`, `src/services/pipeline_manager.py`  
> Merged: [PR #67](https://github.com/Melikeda/yolocilin/pull/67) (`feature/tighten-matching-gates`)  
> Related: [Report 11](11-real-world-matching-improvements.md) (historical `fen` → Nurofen) · [Report 26](26-ocr-engine-comparison.md) (engine trial; matcher was the false-name cause)

**Product:** Yolocilin · catalog **1163** · OCR **EasyOCR** (CPU)

---

## Purpose

Phone photos often yield a 3-letter OCR fragment (`fen`, `alm`, `pal`, `dex`). RapidFuzz `WRatio` ≥ 88 treated those as confident hits (`fen` → Nurofen, `alm` → Mydocalm). Fast mode then **stopped OCR**, so later variants never read the full brand.

Swapping EasyOCR for PaddleOCR did not remove that gate ([Report 26](26-ocr-engine-comparison.md)). The fix is matching policy, not a new engine.

---

## Decision

| Situation | Product behaviour |
|-----------|-------------------|
| Full / exact brand (`parol`, `nurofen`, `etol`) | `matched` |
| Suffix fragment (`fen`, `alm`, `pal`) | `not_found` + retake hint |
| Prefix fragment shorter than 5 letters | `not_found` |
| Blurry / distant / multi-box carpet photo | Slow CPU OCR and/or `not_found` — expected on this stack |

Internship constraint: EasyOCR on **CPU**, sequential variants (fast: up to 8; then a 24-variant deep retry if unmatched). YOLO and RapidFuzz are not the wait. GPU would speed OCR; it is not required to close the internship deliverable.

---

## Gates (current code)

| Setting | Value | Role |
|---------|--------|------|
| `minimum_match_score` | 88 | Final accept floor |
| `early_exit_minimum_score` | **95** | Fast OCR may stop only on a near-complete match |
| `minimum_partial_match_text_length` | **5** | Partial/substring matches |
| `minimum_matching_text_length` | 3 | Filter only — keeps exact short brands (Etol, Avil) |
| `minimum_brand_coverage_ratio` | **0.55** | Prefix fragment must cover enough of the brand |
| Suffix-only fragment | rejected | `fen` in Nurofen, `alm` in Mydocalm |
| Exact catalog label | allowed at ≥ 3 letters | `etol` → Etol Fort |

Tests: `tests/test_matching.py` (suffix rejection, Etol/Parol/Nurofen still match).

---

## What did not change

- Flutter, FastAPI routes, YOLO weights, EasyOCR as the only engine
- Gemini explain stays **optional** (`LLM_ENABLED` + local `.env` key; never commit `.env`)
- Barcode / vision-LLM identity remain Future Development

---

## Operator notes

- Debug APK talks to the PC API (`API_BASE_URL=http://<PC-IP>:8000`). Restart `python run_api.py` after `.env` changes. Port **8000** accepts only one process.
- Clear, close, well-lit single-box photos are the supported demo path.
- Slightly bad photos asking for a retake is the intended medical-safer behaviour.
