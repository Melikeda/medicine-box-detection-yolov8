# Report 14 — Docker Containerization


> **Historical phase report.** Written for that phase; some numbers or “next steps” may be outdated.
> Living docs: [README](../../README.md) · [Architecture](../architecture.md) · [Roadmap](../roadmap.md) · [Reports index](README.md).
> Current product: **Yolocilin** · catalog **131** medicines · APIs: analyze · medicines · explain · scans.

## Overview

Phase 15 packages the FastAPI backend and AI pipeline into a reproducible Docker deployment so the API runs the same way on any machine with Docker installed.

**Branch:** `feature/docker`  
**GitHub Issue:** #29

---

## Objectives

- [x] Create `Dockerfile` for the API service
- [x] Create `docker-compose.yml` with model and database volumes
- [x] Add `.dockerignore` to keep images lean
- [x] Add startup entrypoint (model check + SQLite seed)
- [x] Support `YOLO_MODEL_PATH` via environment variables
- [x] Document local deployment

---

## Architecture

```text
Host machine
├── runs/.../best.pt          (YOLO weights — mounted read-only)
├── data/database/
│   ├── medicines.csv         (seed source)
│   └── medicines.db          (persisted SQLite)
└── docker compose up
         │
         ▼
    medicine-box-api container
    ├── seed SQLite from CSV
    ├── load YOLO + EasyOCR
    └── listen on 0.0.0.0:8000
```

---

## New Files

| Path | Role |
|------|------|
| `Dockerfile` | Python 3.12 slim image with API dependencies |
| `docker-compose.yml` | One-service stack with volume mounts |
| `.dockerignore` | Exclude dataset, tests, venv, weights from build context |
| `scripts/docker-entrypoint.sh` | Verify model exists, seed DB, start API |
| `scripts/install-wsl-docker.ps1` | Windows: first-time WSL2 + Docker Desktop install |
| `scripts/post-reboot-docker.ps1` | Windows: post-reboot WSL/Docker finish + optional compose |
| `scripts/diagnose-wsl.ps1` | Windows: WSL diagnostic log |
| `scripts/fix-docker-wsl.ps1` | Windows: repair WSL features and restart Docker |
| `scripts/README-docker-wsl.md` | Windows WSL/Docker script guide |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` (Docker) | Uvicorn bind address |
| `PORT` | `8000` | API port |
| `OCR_MODE` | `fast` | `fast` or `accurate` |
| `YOLO_MODEL_PATH` | `runs/.../best.pt` | Path inside the container |
| `YOLO_MODEL_HOST_PATH` | same as above | Host path for compose volume mount |
| `SQLITE_PATH` | `data/database/medicines.db` | SQLite file path |
| `USE_GPU` | `false` | CPU-only image (no CUDA) |

---

## Prerequisites

1. **Docker Desktop** (Windows/macOS) or Docker Engine (Linux)
2. **Trained YOLO weights** at  
   `runs/detect/runs/detect/medicine_box_yolov8n-2/weights/best.pt`  
   (train with `python src/train.py` — weights are not in Git)

---

## Quick Start

```bash
# Build and start
docker compose up --build

# Detached mode
docker compose up --build -d

# View logs
docker compose logs -f api

# Stop
docker compose down
```

API: http://127.0.0.1:8000/docs

---

## Verify Deployment

```bash
# Health check
curl http://127.0.0.1:8000/health

# Analyze a sample image (from host)
curl -X POST "http://127.0.0.1:8000/api/v1/analyze?mode=fast" \
  -F "file=@data/samples/samples3.jpg"
```

Expected health response: `"status": "ok"`, `"models_loaded": true`.

---

## Design Choices

- **CPU-only image** — matches local dev defaults (`USE_GPU=false`); GPU/CUDA can be a follow-up
- **Weights via volume** — `.pt` files stay out of Git and the Docker build context
- **SQLite persisted on host** — `data/database/` volume keeps medicine data across restarts
- **EasyOCR cache volume** — avoids re-downloading OCR models on every rebuild
- **Entrypoint seed** — ensures SQLite exists before the API loads matching data

---

## Windows: WSL2 + Docker Desktop

Docker Desktop on Windows requires WSL2. Helper PowerShell scripts under `scripts/` automate install and repair:

```powershell
# Admin PowerShell
.\scripts\install-wsl-docker.ps1
# reboot if needed
.\scripts\post-reboot-docker.ps1
```

Troubleshooting: `.\scripts\diagnose-wsl.ps1` → read `scripts\diagnose-wsl.log`

Full guide: [scripts/README-docker-wsl.md](../../scripts/README-docker-wsl.md)

Common blockers:
- Virtual Machine Platform not enabled → reboot required
- BIOS virtualization disabled
- Low C: drive space for WSL/Docker images

---

- First startup is slow (EasyOCR model download + YOLO load)
- Image size is large due to PyTorch + OpenCV
- Full analyze integration tests are not run inside the container build

---

## Next Phase

Issue #32 — Advanced Features on branch `feature/advanced-features`.  
(Mobile integration completed in Phase 17 — [Report 16](16-mobile-integration.md).)
