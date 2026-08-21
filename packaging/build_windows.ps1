# Build the CareScribe Windows desktop app.
#
#   powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
#
# Produces dist\CareScribe\CareScribe.exe — the file a clinician double-clicks.
# Set $env:CARESCRIBE_BUNDLE_MODEL = "0" to build without the ~2 GB model.

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "Installing build dependencies..."
python -m pip install --quiet pyinstaller pywebview psutil
python -m pip install --quiet llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

Write-Host "Generating icon..."
python packaging\make_icon.py

Write-Host "Building..."
python -m PyInstaller packaging\carescribe.spec --noconfirm --clean

$exe = "dist\CareScribe\CareScribe.exe"
if (-not (Test-Path $exe)) { throw "Build failed: $exe not found" }
Write-Host "Built $exe"

# ---------------------------------------------------------------------------
# Code signing. UNSIGNED BUILDS TRIGGER A SMARTSCREEN WARNING.
#
# A clinician who sees "Windows protected your PC" will not click through, and
# should not be trained to. Sign with an OV or EV certificate:
#
#   signtool sign /fd SHA256 /a /tr http://timestamp.digicert.com /td SHA256 `
#       dist\CareScribe\CareScribe.exe
#
# An EV certificate clears SmartScreen immediately; an OV certificate needs
# reputation to accumulate first.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Installer. Inno Setup 6 is a one-time install:
#     winget install -e --id JRSoftware.InnoSetup
# ---------------------------------------------------------------------------
$iscc = @(
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($iscc) {
    Write-Host "Compiling installer..."
    & $iscc packaging\carescribe.iss
    $setup = "packaging\Output\CareScribeSetup.exe"
    if (Test-Path $setup) { Write-Host "Built $setup" }
} else {
    Write-Host "Inno Setup not found - skipping installer." -ForegroundColor Yellow
    Write-Host "  winget install -e --id JRSoftware.InnoSetup"
}

# ---------------------------------------------------------------------------
# Code signing. SIGN BOTH THE APP AND THE INSTALLER.
#
# The installer is the FIRST thing the clinician runs, so an unsigned
# CareScribeSetup.exe means the very first interaction is a SmartScreen wall
# saying "Windows protected your PC". Sign the inner exe before compiling the
# installer, then sign the installer itself:
#
#   signtool sign /fd SHA256 /a /tr http://timestamp.digicert.com /td SHA256 `
#       dist\CareScribe\CareScribe.exe
#   # then re-run ISCC, then:
#   signtool sign /fd SHA256 /a /tr http://timestamp.digicert.com /td SHA256 `
#       packaging\Output\CareScribeSetup.exe
#
# An EV certificate clears SmartScreen immediately; an OV certificate needs
# reputation to accumulate first.
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "NOT SIGNED. Users will see a SmartScreen warning when they run the installer." -ForegroundColor Yellow
Write-Host "See the comments in this script for signtool commands." -ForegroundColor Yellow
