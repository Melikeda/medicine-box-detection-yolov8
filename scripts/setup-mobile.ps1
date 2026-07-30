Param(
    [switch]$RegeneratePlatforms
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$MobileDir = Join-Path $RepoRoot "mobile"
$EnvScript = Join-Path $RepoRoot "scripts\env-flutter.ps1"

if (-not (Test-Path $EnvScript)) {
    Write-Host "env-flutter.ps1 bulunamadi. Once Flutter SDK kurulumunu tamamlayin." -ForegroundColor Red
    exit 1
}

. $EnvScript

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    Write-Host "Flutter SDK bulunamadi." -ForegroundColor Yellow
    Write-Host "Kurulum: https://docs.flutter.dev/get-started/install/windows"
    Write-Host "Ardindan: . .\scripts\env-flutter.ps1"
    exit 1
}

Push-Location $MobileDir
try {
    if ($RegeneratePlatforms) {
        Write-Host "Android platform dosyalari yeniden olusturuluyor..."
        flutter create . --project-name medicine_box_app --org com.medicinebox --platforms=android
    }

    Write-Host "Bagimliliklar indiriliyor..."
    flutter pub get

    Write-Host "Analiz calistiriliyor..."
    flutter analyze

    Write-Host ""
    Write-Host "Hazir. Calistirmak icin:" -ForegroundColor Green
    Write-Host "  . .\scripts\env-flutter.ps1"
    Write-Host "  cd mobile"
    Write-Host "  flutter emulators --launch medicine_box_emulator"
    Write-Host "  flutter run"
}
finally {
    Pop-Location
}
