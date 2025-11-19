# hyprwhspr for macOS

This document provides instructions for building, installing, and troubleshooting the macOS version of `hyprwhspr`.

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
    -   This uses the `hyprwhspr.spec` file to create a macOS application in `dist/`.
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

Because the application is unsigned, you must follow these steps to run it the first time:

1.  Go to your `Applications` folder.
2.  **Right-click** on `hyprwhspr.app` and select **Open**.
3.  A dialog will warn you that the developer is unverified. Click **Open** to continue.
4.  The app will then prompt for **Microphone** and **Accessibility** permissions. Please approve both.

You only need to right-click the first time. Afterwards, you can launch it normally.

---

## **Troubleshooting: If the App Fails to Launch**

If the application closes silently or does not open, follow these steps to get a detailed error message.

1.  **Open your Terminal.**

2.  **Run the application's internal executable directly.** Copy and paste the following command into your terminal and press Enter:
    ```bash
    /Applications/hyprwhspr.app/Contents/MacOS/hyprwhspr
    ```

3.  **Capture the output.** The terminal will display a detailed error message showing exactly why the application is failing.

4.  **Report the error.** Please copy the full error message from the terminal and provide it so we can issue a final fix.
