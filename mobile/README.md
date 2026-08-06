# Yolocilin Mobile App

Android MVP client for the Yolocilin medicine box detection system.

**Branch:** `feature/mobile-integration`  
**GitHub Issue:** [#31](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/31)

---

## Scope

- Splash, home, image preview, and **result** screens
- Gallery and **camera** image picker
- FastAPI integration (`POST /api/v1/analyze`)
- **Local scan history** (sqflite, device-only)
- Loading overlay, error SnackBars, summary + per-box result cards

Phase 16 foundation: [Report 15](../docs/reports/15-flutter-foundation.md)  
Phase 17 integration: [Report 16](../docs/reports/16-mobile-integration.md)  
Camera capture: [Report 22](../docs/reports/22-camera-capture.md)  
Scan history: [Report 23](../docs/reports/23-scan-history.md)

---

## Prerequisites

| Tool | Version |
|------|---------|
| Flutter SDK | 3.19+ |
| Android Studio | Latest (SDK + emulator) |
| Running API | `python run_api.py` |

Install Flutter: https://docs.flutter.dev/get-started/install

---

## First-time setup

From the repository root:

```powershell
# Load Flutter/Java/Android environment
. .\scripts\env-flutter.ps1

# Install deps + run analyze
.\scripts\setup-mobile.ps1
```

Permanent PATH (run once after SDK install):

```powershell
.\scripts\install-flutter-path.ps1
```

### Dev tools on D: drive (recommended if C: is low on space)

Default layout:

```text
D:\dev\
├── flutter\
├── android-sdk\
├── android-avd\
├── gradle\
└── pub-cache\
```

One-time migration from C::

```powershell
# Close emulator and flutter run first
.\scripts\migrate-dev-to-d.ps1
```

Paths: `scripts/dev-paths.ps1` (loaded by `env-flutter.ps1`).

Regenerate Android scaffolding if needed:

```powershell
.\scripts\setup-mobile.ps1 -RegeneratePlatforms
```

### Emulator test photos

The emulator gallery is empty by default. Load project samples:

```powershell
.\scripts\push-samples-to-emulator.ps1
```

Photos appear under **Pictures → medicine-samples**.

---

## Run on Android

1. Start the FastAPI backend (separate terminal):

```powershell
cd c:\Projects\medicine-box-detection-yolov8
.\.venv\Scripts\Activate.ps1
python run_api.py
```

2. Start the emulator or connect a device:

```powershell
. .\scripts\env-flutter.ps1
flutter emulators --launch medicine_box_emulator
```

3. From `mobile/`:

```powershell
flutter run
```

4. **Fotoğraf Çek** or gallery → pick sample → **Analiz Et** → view results.

### API base URL

Default for Android emulator: `http://10.0.2.2:8000` (maps to host `localhost:8000`).

Override at build/run time (physical device on same LAN):

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000
```

---

## Project layout

```text
mobile/
├── lib/
│   ├── main.dart
│   ├── app.dart
│   ├── config/app_config.dart
│   ├── routes/app_router.dart
│   ├── models/                # API response models
│   ├── screens/               # Splash, home, preview, result
│   ├── services/              # Image picker + analyze API
│   ├── utils/                 # Medicine field display helpers
│   ├── widgets/               # Medicine result card
│   └── theme/app_theme.dart
├── test/                      # Model + widget tests
├── android/
└── pubspec.yaml
```

---

## Screen flow

```text
Splash (2s)
    │
    ▼
Home ── "Fotograf Cek" / "Galeriden Sec" ──► Image Preview ── "Analiz Et" ──► Result
    │                              │                            │
    └──────── "Geri Don" ◄─────────┘                            │
    └──────── "Ana Sayfaya Don" ◄───────────────────────────────┘
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `image_picker` | Gallery + camera image selection |
| `sqflite` | Local scan history storage |
| `path_provider` | Persist scan thumbnails under app documents |
| `http` | Multipart analyze upload |

---

## Tests

```powershell
cd mobile
flutter analyze
flutter test
```

---

## Next phase

Issue #32 — advanced features (LLM, scan history, iOS) on branch `feature/advanced-features`.
