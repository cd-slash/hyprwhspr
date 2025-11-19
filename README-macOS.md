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

1.  **Build the App:**
    -   Follow the "Building from Source" instructions below to create the `hyprwhspr-installer.dmg`.
2.  **Install the App:**
    -   Open the `dist/hyprwhspr-installer.dmg` file.
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

(Note: The `config.json` file is created the first time you run the app.)

### Change the Toggle Key

```json
{
    "primary_shortcut": "fn"
}
```

### Choose a Different Model

Download additional models and place them in:
`~/Library/Application Support/hyprwhspr/models/`

## Building from Source

If you want to build the app and installer yourself:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/goodroot/hyprwhspr.git
    cd hyprwhspr
    ```
2.  **Run the build script:**
    - This will create `hyprwhspr.app` in the `dist/` folder.
    ```bash
    ./scripts/build-macos.sh
    ```
3.  **Create the DMG installer:**
    - This will package the app into `hyprwhspr-installer.dmg` in the `dist/` folder.
    ```bash
    ./scripts/create-dmg.sh
    ```
4.  **Install the app:**
    - Open the newly created DMG and drag the app to your Applications folder.
    ```bash
    open dist/hyprwhspr-installer.dmg
    ```

## Uninstallation

1.  Drag `hyprwhspr.app` from your `Applications` folder to the Trash.
2.  (Optional) Remove the configuration and log files:
    ```bash
    rm -rf "~/Library/Application Support/hyprwhspr"
    ```

## Privacy

All transcription happens locally on your Mac. No audio or text is sent to external servers. Your privacy is protected.

---

**Built with ❤️ for macOS users**

*Fast, private, local speech-to-text*
