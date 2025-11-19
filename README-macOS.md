# hyprwhspr for macOS

Native speech-to-text dictation for macOS with **Globe/Fn key** toggle support.

## Features

- 🎯 **Globe/Fn Key Toggle** - Press the globe (fn) key to start/stop dictation
- 📦 **Easy Installation** - Simple DMG installer, just drag and drop
- 🔒 **Private & Local** - All transcription happens on your Mac
- ⚡ **Fast** - Powered by Whisper.cpp with GPU acceleration
- 🎤 **System-wide** - Works in any application

## Installation

1.  **Build and Install:**
    -   Follow the "Building from Source" instructions below to create and install the application.
2.  **First Run and Permissions:**
    -   Follow the "First Run" instructions to open the app for the first time and grant the necessary permissions.

## Building from Source

This is the standard way to build and install `hyprwhspr`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/goodroot/hyprwhspr.git
    cd hyprwhspr
    ```

2.  **Set up the build environment:**
    -   This will create a local Python environment and install the necessary build tools.
    ```bash
    python3 -m venv venv-build
    source venv-build/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller create-dmg
    ```

3.  **Build the application:**
    -   This uses the `hyprwhspr.spec` file to create a valid macOS application bundle in the `dist/` folder.
    ```bash
    pyinstaller hyprwhspr.spec
    ```

4.  **Create the DMG installer:**
    -   This packages the app into a professional DMG installer in the `dist/` folder.
    ```bash
    ./scripts/create-dmg.sh
    ```

5.  **Install the application:**
    -   Open the newly created DMG and drag the app to your Applications folder.
    ```bash
    open dist/hyprwhspr-installer.dmg
    ```

## First Run (Important!)

Because the application is not signed by a registered Apple Developer, you must follow these steps to run it for the first time.

1.  **Open from the Finder:**
    -   Go to your `Applications` folder.
    -   **Right-click** (or Control-click) on `hyprwhspr.app` and select **Open** from the menu.
2.  **Confirm You Want to Open:**
    -   A dialog will appear warning you that the developer cannot be verified. This is expected.
    -   Click the **Open** button to proceed.
    -   You only need to do this once. After the first successful launch, you can open the app normally.
3.  **Grant Permissions:**
    -   The app will then prompt you for **Microphone** and **Accessibility** permissions. Please approve both.

Once you've completed these steps, you can use the **Globe/Fn key** to toggle dictation.

## Uninstallation

1.  Drag `hyprwhspr.app` from your `Applications` folder to the Trash.
2.  (Optional) Remove the configuration files:
    ```bash
    rm -rf "~/Library/Application Support/hyprwhspr"
    ```
