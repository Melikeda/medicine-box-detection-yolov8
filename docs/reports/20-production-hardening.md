# Report 20 — Production Hardening & Security

## Overview

Hardens the FastAPI backend and Android client for production-adjacent deployment: CORS configuration, analyze rate limiting, security headers, error detail masking, HTTPS/cleartext split, and medical disclaimer.

**Branch:** `feature/production-hardening`  
**GitHub Issue:** #45

---

## Objectives

- [x] Android cleartext HTTP only in **debug** builds (emulator dev)
- [x] Release/main manifest: HTTPS-only network security config
- [x] Configurable CORS via `CORS_ORIGINS` env
- [x] Rate limit on `POST /api/v1/analyze` (429)
- [x] Security headers middleware
- [x] Hide internal error details when `ENVIRONMENT=production`
- [x] Medical disclaimer in API + mobile result screen
- [x] Expanded `.env.example` + pytest coverage

---

## Backend changes

| Component | Change |
|-----------|--------|
| `backend/app/config.py` | `ENVIRONMENT`, `CORS_ORIGINS`, rate limit settings |
| `backend/app/middleware/security_headers.py` | `X-Content-Type-Options`, `X-Frame-Options`, … |
| `backend/app/middleware/rate_limit.py` | IP-based analyze limiter |
| `backend/app/exceptions.py` | No stack/details leak in production |
| `backend/app/constants.py` | `MEDICAL_DISCLAIMER` |
| Analyze response | `disclaimer` field |

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `production` masks 500 details + disables `/docs` |
| `CORS_ORIGINS` | `*` | Comma-separated; `*` rejected in production |
| `RATE_LIMIT_ENABLED` | `true` | Toggle rate limits |
| `RATE_LIMIT_ANALYZE_PER_MINUTE` | `20` | Analyze per IP per minute |
| `RATE_LIMIT_EXPLAIN_PER_MINUTE` | `5` | Explain per IP per minute |
| `RATE_LIMIT_SCANS_PER_MINUTE` | `30` | Scans POST per IP per minute (final-polish-4) |

---

## Mobile changes

| File | Change |
|------|--------|
| `AndroidManifest.xml` (main) | `usesCleartextTraffic=false` + network security config |
| `debug/AndroidManifest.xml` | Cleartext allowed for `http://10.0.2.2` dev |
| `result_screen.dart` | Disclaimer info card |
| `analyze_response.dart` | Parse `disclaimer` from API |

---

## Tests

- `tests/test_security.py` — CORS parsing, rate limit 429, headers, production error masking

---

## Deployment checklist

1. Set `ENVIRONMENT=production` (also disables `/docs`, `/redoc`, `/openapi.json`)
2. Set `CORS_ORIGINS` to your app domain(s) — not `*` (startup fails if missing in production)
3. Pass the same vars via `docker-compose.yml` / `.env` (`ENVIRONMENT`, `CORS_ORIGINS`, rate limits)
4. Deploy API behind **HTTPS** (reverse proxy / cloud)
5. Build **release** APK with `API_BASE_URL=https://...`
6. Keep secrets in `.env` only (never commit)

---

## Out of scope

- JWT / user authentication
- WAF / DDoS protection
- LLM API key vault (Secret Manager) — future production
