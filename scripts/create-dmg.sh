#!/bin/bash
#
# This script creates a professional DMG installer for the hyprwhspr.app bundle.
# It correctly handles permissions to avoid the need for sudo.
#

set -e

echo "==================================================="
echo "Creating Professional DMG Installer for hyprwhspr"
echo "==================================================="

# --- Configuration ---
APP_NAME="hyprwhspr.app"
VOL_NAME="hyprwhspr"
FINAL_DMG_NAME="hyprwhspr-installer.dmg"

# Get project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$REPO_DIR"

# Paths
BUILD_DIR="dist"
APP_PATH="$BUILD_DIR/$APP_NAME"
FINAL_DMG_PATH="$BUILD_DIR/$FINAL_DMG_NAME"
TEMP_DMG_PATH="$BUILD_DIR/temp_$(date +%s).dmg"

# Check if the app bundle exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: $APP_NAME not found in $BUILD_DIR." >&2
    echo "Please run the build script first: ./scripts/build-macos.sh" >&2
    exit 1
fi

echo "App bundle found at: $APP_PATH"

# Clean up old DMG
rm -f "$FINAL_DMG_PATH"

# --- Create a user-owned temporary disk image ---
# This is the key fix. By using -uid and -gid, we create a disk image
# that is owned by the current user, avoiding all permission errors.
USER_ID=$(id -u)
GROUP_ID=$(id -g)

echo "Creating temporary disk image (owned by user $USER_ID)..."
hdiutil create -size 500m \
               -fs HFS+ \
               -volname "$VOL_NAME" \
               -uid "$USER_ID" \
               -gid "$GROUP_ID" \
               -mode 775 \
               "$TEMP_DMG_PATH"

# Mount the disk image
echo "Mounting temporary disk image..."
MOUNT_DIR=$(hdiutil attach "$TEMP_DMG_PATH" -nobrowse -noverify -noautofsck | grep '/Volumes/' | awk 'NR==1{print $3}')
echo "Mounted at: $MOUNT_DIR"

# Copy the application and create a link to /Applications
echo "Copying application files..."
cp -R "$APP_PATH" "$MOUNT_DIR/"
ln -s /Applications "$MOUNT_DIR/Applications"

# --- Customize the DMG Window using AppleScript ---
echo "Customizing DMG window appearance..."
sleep 2 # Give the Finder a moment to catch up

osascript <<EOD
tell application "Finder"
  tell disk "'$VOL_NAME'"
    open
    set current view of container window to icon view
    set toolbar visible of container window to false
    set statusbar visible of container window to false
    set the bounds of container window to {400, 100, 950, 450}
    set theViewOptions to the icon view options of container window
    set arrangement of theViewOptions to not arranged
    set icon size of theViewOptions to 96
    set position of item "'$APP_NAME'" of container window to {150, 175}
    set position of item "Applications" of container window to {400, 175}
    update without registering applications
    delay 1
    close
  end tell
end tell
EOD

# Unmount the disk image
echo "Unmounting disk image..."
hdiutil detach "$MOUNT_DIR" -force

# Convert to a compressed, read-only final DMG
echo "Creating final compressed DMG..."
hdiutil convert "$TEMP_DMG_PATH" -format UDZO -imagekey zlib-level=9 -o "$FINAL_DMG_PATH"

# Clean up temporary file
rm -f "$TEMP_DMG_PATH"

echo ""
echo "✓ Professional DMG installer created successfully!"
echo "  Path: $FINAL_DMG_PATH"
echo ""
echo "Please run the installer to test:"
echo "open $FINAL_DMG_PATH"
echo ""
