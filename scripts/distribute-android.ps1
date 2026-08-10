<#
.SYNOPSIS
  Build a Yolocilin release APK and upload it to Firebase App Distribution.

.DESCRIPTION
  Release builds require an HTTPS API_BASE_URL (cleartext is blocked).
  Start your FastAPI server and an HTTPS tunnel (Cloudflare Tunnel / ngrok)
  before running this script, then pass that URL as -ApiBaseUrl.

.PARAMETER ApiBaseUrl
  Public HTTPS base URL baked into the APK (e.g. https://xxxx.trycloudflare.com).

.PARAMETER FirebaseAppId
  Firebase Android App ID (1:…:android:…). Falls back to env FIREBASE_APP_ID.

.PARAMETER Groups
  Comma-separated App Distribution groups (default: testers).

.PARAMETER ReleaseNotes
  Notes shown to testers in Firebase App Tester.

.PARAMETER SkipUpload
  Only build the APK; do not call Firebase CLI.

.EXAMPLE
  .\scripts\distribute-android.ps1 -ApiBaseUrl "https://abc.trycloudflare.com" -FirebaseAppId "1:123:android:abc"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $ApiBaseUrl,

    [Parameter(Mandatory = $false)]
    [string] $FirebaseAppId = $env:FIREBASE_APP_ID,

    [Parameter(Mandatory = $false)]
    [string] $Groups = "testers",

    [Parameter(Mandatory = $false)]
    [string] $ReleaseNotes = "Yolocilin Android test build",

    [Parameter(Mandatory = $false)]
    [switch] $SkipUpload
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$mobileDir = Join-Path $repoRoot "mobile"
$apkPath = Join-Path $mobileDir "build\app\outputs\flutter-apk\app-release.apk"

if (-not $ApiBaseUrl.StartsWith("https://", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "ApiBaseUrl must start with https:// (release APK blocks cleartext HTTP)."
}

if (-not (Test-Path (Join-Path $mobileDir "pubspec.yaml"))) {
    throw "mobile/pubspec.yaml not found. Run from the Yolocilin repo."
}

Write-Host "==> flutter pub get"
Push-Location $mobileDir
try {
    flutter pub get
    Write-Host "==> flutter analyze"
    flutter analyze
    Write-Host "==> flutter build apk --release"
    flutter build apk --release --dart-define="API_BASE_URL=$ApiBaseUrl"
}
finally {
    Pop-Location
}

if (-not (Test-Path $apkPath)) {
    throw "APK not found at $apkPath"
}

Write-Host "APK ready: $apkPath"

if ($SkipUpload) {
    Write-Host "SkipUpload set — not uploading to Firebase."
    return
}

if ([string]::IsNullOrWhiteSpace($FirebaseAppId)) {
    throw "FirebaseAppId is required (pass -FirebaseAppId or set env FIREBASE_APP_ID)."
}

$firebase = Get-Command firebase -ErrorAction SilentlyContinue
if (-not $firebase) {
    throw "firebase CLI not found. Install with: npm i -g firebase-tools && firebase login"
}

Write-Host "==> firebase appdistribution:distribute"
& firebase appdistribution:distribute $apkPath `
    --app $FirebaseAppId `
    --groups $Groups `
    --release-notes $ReleaseNotes

Write-Host "Done. Testers should open Firebase App Tester and install the new build."
