"""
Configuration manager for hyprwhspr
Handles loading, saving, and managing application settings
"""

import json
import platform
import sys
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manages application configuration and settings"""

    def __init__(self):
        # Platform-specific default shortcut
        is_macos = platform.system() == 'Darwin'
        default_shortcut = 'fn' if is_macos else 'SUPER+ALT+D'

        # Default configuration values
        self.default_config = {
            'primary_shortcut': default_shortcut,
            'model': 'base.en',
            'threads': 4,
            'language': None,
            'word_overrides': {},
            'whisper_prompt': 'Transcribe with proper capitalization...',
            'clipboard_behavior': False,
            'clipboard_clear_delay': 5.0,
            'paste_mode': 'super',
        }
        
        # Set up platform-specific config directory and file path
        if is_macos and getattr(sys, 'frozen', False):
            # Running as a bundled app on macOS
            self.base_dir = Path.home() / 'Library' / 'Application Support' / 'hyprwhspr'
        else:
            # Standard Linux/macOS script-based path
            self.base_dir = Path.home() / '.config' / 'hyprwhspr'

        self.config_dir = self.base_dir
        self.config_file = self.config_dir / 'config.json'
        
        # Current configuration (starts with defaults)
        self.config = self.default_config.copy()
        
        # Ensure config directory exists
        self._ensure_config_dir()
        
        # Load existing configuration
        self._load_config()
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create config directory: {e}")
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                self.config.update(loaded_config)
                print(f"Configuration loaded from {self.config_file}")
            else:
                print("No existing configuration found, creating a new one.")
                self.save_config()
                
        except Exception as e:
            print(f"Warning: Could not load configuration: {e}")
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Error: Could not save configuration: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a configuration setting"""
        self.config[key] = value
    
    def get_temp_directory(self) -> Path:
        """Get the temporary directory for audio files"""
        temp_dir = self.base_dir / 'temp'
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    # ... other methods remain the same ...
    def get_all_settings(self) -> Dict[str, Any]:
        return self.config.copy()
    
    def reset_to_defaults(self):
        self.config = self.default_config.copy()
    
    def get_word_overrides(self) -> Dict[str, str]:
        return self.config.get('word_overrides', {}).copy()
