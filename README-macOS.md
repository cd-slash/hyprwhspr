# hyprwhspr for macOS

Native speech-to-text dictation for macOS with **Globe/Fn key** toggle support.

## Features

- 🎯 **Globe/Fn Key Toggle** - Press the globe (fn) key to start/stop dictation
- 🔒 **Private & Local** - All transcription happens on your Mac
- ⚡ **Fast** - Powered by Whisper.cpp with GPU acceleration
- 🎤 **System-wide** - Works in any application
- 🔧 **Customizable** - Change hotkeys, models, and behavior

## Quick Start

### Prerequisites

- **macOS 10.15 or later**
- **Python 3.8+** (install via [python.org](https://www.python.org/downloads/macos/) or Homebrew)
- **Accessibility Permissions** (required for global hotkeys)

### Installation

```bash
# Clone the repository
git clone https://github.com/goodroot/hyprwhspr.git
cd hyprwhspr

# Run the automated installer
./scripts/install-macos.sh
```

### Grant Accessibility Permissions

**This is required for the globe key to work!**

1. Open **System Preferences** > **Security & Privacy** > **Privacy**
2. Select **Accessibility** from the left sidebar
3. Click the 🔒 lock icon and enter your password
4. Click the **+** button and add your **Terminal** app (or iTerm2, etc.)
5. Check the box next to it

### First Use

1. **Start hyprwhspr**:
   ```bash
   ~/.local/share/hyprwhspr/hyprwhspr-launch.sh
   ```

2. **Press the Globe/Fn key** to start recording - *beep!*

3. **Speak naturally**

4. **Press the Globe/Fn key again** to stop - *boop!*

5. **Text appears in your active window!**

### Auto-start on Login

To start hyprwhspr automatically when you log in:

```bash
launchctl load ~/Library/LaunchAgents/com.hyprwhspr.agent.plist
```

To stop auto-start:

```bash
launchctl unload ~/Library/LaunchAgents/com.hyprwhspr.agent.plist
```

## Configuration

Edit `~/.config/hyprwhspr/config.json`:

### Change the Toggle Key

```json
{
    "primary_shortcut": "fn"
}
```

**Available options:**
- `"fn"` or `"globe"` - Globe/Fn key (default)
- `"f12"` - F12 key
- `"cmd+shift+d"` - Command+Shift+D
- `"cmd+space"` - Command+Space
- Any combination of `cmd`, `ctrl`, `option`, `shift` + any key

### Choose a Different Model

```json
{
    "model": "small.en"
}
```

**Available models:**
- `"tiny.en"` - Fastest, least accurate (~75MB)
- `"base.en"` - Good balance (default, ~148MB)
- `"small.en"` - Better accuracy (~488MB)
- `"medium.en"` - High accuracy (~1.5GB)
- `"large"` - Best accuracy, requires Apple Silicon or GPU (~3GB)

Download additional models:

```bash
cd ~/.local/share/pywhispercpp/models/

# Small model (better accuracy)
curl -LO https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin

# Medium model (high accuracy)
curl -LO https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.en.bin

# Large model (best accuracy, Apple Silicon recommended)
curl -LO https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin
```

### Word Overrides

Customize how Whisper transcribes specific words:

```json
{
    "word_overrides": {
        "hyperwhisper": "hyprwhspr",
        "mac os": "macOS"
    }
}
```

### Audio Feedback

Enable sound notifications:

```json
{
    "audio_feedback": true,
    "start_sound_volume": 0.3,
    "stop_sound_volume": 0.3
}
```

## Troubleshooting

### Globe key not working

**Check accessibility permissions:**

1. System Preferences > Security & Privacy > Privacy > Accessibility
2. Ensure your Terminal app is in the list and checked
3. Try removing and re-adding it
4. Restart hyprwhspr

**Alternative:** Use a different key combination:

```json
{
    "primary_shortcut": "cmd+shift+d"
}
```

### No audio input

Check your microphone is selected:

1. System Preferences > Sound > Input
2. Select your microphone
3. Test the input level
4. Restart hyprwhspr

### Text not appearing

hyprwhspr uses **Cmd+V** to paste text. Make sure:

1. The target application supports paste
2. Cmd+V works normally in that app
3. Check the logs for errors:
   ```bash
   tail -f ~/Library/Logs/hyprwhspr.log
   ```

### Whisper model not found

Download the model manually:

```bash
cd ~/.local/share/pywhispercpp/models/
curl -LO https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

## Uninstall

```bash
# Stop the service
launchctl unload ~/Library/LaunchAgents/com.hyprwhspr.agent.plist

# Remove files
rm -rf ~/.local/share/hyprwhspr
rm -rf ~/.config/hyprwhspr
rm ~/Library/LaunchAgents/com.hyprwhspr.agent.plist
rm ~/Library/Logs/hyprwhspr*.log
```

## Advanced Usage

### Running from Command Line

```bash
# Activate the virtual environment
source ~/.local/share/hyprwhspr/venv/bin/activate

# Run hyprwhspr
cd ~/.local/share/hyprwhspr
python3 lib/main.py
```

### Viewing Logs

```bash
# Real-time logs
tail -f ~/Library/Logs/hyprwhspr.log

# Error logs
tail -f ~/Library/Logs/hyprwhspr-error.log
```

### Manual Start/Stop

```bash
# Start
launchctl start com.hyprwhspr.agent

# Stop
launchctl stop com.hyprwhspr.agent

# Status
launchctl list | grep hyprwhspr
```

## GPU Acceleration

hyprwhspr automatically uses Metal acceleration on Apple Silicon Macs for faster transcription. No configuration needed!

For Intel Macs, CPU-only transcription is used. Consider using smaller models (`tiny.en` or `base.en`) for better performance.

## Privacy

All transcription happens locally on your Mac. No audio or text is sent to external servers. Your privacy is protected.

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

Issues and pull requests welcome! Please open an issue first to discuss major changes.

---

**Built with ❤️ for macOS users**

*Fast, private, local speech-to-text*
