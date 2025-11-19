#!/bin/bash
#
# Build hyprwhspr as a standalone macOS application
# This creates a proper .app bundle that shows as "hyprwhspr" (not Python)
#

set -e

echo "=========================================="
echo "Building hyprwhspr macOS Application"
echo "=========================================="
echo ""

# Get the repo directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$REPO_DIR"

# Check if venv exists
VENV_DIR="$HOME/.local/share/hyprwhspr/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating it..."
    mkdir -p "$HOME/.local/share/hyprwhspr"
    python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

echo "Installing build dependencies..."
pip install --upgrade pip
pip install py2app

echo ""
echo "Installing application dependencies..."
pip install -r requirements.txt

echo ""
echo "Building application bundle..."
python setup.py py2app

echo ""
echo "Application built successfully!"
echo ""

# Post-build: Fix PortAudio dylib location
APP_BUNDLE="$REPO_DIR/dist/hyprwhspr.app"
echo "Fixing PortAudio library location..."

# Check if python310.zip exists (it shouldn't with compressed=0, but just in case)
RESOURCES_DIR="$APP_BUNDLE/Contents/Resources"
if [ -f "$RESOURCES_DIR/lib/python310.zip" ]; then
    echo "WARNING: python310.zip exists even with compressed=0"
    echo "Extracting dylib from zip..."
    cd "$RESOURCES_DIR/lib"
    unzip -q python310.zip "_sounddevice_data/portaudio-binaries/*" 2>/dev/null || true
    cd "$REPO_DIR"
fi

# Ensure dylib is in the right place
DYLIB_SRC=$(find "$VENV_DIR/lib" -name "libportaudio*.dylib" | head -1)
if [ -n "$DYLIB_SRC" ]; then
    DYLIB_DEST_DIR="$RESOURCES_DIR/_sounddevice_data/portaudio-binaries"
    mkdir -p "$DYLIB_DEST_DIR"
    cp "$DYLIB_SRC" "$DYLIB_DEST_DIR/"
    echo "✓ PortAudio dylib copied to bundle"
else
    echo "⚠ PortAudio dylib not found in venv"
fi

echo ""

# Move to Applications
DEST_DIR="$HOME/Applications"

if [ -d "$APP_BUNDLE" ]; then
    echo "Installing to $DEST_DIR..."
    mkdir -p "$DEST_DIR"

    # Remove old version if exists
    if [ -d "$DEST_DIR/hyprwhspr.app" ]; then
        echo "Removing old version..."
        rm -rf "$DEST_DIR/hyprwhspr.app"
    fi

    cp -R "$APP_BUNDLE" "$DEST_DIR/"
    echo "✅ Installed to $DEST_DIR/hyprwhspr.app"
else
    echo "❌ Build failed - app bundle not found"
    exit 1
fi

# Update LaunchAgent
echo ""
echo "Updating LaunchAgent..."
cat > "$HOME/Library/LaunchAgents/com.hyprwhspr.agent.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hyprwhspr.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$DEST_DIR/hyprwhspr.app/Contents/MacOS/hyprwhspr</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/hyprwhspr.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/hyprwhspr-error.log</string>
</dict>
</plist>
EOF

echo "✅ LaunchAgent updated"

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Test the app manually:"
echo "   $DEST_DIR/hyprwhspr.app/Contents/MacOS/hyprwhspr"
echo ""
echo "2. Press the globe key - approve microphone permission for 'hyprwhspr'"
echo ""
echo "3. Once working, load the LaunchAgent:"
echo "   launchctl unload ~/Library/LaunchAgents/com.hyprwhspr.agent.plist 2>/dev/null"
echo "   launchctl load ~/Library/LaunchAgents/com.hyprwhspr.agent.plist"
echo ""
echo "The app will now show as 'hyprwhspr' in System Preferences!"
echo ""
