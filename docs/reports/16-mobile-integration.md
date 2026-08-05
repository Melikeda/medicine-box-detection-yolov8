# Report 16 — Mobile & Backend Integration (MVP)

## Overview

Phase 17 connects the Flutter mobile client to the existing FastAPI analyze endpoint. The mobile app uploads a gallery photo, runs the same YOLO + OCR + matching pipeline as the backend CLI, and displays structured results on a dedicated result screen.

**Branch:** `feature/mobile-integration`  
**GitHub Issue:** #31

---

## Objectives

- [x] Connect mobile app to analyze API
- [x] Display medicine name, match score, and basic info
- [x] Handle loading states and errors
- [x] Test on Android (unit/widget tests + manual E2E)

---

## Architecture

```text
mobile/lib/
├── config/app_config.dart       API base URL, timeouts, endpoints
├── models/
│   ├── analyze_response.dart    Mirrors FastAPI AnalyzeResponseSchema
│   ├── analyze_summary.dart
│   └── medicine_box_result.dart
├── services/
│   ├── analyze_api_service.dart Multipart POST + health check
│   ├── analyze_api_exception.dart
│   └── image_picker_service.dart
├── screens/
│   ├── image_preview_screen.dart  Analyze trigger + loading overlay
│   └── result_screen.dart         Summary chips + per-box cards
├── widgets/
│   └── medicine_result_card.dart
├── utils/
│   └── medicine_display.dart    Placeholder + box label formatting
└── routes/app_router.dart       Added /result route
```

The mobile client consumes the existing `POST /api/v1/analyze?mode=fast` contract. One small backend validation tweak accepts `application/octet-stream` when the filename extension is valid (Android gallery uploads).

---

## Screen Flow

```text
Splash (2s)
    │
    ▼
Home ── "Galeriden Sec" ──► Image Preview ── "Analiz Et" ──► Result
    │                              │                            │
    └──────── "Geri Don" ◄─────────┘                            │
    └──────── "Ana Sayfaya Don" ◄───────────────────────────────┘
```

Before analyze, the app calls `GET /health` and blocks with a SnackBar if models are not loaded.

---

## API Integration

| Setting | Value |
|---------|-------|
| Endpoint | `POST /api/v1/analyze` |
| Body | `multipart/form-data`, field `file` |
| Query | `mode=fast` (default) |
| Emulator base URL | `http://10.0.2.2:8000` |
| Analyze timeout | 300 s (CPU OCR can exceed 2 min) |
| Health check | `GET /health` (`status=ok`, `models_loaded=true`) |
| Gallery compression | max 1280 px, quality 65 % |

Override API URL at build time:

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000
```

Android cleartext HTTP is enabled for local development (`usesCleartextTraffic="true"`).

---

## Integration Fixes (Phase 17)

| Issue | Cause | Fix |
|-------|-------|-----|
| `415 Unsupported Media Type` | Android sends `application/octet-stream` | Mobile sets MIME from extension; backend normalizes octet-stream |
| Timeout / “küçük fotoğraf” message | CPU OCR ~3–5 min on large images | Timeout 300 s; gallery resize; clearer loading text |
| `VERIFY_FROM_OFFICIAL_LEAFLET` in UI | CSV seed placeholder | `MedicineDisplay` shows user-friendly Turkish text |
| “Kutu 2” for single box | Backend uses 1-based `box_index`; UI added +1 | Display `Kutu {box_index}` directly |

---

## Error Handling

| Scenario | User-facing message |
|----------|---------------------|
| Backend not ready | Backend hazir degil… |
| Backend unreachable | Sunucuya baglanilamadi… |
| Timeout | Analiz zaman asimina ugradi… CPU uzerinde OCR uzun surebilir |
| HTTP 413 | Dosya cok buyuk… |
| Server 4xx/5xx | Server `error`/`detail` field or generic message |
| Missing file | Secilen dosya bulunamadi |

Errors appear in a SnackBar on the preview screen. Successful responses navigate to the result screen.

---

## Result UI

- **Summary card:** detection count, matched / not found / not medicine box counts, processing time, OCR mode
- **Medicine cards:** status chip, display message, medicine name, match score, active ingredient, dosage, form, category
- **Placeholder fields:** unverified CSV values shown as “Resmi urun bilgisinden dogrulanmali”
- **Empty state:** message when no boxes detected

---

## E2E Validation (Manual)

Tested on Android emulator (`medicine_box_emulator`) against local FastAPI:

| Input | Result |
|-------|--------|
| A-Ferin Forte sample photo | Matched, score ~85.7 %, OCR `a ferin` |
| Processing time (CPU, fast mode) | ~255 s for one box |

---

## Tests

| File | Coverage |
|------|----------|
| `test/analyze_response_test.dart` | JSON parsing for models |
| `test/result_screen_test.dart` | Result screen widget + placeholders |
| `test/medicine_display_test.dart` | Box label + field formatting |
| `test/widget_test.dart` | Splash screen (existing) |
| `tests/test_api.py` | Backend octet-stream upload acceptance |

Run mobile tests:

```powershell
. .\scripts\env-flutter.ps1
cd mobile
flutter analyze
flutter test
```

Run backend test:

```powershell
pytest tests/test_api.py::test_upload_validator_accepts_octet_stream_with_jpg_suffix -q
```

---

## Manual E2E Checklist

1. Start backend: `venv\Scripts\Activate.ps1` then `python run_api.py`
2. Verify health: `http://127.0.0.1:8000/health`
3. Load Flutter env: `. .\scripts\env-flutter.ps1`
4. Launch emulator: `flutter emulators --launch medicine_box_emulator`
5. Push sample photos: `.\scripts\push-samples-to-emulator.ps1`
6. Run app: `cd mobile; flutter run`
7. Gallery → Preview → **Analiz Et** → wait 1–5 min on CPU
8. Confirm result screen (medicine name, match score)
9. Stop backend → confirm error SnackBar

---

## Dependencies Added

| Package | Purpose |
|---------|---------|
| `http` | Multipart upload + health check |
| `http_parser` | MIME types for multipart parts |

---

## Known Limitations

- **CPU latency:** first analyze can take several minutes (EasyOCR + 8 variants per box)
- **Seed database:** many drugs use `VERIFY_FROM_OFFICIAL_LEAFLET` for active ingredient / dosage
- **OCR mode:** UI always uses `fast`; no toggle yet
- ~~**No camera capture** in MVP (gallery only)~~ → Done (Report 22, `feature/camera-capture`)

---

## Out of Scope (Phase 18+)

- OCR mode toggle in UI
- Scan history / offline cache
- iOS build

---

## Next Phase

Issue #32 — Advanced Features on branch `feature/advanced-features`.
