# CodeDoc installer for Windows
#
# usage:
#   powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/vortex3964/CodeDoc/main/install/install.ps1 | iex"

$ErrorActionPreference = "Stop"

$App = "codedoc"
$Repo = "vortex3964/CodeDoc"
$Branch = "main"

$InstallDir = Join-Path $env:LOCALAPPDATA $App
$BinDir = Join-Path $InstallDir "bin"
$Launcher = Join-Path $BinDir "$App.cmd"

# check for python3 or the py launcher
$python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) {
    Write-Error "$App requires Python 3.10 or newer, install it from https://www.python.org/downloads/"
    exit 1
}
$pyVer = & $python.Source --version 2>&1
if ($pyVer -match "Python (\d+)\.(\d+)") {
    if ([int]$Matches[1] -lt 3 -or ([int]$Matches[1] -eq 3 -and [int]$Matches[2] -lt 10)) {
        Write-Error "$App requires Python 3.10 or newer, found $pyVer"
        exit 1
    }
}

$tmpDir = Join-Path $env:TEMP "$App-install-$PID"
New-Item -ItemType Directory -Path $tmpDir | Out-Null
try {
    $tarball = Join-Path $tmpDir "$App.tar.gz"
    $url = "https://github.com/$Repo/archive/refs/heads/$Branch.tar.gz"
    Write-Host "downloading $App from $url"
    Invoke-WebRequest -Uri $url -OutFile $tarball
    tar -xzf $tarball -C $tmpDir

    $top = Get-ChildItem $tmpDir -Directory | Select-Object -First 1
    if (-not $top) { throw "failed to extract the archive" }

    if (Test-Path $InstallDir) { Remove-Item $InstallDir -Recurse -Force }
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
    Copy-Item (Join-Path $top.FullName "*") $InstallDir -Recurse -Force

    # remember the commit this install came from so "codedoc --update"
    # can report "already up to date", fails silently on no network
    try {
        $sha = (Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/commits/$Branch" -TimeoutSec 10).sha
        if ($sha) { Set-Content -Path (Join-Path $InstallDir ".commit") -Value $sha }
    } catch {
        # no stamp, the first codedoc --update will fetch the latest
    }

    # write the launcher, it tries python3 first and falls back to the py launcher
    New-Item -ItemType Directory -Path $BinDir | Out-Null
    $launcherBody = "@echo off`r`nwhere python3 >nul 2>&1 && (python3 `"$InstallDir\main.py`" %*) || (py -3 `"$InstallDir\main.py`" %*)"
    Set-Content -Path $Launcher -Value $launcherBody -Encoding ASCII

    # add the bin dir to the user PATH
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$BinDir*") {
        $newPath = if ($userPath) { "$userPath;$BinDir" } else { $BinDir }
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "added $BinDir to the user PATH"
    }

    Write-Host ""
    Write-Host "$App installed!"
    Write-Host "install dir: $InstallDir"
    Write-Host "open a new terminal and run: codedoc . -o out"
}
finally {
    Remove-Item $tmpDir -Recurse -Force -ErrorAction SilentlyContinue
}