# Emulatore ornek ilac kutusu fotograflarini galeriye kopyalar.
# Kullanim: .\scripts\push-samples-to-emulator.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$SamplesDir = Join-Path $RepoRoot "data\samples"
$EnvScript = Join-Path $RepoRoot "scripts\env-flutter.ps1"

. $EnvScript

$device = adb devices | Select-String "emulator-\d+\s+device"
if (-not $device) {
    Write-Host "Bagli emulatore/cihaz bulunamadi. Once emulatore baslatin:" -ForegroundColor Yellow
    Write-Host "  flutter emulators --launch medicine_box_emulator"
    exit 1
}

$targetDir = "/sdcard/Pictures/medicine-samples"
adb shell "mkdir -p $targetDir"

$images = Get-ChildItem -Path $SamplesDir -File | Where-Object { $_.Extension -match '^\.(jpg|jpeg|png)$' }
if ($images.Count -eq 0) {
    Write-Host "Ornek gorsel bulunamadi: $SamplesDir" -ForegroundColor Red
    exit 1
}

foreach ($image in $images) {
    Write-Host "Aktariliyor: $($image.Name)"
    adb push $image.FullName "$targetDir/$($image.Name)" | Out-Null
}

# Galerinin yeni dosyalari gormesi icin medya taramasi
adb shell "am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://$targetDir" | Out-Null
adb shell "content call --uri content://media/external/images/media --method scan_volume --arg external_primary" 2>$null | Out-Null

Write-Host ""
Write-Host "$($images.Count) fotograf emulatore yuklendi." -ForegroundColor Green
Write-Host "Galeri uygulamasini acin -> Pictures -> medicine-samples"
Write-Host "Uygulamada 'Galeriden Sec' ile bu fotograflari secebilirsiniz."
