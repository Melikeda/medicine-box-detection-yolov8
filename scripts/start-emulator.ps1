# Android emulator — stabil baslatma (Intel GPU / System UI donmasi icin).
# Kullanim:
#   powershell -ExecutionPolicy Bypass -File scripts/start-emulator.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/start-emulator.ps1 -ColdBoot
#   powershell -ExecutionPolicy Bypass -File scripts/start-emulator.ps1 -WipeData

param(
    [string]$AvdName = "medicine_box_emulator",
    [switch]$ColdBoot,
    [switch]$WipeData,
    [switch]$Restart
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "env-flutter.ps1")

$emulatorExe = Join-Path $env:ANDROID_HOME "emulator\emulator.exe"
if (-not (Test-Path $emulatorExe)) {
    Write-Error "emulator.exe bulunamadi: $emulatorExe"
}

$configIni = Join-Path $env:ANDROID_AVD_HOME "$AvdName.avd\config.ini"
if (Test-Path $configIni) {
    $lines = Get-Content $configIni
    $updated = $false
    $newLines = foreach ($line in $lines) {
        if ($line -match '^hw\.gpu\.enabled\s*=') {
            $updated = $true
            "hw.gpu.enabled = yes"
        }
        elseif ($line -match '^hw\.gpu\.mode\s*=') {
            $updated = $true
            "hw.gpu.mode = angle_indirect"
        }
        else {
            $line
        }
    }
    if ($updated) {
        Set-Content -Path $configIni -Value $newLines -Encoding UTF8
        Write-Host "AVD GPU ayarlari guncellendi (angle_indirect)." -ForegroundColor Cyan
    }
}

if ($Restart) {
    Get-Process -Name "qemu-system*","emulator" -ErrorAction SilentlyContinue |
        Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

$running = Get-Process -Name "qemu-system-x86_64" -ErrorAction SilentlyContinue
if ($running -and -not $Restart -and -not $WipeData) {
    Write-Host "Emulator zaten calisiyor (PID $($running.Id)). Pencereyi gorev cubugundan acin." -ForegroundColor Yellow
    Write-Host "Yeniden baslatmak icin: -Restart parametresi ekleyin."
    exit 0
}

$args = @("-avd", $AvdName, "-gpu", "angle_indirect")
if ($ColdBoot -or $WipeData) {
    $args += "-no-snapshot-load"
}
if ($WipeData) {
    $args += "-wipe-data"
    Write-Host "UYARI: Emulatör verisi silinecek (temiz kurulum)." -ForegroundColor Yellow
}

Write-Host "Emulator baslatiliyor: $AvdName" -ForegroundColor Green
Write-Host "  GPU: angle_indirect | Pencereyi KAPATMAYIN (X ile kapatirsaniz tum oturum biter)."
Write-Host ""

Start-Process -FilePath $emulatorExe -ArgumentList $args -WorkingDirectory (Split-Path $emulatorExe)

Write-Host "Acilis 30-90 sn surebilir. Hazir olunca:" -ForegroundColor Green
Write-Host "  flutter devices"
Write-Host "  cd mobile; flutter run -d emulator-5554"
