# Build the TokenRhythm preset installer as a standalone Windows EXE.
# Usage:  powershell -ExecutionPolicy Bypass -File build_exe.ps1
# Output: dist\opencode-tokenrhythm-preset.exe

$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "python not found. Install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

Write-Host "Installing PyInstaller if needed..."
python -m pip install --upgrade pyinstaller

Write-Host "Building EXE..."
python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --console `
    --name "opencode-tokenrhythm-preset" `
    install_preset.py

Write-Host ""
Write-Host "Done. The installer is at: dist\opencode-tokenrhythm-preset.exe" -ForegroundColor Green
Write-Host "Run it once; it will add the TokenRhythm provider preset to opencode."