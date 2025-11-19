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

# --- Robustly find library paths ---
echo ""
echo "Locating required native libraries..."
SITE_PACKAGES_PATH=$(python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
PYWHISPERCPP_LIB_PATH=$(find "$SITE_PACKAGES_PATH" -name "libwhisper.dylib" | head -n 1)
SOUNDDEVICE_LIB_PATH=$(find "$SITE_PACKAGES_PATH" -name "*portaudio*.dylib" | head -n 1)

# Check if libraries were found
if [ -z "$PYWHISPERCPP_LIB_PATH" ]; then
    echo -e "${RED}ERROR: libwhisper.dylib not found in the Python environment. Build failed.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Found libwhisper.dylib: $PYWHISPERCPP_LIB_PATH"

if [ -z "$SOUNDDEVICE_LIB_PATH" ]; then
    echo -e "${RED}ERROR: PortAudio library not found in the Python environment. Build failed.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Found PortAudio library: $SOUNDDEVICE_LIB_PATH"


# --- Build the application with PyInstaller ---
echo ""
echo "Building hyprwhspr.app with PyInstaller..."

# Clean previous builds
rm -rf build dist hyprwhspr.spec

# PyInstaller arguments
APP_NAME="hyprwhspr"
ENTRY_POINT="lib/main.py"
ASSETS_DIR="share/assets"

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
echo "You can now run the app from 'dist' or create an installer with './scripts/create-dmg.sh'"
