# hyprwhspr for macOS

This document provides instructions for building and installing the macOS version of `hyprwhspr`.

## Build and Installation

Follow these steps to build the application and create an installer.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/goodroot/hyprwhspr.git
    cd hyprwhspr
    ```

2.  **Set up the build environment:**
    -   This creates a local Python environment and installs the required tools.
    ```bash
    python3 -m venv venv-build
    source venv-build/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller create-dmg
    ```

3.  **Build the application:**
    -   This uses the `hyprwhspr.spec` file to create a valid macOS application in `dist/`.
    ```bash
    pyinstaller hyprwhspr.spec
    ```

4.  **Create the DMG installer:**
    -   This packages the app into a professional installer.
    ```bash
    ./scripts/create-dmg.sh
    ```

5.  **Install the application:**
    -   Open the newly created DMG and drag the app to your `Applications` folder.
    ```bash
    open dist/hyprwhspr-installer.dmg
    ```

## First Run and Permissions

Because the application is not signed by a registered Apple Developer, you must follow these steps to run it for the first time.

1.  **Open from the Finder:**
    -   Go to your `Applications` folder.
    -   **Right-click** (or Control-click) on `hyprwhspr.app` and select **Open** from the menu.
2.  **Confirm You Want to Open:**
    -   A dialog will appear warning you that the developer cannot be verified. This is expected.
    -   Click the **Open** button to proceed.
3.  **Grant Permissions:**
    -   The app will then prompt for **Microphone** and **Accessibility** permissions. Please approve both.

You only need to do this once. After the first successful launch, you can open the app normally.
