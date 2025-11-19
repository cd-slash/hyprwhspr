#!/bin/bash
#
# hyprwhspr build script for macOS using PyInstaller
# This script creates a self-contained hyprwhspr.app bundle.
#

set -e # Exit on error

echo "=============================================="
echo "hyprwhspr macOS Build Script (PyInstaller)"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}ERROR: This script is for macOS only${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Running on macOS"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3 from python.org or using Homebrew."
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Get project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
echo "Project directory: $REPO_DIR"
cd "$REPO_DIR"

# Create and activate virtual environment
echo ""
echo "Setting up Python virtual environment..."
VENV_DIR="$REPO_DIR/venv-build"
if [ -d "$VENV_DIR" ]; then
    echo "Using existing virtual environment."
else
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi
source "$VENV_DIR/bin/activate"

# Install/upgrade dependencies
echo ""
echo "Installing/upgrading dependencies..."
pip install --upgrade pip
pip install -r "$REPO_DIR/requirements.txt"
pip install pyinstaller
echo -e "${GREEN}✓${NC} Dependencies installed"

# --- Build the application with PyInstaller ---
echo ""
echo "Building hyprwhspr.app with PyInstaller..."

# Clean previous builds
rm -rf build dist hyprwhspr.spec

# PyInstaller arguments
APP_NAME="hyprwhspr"
ENTRY_POINT="lib/main.py"
ICON_FILE="share/icons/hyprwhspr.icns" # Optional: specify an icon

# Add assets and libraries to be bundled
# PyInstaller's --add-data format is "SOURCE:DESTINATION"
ASSETS_DIR="share/assets"
PYWHISPERCPP_LIB_PATH=$(python -c "import pywhispercpp; from pathlib import Path; print(Path(pywhispercpp.__file__).parent / 'libwhisper.dylib')")
SOUNDDEVICE_LIB_PATH=$(python -c "import sounddevice; from pathlib import Path; print(next(Path(sounddevice.__file__).parent.glob('_sounddevice_data/portaudio-binaries/*.dylib')))")

pyinstaller --name "$APP_NAME" \
            --windowed \
            --noconfirm \
            --hidden-import "pyobjc-framework-Quartz" \
            --hidden-import "pyobjc-framework-Cocoa" \
            --hidden-import "pyobjc-core" \
            --add-data "$ASSETS_DIR:assets" \
            --add-binary "$PYWHISPERCPP_LIB_PATH:." \
            --add-binary "$SOUNDDEVICE_LIB_PATH:." \
            "$ENTRY_POINT"

if [ -d "dist/$APP_NAME.app" ]; then
    echo -e "${GREEN}✓${NC} hyprwhspr.app built successfully in 'dist' folder."
else
    echo -e "${RED}ERROR: Failed to build hyprwhspr.app${NC}"
    exit 1
fi

# Deactivate virtual environment
deactivate
echo ""
echo "Build process complete."
echo "You can now create a DMG installer or run the app directly from the 'dist' folder."
