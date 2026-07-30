#Requires -RunAsAdministrator
<#
  Full WSL2 + Docker Desktop repair for Windows.
  Writes progress to scripts/fix-docker-wsl.log
#>

$LogFile = Join-Path $PSScriptRoot "fix-docker-wsl.log"
$ErrorActionPreference = "Continue"

function Write-Log {
    param([string]$Message)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Add-Content -Path $LogFile -Value $line
    Write-Host $Message
}

"" | Set-Content -Path $LogFile
Write-Log "=== WSL/Docker repair started ==="

function Get-FeatureState {
    param([string]$FeatureName)
    $info = dism /online /get-featureinfo /featurename:$FeatureName 2>&1 | Out-String
    if ($info -match "State : Enabled") { return "Enabled" }
    if ($info -match "State : Disabled") { return "Disabled" }
    return "Unknown"
}

function Enable-FeatureIfNeeded {
    param([string]$FeatureName)

    $state = Get-FeatureState -FeatureName $FeatureName
    Write-Log "$FeatureName : $state"

    if ($state -eq "Enabled") {
        return $false
    }

    Write-Log "Enabling $FeatureName ..."
    $result = dism /online /enable-feature /featurename:$FeatureName /all /norestart 2>&1 | Out-String
    Add-Content -Path $LogFile -Value $result
    Write-Log "$FeatureName enable requested."
    return $true
}

$needsReboot = $false
$needsReboot = (Enable-FeatureIfNeeded "Microsoft-Windows-Subsystem-Linux") -or $needsReboot
$needsReboot = (Enable-FeatureIfNeeded "VirtualMachinePlatform") -or $needsReboot
$needsReboot = (Enable-FeatureIfNeeded "HypervisorPlatform") -or $needsReboot

Write-Log "Feature states after enable:"
Write-Log "  WSL: $(Get-FeatureState 'Microsoft-Windows-Subsystem-Linux')"
Write-Log "  VMP: $(Get-FeatureState 'VirtualMachinePlatform')"
Write-Log "  HypervisorPlatform: $(Get-FeatureState 'HypervisorPlatform')"

if ($needsReboot) {
    Write-Log "REBOOT REQUIRED before WSL commands will work."
} else {
    Write-Log "All features already enabled. Proceeding with WSL setup ..."

    $job = Start-Job { wsl --update 2>&1 | Out-String }
    if (Wait-Job $job -Timeout 60) {
        Write-Log (Receive-Job $job)
    } else {
        Stop-Job $job -Force
        Remove-Job $job -Force
        Write-Log "WARN: wsl --update timed out after 60s"
    }

    $job2 = Start-Job { wsl --set-default-version 2 2>&1 | Out-String }
    if (Wait-Job $job2 -Timeout 30) {
        Write-Log (Receive-Job $job2)
    } else {
        Stop-Job $job2 -Force
        Remove-Job $job2 -Force
        Write-Log "WARN: wsl --set-default-version timed out"
    }

    $job3 = Start-Job { wsl --status 2>&1 | Out-String }
    if (Wait-Job $job3 -Timeout 15) {
        Write-Log "wsl --status:`n$(Receive-Job $job3)"
    } else {
        Stop-Job $job3 -Force
        Remove-Job $job3 -Force
        Write-Log "WARN: wsl --status timed out - WSL service may still be broken"
    }
}

# Start WSL service if present
foreach ($svcName in @("WslService", "LxssManager")) {
    $svc = Get-Service -Name $svcName -ErrorAction SilentlyContinue
    if ($null -eq $svc) {
        Write-Log "Service $svcName not found."
        continue
    }
    if ($svc.Status -ne "Running") {
        Write-Log "Starting service $svcName ..."
        try {
            Start-Service $svcName -ErrorAction Stop
            Write-Log "$svcName started."
        } catch {
            Write-Log "Failed to start ${svcName}: $($_.Exception.Message)"
        }
    } else {
        Write-Log "$svcName already running."
    }
}

# Launch Docker Desktop (per-user install path on this machine)
$dockerCandidates = @(
    "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe",
    "$env:LOCALAPPDATA\Programs\Docker\Docker\Docker Desktop.exe",
    "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
)
$dockerExe = $dockerCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (Test-Path $dockerExe) {
    Write-Log "Starting Docker Desktop ..."
    Start-Process -FilePath $dockerExe
    Write-Log "Docker Desktop launch requested."
} else {
    Write-Log "Docker Desktop executable not found."
}

Write-Log "=== Repair finished ==="
if ($needsReboot) {
    Write-Log "ACTION: Restart Windows, then run this script again OR open Docker Desktop manually."
}
