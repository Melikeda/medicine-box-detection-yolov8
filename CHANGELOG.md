# Changelog

All notable changes to **Yolocilin** (Medicine Box Detection System) are documented here.  
Format inspired by [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased] — popular TR catalog to ~1160

### Added

- Expanded TİTCK brand queries across high-use Turkish categories (pain, cold, antibiotics, GI, vitamins, cardio, diabetes, allergy, derm, …)
- High-volume ATC group fill (`POPULAR_ATC_EXPANSION`) → catalog **1163** medicines (~10.9% placeholders)

## [Unreleased] — `feature/catalog-expand-matching-tighten`

### Added

- Controlled TİTCK catalog expansion: Ferrum / Ferro Sanol and additional pharmacy-shelf brands (Buscopan, Ventolin, Claritine, …) → **153** medicines
- Regression: Ferrum OCR must not match Pharmaton

### Changed

- Matching gates tightened (`minimum_match_score` 88, brand-token overlap required) so missing-catalog OCR returns **not_found** instead of a wrong brand
- Reject foreign brand tokens (e.g. Endofer-like OCR must not map to Coldaway C)

## [Unreleased] — `feature/firebase-app-distribution`

### Added

- Firebase App Distribution pipeline: manual GitHub Action + `scripts/distribute-android.ps1`
- Guide: `docs/guides/firebase-app-distribution.md` (Spark plan, HTTPS `API_BASE_URL`, secrets)
- Templates: `google-services.json.example`, `.firebaserc.example`, `firebase.json`

### Security

- Ignore Firebase config / service-account JSON in git; CI uses repository secrets only

## [Unreleased] — `feature/final-polish-5`

### Security

- Production `DELETE /api/v1/scans/{id}` requires `SCANS_API_KEY` (`X-API-Key`); if unset, DELETE is disabled
- Analyze rejects oversized uploads early via `Content-Length` (before full body read)
- Scan list/get/create/delete share per-IP rate limiting

### Changed

- Upload magic-byte checks no longer use deprecated `imghdr` (JPEG/PNG/WEBP/BMP)
- Removed unused `polars`, `polars-runtime-32`, and `nvidia-ml-py` from `requirements.txt`
- Rate limiter prunes idle client keys under load
- Docs: `.env.example`, `SECURITY.md`, project board status

## [Unreleased] — `feature/final-polish-4`

### Added

- Server scan history API: `POST/GET/DELETE /api/v1/scans` (SQLite `scans` table)
- Mobile best-effort sync via `ScanApiService` after local history save
- API E2E smoke (`tests/test_e2e_api_flow.py`) and live script `scripts/e2e_api_flow.py`
- Benchmark JSON export: `scripts/benchmark_analyze.py --json-out`
- Production fail-fast for wildcard CORS and misconfigured LLM in production
- Shared LLM explanation cache + singleton medicine/scan DB services
- Docs refresh: Yolocilin-branded README, `SECURITY.md`, reports index, `docs/assets/`

### Changed

- Medicine catalog documented as **131** seed records (TİTCK-enriched)
- Explain readiness exposed on `/api/v1/explain/info` (`ready`, `status_message`)
- Docker Compose passes `ENVIRONMENT`, `CORS_ORIGINS`, scan/explain rate limits
- `/docs` disabled when `ENVIRONMENT=production`

### Security

- Stricter production CORS; credentials disabled for `CORS_ORIGINS=*`
- Clearer LLM key validation (placeholders / short keys rejected)

## Earlier milestones

Summaries live in phase reports under [`docs/reports/`](docs/reports/):

| Area | Reports |
|------|---------|
| Pipeline & matching | 08–11 |
| FastAPI / SQLite / tests / Docker | 10–14 |
| Mobile & CI | 15–17 |
| Catalog & performance | 18–19, 24 |
| Hardening, LLM, camera, history, E2E | 20–23, 25 |
