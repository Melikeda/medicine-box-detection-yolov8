# Security Policy

**Yolocilin / Medicine Box Detection System** accepts images and may call external LLM APIs. Please treat secrets and uploads carefully.

---

## Supported versions

Security fixes are applied on the latest `main` branch and the active polish feature branches before merge.

---

## Reporting a vulnerability

Please **do not** open a public GitHub issue for sensitive reports.

- Prefer contacting the maintainer via GitHub: [@Melikeda](https://github.com/Melikeda)
- Include steps to reproduce, impact, and (if possible) a suggested fix
- You should receive an acknowledgement when the report is seen

---

## Hardening already in place

| Control | Notes |
|---------|--------|
| Upload validation | Extension + magic-byte checks, size limit |
| Rate limiting | Analyze / explain / scans (per client IP) |
| Production mode | `ENVIRONMENT=production` masks 500 details, disables `/docs` |
| CORS | Explicit origins required in production (`*` rejected) |
| Secrets | `.env` gitignored; Gemini key stays on the server |
| Mobile release | HTTPS-only network config (cleartext only in debug) |
| Medical disclaimer | API + UI — not a substitute for professional advice |

Details: [docs/reports/20-production-hardening.md](docs/reports/20-production-hardening.md)

---

## Configuration checklist (operators)

1. Copy `.env.example` → `.env` (never commit `.env`)
2. Set `ENVIRONMENT=production`
3. Set `CORS_ORIGINS` to real app origins (comma-separated)
4. Keep `GEMINI_API_KEY` only on the server; rotate if leaked
5. Put the API behind **HTTPS** (reverse proxy)
6. Review rate-limit env vars under load

---

## Out of scope (current MVP)

- End-user authentication / private scan namespaces (scans are global until auth lands)
- WAF / DDoS protection
- Cloud secret managers (recommended for production deploys)

---

## Medical / legal note

Model and LLM outputs can be wrong or incomplete. Yolocilin is an **engineering demo / assistive identifier**, not a clinical decision tool.
