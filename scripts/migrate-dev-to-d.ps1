# Migrate Flutter/Android toolchain from C: to D:\dev and update env vars.
# Run once (close emulator/flutter first): .\scripts\migrate-dev-to-d.ps1

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "dev-paths.ps1")

Write-Host "=== Migrate dev tools to D: ===" -ForegroundColor Cyan
Write-Host "Target: $DevRoot"

function Move-DevTree {
    param([string]$Source, [string]$Dest)
    if (-not (Test-Path $Source)) {
        Write-Host "  skip (missing): $Source"
        return
    }
    if (Test-Path $Dest) {
        $destSize = (Get-ChildItem $Dest -Recurse -ErrorAction SilentlyContinue |
            Measure-Object -Property Length -Sum).Sum
        if ($destSize -gt 0) {
            Write-Host "  skip (dest not empty): $Dest"
            return
        }
        Remove-Item $Dest -Recurse -Force
    }
    $parent = Split-Path $Dest -Parent
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    Write-Host "  move: $Source -> $Dest"
    Move-Item -Path $Source -Destination $Dest -Force
}

New-Item -ItemType Directory -Force -Path $DevRoot | Out-Null

Move-DevTree -Source $LegacyFlutterHome -Dest $FlutterHome
Move-DevTree -Source $LegacyAndroidHome -Dest $AndroidHome
Move-DevTree -Source $LegacyAvdHome -Dest $AndroidAvdHome
Move-DevTree -Source $LegacyGradleHome -Dest $GradleHome
Move-DevTree -Source $LegacyPubCache -Dest $PubCacheHome

# Fix AVD .ini path references after move
if (Test-Path $AndroidAvdHome) {
    Get-ChildItem $AndroidAvdHome -Filter "*.ini" -ErrorAction SilentlyContinue | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        $updated = $content -replace [regex]::Escape($LegacyAvdHome), ($AndroidAvdHome -replace '\\', '\\')
        $updated = $updated -replace 'path=C:\\Users\\[^\\]+\\.android\\avd', "path=$($AndroidAvdHome -replace '\\','\\')"
        if ($updated -ne $content) {
            Set-Content -Path $_.FullName -Value $updated -NoNewline
            Write-Host "  fixed AVD ini: $($_.Name)"
        }
    }
}

# Update mobile local.properties sdk.dir
$localProps = Join-Path (Split-Path $PSScriptRoot -Parent) "mobile\android\local.properties"
if (Test-Path $localProps) {
    $lines = Get-Content $localProps
    $newLines = $lines | ForEach-Object {
        if ($_ -match '^sdk\.dir=') { "sdk.dir=$($AndroidHome -replace '\\','\\')" } else { $_ }
    }
    if ($newLines -notmatch '^sdk\.dir=') {
        $newLines += "sdk.dir=$($AndroidHome -replace '\\','\\')"
    }
    Set-Content -Path $localProps -Value $newLines
    Write-Host "  updated mobile/android/local.properties"
}

# User environment variables
$env:FLUTTER_HOME = $FlutterHome
$env:JAVA_HOME = $JavaHome
$env:ANDROID_HOME = $AndroidHome
$env:ANDROID_SDK_ROOT = $AndroidHome
$env:ANDROID_AVD_HOME = $AndroidAvdHome
$env:GRADLE_USER_HOME = $GradleHome
$env:PUB_CACHE = $PubCacheHome

[Environment]::SetEnvironmentVariable("FLUTTER_HOME", $FlutterHome, "User")
[Environment]::SetEnvironmentVariable("JAVA_HOME", $JavaHome, "User")
[Environment]::SetEnvironmentVariable("ANDROID_HOME", $AndroidHome, "User")
[Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $AndroidHome, "User")
[Environment]::SetEnvironmentVariable("ANDROID_AVD_HOME", $AndroidAvdHome, "User")
[Environment]::SetEnvironmentVariable("GRADLE_USER_HOME", $GradleHome, "User")
[Environment]::SetEnvironmentVariable("PUB_CACHE", $PubCacheHome, "User")

# Rebuild user PATH — remove legacy entries, add D: entries
$pathEntries = @(
    (Join-Path $FlutterHome "bin"),
    (Join-Path $JavaHome "bin"),
    (Join-Path $AndroidHome "platform-tools"),
    (Join-Path $AndroidHome "cmdline-tools\latest\bin"),
    (Join-Path $AndroidHome "emulator")
)
$legacyPathEntries = @(
    (Join-Path $LegacyFlutterHome "bin"),
    (Join-Path $LegacyAndroidHome "platform-tools"),
    (Join-Path $LegacyAndroidHome "cmdline-tools\latest\bin"),
    (Join-Path $LegacyAndroidHome "emulator")
)

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$parts = $userPath -split ';' | Where-Object { $_ -and ($_ -notin $legacyPathEntries) }
foreach ($entry in $pathEntries) {
    if ((Test-Path $entry) -and ($parts -notcontains $entry)) {
        $parts += $entry
    }
}
[Environment]::SetEnvironmentVariable("Path", ($parts -join ';'), "User")

Write-Host ""
Write-Host "Migration complete." -ForegroundColor Green
Write-Host "  FLUTTER_HOME=$FlutterHome"
Write-Host "  ANDROID_HOME=$AndroidHome"
Write-Host "  ANDROID_AVD_HOME=$AndroidAvdHome"
Write-Host "  GRADLE_USER_HOME=$GradleHome"
Write-Host ""
Write-Host "Open a new terminal, then run:"
Write-Host "  . .\scripts\env-flutter.ps1"
Write-Host "  flutter doctor"
