#!/usr/bin/env python3
"""
Benchmarking module for hyprwhspr.
Measures transcription performance with audio files or live recording.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np
from scipy.io import wavfile

from src.config_manager import ConfigManager
from src.whisper_manager import WhisperManager
from src.audio_capture import AudioCapture
from src.logger import logger


class BenchmarkRunner:
    """Handles benchmarking of audio transcription performance."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize benchmark runner with configuration.

        Args:
            config_path: Optional path to config file. Uses default if None.
        """
        self.config_manager = ConfigManager()

        # If custom config path provided, load it manually
        if config_path:
            try:
                custom_config_path = Path(config_path)
                if custom_config_path.exists():
                    with open(custom_config_path, 'r', encoding='utf-8') as f:
                        custom_config = json.load(f)
                        self.config_manager.config.update(custom_config)
                        logger.info(f"Loaded custom config from: {config_path}")
                else:
                    logger.warning(f"Custom config not found: {config_path}, using default")
            except Exception as e:
                logger.error(f"Failed to load custom config: {e}, using default")

        self.config = self.config_manager.config
        self.whisper_manager = None
        self.audio_capture = None

    def initialize_whisper(self) -> bool:
        """Initialize Whisper transcription backend.

        Returns:
            True if initialization successful, False otherwise.
        """
        try:
            logger.info("Initializing Whisper transcription backend...")
            self.whisper_manager = WhisperManager(self.config_manager)
            if not self.whisper_manager.initialize():
                logger.error("Failed to initialize Whisper backend")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Whisper: {e}")
            return False

    def load_audio_file(self, file_path: str) -> Optional[np.ndarray]:
        """Load audio from WAV file.

        Args:
            file_path: Path to WAV file.

        Returns:
            Audio data as numpy array (16kHz, mono, float32), or None on error.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"Audio file not found: {file_path}")
                return None

            if path.suffix.lower() != '.wav':
                logger.error(f"Only WAV files are supported. Got: {path.suffix}")
                return None

            logger.info(f"Loading audio file: {file_path}")
            sample_rate, audio_data = wavfile.read(file_path)

            # Convert to float32 if needed
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483648.0
            elif audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                logger.info("Converting stereo to mono...")
                audio_data = np.mean(audio_data, axis=1)

            # Resample to 16kHz if needed
            if sample_rate != 16000:
                logger.info(f"Resampling from {sample_rate}Hz to 16000Hz...")
                from scipy import signal
                num_samples = int(len(audio_data) * 16000 / sample_rate)
                audio_data = signal.resample(audio_data, num_samples)

            duration = len(audio_data) / 16000.0
            logger.info(f"Loaded {duration:.2f}s of audio (16kHz, mono, float32)")

            return audio_data

        except Exception as e:
            logger.error(f"Error loading audio file: {e}")
            return None

    def record_audio(self, duration: Optional[float] = None) -> Optional[np.ndarray]:
        """Record audio from microphone.

        Args:
            duration: Optional fixed duration in seconds. If None, uses toggle recording.

        Returns:
            Recorded audio data as numpy array, or None on error.
        """
        try:
            logger.info("Initializing audio capture...")
            audio_device_id = self.config.get('audio_device', None)
            self.audio_capture = AudioCapture(device_id=audio_device_id)

            if duration:
                logger.info(f"Recording {duration}s of audio...")
                logger.info("Speak now!")
                self.audio_capture.start_recording()
                time.sleep(duration)
                audio_data = self.audio_capture.stop_recording()
            else:
                logger.info("Press Enter to start recording...")
                input()
                logger.info("Recording started. Speak now!")
                self.audio_capture.start_recording()
                logger.info("Press Enter to stop recording...")
                input()
                logger.info("Stopping recording...")
                audio_data = self.audio_capture.stop_recording()

            if audio_data is not None:
                duration = len(audio_data) / 16000.0
                logger.info(f"Recorded {duration:.2f}s of audio")
                return audio_data
            else:
                logger.error("Failed to record audio")
                return None

        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None

    def save_audio(self, audio_data: np.ndarray, file_path: str) -> bool:
        """Save audio data to WAV file.

        Args:
            audio_data: Audio data to save (16kHz, mono, float32).
            file_path: Path where to save the file.

        Returns:
            True if save successful, False otherwise.
        """
        try:
            # Convert float32 to int16 for WAV
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wavfile.write(file_path, 16000, audio_int16)
            logger.info(f"Saved audio to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return False

    def benchmark_transcription(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Benchmark transcription performance.

        Args:
            audio_data: Audio data to transcribe.

        Returns:
            Dictionary containing benchmark results.
        """
        results = {
            'audio_duration_seconds': len(audio_data) / 16000.0,
            'transcription_time_seconds': 0.0,
            'real_time_factor': 0.0,
            'transcription': '',
            'backend': self.config.get('transcription_backend', 'local'),
            'model': self.config.get('model', 'base'),
            'success': False
        }

        try:
            logger.info("Starting transcription benchmark...")
            start_time = time.perf_counter()

            transcription = self.whisper_manager.transcribe_audio(audio_data)

            end_time = time.perf_counter()
            transcription_time = end_time - start_time

            results['transcription_time_seconds'] = transcription_time
            results['real_time_factor'] = transcription_time / results['audio_duration_seconds']
            results['transcription'] = transcription
            results['success'] = bool(transcription)

            logger.info(f"Transcription completed in {transcription_time:.3f}s")
            logger.info(f"Real-time factor: {results['real_time_factor']:.2f}x")

        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            results['error'] = str(e)

        return results

    def print_results(self, results: Dict[str, Any], verbose: bool = False):
        """Print benchmark results in a formatted way.

        Args:
            results: Benchmark results dictionary.
            verbose: If True, print detailed information.
        """
        logger.info("\n" + "=" * 60)
        logger.info("BENCHMARK RESULTS")
        logger.info("=" * 60)

        if not results['success']:
            logger.error("Transcription failed!")
            if 'error' in results:
                logger.error(f"Error: {results['error']}")
            return

        logger.info(f"Backend: {results['backend']}")
        logger.info(f"Model: {results['model']}")
        logger.info(f"Audio Duration: {results['audio_duration_seconds']:.2f}s")
        logger.info(f"Transcription Time: {results['transcription_time_seconds']:.3f}s")
        logger.info(f"Real-Time Factor: {results['real_time_factor']:.2f}x")

        if results['real_time_factor'] < 1.0:
            logger.info("✓ Faster than real-time!")
        else:
            logger.info("✗ Slower than real-time")

        logger.info("-" * 60)
        logger.info("Transcription:")
        logger.info(f'"{results["transcription"]}"')
        logger.info("-" * 60)

        if verbose:
            logger.info("\nDetailed Results (JSON):")
            print(json.dumps(results, indent=2))


def main():
    """Main entry point for benchmark CLI."""
    parser = argparse.ArgumentParser(
        description='Benchmark hyprwhspr transcription performance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Benchmark with existing audio file
  hyprwhspr-benchmark --audio-file recording.wav

  # Record and benchmark
  hyprwhspr-benchmark --record

  # Record fixed duration
  hyprwhspr-benchmark --record --duration 5

  # Record and save for later use
  hyprwhspr-benchmark --record --save-audio test.wav

  # Use custom config
  hyprwhspr-benchmark --audio-file test.wav --config ~/my-config.json

  # JSON output for scripting
  hyprwhspr-benchmark --audio-file test.wav --json
        """
    )

    # Input mode
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--audio-file',
        type=str,
        help='Path to input WAV file to benchmark'
    )
    input_group.add_argument(
        '--record',
        action='store_true',
        help='Record audio from microphone'
    )

    # Recording options
    parser.add_argument(
        '--duration',
        type=float,
        help='Recording duration in seconds (default: manual start/stop)'
    )
    parser.add_argument(
        '--save-audio',
        type=str,
        help='Save recorded/processed audio to this file'
    )

    # Configuration
    parser.add_argument(
        '--config',
        type=str,
        help='Path to config file (default: ~/.config/hyprwhspr/config.json)'
    )

    # Output options
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Initialize benchmark runner
    runner = BenchmarkRunner(config_path=args.config)

    # Initialize Whisper
    if not runner.initialize_whisper():
        logger.error("Failed to initialize Whisper. Exiting.")
        sys.exit(1)

    # Get audio data
    audio_data = None

    if args.audio_file:
        audio_data = runner.load_audio_file(args.audio_file)
    elif args.record:
        audio_data = runner.record_audio(duration=args.duration)

        # Save recorded audio if requested
        if audio_data is not None and args.save_audio:
            runner.save_audio(audio_data, args.save_audio)

    if audio_data is None:
        logger.error("Failed to get audio data. Exiting.")
        sys.exit(1)

    # Run benchmark
    results = runner.benchmark_transcription(audio_data)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        runner.print_results(results, verbose=args.verbose)

    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == '__main__':
    main()
