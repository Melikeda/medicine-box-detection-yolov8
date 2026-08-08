# Report 23 — Mobile Scan History

## Overview

Stores successful analyze results on the device so users can reopen past scans without re-running the backend pipeline.

**Scope:** Mobile local SQLite (MVP) + server sync via `/api/v1/scans` (final-polish-4).

**Branch:** `feature/scan-history` (merged PR #49); server API on `feature/final-polish-4`

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

## Server sync (final-polish-4)

| Layer | Detail |
|-------|--------|
| Table | SQLite `scans` (same DB as medicines) |
| API | `POST/GET/DELETE /api/v1/scans`, `GET /api/v1/scans/info` |
| Auth | None yet — global list (document for production) |
| Mobile | After local `saveScan`, best-effort `ScanApiService.createScan` |
| Images | Stay on device; server stores analyze JSON only |
| Cap | `SCAN_HISTORY_MAX_ENTRIES` (default 200) |

## Future (optional)

- Per-user auth + private scan lists
- PostgreSQL migration can absorb `scans` table later
- Pull remote history into the mobile list UI
