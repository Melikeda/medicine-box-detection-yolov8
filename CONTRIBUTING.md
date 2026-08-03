# Contributing

Thank you for contributing to the **Medicine Box Detection System**. This project uses a **Git Feature Branch Workflow**: one issue → one branch → one pull request → merge into `main`.

---

## Development setup

1. Clone the repository and create a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. For mobile work, load Flutter/Android tooling:

```powershell
. .\scripts\env-flutter.ps1
cd mobile
flutter pub get
```

See [docs/setup-guide.md](docs/setup-guide.md) for full instructions.

---

## Branch naming

| Pattern | Example |
|---------|---------|
| `feature/<short-name>` | `feature/ci-cd` |
| `fix/<short-name>` | `fix/upload-mime` |

Create branches from up-to-date `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/my-change
```

---

## Required checks before opening a PR

Run the same commands that GitHub Actions runs locally:

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

### Docker (optional, when Dockerfile changes)

```bash
docker compose build
```

---

## Continuous Integration (GitHub Actions)

| Workflow | Trigger | What it runs |
|----------|---------|--------------|
| [Backend Tests](.github/workflows/backend-tests.yml) | Push/PR touching backend, `src/`, `tests/` | `pytest` on Ubuntu, Python 3.11 |
| [Mobile Tests](.github/workflows/mobile-tests.yml) | Push/PR touching `mobile/` | `flutter analyze`, `flutter test` |
| [Docker Build](.github/workflows/docker-build.yml) | Push to `main` (Docker paths) or manual | `docker build` (no push) |

Status badges are shown in [README.md](README.md).

### Enabling required checks (repository maintainers)

After the first successful workflow run on `main`:

1. GitHub → **Settings** → **Branches** → **Branch protection rules** → Add rule for `main`
2. Enable **Require status checks to pass before merging**
3. Select:
   - `pytest (Python 3.11)` (Backend Tests)
   - `flutter analyze & test` (Mobile Tests)
4. Optional: require pull request reviews

---

## Pull request guidelines

1. Link the GitHub issue (`Closes #39` in PR body)
2. Keep PRs focused — one feature or fix per PR
3. Update docs when setup, API, or architecture changes
4. Add or update tests when behavior changes
5. Do not commit secrets, model weights (`.pt`), or local databases

Use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) when opening a PR.

---

## Documentation

| Document | When to update |
|----------|----------------|
| `README.md` | User-facing setup or feature changes |
| `docs/roadmap.md` | Phase completion |
| `docs/architecture.md` | System design changes |
| `docs/setup-guide.md` | Environment instructions |
| `docs/reports/` | New technical report per major phase |

---

## Code style

- **Python:** Match existing modules under `src/` and `backend/`; run `pytest` before push
- **Dart/Flutter:** Follow `flutter analyze`; use `flutter_lints` rules in `mobile/analysis_options.yaml`
- Prefer small, focused diffs over large refactors mixed with feature work

---

## Questions

Open a [GitHub Issue](https://github.com/Melikeda/medicine-box-detection-yolov8/issues) for bugs, features, or questions.
