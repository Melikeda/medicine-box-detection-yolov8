#Requires -RunAsAdministrator
<#
  Run once after reboot to finish WSL + Docker setup.
  Usage (elevated PowerShell):
    .\scripts\post-reboot-docker.ps1
#>

$ErrorActionPreference = "Continue"
$LogFile = Join-Path $PSScriptRoot "post-reboot-docker.log"

function Write-Log([string]$Message) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Add-Content -Path $LogFile -Value $line
    Write-Host $Message
}

function Test-Wsl2Ready {
    $status = wsl --status 2>&1 | Out-String
    if ($status -match "WSL2 ba") { return $false }
    if ($status -match "WSL2 baslatilamiyor") { return $false }
    if ($status -match "Sanal Makine Platformu") { return $false }
    if ($status -match "Virtual Machine Platform") { return $false }
    if ($status -match "enablevirtualization") { return $false }
    return $true
}

function Enable-WslWindowsFeatures {
    Write-Log "Enabling Windows optional features (DISM) ..."
    foreach ($feat in @("Microsoft-Windows-Subsystem-Linux", "VirtualMachinePlatform")) {
        dism /online /enable-feature /featurename:$feat /all /norestart 2>&1 | Out-Null
    }
    wsl --install --no-distribution 2>&1 | ForEach-Object { Write-Log $_ }
}

"" | Set-Content -Path $LogFile
Write-Log "=== Post-reboot Docker setup ==="

Write-Log "WSL status:"
$wslStatus = wsl --status 2>&1 | Out-String
Write-Log $wslStatus

if (-not (Test-Wsl2Ready)) {
    Write-Host ""
    Write-Host "HATA: WSL2 henuz hazir degil (Sanal Makine Platformu aktif degil)." -ForegroundColor Red
    Write-Host ""
    Write-Log "WSL2 not ready - attempting feature enable ..."
    Enable-WslWindowsFeatures

    Write-Log "WSL status after enable attempt:"
    Write-Log (wsl --status 2>&1 | Out-String)

    if (-not (Test-Wsl2Ready)) {
        Write-Host "Asagidaki adimlari sirayla uygulayin:" -ForegroundColor Yellow
        Write-Host "  1. Win+R -> optionalfeatures.exe -> Enter"
        Write-Host "     [x] Windows Subsystem for Linux"
        Write-Host "     [x] Virtual Machine Platform"
        Write-Host "     Tamam -> bilgisayari YENIDEN BASLAT"
        Write-Host ""
        Write-Host "  2. Hizli baslangici kapat (tam reboot icin):"
        Write-Host "     Denetim Masasi -> Guc secenekleri -> Guc dugmeleri"
        Write-Host "     'Hizli baslangici etkinlestir' isaretini KALDIR"
        Write-Host ""
        Write-Host "  3. Yeniden baslatma icin (Yonetici PowerShell):"
        Write-Host "     shutdown /r /t 0"
        Write-Host ""
        Write-Host "  4. Reboot sonrasi tekrar:"
        Write-Host "     .\scripts\post-reboot-docker.ps1"
        Write-Host ""
        Write-Host "  BIOS (Huawei): Virtualization Technology -> Enabled"
        Write-Host "  https://aka.ms/enablevirtualization"
        Write-Log "ABORT: WSL2 prerequisites missing."
        exit 1
    }
}

Write-Log "Updating WSL ..."
wsl --update 2>&1 | ForEach-Object { Write-Log $_ }
wsl --set-default-version 2 2>&1 | ForEach-Object { Write-Log $_ }

$dockerExe = "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe"
if (Test-Path $dockerExe) {
    Write-Log "Starting Docker Desktop ..."
    Start-Process -FilePath $dockerExe
} else {
    Write-Log "ERROR: Docker Desktop not found at $dockerExe"
    exit 1
}

Write-Log "Waiting for Docker engine (up to 3 minutes) ..."
$ready = $false
for ($i = 1; $i -le 36; $i++) {
    Start-Sleep -Seconds 5
    $out = docker info 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0 -and $out -match "Server:") {
        Write-Log "Docker engine is running."
        $ready = $true
        break
    }
    Write-Log "  attempt $i/36 ..."
}

if (-not $ready) {
    Write-Log "ERROR: Docker engine did not start. WSL2/VMP may still be inactive."
    Write-Host "Docker engine baslamadi. Docker Desktop penceresindeki hatayi kontrol edin." -ForegroundColor Red
    exit 1
}

$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
Write-Log "Project: $projectRoot"

$modelPath = Join-Path $projectRoot "runs\detect\runs\detect\medicine_box_yolov8n-2\weights\best.pt"
if (-not (Test-Path $modelPath)) {
    Write-Log "WARN: YOLO model missing at $modelPath"
    Write-Log "Train or copy best.pt before running docker compose."
} else {
    Write-Log "Building and starting containers ..."
    docker compose up --build -d 2>&1 | ForEach-Object { Write-Log $_ }
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Containers started. Test: curl http://127.0.0.1:8000/health"
    } else {
        Write-Log "docker compose failed with exit code $LASTEXITCODE"
    }
}

Write-Log "=== Done ==="
