# hyprwhspr for macOS

Native speech-to-text dictation for macOS with **Globe/Fn key** toggle support.

## Features

- 🎯 **Globe/Fn Key Toggle** - Press the globe (fn) key to start/stop dictation
- 📦 **Easy Installation** - Simple DMG installer, just drag and drop
- 🔒 **Private & Local** - All transcription happens on your Mac
- ⚡ **Fast** - Powered by Whisper.cpp with GPU acceleration
- 🎤 **System-wide** - Works in any application
- 🔧 **Customizable** - Change hotkeys, models, and behavior

## Quick Start

### Installation

1.  **Download the DMG:**
    -   Go to the [releases page](https://github.com/goodroot/hyprwhspr/releases) and download the latest `hyprwhspr-installer.dmg`.
2.  **Install the App:**
    -   Open the DMG file.
    -   Drag `hyprwhspr.app` to your `Applications` folder.

### First Use

1.  **Launch hyprwhspr:**
    -   Open your `Applications` folder and double-click `hyprwhspr`.
2.  **Grant Permissions:**
    -   The first time you run the app, macOS will prompt you for:
        -   **Microphone Access:** Required to capture your voice.
        -   **Accessibility Access:** Required for the global hotkey (Globe/Fn key) to work.
    -   Follow the on-screen instructions to grant both permissions.
3.  **Start Dictation:**
    -   Press the **Globe/Fn key** to start recording - *beep!*
    -   Speak naturally.
    -   Press the **Globe/Fn key** again to stop - *boop!*
    -   Your transcribed text will appear in the active window.

### Auto-start on Login (Optional)

To have hyprwhspr launch automatically when you log in:

1.  Open **System Settings** > **General** > **Login Items**.
2.  Click the **+** button and add `hyprwhspr` from your `Applications` folder.

## Configuration

You can customize hyprwhspr by editing the configuration file located at:
`~/Library/Application Support/hyprwhspr/config.json`

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

You can download additional models and place them in:
`~/Library/Application Support/hyprwhspr/models/`

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

## Troubleshooting

### Globe Key Not Working

-   **Check Accessibility Permissions:**
    1.  Go to **System Settings** > **Privacy & Security** > **Accessibility**.
    2.  Make sure `hyprwhspr` is in the list and the toggle is enabled.
    3.  If it's already enabled, try toggling it off and on again.

### No Audio Input

-   **Check Microphone Permissions:**
    1.  Go to **System Settings** > **Privacy & Security** > **Microphone**.
    2.  Ensure `hyprwhspr` is in the list and the toggle is enabled.
-   **Check System Sound Settings:**
    1.  Go to **System Settings** > **Sound** > **Input**.
    2.  Select your preferred microphone and check the input level.

### Text Not Appearing

-   hyprwhspr uses the clipboard and simulates **Cmd+V** to paste text. Make sure the target application supports pasting.

### Viewing Logs

Logs are stored at:
-   `~/Library/Logs/hyprwhspr/hyprwhspr.log` (for general output)
-   `~/Library/Logs/hyprwhspr/hyprwhspr-error.log` (for errors)

## Uninstalling

1.  Drag `hyprwhspr.app` from your `Applications` folder to the Trash.
2.  (Optional) Remove the configuration and log files:
    ```bash
    rm -rf "~/Library/Application Support/hyprwhspr"
    rm -rf "~/Library/Logs/hyprwhspr"
    ```

## Building from Source

If you want to build the app yourself:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/goodroot/hyprwhspr.git
    cd hyprwhspr
    ```
2.  **Run the build script:**
    ```bash
    ./scripts/install-macos.sh
    ```
3.  **Find the installer:**
    -   The DMG will be in the `dist` folder.

## Privacy

All transcription happens locally on your Mac. No audio or text is sent to external servers. Your privacy is protected.

---

**Built with ❤️ for macOS users**

*Fast, private, local speech-to-text*
