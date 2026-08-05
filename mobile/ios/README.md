# iOS camera setup (when `ios/` platform is added)

The Android MVP ships first. When you run `flutter create .` under `mobile/` to add iOS, add these keys to `ios/Runner/Info.plist` **inside** the top-level `<dict>`:

```xml
<key>NSCameraUsageDescription</key>
<string>Ilac kutusu fotografini analiz etmek icin kameraya erisim gerekir.</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Galeriden ilac kutusu fotografi secmek icin erisim gerekir.</string>
```

No code changes are required beyond the existing `ImagePickerService.pickFromCamera()` call.
