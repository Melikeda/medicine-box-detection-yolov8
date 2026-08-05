# Report 23 — Mobile Scan History

## Overview

Stores successful analyze results on the device so users can reopen past scans without re-running the backend pipeline.

**Scope:** Mobile-only (local SQLite). Backend `/api/v1/scans` is out of scope for this MVP slice.

---

## Speed impact

| Phase | Blocks analyze UI? |
|-------|-------------------|
| `POST /analyze` (YOLO + OCR) | Unchanged — same as before |
| Save to local DB | **No** — `unawaited()` after response; runs in background |
| Image copy to app documents | Background (~50–200 ms typical) |

Analyze wait time is dominated by backend CPU work (often tens of seconds). Local persistence does not add to that path.

---

## Technology

| Layer | Choice | Why |
|-------|--------|-----|
| Storage | `sqflite` | Structured list, delete, sort; fits history better than `shared_preferences` |
| Paths | `path_provider` | Stable image copies under app documents |
| Limit | 50 entries | Prevents unbounded disk growth |

Medicine catalog remains in backend `medicines.db`. Scan history uses a **separate** mobile DB file: `scan_history.db`.

---

## Mobile changes

| File | Change |
|------|--------|
| `lib/services/scan_history_service.dart` | SQLite CRUD, image persist, trim old entries |
| `lib/screens/history_screen.dart` | List, swipe-to-delete, open detail |
| `lib/screens/image_preview_screen.dart` | Background save after successful analyze |
| `lib/screens/home_screen.dart` | History icon in AppBar |
| `lib/models/*.dart` | `toJson()` for round-trip storage |
| `test/scan_history_service_test.dart` | Service tests (`sqflite_common_ffi`) |
| `test/history_screen_test.dart` | Empty + list widget tests |

---

## User flow

```text
Analyze success → (background save) → Result screen
Home → History icon → List → Tap → Result screen (saved JSON)
```

---

## Manual test

1. Run backend + `flutter run`
2. Analyze a sample photo
3. Home → history icon → entry appears
4. Tap entry → same result cards as live analyze
5. Swipe delete / clear all

---

## Future (optional)

- `POST /api/v1/scans` on backend when multi-device sync is needed
- PostgreSQL migration can absorb `scans` table later
