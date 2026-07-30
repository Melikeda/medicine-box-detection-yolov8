# Report 15 — Flutter Mobile App Foundation

## Overview

Phase 16 adds the Flutter mobile client foundation under `mobile/`. This phase focuses on UI scaffolding and gallery image selection; API integration is deferred to Phase 17 (Issue #31).

**Branch:** `feature/flutter-foundation`  
**GitHub Issue:** #30

---

## Objectives

- [x] Initialize Flutter project
- [x] Build splash, home, and image preview screens
- [x] Integrate gallery image picker

---

## Architecture

```text
mobile/lib/
├── main.dart
├── app.dart                 MaterialApp + theme + routes
├── config/app_config.dart   App name, API URL placeholder
├── routes/app_router.dart   Named navigation
├── screens/
│   ├── splash_screen.dart   2s intro → home
│   ├── home_screen.dart     Gallery picker + thumbnail
│   └── image_preview_screen.dart
├── services/
│   └── image_picker_service.dart
└── theme/app_theme.dart
```

---

## Screen Flow

```text
Splash (2s)
    │
    ▼
Home ── "Galeriden Sec" ──► Image Preview
    │                              │
    └──────── "Geri Don" ◄─────────┘
```

The **Analiz Et** button on the preview screen is disabled in this phase. It will call `POST /api/v1/analyze` in Phase 17.

---

## New Files

| Path | Role |
|------|------|
| `mobile/pubspec.yaml` | Flutter project manifest |
| `mobile/lib/` | Dart source (screens, routing, theme) |
| `mobile/android/` | Android MVP platform config |
| `mobile/README.md` | Mobile setup and run instructions |
| `scripts/setup-mobile.ps1` | `flutter pub get` + analyze helper (Windows) |
| `scripts/env-flutter.ps1` | Session env vars (Flutter, Java, Android SDK) |
| `scripts/install-flutter-path.ps1` | Permanent user PATH setup |
| `scripts/push-samples-to-emulator.ps1` | Push `data/samples/` photos to emulator gallery |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `image_picker` | Gallery image selection |

---

## Android Permissions

| Permission | Purpose |
|------------|---------|
| `READ_MEDIA_IMAGES` | Gallery access (Android 13+) |
| `READ_EXTERNAL_STORAGE` | Legacy gallery access (≤ API 32) |
| `INTERNET` | Reserved for Phase 17 API calls |

---

## Configuration

| Constant | Default | Notes |
|----------|---------|-------|
| `AppConfig.apiBaseUrl` | `http://10.0.2.2:8000` | Android emulator → host localhost |
| `AppConfig.analyzeEndpoint` | `/api/v1/analyze` | Used in Phase 17 |

Override at run time:

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000
```

---

## Prerequisites

1. **Flutter SDK** 3.19+ — https://docs.flutter.dev/get-started/install
2. **Android Studio** with SDK and emulator (or physical device)
3. FastAPI backend running for Phase 17 testing (`python run_api.py`)

---

## Quick Start

```powershell
cd mobile
flutter pub get
flutter run
```

If launcher icons or platform files are missing:

```powershell
.\scripts\setup-mobile.ps1 -RegeneratePlatforms
```

---

## Out of Scope (Phase 17)

- HTTP client and multipart upload to `/api/v1/analyze`
- Result screen with medicine name and match score
- Loading and error states during analysis
- Camera capture (gallery only for MVP)

---

## Next

Issue #31 — Mobile & Backend Integration (MVP) on branch `feature/mobile-integration`.
