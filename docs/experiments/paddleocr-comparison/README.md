# Experiment: EasyOCR vs PaddleOCR

**Status:** closed  
**Product decision:** keep **EasyOCR**  
**PaddleOCR is not part of the application.** It is not in `requirements.txt`, Docker, CI, `.env`, the API, or `src/`.

This folder is the internship record of a side-by-side trial on branch `feature/paddleocr-engine`. The same YOLO crops and RapidFuzz catalog were used; only the OCR reader changed.

Full write-up: [Report 26](../../reports/26-ocr-engine-comparison.md).

---

## Why it was tried

Public OCR benchmarks often rank PaddleOCR above EasyOCR on dense scene text. The question for Yolocilin was practical: on **Turkish medicine boxes**, CPU, and the existing OpenCV + matcher pipeline, does PaddleOCR identify more drugs correctly without slowing the API?

## What stayed in the product

| Layer | After the trial |
|-------|-----------------|
| OCR engine | EasyOCR only (`tr` + `en`) |
| Install | `pip install -r requirements.txt` — no Paddle packages |
| CLI / API | No `--engine` / `OCR_ENGINE` switch |
| Flutter | Unchanged |

Two matching helpers discovered during the trial remain, because they also help EasyOCR:

- strip `®` from OCR text
- drop a trailing dosage (`Levopront 60 mg` → `levopront`) so brand+dose lines can match

Wrong-name errors from **short OCR fragments** (`dex` → Dodex) are a matcher issue, not a reason to swap engines. See Report 26.

## Results (fast mode, CPU)

| Photo | EasyOCR | PaddleOCR | Wall time |
|-------|---------|-----------|-----------|
| Arveles | Arveles 93 | Arveles 93 | ~3 s vs ~6 s |
| Aferin + Dolorex | Aferin not found (not in catalog) + Dolorex 100 | **Biteral 90 (wrong)** + Dolorex 93 | ~50 s vs ~183 s |
| Five boxes (Omesek, Levopront, Biteral, Nurofen Cold & Flu, Ibucold C) | **2/5** correct | **2/5** correct | ~35 s vs ~151 s |
| Levopront (first Paddle run) | `dompe` → not found | Windows oneDNN crash | — |
| Large `parol_plus.jpg` crop | Parol 100 (typical ~12 s on API) | Very slow / process crash | — |

On the five-box carpet photo both engines missed the upside-down brands and both accepted 3-letter garbage as a “confident” match (≥88). PaddleOCR won Nurofen (`nurofen`) where EasyOCR only read `cold & flu` → Gribex. EasyOCR won Omesek. Neither is a net upgrade.

Raw JSON: [results/](results/). Trial photos: [photos/](photos/).

## Adapter snapshot (not loaded)

[adapter/](adapter/) is a **frozen copy** of the trial code (reader wrapper, compare script, extra requirements). The product does not import it. Do not install those packages to run Yolocilin.
