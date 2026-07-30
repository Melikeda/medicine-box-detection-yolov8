#Requires -RunAsAdministrator
<#
  Install and enable everything needed for WSL2 + Docker Desktop.
  Logs to scripts/install-wsl-docker.log
#>

$ErrorActionPreference = "Continue"
$Log = Join-Path $PSScriptRoot "install-wsl-docker.log"
"" | Set-Content $Log

function L($m) {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $m"
    Add-Content $Log $line
    Write-Host $m
}

function FeatureState($name) {
    $o = dism /online /get-featureinfo /featurename:$name 2>&1 | Out-String
    if ($o -match "State : (\w+)") { return $matches[1] }
    return "?"
}

L "=== WSL2 + Docker setup ==="

# Step 1: Enable Windows features
foreach ($feat in @("Microsoft-Windows-Subsystem-Linux", "VirtualMachinePlatform")) {
    $state = FeatureState $feat
    L "$feat => $state"
    if ($state -ne "Enabled") {
        L "Enabling $feat ..."
        dism /online /enable-feature /featurename:$feat /all /norestart 2>&1 | Out-File -Append $Log
        L "$feat => $(FeatureState $feat)"
    }
}

# Step 2: Install WSL via winget
L "Installing Microsoft.WSL via winget ..."
$wslInstall = winget install --id Microsoft.WSL `
    --accept-package-agreements `
    --accept-source-agreements `
    --disable-interactivity 2>&1 | Out-String
Add-Content $Log $wslInstall
L ($wslInstall.Trim())

# Step 3: wsl --install (no distro - Docker brings its own)
L "Running wsl --install --no-distribution ..."
$wslOut = wsl --install --no-distribution 2>&1 | Out-String
Add-Content $Log $wslOut
L ($wslOut.Trim())

L "Running wsl --update ..."
wsl --update 2>&1 | ForEach-Object { L $_ }

L "Setting default WSL version to 2 ..."
wsl --set-default-version 2 2>&1 | ForEach-Object { L $_ }

# Step 4: Start WSL service
$svc = Get-Service WslService -ErrorAction SilentlyContinue
if ($svc) {
    if ($svc.Status -ne "Running") {
        Start-Service WslService
        L "WslService started."
    } else {
        L "WslService already running."
    }
} else {
    L "WslService not found yet (may appear after reboot)."
}

# Step 5: Check WSL status
L "wsl --status:"
$status = wsl --status 2>&1 | Out-String
L $status

function Test-Wsl2Ready {
    param([string]$Status)
    if ($Status -match "enablevirtualization") { return $false }
    if ($Status -match "WSL2") { return $false }
    if ($Status -match "Virtual Machine Platform") { return $false }
    if ($Status -match "Sanal") { return $false }
    if ($Status -match "baslatilam") { return $false }
    if ($Status -match "ba.lat") { return $false }
    return $true
}

$dockerReady = Test-Wsl2Ready -Status $status
$needsReboot = -not $dockerReady -or ((FeatureState "VirtualMachinePlatform") -eq "Disabled")

if ($dockerReady) {
    L "WSL looks ready. Installing Docker Desktop ..."
    $dockerInstall = winget install --id Docker.DockerDesktop `
        --accept-package-agreements `
        --accept-source-agreements `
        --disable-interactivity 2>&1 | Out-String
    Add-Content $Log $dockerInstall
    L ($dockerInstall.Trim())

    $dockerExe = "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe"
    if (Test-Path $dockerExe) {
        L "Starting Docker Desktop ..."
        Start-Process $dockerExe
    }
} else {
    L "WSL not fully ready yet - Docker install deferred until after reboot."
}

L "Feature states:"
L "  WSL=$(FeatureState 'Microsoft-Windows-Subsystem-Linux')"
L "  VMP=$(FeatureState 'VirtualMachinePlatform')"

if ($needsReboot) {
    L "REBOOT REQUIRED. After reboot run: .\scripts\post-reboot-docker.ps1"
} else {
    L "If Docker was installed, wait for 'Engine running' then run: docker compose up --build"
}

L "=== Done ==="
