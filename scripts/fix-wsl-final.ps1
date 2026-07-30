#Requires -RunAsAdministrator
$Log = Join-Path $PSScriptRoot "fix-wsl-final.log"
"" | Set-Content $Log
function L($m){ Add-Content $Log $m; Write-Host $m }

L "=== Final WSL2 fix $(Get-Date) ==="

function GetFeat($n) {
    $o = dism /online /get-featureinfo /featurename:$n 2>&1 | Out-String
    $s = if ($o -match "State : (\w+)") { $matches[1] } else { "?" }
    $r = if ($o -match "Restart Required : (\w+)") { $matches[1] } else { "?" }
    L "$n => State=$s RestartRequired=$r"
    return $s
}

L "BEFORE:"
GetFeat "Microsoft-Windows-Subsystem-Linux" | Out-Null
GetFeat "VirtualMachinePlatform" | Out-Null

# Method 1: DISM
foreach ($f in @("Microsoft-Windows-Subsystem-Linux","VirtualMachinePlatform")) {
    if ((GetFeat $f) -ne "Enabled") {
        L "DISM enable $f ..."
        dism /online /enable-feature /featurename:$f /all /norestart 2>&1 | Out-File -Append $Log
    }
}

# Method 2: OptionalFeature cmdlet (sometimes sticks better)
foreach ($f in @("Microsoft-Windows-Subsystem-Linux","VirtualMachinePlatform")) {
    try {
        $state = (Get-WindowsOptionalFeature -Online -FeatureName $f).State
        L "OptionalFeature $f => $state"
        if ($state -ne "Enabled") {
            L "Enable-WindowsOptionalFeature $f ..."
            Enable-WindowsOptionalFeature -Online -FeatureName $f -All -NoRestart | Out-File -Append $Log
        }
    } catch {
        L "OptionalFeature $f error: $($_.Exception.Message)"
    }
}

# Method 3: wsl --install
L "wsl --install --no-distribution ..."
wsl --install --no-distribution 2>&1 | Out-File -Append $Log

L "AFTER:"
$wsl = GetFeat "Microsoft-Windows-Subsystem-Linux"
$vmp = GetFeat "VirtualMachinePlatform"

L "wsl --status:"
L (wsl --status 2>&1 | Out-String)

if ($wsl -eq "Enabled" -and $vmp -eq "Enabled") {
    L "Both features ENABLED. If wsl still errors, REBOOT once more."
} else {
    L "Features NOT fully enabled. Try manual: Win+R -> optionalfeatures.exe"
}

L "=== Done ==="
