# CodeDoc uninstaller for Windows
# removes the install dir, the launcher and the user PATH entry

$ErrorActionPreference = "Stop"

$App = "codedoc"
$InstallDir = Join-Path $env:LOCALAPPDATA $App
$BinDir = Join-Path $InstallDir "bin"

if (Test-Path $InstallDir) {
    Remove-Item $InstallDir -Recurse -Force
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath) {
    $newPath = ($userPath -split ';' | Where-Object { $_ -ne $BinDir }) -join ';'
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
}

Write-Host "$App uninstalled"