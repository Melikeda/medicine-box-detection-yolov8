# Permanently add Flutter/Android/Java to the current user's PATH (Windows).
# Run once after initial setup: .\scripts\install-flutter-path.ps1

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "dev-paths.ps1")

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

$entries = @(
    (Join-Path $FlutterHome "bin"),
    (Join-Path $JavaHome "bin"),
    (Join-Path $AndroidHome "platform-tools"),
    (Join-Path $AndroidHome "cmdline-tools\latest\bin"),
    (Join-Path $AndroidHome "emulator")
)

$legacyEntries = @(
    (Join-Path $LegacyFlutterHome "bin"),
    (Join-Path $LegacyAndroidHome "platform-tools"),
    (Join-Path $LegacyAndroidHome "cmdline-tools\latest\bin"),
    (Join-Path $LegacyAndroidHome "emulator")
)

# Drop legacy C: paths
$parts = $userPath -split ';' | Where-Object { $_ -and ($_ -notin $legacyEntries) }

foreach ($entry in $entries) {
    if (-not (Test-Path $entry)) {
        Write-Warning "Path not found, skipping: $entry"
        continue
    }
    if ($parts -notcontains $entry) {
        $parts += $entry
        Write-Host "Added to PATH: $entry" -ForegroundColor Green
    } else {
        Write-Host "Already in PATH: $entry"
    }
}

[Environment]::SetEnvironmentVariable("Path", ($parts -join ';'), "User")
[Environment]::SetEnvironmentVariable("FLUTTER_HOME", $FlutterHome, "User")
[Environment]::SetEnvironmentVariable("JAVA_HOME", $JavaHome, "User")
[Environment]::SetEnvironmentVariable("ANDROID_HOME", $AndroidHome, "User")
[Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $AndroidHome, "User")
[Environment]::SetEnvironmentVariable("ANDROID_AVD_HOME", $AndroidAvdHome, "User")
[Environment]::SetEnvironmentVariable("GRADLE_USER_HOME", $GradleHome, "User")
[Environment]::SetEnvironmentVariable("PUB_CACHE", $PubCacheHome, "User")

Write-Host ""
Write-Host "User environment variables updated (D: dev layout)." -ForegroundColor Green
Write-Host "Open a new terminal for PATH changes to take effect globally."
