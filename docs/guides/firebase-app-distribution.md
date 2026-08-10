# Firebase App Distribution — Yolocilin (Android)

Distribute **test APKs** to phones that are **not** on your LAN Wi‑Fi.  
App Distribution only ships the APK; the FastAPI backend must still be reachable over **HTTPS**.

Spark (free) plan is enough for App Distribution. No Play Store listing required.

---

## What lives in this repo

| Path | Purpose |
|------|---------|
| [`.github/workflows/mobile-distribute.yml`](../../.github/workflows/mobile-distribute.yml) | Manual CI: build release APK → upload to Firebase |
| [`scripts/distribute-android.ps1`](../../scripts/distribute-android.ps1) | Local build + upload (Firebase CLI) |
| [`mobile/android/app/google-services.json.example`](../../mobile/android/app/google-services.json.example) | Placeholder shape for the real Firebase config |
| [`firebase.json`](../../firebase.json) | Minimal Firebase project config |
| [`.firebaserc.example`](../../.firebaserc.example) | Copy to `.firebaserc` with your Firebase project id |

Secrets (`google-services.json`, service account JSON, Firebase tokens) are **never** committed.

---

## One-time setup (you do this in Firebase + GitHub)

### 1. Firebase project

1. Open [Firebase Console](https://console.firebase.google.com/) → **Add project** (Spark).
2. Add an **Android** app:
   - Package name: `com.medicinebox.medicine_box_app`
   - App nickname: `Yolocilin`
3. Download **`google-services.json`** → place at  
   `mobile/android/app/google-services.json` (gitignored).
4. Enable **App Distribution** for the project.
5. Create a tester group (e.g. `testers`) and invite Gmail addresses.
6. Copy the Android **App ID** (looks like `1:1234567890:android:abcdef…`) from Project settings.

### 2. Service account (for GitHub Actions)

1. Firebase / Google Cloud → IAM → create a service account with role  
   **Firebase App Distribution Admin** (or Firebase Admin).
2. Create a JSON key → save locally (do not commit).
3. In GitHub repo → **Settings → Secrets and variables → Actions**, add:

| Secret / variable | Required | Notes |
|-------------------|----------|--------|
| `FIREBASE_APP_ID` | Yes | Android App ID from Firebase |
| `FIREBASE_SERVICE_ACCOUNT` | Yes (CI) | Full JSON key contents |
| `API_BASE_URL` | Yes | Public **HTTPS** API (tunnel or cloud), e.g. `https://….trycloudflare.com` |
| `FIREBASE_TESTER_GROUPS` | No | Default `testers` if unset |

Optional repo variable `FIREBASE_PROJECT_ID` if you use local `.firebaserc`.

### 3. Backend for testers

Release APKs **reject cleartext HTTP**. Before every tester build:

1. Start the API on your PC (`python run_api.py` or Docker).
2. Expose it with a free HTTPS tunnel (**Cloudflare Tunnel** or **ngrok**).
3. Use that `https://…` URL as `API_BASE_URL` when building.

If the tunnel or PC stops, the app installs but analyze fails — expected.

---

## Local distribute (PowerShell)

```powershell
# From repo root — API + HTTPS tunnel already running
.\scripts\distribute-android.ps1 `
  -ApiBaseUrl "https://YOUR-TUNNEL.example" `
  -FirebaseAppId "1:….android:…" `
  -Groups "testers" `
  -ReleaseNotes "Yolocilin demo build"
```

Requires: Flutter SDK, Node.js (`npm i -g firebase-tools`), `firebase login` once.

APK path: `mobile/build/app/outputs/flutter-apk/app-release.apk`.

---

## GitHub Actions distribute

1. Ensure secrets above are set.
2. **Actions → Mobile Distribute (Firebase) → Run workflow**.
3. Optionally override `api_base_url` / `release_notes` / `groups` in the form.
4. Testers get an email → install **Firebase App Tester** → download the build.

Workflow is **manual only** (`workflow_dispatch`) so every push does not spam testers.

---

## Tester checklist

1. Accept the App Distribution invite (email).
2. Install **Firebase App Tester** from Play Store.
3. Open the Yolocilin build and install.
4. Confirm analyze works while your HTTPS API/tunnel is up.

---

## Out of scope (later)

- Play Store / production keystore (release currently uses debug signing for internal tests)
- Embedding Firebase Analytics / Crashlytics SDKs (optional; needs `google-services` Gradle plugin)
- Hosting the FastAPI backend on cloud (separate from APK distribution)
