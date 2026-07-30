#Requires -RunAsAdministrator
$LogFile = "c:\Projects\medicine-box-detection-yolov8\scripts\diagnose-wsl.log"
"" | Set-Content $LogFile

function Log($m) { Add-Content $LogFile $m; Write-Host $m }

Log "=== WSL Diagnostic $(Get-Date) ==="

# Pending reboot?
$pending = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending" -ErrorAction SilentlyContinue
Log "RebootPending CBS: $(if($pending){'YES'}else{'no'})"

foreach ($feat in @(
    "Microsoft-Windows-Subsystem-Linux",
    "VirtualMachinePlatform",
    "HypervisorPlatform"
)) {
    $info = dism /online /get-featureinfo /featurename:$feat 2>&1 | Out-String
    $state = if ($info -match "State : (\w+)") { $matches[1] } else { "?" }
    $restart = if ($info -match "Restart Required : (\w+)") { $matches[1] } else { "?" }
    Log "$feat => State=$state RestartRequired=$restart"
}

Log "--- Services ---"
foreach ($s in @("WslService","LxssManager","vmcompute","HvHost")) {
    $svc = Get-Service -Name $s -ErrorAction SilentlyContinue
    if ($svc) { Log "$s : $($svc.Status)" } else { Log "$s : NOT FOUND" }
}

Log "--- wsl.exe ---"
if (Test-Path "$env:WINDIR\System32\wsl.exe") {
    Log "wsl.exe exists"
} else {
    Log "wsl.exe MISSING"
}

Log "--- wsl --status (15s timeout) ---"
$job = Start-Job { & wsl.exe --status 2>&1 | Out-String }
if (Wait-Job $job -Timeout 15) {
    Log (Receive-Job $job)
} else {
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -Force -ErrorAction SilentlyContinue
    Log "TIMEOUT - WSL not responding"
}

Log "--- bcdedit hypervisor ---"
Log (bcdedit /enum "{current}" 2>&1 | Select-String -Pattern "hypervisor")

Log "=== Done ==="
