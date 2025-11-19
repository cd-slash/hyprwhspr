#!/bin/bash
#
# This script creates a DMG installer for the hyprwhspr.app bundle.
# It should be run after the main build script (build-macos.sh).
#

set -e

echo "========================================"
echo "Creating DMG Installer for hyprwhspr"
echo "========================================"

# Get project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$REPO_DIR"

BUILD_DIR="$REPO_DIR/dist"
APP_NAME="hyprwhspr.app"
APP_PATH="$BUILD_DIR/$APP_NAME"
DMG_NAME="hyprwhspr-installer.dmg"
DMG_PATH="$BUILD_DIR/$DMG_NAME"

# Check if the app bundle exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: $APP_NAME not found in $BUILD_DIR."
    echo "Please run the build script first: ./scripts/build-macos.sh"
    exit 1
fi

echo "App bundle found at: $APP_PATH"

# Remove old DMG if it exists
if [ -f "$DMG_PATH" ]; then
    echo "Removing existing DMG..."
    rm "$DMG_PATH"
fi

# Create a temporary directory for the DMG content
echo "Creating temporary directory for DMG content..."
DMG_CONTENT_DIR=$(mktemp -d)
cp -R "$APP_PATH" "$DMG_CONTENT_DIR/"
ln -s /Applications "$DMG_CONTENT_DIR/Applications"

# Create the DMG
echo "Creating DMG..."
hdiutil create -volname "hyprwhspr Installer" \
               -srcfolder "$DMG_CONTENT_DIR" \
               -ov \
               -format UDZO \
               "$DMG_PATH"

# Clean up
echo "Cleaning up..."
rm -rf "$DMG_CONTENT_DIR"

if [ -f "$DMG_PATH" ]; then
    echo "✓ DMG installer created successfully at: $DMG_PATH"
else
    echo "Error: Failed to create DMG installer."
    exit 1
fi

echo ""
echo "To install, open the DMG and drag the app to your Applications folder:"
echo "open $DMG_PATH"
echo ""
