"""
Audio feedback manager for hyprwhspr
Handles audio feedback for dictation start/stop events
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

class AudioManager:
    """Handles audio feedback for recording events."""

    def __init__(self, config_manager):
        self.config = config_manager
        self.enabled = self.config.get_setting('audio_feedback', True)
        self.start_volume = self.config.get_setting('start_sound_volume', 0.3)
        self.stop_volume = self.config.get_setting('stop_sound_volume', 0.3)

        # Determine the assets directory based on execution context
        if getattr(sys, 'frozen', False):
            # Running in a bundled app (PyInstaller)
            self.assets_dir = Path(sys._MEIPASS) / 'assets'
        else:
            # Running as a script
            self.assets_dir = Path(__file__).parent.parent.parent / 'share' / 'assets'
            
        self.start_sound = self.assets_dir / "ping-up.ogg"
        self.stop_sound = self.assets_dir / "ping-down.ogg"

    def _play_sound(self, sound_file: Path, volume: float):
        """Plays a sound file using the appropriate system command."""
        if not self.enabled or not sound_file.exists():
            return

        is_macos = platform.system() == 'Darwin'
        try:
            if is_macos:
                # Use afplay on macOS, which is always available
                vol_arg = f"-v {volume}"
                subprocess.Popen(['afplay', str(sound_file), vol_arg])
            else:
                # Use ffplay on Linux, assuming it's installed
                ffplay_volume = int(volume * 100)
                cmd = ['ffplay', '-nodisp', '-autoexit', '-volume', str(ffplay_volume), '-loglevel', 'error', str(sound_file)]
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[Audio] ERROR: Could not play sound {sound_file}: {e}")

    def play_start_sound(self):
        """Play the recording start sound."""
        self._play_sound(self.start_sound, self.start_volume)

    def play_stop_sound(self):
        """Play the recording stop sound."""
        self._play_sound(self.stop_sound, self.stop_volume)
