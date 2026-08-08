# Technical reports

Phase-by-phase engineering notes for the **Yolocilin** medicine box detection internship project.

> **Living docs** (always prefer these for current truth):  
> [Root README](../../README.md) · [Architecture](../architecture.md) · [Roadmap](../roadmap.md) · [Setup](../setup-guide.md) · [SECURITY](../../SECURITY.md)

**Current product snapshot:** Flutter app **Yolocilin** · catalog **131** medicines · APIs: analyze · medicines · explain · scans.

---

## How to read these files

| Kind | Reports | Guidance |
|------|---------|----------|
| Historical diaries | **01–19**, **22** | Written at the time of that phase. Numbers (e.g. 38/107 drugs) may be outdated — see “Current snapshot” above. |
| Still accurate feature docs | **20**, **21**, **23**, **24**, **25** | Keep aligned with code; small footnotes added when superseding work lands. |

---

## Index

| # | Report | Topic |
|---|--------|--------|
| 01 | [01-project-setup.md](01-project-setup.md) | Repo & folder layout |
| 02 | [02-development-environment.md](02-development-environment.md) | Dev environment |
| 03 | [03-dataset-preparation.md](03-dataset-preparation.md) | Dataset |
| 04 | [04-roboflow-annotation.md](04-roboflow-annotation.md) | Annotation |
| 05 | [05-yolov8-training.md](05-yolov8-training.md) | YOLO training |
| 06 | [06-opencv-preprocessing.md](06-opencv-preprocessing.md) | OpenCV |
| 07 | [07-ocr-integration.md](07-ocr-integration.md) | EasyOCR |
| 08 | [08-pipeline-unification.md](08-pipeline-unification.md) | Pipeline unify |
| 09 | [09-pipeline-servicification.md](09-pipeline-servicification.md) | Service layer |
| 10 | [10-fastapi-analyze-api.md](10-fastapi-analyze-api.md) | Analyze API |
| 11 | [11-real-world-matching-improvements.md](11-real-world-matching-improvements.md) | Matching hardening |
| 12 | [12-sqlite-database.md](12-sqlite-database.md) | SQLite |
| 13 | [13-automated-testing.md](13-automated-testing.md) | pytest |
| 14 | [14-docker-containerization.md](14-docker-containerization.md) | Docker |
| 15 | [15-flutter-foundation.md](15-flutter-foundation.md) | Flutter foundation |
| 16 | [16-mobile-integration.md](16-mobile-integration.md) | Mobile ↔ API |
| 17 | [17-ci-cd-github-actions.md](17-ci-cd-github-actions.md) | CI/CD |
| 18 | [18-medicine-database-expansion.md](18-medicine-database-expansion.md) | 38 → 107 catalog |
| 19 | [19-performance-optimization.md](19-performance-optimization.md) | Fast OCR mode |
| 20 | [20-production-hardening.md](20-production-hardening.md) | Security / prod |
| 21 | [21-llm-integration.md](21-llm-integration.md) | Gemini explain |
| 22 | [22-camera-capture.md](22-camera-capture.md) | Camera |
| 23 | [23-scan-history.md](23-scan-history.md) | Local + server history |
| 24 | [24-medicine-database-final-refresh.md](24-medicine-database-final-refresh.md) | **131** catalog |
| 25 | [25-e2e-performance.md](25-e2e-performance.md) | E2E & benchmarks |
