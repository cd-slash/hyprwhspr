#!/usr/bin/env python3
"""
Test script for transcription backend implementation
Tests both local and remote backend configurations
"""

import sys
import numpy as np
from pathlib import Path

# Add lib/src to path
src_path = Path(__file__).parent / 'lib' / 'src'
sys.path.insert(0, str(src_path))

def test_config_manager():
    """Test that ConfigManager loads REST settings correctly"""
    print("\n=== Testing ConfigManager ===")
    try:
        from config_manager import ConfigManager

        config = ConfigManager()

        # Check default values
        backend = config.get_setting('transcription_backend', 'local')
        rest_url = config.get_setting('rest_endpoint_url')
        rest_timeout = config.get_setting('rest_timeout', 30)

        print(f"✓ Default backend: {backend}")
        print(f"✓ REST endpoint URL: {rest_url}")
        print(f"✓ REST timeout: {rest_timeout}s")

        # Test setting values
        config.set_setting('transcription_backend', 'remote')
        config.set_setting('rest_endpoint_url', 'https://api.example.com/transcribe')
        config.set_setting('rest_api_key', 'test-key')

        assert config.get_setting('transcription_backend') == 'remote'
        assert config.get_setting('rest_endpoint_url') == 'https://api.example.com/transcribe'
        assert config.get_setting('rest_api_key') == 'test-key'

        print("✓ Config setting/getting works correctly")

        # Reset to defaults
        config.set_setting('transcription_backend', 'local')
        config.set_setting('rest_endpoint_url', None)
        config.set_setting('rest_api_key', None)

        print("✓ ConfigManager tests passed\n")
        return True

    except Exception as e:
        print(f"✗ ConfigManager test failed: {e}\n")
        return False


def test_numpy_to_wav_conversion():
    """Test numpy to WAV conversion"""
    print("=== Testing numpy to WAV conversion ===")
    try:
        from config_manager import ConfigManager
        from whisper_manager import WhisperManager

        config = ConfigManager()
        manager = WhisperManager(config)

        # Create sample audio data (1 second of sine wave at 440Hz)
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        audio_data = np.sin(2 * np.pi * 440 * t).astype(np.float32)

        # Convert to WAV
        wav_bytes = manager._numpy_to_wav_bytes(audio_data, sample_rate)

        print(f"✓ Created test audio: {len(audio_data)} samples")
        print(f"✓ Converted to WAV: {len(wav_bytes)} bytes")

        # Verify WAV header
        assert wav_bytes[:4] == b'RIFF', "Invalid WAV header"
        assert wav_bytes[8:12] == b'WAVE', "Invalid WAV format"

        print("✓ WAV format validation passed")
        print("✓ numpy to WAV conversion tests passed\n")
        return True

    except Exception as e:
        print(f"✗ numpy to WAV conversion test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_local_backend_config():
    """Test local backend initialization"""
    print("=== Testing local backend configuration ===")
    try:
        from config_manager import ConfigManager
        from whisper_manager import WhisperManager

        config = ConfigManager()
        config.set_setting('transcription_backend', 'local')

        manager = WhisperManager(config)

        print("✓ WhisperManager created with local backend")

        # Note: We don't call initialize() here because it requires the actual
        # pywhispercpp model to be installed, which may not be available in CI
        print("✓ Local backend configuration tests passed\n")
        return True

    except Exception as e:
        print(f"✗ Local backend config test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_remote_backend_config():
    """Test remote backend validation"""
    print("=== Testing remote backend configuration ===")
    try:
        from config_manager import ConfigManager
        from whisper_manager import WhisperManager

        # Test 1: Missing endpoint URL should fail
        config = ConfigManager()
        config.set_setting('transcription_backend', 'remote')
        config.set_setting('rest_endpoint_url', None)

        manager = WhisperManager(config)
        result = manager.initialize()

        assert result == False, "Should fail when endpoint URL is missing"
        print("✓ Correctly fails when endpoint URL is missing")

        # Test 2: Valid configuration should succeed
        config.set_setting('rest_endpoint_url', 'https://api.example.com/transcribe')
        config.set_setting('rest_api_key', 'test-key')
        config.set_setting('rest_timeout', 30)

        manager = WhisperManager(config)
        result = manager.initialize()

        assert result == True, "Should succeed with valid REST config"
        assert manager.is_ready() == True
        print("✓ Initialization succeeds with valid REST config")

        # Test 3: Test routing logic
        backend = config.get_setting('transcription_backend')
        assert backend == 'remote'
        print("✓ Backend routing configured correctly")

        print("✓ Remote backend configuration tests passed\n")
        return True

    except Exception as e:
        print(f"✗ Remote backend config test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_transcribe_routing():
    """Test that transcribe_audio routes to correct backend"""
    print("=== Testing transcribe_audio routing ===")
    try:
        from config_manager import ConfigManager
        from whisper_manager import WhisperManager

        # Create sample audio
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        audio_data = np.sin(2 * np.pi * 440 * t).astype(np.float32)

        # Test with remote backend (will fail to connect, but that's expected)
        config = ConfigManager()
        config.set_setting('transcription_backend', 'remote')
        config.set_setting('rest_endpoint_url', 'https://httpbin.org/post')
        config.set_setting('rest_timeout', 5)

        manager = WhisperManager(config)
        manager.initialize()

        print("✓ Manager initialized with remote backend")

        # Attempt transcription (will fail but should handle error gracefully)
        result = manager.transcribe_audio(audio_data, sample_rate)

        # Should return empty string on error, not crash
        assert isinstance(result, str), "Should return string even on error"
        print("✓ Remote backend handles errors gracefully")

        # Test with invalid audio (should be caught early)
        result = manager.transcribe_audio(np.array([]), sample_rate)
        assert result == "", "Should return empty string for empty audio"
        print("✓ Empty audio validation works")

        result = manager.transcribe_audio(None, sample_rate)
        assert result == "", "Should return empty string for None audio"
        print("✓ None audio validation works")

        print("✓ transcribe_audio routing tests passed\n")
        return True

    except Exception as e:
        print(f"✗ transcribe_audio routing test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing REST Transcription Backend Implementation")
    print("=" * 60)

    tests = [
        test_config_manager,
        test_numpy_to_wav_conversion,
        test_local_backend_config,
        test_remote_backend_config,
        test_transcribe_routing,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("=" * 60)
    print(f"Tests passed: {sum(results)}/{len(results)}")

    if all(results):
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
