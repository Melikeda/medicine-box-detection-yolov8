# Report 21 — LLM Medicine Explanations (Gemini)

## Overview

Adds AI-generated Turkish medicine descriptions after a successful match using the Google Gemini API free tier. Includes backend explain endpoint, mobile “İlaç hakkında” UI, caching, rate limiting, and medical disclaimer.

**Branch:** `feature/llm-integration`  
**GitHub Issue:** [#8](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/8)  
**Phase:** 18 — Advanced Features ([#32](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/32))

---

## Objectives

- [x] `POST /api/v1/explain` — short Turkish explanation for a matched drug
- [x] `GET /api/v1/explain/info` — LLM configuration status
- [x] Gemini integration (`google-genai`) with model fallback
- [x] Mobile expandable “İlaç hakkında” card (lazy load)
- [x] Mandatory LLM disclaimer (not medical advice)
- [x] In-memory cache by `medicine_id` + locale
- [x] Explain-specific rate limit (default 5 req/min per IP)
- [x] Mock mode for dev/tests without API key
- [x] `.env.example` + helper scripts
- [x] Backend + mobile tests

---

## Architecture

```text
Flutter Result Screen (matched box)
   │
   ▼ (user expands "İlaç hakkında")
POST /api/v1/explain { medicine_id, locale }
   │
   ▼
MedicineQueryService (SQLite lookup)
   │
   ▼
LlmExplanationService → Gemini API
   │                      (gemini-flash-latest
   │                       → fallback flash-lite-latest)
   ▼
JSON { explanation, disclaimer, cached, model }
```

**Design choice:** Explain is a **separate endpoint** (not inline in `/analyze`) to keep analyze latency unchanged and to load LLM only on demand.

---

## Backend changes

| Component | Purpose |
|-----------|---------|
| `backend/app/routers/explain.py` | Explain routes + rate limit |
| `backend/app/services/llm_service.py` | Gemini client, prompt, fallback |
| `backend/app/services/explanation_cache.py` | Per-drug memory cache |
| `backend/app/llm_models.py` | Free-tier model priority list |
| `backend/app/schemas/explain.py` | Request/response schemas |
| `backend/app/config.py` | LLM env settings (absolute `.env` path) |
| `backend/app/constants.py` | `LLM_EXPLANATION_DISCLAIMER` |

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_ENABLED` | `false` | Enable explain feature |
| `GEMINI_API_KEY` | — | Server-side only; never in mobile |
| `LLM_MODEL` | `gemini-flash-latest` | Primary Gemini model |
| `LLM_MOCK_MODE` | `false` | Deterministic mock responses |
| `LLM_CACHE_ENABLED` | `true` | Shared in-process cache by medicine_id + locale |
| `RATE_LIMIT_EXPLAIN_PER_MINUTE` | `5` | Per IP; aligns with free tier RPM |

### Reliable enable checklist

1. Set `GEMINI_API_KEY` (real key; placeholders rejected)
2. Set `LLM_ENABLED=true` (production fails startup if enabled without key/mock)
3. Keep `LLM_CACHE_ENABLED=true` and `RATE_LIMIT_EXPLAIN_PER_MINUTE=5`
4. Verify `GET /api/v1/explain/info` → `ready=true`

### API response (POST /api/v1/explain)

```json
{
  "success": true,
  "medicine_id": "MED001",
  "medicine_name": "Parol",
  "explanation": "...",
  "disclaimer": "Bu açıklama yapay zeka tarafından üretilmiştir...",
  "cached": false,
  "provider": "gemini",
  "model": "gemini-flash-latest"
}
```

---

## Mobile changes

| File | Change |
|------|--------|
| `explain_api_service.dart` | POST explain client |
| `explain_response.dart` | Response model |
| `medicine_explanation_section.dart` | Expandable LLM card + loading/error |
| `medicine_result_card.dart` | Shows section when matched |
| `medicine_box_result.dart` | `medicineId` getter |
| `app_config.dart` | `explainEndpoint`, timeout |

---

## Security

- API key stored only in server `.env` (gitignored)
- Placeholder keys rejected by `llm_is_configured`
- Explain rate limit reduces quota abuse / cost
- LLM prompt constrained to DB fields only (no invented dosing)
- Separate disclaimer for AI-generated text
- Errors do not expose Gemini API key or raw stack traces in production

---

## Helper scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup-gemini-key.ps1` | Securely write key to `.env` |
| `scripts/start-backend.ps1` | Stop stale processes + start API |
| `scripts/stop-backend.ps1` | Free port 8000 (Windows) |
| `scripts/test_llm_explain.py` | End-to-end explain test |
| `scripts/diagnose_gemini.py` | Model/quota diagnostics |

---

## Tests

- `tests/test_explain.py` — explain endpoint, cache, rate limit 429, missing key
- `tests/test_llm_config.py` — key validation + production fail-fast
- `tests/test_llm_models.py` — model fallback chain
- `mobile/test/explain_response_test.dart` — JSON parsing

---

## Free tier model selection

Tested against Google AI Studio free tier (Aug 2026):

| Model | Status |
|-------|--------|
| `gemini-flash-latest` | ✅ Primary — best working free Flash |
| `gemini-flash-lite-latest` | ✅ Automatic fallback |
| `gemini-2.0-flash` | ⚠️ Separate quota; may 429 on new accounts |
| `gemini-2.5-flash` | ❌ 404 for new users |

---

## Setup (developer)

1. Copy `.env.example` → `.env`
2. Get key from [Google AI Studio](https://aistudio.google.com/)
3. Set `LLM_ENABLED=true`, `GEMINI_API_KEY=...`, `LLM_MODEL=gemini-flash-latest`
4. `pip install -r requirements.txt`
5. `powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1`
6. `python scripts/test_llm_explain.py`

---

## Out of scope

- Billing / paid Gemini tier
- Key vault (Secret Manager) — future production hardening

> **Update (final-polish-4):** Server scan history is implemented separately — see [Report 23](23-scan-history.md) and `POST /api/v1/scans`. PostgreSQL remains optional.
