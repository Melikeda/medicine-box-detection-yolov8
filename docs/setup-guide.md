# Setup Guide

Environment setup for **Yolocilin** (Medicine Box Detection System).

Product overview: [root README](../README.md) · Security: [SECURITY.md](../SECURITY.md)

---

## Prerequisites

| Software | Purpose |
|----------|---------|
| Python **3.11+** (CI: 3.11 · Docker image: 3.12) | AI pipeline and backend |
| Git | Version control |
| VS Code (recommended) | Development IDE |
| Docker Desktop | Container deployment (API) |
| Flutter SDK 3.19+ | Yolocilin mobile app (`mobile/`) |
| Android Studio | Android emulator / device testing |

---

## 1. Clone the Repository

```bash
git clone https://github.com/Melikeda/medicine-box-detection-yolov8.git
cd medicine-box-detection-yolov8
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Activate — Windows (PowerShell), from the **repository root**:

```powershell
venv\Scripts\Activate.ps1
```

> Note: the virtual environment folder is `venv`, not `.venv`.

### Activate — Windows (CMD)

```cmd
venv\Scripts\activate
```

### Activate — Linux / macOS

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

First run downloads PyTorch and EasyOCR models — this may take several minutes.

---

## 4. Verify Installation

```bash
python --version
pip list
```

---

## 5. YOLO Model

Training produces weights under `runs/detect/`. For inference scripts, point to your trained `best.pt` file. Model files (`.pt`) are excluded from Git.

Train from scratch:

```bash
python src/train.py
```

Run detection on a sample image:

```bash
python src/predict.py
```

---

## 6. Run Pipeline (CLI)

See [examples/README.md](../examples/README.md) for the full learning path.

Unified pipeline (fast mode, recommended):

```bash
python run_analyze.py --image data/samples/samples3.jpg --mode fast
```

Multi-box sample:

```bash
python run_analyze.py --image data/samples/coklu_resim.jpg --mode fast
```

Accurate mode (slow on CPU):

```bash
python run_analyze.py --image data/samples/samples3.jpg --mode accurate
```

JSON output:

```bash
python run_analyze.py --image data/samples/parol_plus.jpg --mode fast --json
```

**New photo vs new drug**

| Goal | Action |
|------|--------|
| Try another photo | Pass `--image path/to/photo.jpg` — no code change |
| Recognize a new drug | Add a row to `data/database/medicines.csv` |

YOLO detects boxes; OCR reads text; RapidFuzz matches only drugs listed in the CSV (**131** records).

---

## 7. Run FastAPI Backend

```bash
python run_api.py
```

Server starts at http://127.0.0.1:8000

| Endpoint | Description |
|----------|-------------|
| `GET /health` | API and model readiness |
| `GET /api/v1/analyze/info` | Upload limits, formats, OCR modes |
| `POST /api/v1/analyze?mode=fast` | Upload image (`file` field) |
| `GET /api/v1/medicines` | List / search medicines (SQLite, 131 drugs) |
| `GET /api/v1/medicines/categories` | Distinct categories |
| `GET /api/v1/medicines/{id}` | Medicine detail |
| `GET /api/v1/explain/info` | LLM / explain readiness |
| `POST /api/v1/explain` | Gemini short explanation |
| `GET /api/v1/scans` | Server scan history list |
| `POST /api/v1/scans` | Persist successful analyze result |

Example:

```bash
curl http://127.0.0.1:8000/health
curl -X POST "http://127.0.0.1:8000/api/v1/analyze?mode=fast" \
  -F "file=@data/samples/coklu_resim.jpg"
```

Interactive docs (development): http://127.0.0.1:8000/docs  
Disabled when `ENVIRONMENT=production`.

### Environment & production

```bash
copy .env.example .env   # Windows
```

| Variable | Notes |
|----------|--------|
| `ENVIRONMENT` | `production` → hide 500 details, close `/docs`, require real CORS |
| `CORS_ORIGINS` | Comma-separated; `*` forbidden in production |
| `LLM_ENABLED` / `GEMINI_API_KEY` | Required for explain (or `LLM_MOCK_MODE=true`) |
| `SCAN_HISTORY_MAX_ENTRIES` | Server history cap (default 200) |
| `RATE_LIMIT_*` | Analyze / explain / scans |

Check explain readiness: `curl http://127.0.0.1:8000/api/v1/explain/info`

### Run tests & E2E smoke

```bash
pytest
pytest tests/test_e2e_api_flow.py -q
python scripts/e2e_api_flow.py --skip-analyze
```

See [Report 25](reports/25-e2e-performance.md).

Restart the server after pulling code changes.

Seed SQLite (optional — also runs automatically on pipeline load):

```bash
python scripts/seed_sqlite.py
```

---

## 8. Troubleshooting

| Problem | Likely cause | What to do |
|---------|--------------|------------|
| YOLO count = 0 | Blurry photo, high confidence threshold | Retake photo; fallback runs automatically at conf 0.25 |
| `not_found` | Drug not in CSV or OCR unreadable | Add drug to CSV; use `mode=accurate` |
| Wrong drug match | Dosage text matched (fixed in latest) | Pull latest `main`; restart API |
| Ibucold vs Ibucold C | OCR read `€` instead of `C` | Fixed via text normalizer |
| Slow analyze | CPU + many boxes | Use `mode=fast`; reduce box count in photo |

---

## 9. Flutter Mobile App

Phases 16–17 deliver the Android MVP client under `mobile/` (gallery picker, API integration, result screen).

### Install Flutter

Follow the official guide: https://docs.flutter.dev/get-started/install/windows

Verify:

```powershell
flutter doctor
```

### Setup and run

Start the backend first (required for analyze):

```powershell
python run_api.py
```

Then run the app:

```powershell
cd mobile
flutter pub get
flutter run
```

Or use the helper script from the repo root:

```powershell
.\scripts\setup-mobile.ps1
```

If Android launcher icons are missing, regenerate platform files:

```powershell
.\scripts\setup-mobile.ps1 -RegeneratePlatforms
```

See [mobile/README.md](../mobile/README.md), [Report 15](reports/15-flutter-foundation.md), and [Report 16](reports/16-mobile-integration.md).

Emulator sample photos:

```powershell
.\scripts\push-samples-to-emulator.ps1
```

---

## 10. Docker Deployment

Requires Docker Desktop and trained YOLO weights at  
`runs/detect/runs/detect/medicine_box_yolov8n-2/weights/best.pt`.

```bash
docker compose up --build
```

Verify:

```bash
curl http://127.0.0.1:8000/health
```

Details: [Report 14 — Docker Containerization](reports/14-docker-containerization.md)

### Windows: WSL2 + Docker Desktop setup

On Windows, Docker Desktop needs WSL2. Helper scripts (elevated PowerShell):

| Script | When to use |
|--------|-------------|
| `scripts/install-wsl-docker.ps1` | First-time WSL2 + Docker install |
| `scripts/post-reboot-docker.ps1` | After reboot — finish WSL, start Docker, optional `docker compose up` |
| `scripts/diagnose-wsl.ps1` | Troubleshoot WSL features and services |
| `scripts/fix-docker-wsl.ps1` | Repair WSL features and restart Docker |
| `scripts/fix-wsl-winget.ps1` | Reinstall WSL via winget if DISM enable reverts |
| `scripts/fix-wsl-final.ps1` | Last-resort DISM + OptionalFeatures enable |
| `scripts/fix-vmp.ps1` | Enable Virtual Machine Platform only |
| `scripts/uninstall-docker.ps1` | Complete Docker Desktop removal |

See [scripts/README-docker-wsl.md](../scripts/README-docker-wsl.md).

### Flutter/Android on D: drive

If C: is low on space, migrate dev tools to `D:\dev\`:

```powershell
.\scripts\migrate-dev-to-d.ps1
```

See [mobile/README.md](../mobile/README.md) for layout details.

Typical WSL flow:

```powershell
# 1) Admin PowerShell — first install
.\scripts\install-wsl-docker.ps1

# 2) Reboot if prompted, then:
.\scripts\post-reboot-docker.ps1

# 3) If WSL still fails:
.\scripts\diagnose-wsl.ps1
# read scripts\diagnose-wsl.log
```

See [scripts/README-docker-wsl.md](../scripts/README-docker-wsl.md) for full details.

---

## Project Layout (summary)

```text
medicine-box-detection-yolov8/
├── backend/app/   FastAPI application
├── data/          samples, database, dataset config
├── docs/          architecture, roadmap, reports
├── examples/      learning scripts and usage demos
├── src/           reusable production AI modules
├── tests/         automated tests
├── mobile/        Flutter Android MVP client
├── run_api.py     FastAPI entry point
├── run_analyze.py CLI pipeline runner
├── Dockerfile     API container image
├── docker-compose.yml  Docker stack
├── requirements.txt
└── README.md
```

| Directory | Role |
|-----------|------|
| `src/` | Production-ready application logic |
| `backend/` | REST API layer |
| `examples/` | Step-by-step learning demonstrations |
| `docs/` | Documentation and technical reports |

---

## 10. Continuous Integration (GitHub Actions)

Every push and pull request to `main` runs automated checks:

| Workflow | Command (local equivalent) |
|----------|----------------------------|
| Backend Tests | `pytest` |
| Mobile Tests | `cd mobile && flutter analyze && flutter test` |
| Docker Build | `docker compose build` (on `main`, Docker path changes) |

See [CONTRIBUTING.md](../CONTRIBUTING.md) and [Report 17](reports/17-ci-cd-github-actions.md).

Workflow files: `.github/workflows/`

---

## Next Steps

1. Review [architecture.md](architecture.md) and [roadmap.md](roadmap.md)
2. Read [Report 16](reports/16-mobile-integration.md) and [Report 17](reports/17-ci-cd-github-actions.md)
3. Pick the next GitHub Issue — [#32](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/32) (advanced features on `feature/advanced-features`)


### Run the unified pipeline from Python

```python
from src.services import analyze_medicine_boxes, PipelineConfig

result = analyze_medicine_boxes(
    "data/samples/coklu_resim.jpg",
    config=PipelineConfig(ocr_mode="fast"),
)
print(result.detection_count)
for box in result.medicines:
    print(box.status, box.medicine_name, box.matching_score)
```
