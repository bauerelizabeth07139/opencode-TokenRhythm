#!/usr/bin/env bash
# Build the TokenRhythm preset installer as a standalone binary (macOS/Linux).
set -e
python -m pip install --upgrade pyinstaller || true
python -m PyInstaller --noconfirm --clean --onefile --console --name "opencode-tokenrhythm-preset" install_preset.py
echo "Done. Binary at: dist/opencode-tokenrhythm-preset"