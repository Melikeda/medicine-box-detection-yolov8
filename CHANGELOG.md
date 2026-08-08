# Changelog

All notable changes to **Yolocilin** (Medicine Box Detection System) are documented here.  
Format inspired by [Keep a Changelog](https://keepachangelog.com/).

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
