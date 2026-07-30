#Requires -RunAsAdministrator
<#
  Install WSL via winget + enable Windows features.
  Use when DISM enable reverts after reboot ("changes could not be completed").
#>

$LogFile = Join-Path $PSScriptRoot "fix-wsl-winget.log"
$ErrorActionPreference = "Continue"

function Log([string]$Message) {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $Message"
    Add-Content -Path $LogFile -Value $line
    Write-Host $Message
}

"" | Set-Content -Path $LogFile
Log "=== WSL winget install fix ==="

function FeatureState([string]$Name) {
    $info = dism /online /get-featureinfo /featurename:$Name 2>&1 | Out-String
    if ($info -match "State : (\w+)") { return $matches[1] }
    return "?"
}

Log "Before: WSL=$(FeatureState 'Microsoft-Windows-Subsystem-Linux') VMP=$(FeatureState 'VirtualMachinePlatform')"

foreach ($feat in @("Microsoft-Windows-Subsystem-Linux", "VirtualMachinePlatform")) {
    if ((FeatureState $feat) -ne "Enabled") {
        Log "DISM enabling $feat ..."
        dism /online /enable-feature /featurename:$feat /all /norestart 2>&1 | Out-File -Append $LogFile
    }
}

Log "Installing/upgrading WSL via winget (Microsoft.WSL) ..."
$wingetOut = winget install --id Microsoft.WSL `
    --accept-package-agreements `
    --accept-source-agreements `
    --disable-interactivity 2>&1 | Out-String
Add-Content -Path $LogFile -Value $wingetOut
Log $wingetOut

Log "After DISM: WSL=$(FeatureState 'Microsoft-Windows-Subsystem-Linux') VMP=$(FeatureState 'VirtualMachinePlatform')"

Log "Running wsl --update ..."
$job = Start-Job { wsl --update 2>&1 | Out-String }
if (Wait-Job $job -Timeout 120) {
    Log (Receive-Job $job)
} else {
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -Force -ErrorAction SilentlyContinue
    Log "wsl --update timed out (may need reboot first)"
}

Log "Services:"
foreach ($s in @("WslService", "LxssManager")) {
    $svc = Get-Service -Name $s -ErrorAction SilentlyContinue
    Log "  $s : $(if($svc){$svc.Status}else{'NOT FOUND'})"
}

Log "wsl --status:"
$job2 = Start-Job { wsl --status 2>&1 | Out-String }
if (Wait-Job $job2 -Timeout 20) {
    Log (Receive-Job $job2)
} else {
    Stop-Job $job2 -ErrorAction SilentlyContinue
    Remove-Job $job2 -Force -ErrorAction SilentlyContinue
    Log "  TIMEOUT"
}

$dockerExe = "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe"
if (Test-Path $dockerExe) {
    Log "Starting Docker Desktop ..."
    Start-Process -FilePath $dockerExe
}

Log "=== Finished ==="
Log "If wsl --status still fails: RESTART once more, then run scripts/post-reboot-docker.ps1"
