# Report 29 — Project Release v1.0.0

> Living decision record for the first public GitHub Release.  
> Branch: `feature/project-release`  
> Tag: [`v1.0.0`](https://github.com/Melikeda/yolocilin/releases/tag/v1.0.0)

**Product:** Yolocilin · API **1.0.0** · Flutter **1.0.0+1** · catalog **1163** · OCR **EasyOCR**

---

## Purpose

Close Phase 21: ship a SemVer tag, a GitHub Release, and aligned version strings so the internship MVP is a citable, cloneable snapshot — not an unversioned `main`.

## What 1.0.0 means

| Layer | Version | Where |
|-------|---------|--------|
| FastAPI | `1.0.0` | `backend/app/config.py` (`app_version`, `/health`) |
| Flutter | `1.0.0+1` | `mobile/pubspec.yaml` |
| Git | annotated tag `v1.0.0` on `main` | GitHub Release |

This is the **first public** release. It is not a claim of clinical accuracy or full-market coverage.

## In scope

- YOLOv8 box detection → crop → OpenCV → EasyOCR → RapidFuzz → SQLite (1163)
- Optional barcode path (EAN-13 / DataMatrix) before OCR
- FastAPI: analyze, medicines, barcode, explain, scans
- Flutter Android client (gallery, camera, live barcode, local + server history)
- Docker, GitHub Actions CI, production CORS / docs hardening
- Kaggle dataset (CC BY 4.0) linked from README

## Out of scope (post-MVP)

PostgreSQL, cloud HTTPS host, per-user scan auth, iOS. These stay on the [roadmap](../roadmap.md) as future work.

## How to cut a later release

1. Move notes from `[Unreleased]` in [CHANGELOG.md](../../CHANGELOG.md) into a new `## [X.Y.Z]` section.
2. Bump `app_version` and `mobile/pubspec.yaml` together.
3. Merge to `main`, then:

```bash
git tag -a vX.Y.Z -m "Yolocilin vX.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z --title "Yolocilin vX.Y.Z" --notes-file CHANGELOG.md
```

Prefer a short release body that summarizes the changelog section, plus clone / run pointers and the medical disclaimer.

## Notes

YOLO weights (`best.pt`) and dataset images under `data/dataset/` are **not** in Git. See [models/README.md](../../models/README.md) and the [Kaggle dataset](https://www.kaggle.com/datasets/melikeklahc/yolocilin-medicine-box-detection).
