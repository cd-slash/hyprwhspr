# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# --- Configuration ---
APP_NAME = 'hyprwhspr'
ENTRY_POINT = 'lib/main.py'
ASSETS_DIR = 'share/assets'

# --- Find required libraries robustly ---
# This ensures that the native libraries are found regardless of the exact path
site_packages = next(p for p in sys.path if 'site-packages' in p)
pywhispercpp_lib = next(Path(site_packages).glob('pywhispercpp*/libwhisper.dylib'))
sounddevice_lib = next(Path(site_packages).glob('_sounddevice_data/portaudio-binaries/*.dylib'))

# --- PyInstaller Analysis ---
a = Analysis(
    [ENTRY_POINT],
    pathex=[],
    binaries=[
        (str(pywhispercpp_lib), '.'),
        (str(sounddevice_lib), '.'),
    ],
    datas=[
        (ASSETS_DIR, 'assets'),
    ],
    hiddenimports=[
        'pyobjc-framework-Quartz',
        'pyobjc-framework-Cocoa',
        'pyobjc-core',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=None,
    # --- Enable Debugging ---
    debug=True,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# --- macOS Application Bundle Configuration ---
app = BUNDLE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name=APP_NAME,
    icon=None,
    bundle_identifier=f'com.{APP_NAME}.app',
    info_plist={
        'NSMicrophoneUsageDescription': 'hyprwhspr needs microphone access for speech-to-text.',
        'NSAppleEventsUsageDescription': 'hyprwhspr needs accessibility permissions to paste text.',
        # 'LSUIElement': True, # Disabled for debugging to show Dock icon
    },
)
