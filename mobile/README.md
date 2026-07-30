# Flutter Mobile App

Android MVP client for the Medicine Box Detection System.

**Branch:** `feature/flutter-foundation`  
**GitHub Issue:** [#30](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/30)

---

## Scope (Phase 16)

This phase delivers the mobile **foundation** only:

- Splash screen
- Home screen with gallery picker
- Image preview screen
- App theme and routing scaffold

API integration (`POST /api/v1/analyze`) is planned in Phase 17 ([#31](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/31)).

---

## Prerequisites

| Tool | Version |
|------|---------|
| Flutter SDK | 3.19+ |
| Android Studio | Latest (SDK + emulator) |
| Running API | `python run_api.py` (for Phase 17) |

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

1. Start the emulator or connect a device:

```powershell
. .\scripts\env-flutter.ps1
flutter emulators --launch medicine_box_emulator
```

2. From `mobile/`:

```powershell
flutter run
```

### API base URL (Phase 17)

Default for Android emulator: `http://10.0.2.2:8000`

Override at build/run time:

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000
```

---

## Project layout

```text
mobile/
├── lib/
│   ├── main.dart              # Entry point
│   ├── app.dart               # MaterialApp + theme + routes
│   ├── config/app_config.dart # App name, API URL placeholder
│   ├── routes/app_router.dart # Named routes
│   ├── screens/               # Splash, home, preview
│   ├── services/              # Image picker wrapper
│   └── theme/app_theme.dart   # Material 3 theme
├── android/                   # Android MVP target
└── pubspec.yaml
```

---

## Screen flow

```text
Splash (2s)
    │
    ▼
Home ── "Galeriden Sec" ──► Image Preview
    │                              │
    └──────── "Geri Don" ◄─────────┘
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `image_picker` | Gallery image selection |

---

## Next phase

Issue #31 — connect preview screen to FastAPI, show medicine name, match score, and loading/error states.
