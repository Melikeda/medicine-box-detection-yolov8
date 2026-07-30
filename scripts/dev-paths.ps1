# Shared development tool paths (D: drive layout).
# Used by env-flutter.ps1, install-flutter-path.ps1, migrate-dev-to-d.ps1

$script:DevRoot = "D:\dev"
$script:FlutterHome = Join-Path $DevRoot "flutter"
$script:AndroidHome = Join-Path $DevRoot "android-sdk"
$script:AndroidAvdHome = Join-Path $DevRoot "android-avd"
$script:GradleHome = Join-Path $DevRoot "gradle"
$script:PubCacheHome = Join-Path $DevRoot "pub-cache"
$script:JavaHome = "C:\Program Files\Microsoft\jdk-17.0.20.8-hotspot"

# Legacy C: locations (pre-migration)
$script:LegacyFlutterHome = "C:\src\flutter"
$script:LegacyAndroidHome = Join-Path $env:LOCALAPPDATA "Android\Sdk"
$script:LegacyAvdHome = Join-Path $env:USERPROFILE ".android\avd"
$script:LegacyGradleHome = Join-Path $env:USERPROFILE ".gradle"
$script:LegacyPubCache = Join-Path $env:LOCALAPPDATA "Pub\Cache"
