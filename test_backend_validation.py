#!/usr/bin/env python3
"""
Minimal validation test for REST backend implementation
Tests code structure without requiring full dependency installation
"""

import sys
import ast
from pathlib import Path

def test_config_manager_structure():
    """Validate config_manager.py has required settings"""
    print("=== Validating config_manager.py structure ===")
    try:
        config_file = Path(__file__).parent / 'lib' / 'src' / 'config_manager.py'
        with open(config_file, 'r') as f:
            content = f.read()

        # Check for required config keys
        required_keys = [
            'transcription_backend',
            'rest_endpoint_url',
            'rest_api_key',
            'rest_timeout',
            'rest_audio_format'
        ]

        for key in required_keys:
            assert f"'{key}'" in content, f"Missing config key: {key}"
            print(f"✓ Found config key: {key}")

        # Check default value
        assert "'transcription_backend': 'local'" in content
        print("✓ Default backend is 'local'")

        print("✓ config_manager.py validation passed\n")
        return True

    except Exception as e:
        print(f"✗ config_manager.py validation failed: {e}\n")
        return False


def test_whisper_manager_structure():
    """Validate whisper_manager.py has required methods"""
    print("=== Validating whisper_manager.py structure ===")
    try:
        whisper_file = Path(__file__).parent / 'lib' / 'src' / 'whisper_manager.py'
        with open(whisper_file, 'r') as f:
            content = f.read()

        # Parse the Python file
        tree = ast.parse(content)

        # Find WhisperManager class
        whisper_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'WhisperManager':
                whisper_class = node
                break

        assert whisper_class is not None, "WhisperManager class not found"
        print("✓ Found WhisperManager class")

        # Check for required methods
        methods = [m.name for m in whisper_class.body if isinstance(m, ast.FunctionDef)]

        required_methods = [
            '_numpy_to_wav_bytes',
            '_transcribe_rest',
            'transcribe_audio',
            'initialize'
        ]

        for method in required_methods:
            assert method in methods, f"Missing method: {method}"
            print(f"✓ Found method: {method}")

        # Check imports
        assert 'from io import BytesIO' in content
        assert 'import wave' in content
        print("✓ Required imports present")

        # Check for backend routing in transcribe_audio
        assert "backend = self.config.get_setting('transcription_backend'" in content
        assert "if backend == 'remote':" in content
        print("✓ Backend routing logic present")

        # Check for REST config validation in initialize
        assert "rest_endpoint_url" in content
        print("✓ REST config validation present")

        print("✓ whisper_manager.py validation passed\n")
        return True

    except Exception as e:
        print(f"✗ whisper_manager.py validation failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_wav_conversion_logic():
    """Validate WAV conversion code structure"""
    print("=== Validating WAV conversion logic ===")
    try:
        whisper_file = Path(__file__).parent / 'lib' / 'src' / 'whisper_manager.py'
        with open(whisper_file, 'r') as f:
            content = f.read()

        # Check for key conversion steps
        conversion_checks = [
            'wav_buffer = BytesIO()',
            'wave.open(wav_buffer',
            'setnchannels(1)',  # mono
            'setsampwidth(2)',  # 16-bit
            'setframerate(sample_rate)',
            'audio_int16 = (audio_data * 32767).astype(np.int16)',
            'writeframes(audio_int16.tobytes())',
            'wav_buffer.getvalue()'
        ]

        for check in conversion_checks:
            assert check in content, f"Missing WAV conversion step: {check}"
            print(f"✓ Found: {check}")

        print("✓ WAV conversion logic validation passed\n")
        return True

    except Exception as e:
        print(f"✗ WAV conversion logic validation failed: {e}\n")
        return False


def test_rest_api_logic():
    """Validate REST API request logic"""
    print("=== Validating REST API request logic ===")
    try:
        whisper_file = Path(__file__).parent / 'lib' / 'src' / 'whisper_manager.py'
        with open(whisper_file, 'r') as f:
            content = f.read()

        # Check for REST API implementation details
        rest_checks = [
            'import requests',
            "files = {",
            "'file':",
            "requests.post(",
            "response.status_code",
            "response.json()",
            "requests.exceptions.Timeout",
            "requests.exceptions.ConnectionError",
            "Authorization"
        ]

        for check in rest_checks:
            assert check in content, f"Missing REST API logic: {check}"
            print(f"✓ Found: {check}")

        # Check for multiple response format handling
        response_formats = ["'text'", "'transcription'", "'result'"]
        for fmt in response_formats:
            assert fmt in content, f"Missing response format handling: {fmt}"
        print("✓ Multiple response formats supported")

        print("✓ REST API logic validation passed\n")
        return True

    except Exception as e:
        print(f"✗ REST API logic validation failed: {e}\n")
        return False


def test_error_handling():
    """Validate error handling is present"""
    print("=== Validating error handling ===")
    try:
        whisper_file = Path(__file__).parent / 'lib' / 'src' / 'whisper_manager.py'
        with open(whisper_file, 'r') as f:
            content = f.read()

        # Check for error handling
        error_checks = [
            'try:',
            'except',
            'timeout',
            'ConnectionError',
            'RequestException',
            'return ""'  # Returns empty string on error
        ]

        for check in error_checks:
            assert check in content, f"Missing error handling: {check}"

        print("✓ Error handling present")
        print("✓ Error handling validation passed\n")
        return True

    except Exception as e:
        print(f"✗ Error handling validation failed: {e}\n")
        return False


def test_backend_validation_logic():
    """Validate backend validation in initialize()"""
    print("=== Validating backend validation logic ===")
    try:
        whisper_file = Path(__file__).parent / 'lib' / 'src' / 'whisper_manager.py'
        with open(whisper_file, 'r') as f:
            content = f.read()

        # Check initialize() handles both backends
        validation_checks = [
            "backend = self.config.get_setting('transcription_backend'",
            "if backend == 'remote':",
            "endpoint_url = self.config.get_setting('rest_endpoint_url')",
            "if not endpoint_url:",
            "return False",
            "self.ready = True",
            "return True"
        ]

        for check in validation_checks:
            assert check in content, f"Missing validation logic: {check}"
            print(f"✓ Found: {check}")

        print("✓ Backend validation logic passed\n")
        return True

    except Exception as e:
        print(f"✗ Backend validation logic failed: {e}\n")
        return False


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("REST Transcription Backend - Structure Validation")
    print("=" * 60)
    print()

    tests = [
        test_config_manager_structure,
        test_whisper_manager_structure,
        test_wav_conversion_logic,
        test_rest_api_logic,
        test_error_handling,
        test_backend_validation_logic,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("=" * 60)
    print(f"Validation tests passed: {sum(results)}/{len(results)}")

    if all(results):
        print("✓ All structural validations passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some validations failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
