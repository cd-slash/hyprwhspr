#!/usr/bin/env python3
"""
hyprwhspr - Voice dictation application (Cross-platform)
"""

import sys
import platform
import time
import traceback
from pathlib import Path

# --- Robust Crash Logging ---
# This will catch any error during startup and write it to a log file on the desktop.
CRASH_LOG_FILE = Path.home() / "Desktop" / "hyprwhspr-crash.log"

def log_crash(e, tb):
    """Write exception details to a crash log file."""
    with open(CRASH_LOG_FILE, "w") as f:
        f.write("="*50 + "\n")
        f.write("HYPRWHSPR CRASH REPORT\n")
        f.write("="*50 + "\n\n")
        f.write(f"An unexpected error occurred: {e}\n\n")
        f.write("Traceback:\n")
        f.write(tb)
        f.write("\n\nPlease report this issue on GitHub.\n")

try:
    # --- Main Application Code ---

    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))

    from config_manager import ConfigManager
    from audio_capture import AudioCapture
    from whisper_manager import WhisperManager
    from audio_manager import AudioManager

    PLATFORM = platform.system()
    if PLATFORM == 'Darwin':
        from text_injector_macos import TextInjector
        from global_shortcuts_macos import GlobalShortcuts
    elif PLATFORM == 'Linux':
        from text_injector import TextInjector
        from global_shortcuts import GlobalShortcuts
    else:
        raise RuntimeError(f"Unsupported platform: {PLATFORM}")

    class hyprwhsprApp:
        def __init__(self):
            self.config = ConfigManager()
            self.audio_capture = AudioCapture(device_id=self.config.get_setting('audio_device'))
            self.audio_manager = AudioManager(self.config)
            self.whisper_manager = WhisperManager(self.config)
            self.text_injector = TextInjector(self.config)
            self.is_recording = False
            self.global_shortcuts = GlobalShortcuts(self.config.get_setting('primary_shortcut'), self._on_shortcut_triggered)

        def _on_shortcut_triggered(self):
            if self.is_recording:
                self._stop_recording()
            else:
                self._start_recording()

        def _start_recording(self):
            if self.is_recording: return
            self.is_recording = True
            self.audio_manager.play_start_sound()
            self.audio_capture.start_recording()

        def _stop_recording(self):
            if not self.is_recording: return
            self.is_recording = False
            audio_data = self.audio_capture.stop_recording()
            self.audio_manager.play_stop_sound()
            if audio_data is not None:
                transcription = self.whisper_manager.transcribe_audio(audio_data)
                if transcription:
                    self.text_injector.inject_text(transcription)

        def run(self):
            if not self.whisper_manager.initialize():
                raise RuntimeError("Failed to initialize Whisper.")
            self.global_shortcuts.start()
            try:
                while True: time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                self.global_shortcuts.stop()

    def main():
        app = hyprwhsprApp()
        app.run()
        # If we get here, the app ran successfully without crashing.
        if CRASH_LOG_FILE.exists():
             CRASH_LOG_FILE.unlink() # Clean up old crash logs

    if __name__ == "__main__":
        main()

except Exception as e:
    # If any exception occurs during the entire application lifecycle, log it.
    tb_str = traceback.format_exc()
    log_crash(e, tb_str)
    # Re-raise the exception so the app still terminates
    raise
