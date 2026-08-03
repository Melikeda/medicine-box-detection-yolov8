# Report 19 — Pipeline Performance Optimization

## Overview

Reduces CPU analyze latency in `fast` mode by cutting OCR search space, stopping early on confident matches, resizing large uploads server-side, and exposing per-stage timing in the API response.

**Branch:** `feature/performance-improvement`  
**GitHub Issue:** [#43](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/43)

---

## Problem

Report 16 measured ~255 s for a single-box analyze on CPU (`mode=fast`). The bottleneck is sequential EasyOCR over many preprocessing variants (previously 4 rotations × 2 variants = **8 OCR passes** per box).

---

## Changes

| Optimization | Fast mode before | Fast mode after |
|--------------|------------------|-----------------|
| Rotation angles | 0°, 90°, 180°, 270° | **0°, 90°** |
| Upscale factor | 2.0× | **1.5×** |
| Max variants / box | ~8 | **~4** (worst case) |
| Early OCR exit | No | **Yes** (stop when match ≥ 80) |
| Server image resize | No | **Yes** (max 1280 px long edge) |
| Stage timing in API | No | **Yes** (`timing.yolo_ms`, `ocr_ms`, …) |

Accurate mode behaviour is unchanged (full rotation set, 2.0× scale, no early exit).

---

## Architecture

```text
POST /api/v1/analyze?mode=fast
  → resize_image_bytes_if_large (1280 px)
  → PipelineManager.analyze_all()
      → YOLO detect (timed)
      → for each box:
          → run_ocr_pipeline(should_stop_after_variant=…)
          → match_text (timed)
  → AnalyzeResponseSchema.timing + processing_time_ms
```

Key files:

- `src/services/config.py` — mode-specific scale/rotation/early-exit flags
- `src/ocr/ocr_pipeline.py` — incremental early-stop hook
- `src/services/pipeline_manager.py` — timing + early-stop wiring
- `backend/app/services/image_optimizer.py` — upload resize
- `scripts/benchmark_analyze.py` — local profiling CLI

---

## Expected impact

Theoretical fast-mode OCR work drops by up to **~75%** in the worst case (8 → 4 variants) and often much more when early exit triggers after the first successful variant. Real wall-clock improvement depends on image size, box count, and CPU/GPU; use:

```bash
python scripts/benchmark_analyze.py --image data/samples/parol_plus.jpg --mode fast
```

---

## API additions (backward compatible)

| Field | Type | Description |
|-------|------|-------------|
| `timing` | object \| null | `yolo_ms`, `ocr_ms`, `matching_ms`, `total_ms` |
| `image_resized` | bool | Server downscaled the upload before analysis |

Existing clients ignore unknown fields; mobile app requires no change.

---

## Tests

- `tests/test_performance.py` — fast/accurate config, OCR early exit, image resize

---

## Follow-up

- Optional GPU via `USE_GPU=true` (already supported)
- Parallel variant OCR (thread pool) if further CPU gains needed
- Adaptive escalation: retry `not_found` boxes in accurate mode only
