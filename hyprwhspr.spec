# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# --- Configuration ---
APP_NAME = 'hyprwhspr'
ENTRY_POINT = 'lib/main.py'
ASSETS_DIR = 'share/assets'

# --- Find required libraries robustly ---
site_packages = Path(sys.path[-1])
pywhispercpp_lib = next(site_packages.glob('pywhispercpp*/libwhisper.dylib'))
sounddevice_lib = next(site_packages.glob('_sounddevice_data/portaudio-binaries/*.dylib'))

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
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# --- macOS Application Bundle Configuration ---
app = BUNDLE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    icon=None,
    bundle_identifier=f'com.{APP_NAME}.app',
    # --- CRITICAL: Add Info.plist entries for permissions ---
    info_plist={
        'NSMicrophoneUsageDescription': 'hyprwhspr needs microphone access to transcribe your speech to text.',
        'NSAppleEventsUsageDescription': 'hyprwhspr needs to send keystrokes to paste transcribed text.',
        'LSUIElement': True,  # Run without a Dock icon
    },
)
