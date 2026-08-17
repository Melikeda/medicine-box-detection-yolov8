# Yolocilin — Mobile (Android)

Flutter client for **Yolocilin**: detect the box, identify the medicine, show a short explanation.

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
| Barcode (live frame + photo) | Done (`GET/POST /api/v1/barcode`) |
| iOS | Not yet |

Reports: [15](../docs/reports/15-flutter-foundation.md) · [16](../docs/reports/16-mobile-integration.md) · [22](../docs/reports/22-camera-capture.md) · [23](../docs/reports/23-scan-history.md) · [21](../docs/reports/21-llm-integration.md)

---

## Prerequisites

| Tool | Version |
|------|---------|
| Flutter SDK | 3.19+ |
| Android Studio | SDK + emulator |
| Backend | `python run_api.py` or `.\scripts\start-backend.ps1` (repo root, `venv`; catalog **1163** medicines) |

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

Flow: **Fotoğraf Çek** / gallery → preview → choose **OCR mode** (Hızlı / Hassas) → **Analiz Et** → result.  
Barcode: on the scan viewfinder tap **Barkod tara** → live frame (or **Fotoğraftan oku**) → same result screen + “İlaç hakkında”.

| OCR mode | API | Notes |
|----------|-----|--------|
| Hızlı (`fast`, default) | `?mode=fast` | Typical 1–3 min/box on CPU |
| Hassas (`accurate`) | `?mode=accurate` | More OCR variants; much slower |

Preference is stored on device (`SharedPreferences`).

### API base URL

| Target | URL |
|--------|-----|
| Android emulator (default) | `http://10.0.2.2:8000` |
| Physical device (LAN) | `flutter run --dart-define=API_BASE_URL=http://<PC-IP>:8000` |
| Testers (any network) | Release APK with `API_BASE_URL=https://…` (tunnel or cloud) |

Release builds **block cleartext HTTP** — use HTTPS for Firebase / remote testers.

### Firebase App Distribution (test APKs)

Ship builds to phones outside your Wi‑Fi without Play Store:

1. One-time Firebase + GitHub secrets setup — [guide](../docs/guides/firebase-app-distribution.md)
2. Local: `.\scripts\distribute-android.ps1 -ApiBaseUrl "https://…" -FirebaseAppId "1:…:android:…"`
3. CI: Actions → **Mobile Distribute (Firebase)** → Run workflow

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
