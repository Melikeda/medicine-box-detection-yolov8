# Yolocilin — Mobile (Android)

Flutter client for the **Yolocilin** medicine box detection system.

<p align="center">
  <img src="../docs/assets/yolocilin-logo.png" alt="Yolocilin" width="120" />
</p>

Talks to the FastAPI backend: analyze → result UI → optional Gemini explain → local + server scan history.

---

## Features

| Feature | Status |
|---------|--------|
| Splash / home / preview / result | Done |
| Gallery + camera capture | Done |
| `POST /api/v1/analyze` | Done |
| Bilingual UI (TR / EN) | Done |
| Local scan history (sqflite) | Done |
| Best-effort `POST /api/v1/scans` sync | Done |
| “İlaç hakkında” (`POST /api/v1/explain`) | Done (needs backend LLM) |
| iOS | Not yet |

Reports: [15](../docs/reports/15-flutter-foundation.md) · [16](../docs/reports/16-mobile-integration.md) · [22](../docs/reports/22-camera-capture.md) · [23](../docs/reports/23-scan-history.md) · [21](../docs/reports/21-llm-integration.md)

---

## Prerequisites

| Tool | Version |
|------|---------|
| Flutter SDK | 3.19+ |
| Android Studio | SDK + emulator |
| Backend | `python run_api.py` (repo root, `venv`) |

---

## Setup

From the **repository root**:

```powershell
. .\scripts\env-flutter.ps1
.\scripts\setup-mobile.ps1
.\scripts\push-samples-to-emulator.ps1   # fill emulator gallery
```

Optional D: drive layout for SDKs: `.\scripts\migrate-dev-to-d.ps1` (see comments in that script).

---

## Run

```powershell
# Terminal 1 — API
cd c:\Projects\medicine-box-detection-yolov8
.\venv\Scripts\Activate.ps1
python run_api.py

# Terminal 2 — app
. .\scripts\env-flutter.ps1
flutter emulators --launch medicine_box_emulator
cd mobile
flutter run
```

Flow: **Fotoğraf Çek** / gallery → preview → **Analiz Et** → result (CPU OCR may take 1–3 minutes).

### API base URL

| Target | URL |
|--------|-----|
| Android emulator (default) | `http://10.0.2.2:8000` |
| Physical device (LAN) | `flutter run --dart-define=API_BASE_URL=http://<PC-IP>:8000` |

---

## Screen flow

```text
Splash
  └─► Home ── camera / gallery ──► Preview ── Analiz Et ──► Result
        │                                              │
        └──── History (local) ─────────────────────────┘
                              Result may call explain + sync scans
```

---

## Layout

```text
mobile/lib/
├── config/app_config.dart      # endpoints, timeouts
├── services/
│   ├── analyze_api_service.dart
│   ├── explain_api_service.dart
│   ├── scan_api_service.dart     # server history
│   └── scan_history_service.dart # local SQLite
├── screens/                    # splash, home, preview, result, history, …
├── models/
├── l10n/                       # TR / EN strings
├── theme/
└── widgets/
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `image_picker` | Gallery + camera |
| `http` | Analyze / explain / scans |
| `sqflite` + `path_provider` | Local history + thumbnails |
| `google_fonts` | Brand typography |
| `shared_preferences` | Locale prefs |

---

## Tests

```powershell
cd mobile
flutter analyze
flutter test
```

---

## Related backend

- Health: `GET /health`
- Analyze: `POST /api/v1/analyze`
- Explain: `POST /api/v1/explain` (enable LLM in `.env`)
- Scans: `POST /api/v1/scans` (best-effort after local save)

Root docs: [README](../README.md) · [SECURITY](../SECURITY.md) · [E2E Report 25](../docs/reports/25-e2e-performance.md)
