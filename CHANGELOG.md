# Changelog

All notable changes to **Yolocilin** (Medicine Box Detection, Identification and Information System) are documented here.  
Format inspired by [Keep a Changelog](https://keepachangelog.com/).

API / app version remains **0.1.0** until a GitHub Release. This file does not invent semver tags.

## [Unreleased]

### Added

- Optional barcode identity path beside OCR: `GET/POST /api/v1/barcode/*`, `medicine_barcodes.csv` (2043 GTINs → 1041 of 1163 catalog rows), zxing-cpp decoder ([Report 28](docs/reports/28-barcode-reading.md))
- Flutter **Barkod tara** on the scan tab (live camera + photo backup) → existing result screen and explain card
- Analyze tries barcode on the YOLO crop (and full frame if no box) before OCR; a miss continues to EasyOCR
- TİTCK SKRS fallback when a GTIN is not in the catalog map; AIM `]C1` prefixes from phone scanners are stripped
- Matching reliability gates: suffix OCR (`fen`, `alm`, `pal`) → `not_found` instead of a wrong drug card ([Report 27](docs/reports/27-matching-reliability.md))
- Report 26 and `docs/experiments/paddleocr-comparison/` (PaddleOCR trial; EasyOCR kept)
- TİTCK-enriched catalog growth to **1163** medicines (pharmacy-shelf brands + high-use ATC groups)
- Server scan history: `POST/GET/DELETE /api/v1/scans` + mobile best-effort sync
- Firebase App Distribution pipeline (manual GitHub Action + `scripts/distribute-android.ps1`)
- API E2E smoke (`tests/test_e2e_api_flow.py`) and live `scripts/e2e_api_flow.py`
- Benchmark JSON export: `scripts/benchmark_analyze.py --json-out`
- Word generators for the CE499 internship report (local `.docx`, gitignored)
- CV-facing product summary: [`docs/technical-report.md`](docs/technical-report.md)
- `ruff check` on `backend` / `src` / `tests` / `scripts` in backend CI
- Gemini explain: locale-aware JSON (`tr` / `en`); catalog text when the model is unavailable

### Changed

- Production OCR stays **EasyOCR** only; PaddleOCR is not installed or selectable
- Fast-mode OCR early-exit requires a near-complete match (score ≥ 95)
- Exact short brands such as Etol still match; a miss returns `not_found` instead of a wrong card
- Matching strips `®` and trailing dosage from OCR lines (`Levopront 60 mg` → brand)
- Flutter Dart package `yolocilin`; Android `applicationId` `com.yolocilin.app` (launcher label remains **Yolocilin**)
- Public clone URLs and product subtitle aligned with the `yolocilin` repository
- Living docs report the current **1163**-row catalog (older reports still show 38 / 107 / 131 / 153)
- Explain readiness on `/api/v1/explain/info`; shared explanation cache
- Docker Compose passes `ENVIRONMENT`, `CORS_ORIGINS`, scan/explain rate limits
- `/docs` disabled when `ENVIRONMENT=production`
- Upload magic-byte checks no longer use deprecated `imghdr`
- Rate limiter prunes idle client keys; class renamed `IpRateLimiter`

### Security

- Production `DELETE /api/v1/scans/{id}` requires `SCANS_API_KEY` (`X-API-Key`); if unset, DELETE is disabled
- Analyze rejects oversized uploads early via `Content-Length`
- Scan list/get/create/delete share per-IP rate limiting
- Stricter production CORS; credentials disabled for `CORS_ORIGINS=*`
- LLM key validation rejects placeholders / short keys; production fail-fast for wildcard CORS and misconfigured LLM
- Firebase `google-services.json` and service-account JSON stay gitignored; CI uses repository secrets
- Generated internship `.docx` files and university cover logo stay local (gitignored)

## Earlier milestones

Summaries live in phase reports under [`docs/reports/`](docs/reports/):

| Area | Reports |
|------|---------|
| Pipeline & matching | 08–11, 27 |
| FastAPI / SQLite / tests / Docker | 10–14 |
| Mobile & CI | 15–17 |
| Catalog & performance | 18–19, 24–25 |
| Hardening, LLM, camera, history | 20–23 |
| OCR trial & barcode | 26, 28 |
