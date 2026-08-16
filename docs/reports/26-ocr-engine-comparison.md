# Report 26 — OCR Engine Comparison (EasyOCR vs PaddleOCR)

> Living decision record. Product OCR remains **EasyOCR**.  
> Experiment folder: [docs/experiments/paddleocr-comparison](../experiments/paddleocr-comparison/).  
> Related: [Report 07](07-ocr-integration.md) (EasyOCR integration) · [technology-selection.md](../technology-selection.md).

**Branch:** `feature/paddleocr-engine` (evaluation only)  
**Outcome:** PaddleOCR is **not** adopted. It is not installed, loaded, or configurable in the application.

---

## Purpose

Decide whether Yolocilin should replace or dual-run EasyOCR with PaddleOCR.

Constraints:

- Do not break the existing YOLO → OpenCV → RapidFuzz → FastAPI → Flutter path
- Do not add Paddle packages to `requirements.txt`, Docker, or CI
- Judge engines on **correct catalog identity**, not OCR character error rate alone

---

## Method

The same pipeline processed each photo twice (`ocr_mode=fast`):

1. YOLOv8 crop (identical boxes)
2. OpenCV variants (scale, sharpen, 0/90/180/270°)
3. OCR reader (EasyOCR **or** PaddleOCR)
4. Existing matcher + SQLite catalog (1163)

PaddleOCR 3.x was wrapped to EasyOCR’s `readtext()` shape so matching did not change. On Windows CPU, PaddlePaddle 3.3 + oneDNN crashed (`ConvertPirAttribute2RuntimeAttribute`); the trial adapter disabled MKLDNN so inference could finish.

Trial photos and JSON: [paddleocr-comparison](../experiments/paddleocr-comparison/).

---

## Results

### Single / two-box photos

| Photo | Ground truth | EasyOCR | PaddleOCR |
|-------|--------------|---------|-----------|
| Arveles | Arveles | Arveles 93 (~3 s) | Arveles 93 (~6.5 s) |
| Aferin + Dolorex | Aferin (not in catalog), Dolorex | `cua` → not found; Dolorex 100 (~50 s) | `ite` → **Biteral 90 (wrong)**; Dolorex 93 (~183 s) |
| Levopront | Levopront | `dompe` → not found (~125 s) | First run: crash. After MKLDNN off: Levopront 100, early exit (~10 s) |

Aferin is absent from the seed catalog; “not found” is the correct product behaviour. PaddleOCR’s `ite` → Biteral is a **false match**.

### Five-box photo

Ground truth: Omesek, Levopront (upside-down), Biteral (upside-down), Nurofen Cold & Flu, Ibucold C. YOLO detected **5** boxes.

| Box (OCR text → match) | EasyOCR | PaddleOCR |
|------------------------|---------|-----------|
| 1 | `cold & flu` → **Gribex Cold & Flu 90** (wrong) | `nurofen` → **Nurofen Cold & Flu 100** |
| 2 | `dex` → **Dodex 90** (wrong) | `itr` → **Azitro 90** (wrong) |
| 3 | `omesek` → **Omesek 100** | `nãn` → not found |
| 4 | `ibucold c` → **Ibucold C 100** | `ibucold c` → **Ibucold C 100** |
| 5 | `uno` → **Imunol Defence 90** (wrong) | `uda` → **Neruda 90** (wrong) |

| Engine | Correct identities | Wall time |
|--------|--------------------|-----------|
| EasyOCR | **2 / 5** | ~35 s |
| PaddleOCR | **2 / 5** | ~151 s |

JSON: [ocr-compare-five-boxes.json](../experiments/paddleocr-comparison/results/ocr-compare-five-boxes.json).

### Large crop

On a full-resolution `parol_plus.jpg` crop, PaddleOCR hit `max_side_limit` (4000 px), ran for minutes per variant, and the process crashed (`exit 3221225477`). EasyOCR completed the same photo in the API path in about 12 s (Parol 100).

---

## Interpretation

1. **PaddleOCR is not a net accuracy win** on these packs. It helped on some single brands (Levopront after the Windows fix, Nurofen) and failed on others (Omesek, Aferin false match, large images).
2. **It is slower on CPU** in this pipeline (typically 2–4× on multi-box photos; worse on large crops).
3. **Wrong names are mostly the matcher**, not the engine. Fast mode treats RapidFuzz `WRatio` ≥ 88 as a confident hit and **stops OCR**. Three-letter fragments (`dex`, `uno`, `ite`) and shared slogans (`cold & flu`) match unrelated catalog rows. Swapping EasyOCR for PaddleOCR does not remove that gate.
4. **Windows/Paddle operational cost** (oneDNN crash, large extra wheels, first-run model download) is unjustified for an internship CPU API that already ships EasyOCR.

---

## Decision

| Action | Detail |
|--------|--------|
| Production OCR | EasyOCR only |
| Install | No `requirements-paddleocr.txt` at repo root; not in Docker/CI |
| Runtime | No `OCR_ENGINE`, no `--engine paddleocr`, API `ocr_engines`: `["easyocr"]` |
| Docs | This report + [experiments/paddleocr-comparison](../experiments/paddleocr-comparison/) |
| Kept from the trial | `®` stripping; `brand_without_trailing_dosage()` for `Brand 60 mg` lines |

Follow-up: short OCR fragments no longer early-exit as a match. See [Report 27](27-matching-reliability.md) (PR [#67](https://github.com/Melikeda/yolocilin/pull/67)). Independent of which OCR engine is used.

---

## References

- EasyOCR integration: [Report 07](07-ocr-integration.md)
- Fast OCR mode: [Report 19](19-performance-optimization.md)
- Archived adapter snapshot: [adapter/](../experiments/paddleocr-comparison/adapter/)
