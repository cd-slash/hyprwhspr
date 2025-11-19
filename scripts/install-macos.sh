#!/bin/bash
#
# hyprwhspr build script for macOS
# This script builds the hyprwhspr.app bundle and creates a DMG installer.
#

set -e # Exit on error

echo "======================================"
echo "hyprwhspr macOS Build Script"
echo "======================================"
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
    echo "Please install Python 3 from python.org or using Homebrew:"
    echo "  brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python 3 found: $PYTHON_VERSION"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo ""
echo "Project directory: $REPO_DIR"
echo ""

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
VENV_DIR="$REPO_DIR/venv-build"

if [ -d "$VENV_DIR" ]; then
    echo "Using existing virtual environment."
else
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

source "$VENV_DIR/bin/activate"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing build dependencies..."
pip install -r "$REPO_DIR/requirements.txt"
pip install py2app

echo -e "${GREEN}✓${NC} Dependencies installed"

# Build the application
echo ""
echo "Building hyprwhspr.app..."
cd "$REPO_DIR"
python3 setup.py py2app

if [ -d "dist/hyprwhspr.app" ]; then
    echo -e "${GREEN}✓${NC} hyprwhspr.app built successfully"
else
    echo -e "${RED}ERROR: Failed to build hyprwhspr.app${NC}"
    exit 1
fi

# Create DMG installer
echo ""
echo "Creating DMG installer..."
BUILD_DIR="$REPO_DIR/dist"
DMG_NAME="hyprwhspr-installer.dmg"
DMG_PATH="$BUILD_DIR/$DMG_NAME"
APP_NAME="hyprwhspr.app"

# Remove old DMG if it exists
if [ -f "$DMG_PATH" ]; then
    rm "$DMG_PATH"
fi

# Create a temporary directory for the DMG content
DMG_CONTENT_DIR=$(mktemp -d)
cp -R "$BUILD_DIR/$APP_NAME" "$DMG_CONTENT_DIR/"
ln -s /Applications "$DMG_CONTENT_DIR/Applications"

# Create the DMG
hdiutil create -volname "hyprwhspr" -srcfolder "$DMG_CONTENT_DIR" -ov -format UDZO "$DMG_PATH"

# Clean up
rm -rf "$DMG_CONTENT_DIR"

if [ -f "$DMG_PATH" ]; then
    echo -e "${GREEN}✓${NC} DMG installer created at: $DMG_PATH"
else
    echo -e "${RED}ERROR: Failed to create DMG installer${NC}"
    exit 1
fi

# Deactivate virtual environment
deactivate

echo ""
echo "======================================"
echo -e "${GREEN}Build Complete!${NC}"
echo "======================================"
echo ""
echo "To install, open the DMG and drag hyprwhspr.app to your Applications folder:"
echo "  open $DMG_PATH"
echo ""
echo "After installing, you can grant microphone and accessibility permissions"
echo "by running the app and following the on-screen prompts."
echo ""
