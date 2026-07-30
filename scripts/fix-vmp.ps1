#Requires -RunAsAdministrator
$LogFile = Join-Path $PSScriptRoot "fix-vmp.log"
"" | Set-Content $LogFile
function Log($m){ Add-Content $LogFile $m; Write-Host $m }

Log "=== Enable Virtual Machine Platform ==="

Log "Enabling VirtualMachinePlatform ..."
dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart 2>&1 | Out-File -Append $LogFile

Log "Enabling Microsoft-Windows-Subsystem-Linux ..."
dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart 2>&1 | Out-File -Append $LogFile

$vmp = dism /online /get-featureinfo /featurename:VirtualMachinePlatform 2>&1 | Out-String
Log $vmp

Log "Running: wsl --install --no-distribution"
wsl --install --no-distribution 2>&1 | Out-File -Append $LogFile

$svc = Get-Service WslService -ErrorAction SilentlyContinue
if ($svc) {
    if ($svc.Status -ne "Running") {
        Start-Service WslService
        Log "WslService started."
    } else {
        Log "WslService already running."
    }
}

Log "wsl --status:"
Log (wsl --status 2>&1 | Out-String)

$needsReboot = $vmp -match "Restart Required : Yes"
if ($needsReboot -or ($vmp -match "State : Disabled")) {
    Log "REBOOT REQUIRED to activate Virtual Machine Platform."
} else {
    Log "VMP enabled. Starting Docker Desktop ..."
    $docker = "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe"
    if (Test-Path $docker) { Start-Process $docker }
}

Log "=== Done ==="
