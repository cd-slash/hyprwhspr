#!/usr/bin/env python3
"""
hyprwhspr - Voice dictation application (Cross-platform)
Fast, reliable speech-to-text with instant text injection
Supports Linux (Hyprland) and macOS
"""

import sys
import platform
import time
import traceback
from pathlib import Path

# --- Robust Error Logging ---
# This will catch any error during startup and write it to a log file on the desktop.
# This is crucial for debugging py2app bundles, which often fail silently.
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
    print("🚀 HYPRWHSPR STARTING UP!")
    print("=" * 50)

    # Add the src directory to the Python path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))

    from config_manager import ConfigManager
    from audio_capture import AudioCapture
    from whisper_manager import WhisperManager
    from audio_manager import AudioManager

    # Detect platform and import platform-specific modules
    PLATFORM = platform.system()
    print(f"Platform detected: {PLATFORM}")
    if PLATFORM == 'Darwin':  # macOS
        print("Loading macOS modules...")
        from text_injector_macos import TextInjector
        from global_shortcuts_macos import GlobalShortcuts
    elif PLATFORM == 'Linux':
        print("Loading Linux modules...")
        from text_injector import TextInjector
        from global_shortcuts import GlobalShortcuts
    else:
        raise RuntimeError(f"Unsupported platform: {PLATFORM}")

    class hyprwhsprApp:
        """Main application class for hyprwhspr voice dictation (Headless Mode)"""

        def __init__(self):
            # ... (rest of the class is the same) ...
            self.config = ConfigManager()
            audio_device_id = self.config.get_setting('audio_device', None)
            self.audio_capture = AudioCapture(device_id=audio_device_id)
            self.audio_manager = AudioManager(self.config)
            self.whisper_manager = WhisperManager()
            self.text_injector = TextInjector(self.config)
            self.global_shortcuts = None
            self.is_recording = False
            self.is_processing = False
            self.current_transcription = ""
            self.processing_start_time = None
            self._setup_global_shortcuts()

        def _setup_global_shortcuts(self):
            """Initialize global keyboard shortcuts"""
            try:
                shortcut_key = self.config.get_setting('primary_shortcut', 'Super+Alt+D')
                self.global_shortcuts = GlobalShortcuts(shortcut_key, self._on_shortcut_triggered)
                print(f"🎯 Global shortcut configured: {shortcut_key}")
            except Exception as e:
                print(f"❌ Failed to initialize global shortcuts: {e}")
                self.global_shortcuts = None

        def _on_shortcut_triggered(self):
            """Handle global shortcut trigger"""
            if self.is_recording:
                self._stop_recording()
            else:
                self._start_recording()

        def _start_recording(self):
            """Start voice recording"""
            if self.is_recording:
                return
            try:
                print("🎤 Starting recording...")
                self.is_recording = True
                self._write_recording_status(True)
                self.audio_manager.play_start_sound()
                self.audio_capture.start_recording()
                print("✅ Recording started - speak now!")
            except Exception as e:
                print(f"❌ Failed to start recording: {e}")
                self.is_recording = False
                self._write_recording_status(False)

        def _stop_recording(self):
            """Stop voice recording and process audio"""
            if not self.is_recording:
                return
            try:
                print("🛑 Stopping recording...")
                self.is_recording = False
                self._write_recording_status(False)
                audio_data = self.audio_capture.stop_recording()
                self.processing_start_time = time.time()
                self.audio_manager.play_stop_sound()
                if audio_data is not None:
                    self._process_audio(audio_data)
                else:
                    print("⚠️ No audio data captured")
            except Exception as e:
                print(f"❌ Error stopping recording: {e}")

        def _process_audio(self, audio_data):
            """Process captured audio through Whisper"""
            if self.is_processing:
                return
            try:
                self.is_processing = True
                print("🧠 Processing audio with Whisper...")
                transcription = self.whisper_manager.transcribe_audio(audio_data)
                if transcription and transcription.strip():
                    self.current_transcription = transcription.strip()
                    print(f"📝 Transcription: {self.current_transcription}")
                    self._inject_text(self.current_transcription)
                else:
                    print("⚠️ No transcription generated")
            except Exception as e:
                print(f"❌ Error processing audio: {e}")
            finally:
                self.is_processing = False

        def _inject_text(self, text):
            """Inject transcribed text into active application"""
            try:
                print(f"⌨️ Injecting text: {text}")
                self.text_injector.inject_text(text)
                if self.processing_start_time is not None:
                    response_time_ms = (time.time() - self.processing_start_time) * 1000
                    print(f"✅ Text injection completed ({response_time_ms:.0f}ms)")
                else:
                    print("✅ Text injection completed")
            except Exception as e:
                print(f"❌ Text injection failed: {e}")

        def _write_recording_status(self, is_recording):
            """Write recording status to file for tray script"""
            try:
                status_file = Path.home() / '.config' / 'hyprwhspr' / 'recording_status'
                status_file.parent.mkdir(parents=True, exist_ok=True)
                if is_recording:
                    with open(status_file, 'w') as f:
                        f.write('true')
                else:
                    if status_file.exists():
                        status_file.unlink()
            except Exception as e:
                print(f"⚠️ Failed to write recording status: {e}")

        def run(self):
            """Start the application"""
            print("🚀 Starting hyprwhspr...")
            if not self.whisper_manager.initialize():
                raise RuntimeError("Failed to initialize Whisper. Please ensure whisper.cpp is built.")
            print("✅ hyprwhspr initialized successfully")
            print("🎤 Listening for global shortcuts...")
            if self.global_shortcuts:
                self.global_shortcuts.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down hyprwhspr...")
            finally:
                self._cleanup()

        def _cleanup(self):
            """Clean up resources when shutting down"""
            print("🧹 Cleaning up resources...")
            try:
                if self.global_shortcuts:
                    self.global_shortcuts.stop()
                if self.is_recording:
                    self.audio_capture.stop_recording()
                self.config.save_config()
                print("✅ Cleanup completed")
            except Exception as e:
                print(f"⚠️ Error during cleanup: {e}")

    def main():
        """Main entry point"""
        print("🎤 hyprwhspr")
        app = hyprwhsprApp()
        app.run()
        # If the app starts successfully, write a success message to the log file.
        with open(CRASH_LOG_FILE, "w") as f:
            f.write("hyprwhspr started successfully and did not crash on launch.\n")


    if __name__ == "__main__":
        main()

except Exception as e:
    # If any exception occurs during the import or setup phase, log it.
    tb_str = traceback.format_exc()
    log_crash(e, tb_str)
    # Re-raise the exception so the app still terminates
    raise
