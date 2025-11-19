"""
Whisper manager for hyprwhspr
Handles model loading and transcription.
"""

import os
import platform
import sys
from pathlib import Path
from typing import Optional

try:
    from .config_manager import ConfigManager
except ImportError:
    from config_manager import ConfigManager


class WhisperManager:
    """Manages whisper transcription."""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config = config_manager or ConfigManager()
        self.current_model = self.config.get_setting('model', 'base.en')
        self._pywhisper_model = None
        self.ready = False
        
        # Determine the correct models directory
        is_macos = platform.system() == 'Darwin'
        if is_macos and getattr(sys, 'frozen', False):
            # Bundled app on macOS
            self.models_dir = self.config.base_dir / 'models'
        else:
            # Standard script-based path
            self.models_dir = Path.home() / '.local' / 'share' / 'pywhispercpp' / 'models'
        
        # Ensure the models directory exists
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> bool:
        """Initialize the whisper manager."""
        try:
            from pywhispercpp.model import Model
            print(f"[Whisper] Initializing model: {self.current_model}")

            # This is where pywhispercpp will look for the model file
            os.environ['WHISPER_CPP_MODELS_PATH'] = str(self.models_dir)

            self._pywhisper_model = Model(
                model=self.current_model,
                n_threads=self.config.get_setting('threads', 4),
            )
            self.ready = True
            print("[Whisper] Model loaded successfully.")
            return True
        except Exception as e:
            print(f"[Whisper] ERROR: Failed to initialize model: {e}")
            print(f"Ensure the model '{self.current_model}' exists in: {self.models_dir}")
            return False

    def transcribe_audio(self, audio_data) -> str:
        """Transcribe audio data."""
        if not self.ready or self._pywhisper_model is None:
            raise RuntimeError('Whisper manager not initialized')
        
        if audio_data is None or len(audio_data) < 1000: # Basic check for valid audio
            return ""

        try:
            language = self.config.get_setting('language', None) or 'en'
            segments = self._pywhisper_model.transcribe(audio_data, language=language)
            return ' '.join(seg.text for seg in segments).strip()
        except Exception as e:
            print(f"[Whisper] ERROR: Transcription failed: {e}")
            return ""

    # ... other methods like set_model, get_available_models can be added if needed ...
