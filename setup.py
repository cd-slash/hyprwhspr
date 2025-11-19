"""
Setup script to build hyprwhspr as a standalone macOS application
Uses py2app to create a proper .app bundle with all dependencies
"""

import sys
import sysconfig
from pathlib import Path
from setuptools import setup

# Add lib/src to path so py2app can find the modules
repo_dir = Path(__file__).parent
lib_src = repo_dir / 'lib' / 'src'
sys.path.insert(0, str(lib_src))

APP = ['lib/main.py']
DATA_FILES = []

# Include audio assets if they exist
assets_dir = repo_dir / 'share' / 'assets'
if assets_dir.exists():
    asset_files = []
    for asset in assets_dir.glob('*.ogg'):
        asset_files.append(str(asset))
    if asset_files:
        DATA_FILES.append(('assets', asset_files))

# Find and include sounddevice's PortAudio library
try:
    import sounddevice
    sd_path = Path(sounddevice.__file__).parent
    portaudio_dir = sd_path / '_sounddevice_data' / 'portaudio-binaries'
    if portaudio_dir.exists():
        portaudio_files = list(portaudio_dir.glob('*.dylib'))
        if portaudio_files:
            DATA_FILES.append(('_sounddevice_data/portaudio-binaries', [str(f) for f in portaudio_files]))
            print(f"Found PortAudio library: {portaudio_files}")
except ImportError:
    print("Warning: sounddevice not found, PortAudio may not be included")

OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,
    'plist': {
        'CFBundleName': 'hyprwhspr',
        'CFBundleDisplayName': 'hyprwhspr',
        'CFBundleIdentifier': 'com.hyprwhspr.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSMicrophoneUsageDescription': 'hyprwhspr needs microphone access to transcribe your speech to text.',
        'NSAppleEventsUsageDescription': 'hyprwhspr needs to send keystrokes to paste transcribed text.',
        'LSUIElement': True,  # Run without dock icon
        'LSMinimumSystemVersion': '10.15.0',
    },
    'packages': [
        'numpy',
        'sounddevice',
        'scipy',
        'pywhispercpp',
        'requests',
        'psutil',
        'rich',
    ],
    'includes': [
        'config_manager',
        'audio_capture',
        'whisper_manager',
        'audio_manager',
        'text_injector_macos',
        'global_shortcuts_macos',
        'logger',
    ],
    'excludes': [
        'tkinter',
        'PyQt5',
        'matplotlib',
        'evdev',  # Linux only
        'text_injector',  # Linux version
        'global_shortcuts',  # Linux version
    ],
    'site_packages': True,
    'strip': False,
    'semi_standalone': False,
    'compressed': False,  # DON'T compress - dylibs can't load from zip!
    'optimize': 0,  # Don't optimize to keep everything accessible
}

setup(
    app=APP,
    name='hyprwhspr',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
