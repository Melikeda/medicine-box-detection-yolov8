# Contributing

Thanks for helping improve **Yolocilin** (Medicine Box Detection System).

We use a **Git Feature Branch Workflow**: one focused change → one branch → one pull request → merge to `main`.

Please read [SECURITY.md](SECURITY.md) before reporting vulnerabilities.

---

## Development setup

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

**Python:** 3.11+ (CI: 3.11 · Docker: 3.12).

Mobile:

```powershell
. .\scripts\env-flutter.ps1
cd mobile
flutter pub get
```

Full guide: [docs/setup-guide.md](docs/setup-guide.md)

---

## Branch naming

| Pattern | Example |
|---------|---------|
| `feature/<short-name>` | `feature/final-polish-4` |
| `fix/<short-name>` | `fix/upload-mime` |

```bash
git checkout main
git pull origin main
git checkout -b feature/my-change
```

---

## Checks before a PR

### Backend

```bash
pytest
```

### Mobile

```bash
cd mobile
flutter analyze
flutter test
```

### Optional

```bash
python scripts/e2e_api_flow.py --skip-analyze
docker compose build
```

---

## Continuous Integration

| Workflow | Runs |
|----------|------|
| [Backend Tests](.github/workflows/backend-tests.yml) | `pytest` (Python 3.11) |
| [Mobile Tests](.github/workflows/mobile-tests.yml) | `flutter analyze` + `flutter test` |
| [Docker Build](.github/workflows/docker-build.yml) | image build on Docker path changes |

Badges: [README.md](README.md)

---

## Pull requests

- Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
- Link related issues (`Fixes #…` / `Refs #…`)
- Prefer small, reviewable diffs
- Update docs when behaviour or setup changes ([CHANGELOG.md](CHANGELOG.md) for user-facing notes)

---

## Project docs map

| Doc | Role |
|-----|------|
| [README.md](README.md) | Product overview |
| [docs/architecture.md](docs/architecture.md) | Design |
| [docs/roadmap.md](docs/roadmap.md) | Phases |
| [docs/reports/](docs/reports/) | Historical + feature reports |
| [tests/README.md](tests/README.md) | Test inventory |

---

## Code style

- Prefer clear names and small modules under `src/` / `backend/app/`
- Match existing patterns (routers → services → repository)
- Do not commit secrets, weights (`.pt`), or local `.env`
