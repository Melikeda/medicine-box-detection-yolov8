# Report 17 — CI/CD (GitHub Actions)


> **Historical phase report.** Written for that phase; some numbers or “next steps” may be outdated.
> Living docs: [README](../../README.md) · [Architecture](../architecture.md) · [Roadmap](../roadmap.md) · [Reports index](README.md).
> Current product: **Yolocilin** · catalog **131** medicines · APIs: analyze · medicines · explain · scans.

## Overview

Adds automated continuous integration for backend pytest, Flutter analyze/test, and optional Docker image build verification. Every push and pull request to `main` runs the relevant workflows before merge.

**Branch:** `feature/ci-cd`  
**GitHub Issue:** #39

---

## Objectives

- [x] Backend pytest workflow on Ubuntu (Python 3.11)
- [x] Mobile `flutter analyze` + `flutter test` workflow
- [x] Optional Docker build workflow on `main`
- [x] CONTRIBUTING.md and PR template
- [x] README CI badges and setup documentation

---

## Workflows

| File | Job | Trigger paths |
|------|-----|---------------|
| `.github/workflows/backend-tests.yml` | `pytest` | `backend/`, `src/`, `tests/`, `requirements.txt` |
| `.github/workflows/mobile-tests.yml` | Flutter analyze + test | `mobile/` |
| `.github/workflows/docker-build.yml` | `docker build` | Dockerfile, compose, backend, src |

All PR workflows use **concurrency** groups to cancel outdated runs on the same branch.

---

## Design choices

- **Full `requirements.txt` in CI** — pytest imports backend routers that transitively load pipeline modules; lightweight installs would break collection
- **Path filters** — mobile workflow does not run on Python-only changes (and vice versa)
- **Docker build without push** — verifies Dockerfile and dependency install; model weights are mounted at runtime, not baked into CI
- **No deploy step yet** — CD (cloud deploy) remains Phase 18+ scope

---

## Local parity

Developers should run before opening a PR:

```bash
pytest
cd mobile && flutter analyze && flutter test
```

See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## Branch protection (manual step)

After merging to `main`, enable required status checks in GitHub Settings → Branches:

- `pytest (Python 3.11)`
- `flutter analyze & test`

Documented in CONTRIBUTING.md.

---

## Next Phase

Issue #32 — Advanced Features, or Issue #9 — Final Testing & Documentation.
