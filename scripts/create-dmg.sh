#!/bin/bash
#
# This script creates a professional DMG installer for the hyprwhspr.app bundle
# using the industry-standard 'create-dmg' tool.
#

set -e

echo "==================================================="
echo "Creating Professional DMG Installer for hyprwhspr"
echo "==================================================="

# --- Check for create-dmg tool ---
if ! command -v create-dmg &> /dev/null; then
    echo "ERROR: 'create-dmg' command not found." >&2
    echo "This script requires the 'create-dmg' tool." >&2
    echo "Please install it using Homebrew:" >&2
    echo "  brew install create-dmg" >&2
    exit 1
fi

echo "✓ 'create-dmg' tool found."

# --- Configuration ---
APP_NAME="hyprwhspr.app"
VOL_NAME="hyprwhspr Installer"
FINAL_DMG_NAME="hyprwhspr-installer.dmg"

# Get project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$REPO_DIR"

# Paths
BUILD_DIR="dist"
APP_PATH="$BUILD_DIR/$APP_NAME"
FINAL_DMG_PATH="$BUILD_DIR/$FINAL_DMG_NAME"

# Check if the app bundle exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: $APP_NAME not found in $BUILD_DIR." >&2
    echo "Please run the build script first: ./scripts/build-macos.sh" >&2
    exit 1
fi

echo "App bundle found at: $APP_PATH"

# Clean up old DMG
rm -f "$FINAL_DMG_PATH"

# --- Create the DMG using the create-dmg tool ---
echo "Creating DMG with 'create-dmg'..."

create-dmg \
  --volname "$VOL_NAME" \
  --window-pos 200 120 \
  --window-size 600 420 \
  --icon-size 100 \
  --icon "$APP_NAME" 175 180 \
  --hide-extension "$APP_NAME" \
  --app-drop-link 425 180 \
  "$FINAL_DMG_PATH" \
  "$BUILD_DIR/"

echo ""
echo "✓ Professional DMG installer created successfully!"
echo "  Path: $FINAL_DMG_PATH"
echo ""
echo "To install, run:"
echo "open $FINAL_DMG_PATH"
echo ""
