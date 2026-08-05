# Report 22 — Mobile Camera Capture

## Overview

Adds direct camera capture on the home screen so users can photograph a medicine box in real time, not only pick from the gallery.

**Branch:** `feature/camera-capture` (merged PR #48)  
**Phase:** 18 — Advanced Features ([#32](https://github.com/Melikeda/medicine-box-detection-yolov8/issues/32))

---

## Objectives

- [x] `image_picker` with `ImageSource.camera`
- [x] Android `CAMERA` permission + camera intent query
- [x] Home screen **Fotoğraf Çek** button (primary action)
- [x] Gallery flow preserved (**Galeriden Seç**)
- [x] Shared preview → analyze flow unchanged
- [x] iOS Info.plist guidance (platform scaffold pending)
- [x] Widget test for home actions

---

## Mobile changes

| File | Change |
|------|--------|
| `lib/services/image_picker_service.dart` | `pickFromCamera()`, shared `_pickImage()` |
| `lib/screens/home_screen.dart` | Camera + gallery buttons, loading states |
| `android/app/src/main/AndroidManifest.xml` | `CAMERA`, optional camera feature, capture intent |
| `mobile/ios/README.md` | `NSCameraUsageDescription` snippet for future iOS |
| `test/home_screen_test.dart` | Verifies both buttons |

### Image settings (aligned with backend resize)

| Setting | Value |
|---------|--------|
| `imageQuality` | 65 |
| `maxWidth` / `maxHeight` | 1280 |
| `preferredCameraDevice` | Rear |

---

## Screen flow

```text
Home
 ├── "Fotograf Cek" ──► Camera ──► Image Preview ──► Analyze ──► Result
 └── "Galeriden Sec" ──► Gallery ──► Image Preview ──► Analyze ──► Result
```

---

## Android permissions

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-feature android:name="android.hardware.camera" android:required="false" />
```

`android:required="false"` keeps the app installable on devices without a camera (gallery still works).

Runtime permission prompts are handled by `image_picker`.

---

## iOS (future)

See [mobile/ios/README.md](../../mobile/ios/README.md). Add `NSCameraUsageDescription` when the iOS platform folder is generated.

---

## Tests

```powershell
cd mobile
flutter analyze
flutter test
```

---

## Manual test (Android)

1. Start backend: `python run_api.py`
2. `flutter run` on emulator or device with camera
3. Tap **Fotoğraf Çek** → grant camera permission → capture → preview → analyze
4. Tap **Galeriden Seç** → existing gallery flow still works

Emulator: use **Virtual scene** or extended controls camera feed if hardware camera unavailable.
