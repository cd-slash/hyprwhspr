"""
Setup script to build hyprwhspr as a standalone macOS application
Uses py2app to create a proper .app bundle with all dependencies
"""

from setuptools import setup

APP = ['lib/main.py']
DATA_FILES = [
    ('share/assets', ['share/assets/ping-up.ogg', 'share/assets/ping-down.ogg'])
] if __import__('os').path.exists('share/assets') else []

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
        'AppKit',
        'Quartz',
        'Cocoa',
    ],
    'includes': [
        'config_manager',
        'audio_capture',
        'whisper_manager',
        'audio_manager',
        'text_injector_macos',
        'global_shortcuts_macos',
    ],
    'excludes': [
        'tkinter',
        'PyQt5',
        'matplotlib',
    ],
    'site_packages': True,
}

setup(
    app=APP,
    name='hyprwhspr',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
