#!/bin/bash
#
# Create a macOS app bundle for hyprwhspr
# This makes it appear as "hyprwhspr" in System Preferences instead of "python"
#

set -e

echo "Creating hyprwhspr.app bundle..."

# Paths
APP_NAME="hyprwhspr"
APP_BUNDLE="$HOME/Applications/${APP_NAME}.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
INSTALL_DIR="$HOME/.local/share/hyprwhspr"

# Create bundle structure
echo "Creating bundle structure..."
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"
mkdir -p "$HOME/Applications"

# Create Info.plist
echo "Creating Info.plist..."
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>hyprwhspr</string>
    <key>CFBundleIdentifier</key>
    <string>com.hyprwhspr.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>hyprwhspr</string>
    <key>CFBundleDisplayName</key>
    <string>hyprwhspr</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSMicrophoneUsageDescription</key>
    <string>hyprwhspr needs microphone access to transcribe your speech to text.</string>
    <key>NSAppleEventsUsageDescription</key>
    <string>hyprwhspr needs to send keystrokes to paste transcribed text.</string>
</dict>
</plist>
EOF

# Create launcher script
echo "Creating launcher script..."
cat > "$MACOS_DIR/hyprwhspr" << 'LAUNCHER_EOF'
#!/bin/bash

# Launcher for hyprwhspr app bundle
INSTALL_DIR="$HOME/.local/share/hyprwhspr"

# Change to install directory
cd "$INSTALL_DIR"

# Activate virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# Run hyprwhspr
exec python3 "$INSTALL_DIR/lib/main.py"
LAUNCHER_EOF

chmod +x "$MACOS_DIR/hyprwhspr"

# Update LaunchAgent to use the app bundle
echo "Creating/updating LaunchAgent..."
cat > "$HOME/Library/LaunchAgents/com.hyprwhspr.agent.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hyprwhspr.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$APP_BUNDLE/Contents/MacOS/hyprwhspr</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ProcessType</key>
    <string>Interactive</string>
    <key>LimitLoadToSessionType</key>
    <string>Aqua</string>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/hyprwhspr.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/hyprwhspr-error.log</string>
</dict>
</plist>
EOF

echo ""
echo "✅ App bundle created at: $APP_BUNDLE"
echo ""
echo "Next steps:"
echo ""
echo "1. Unload existing LaunchAgent (if running):"
echo "   launchctl unload ~/Library/LaunchAgents/com.hyprwhspr.agent.plist 2>/dev/null"
echo ""
echo "2. Test the app manually first (to trigger permission prompt):"
echo "   open -a $APP_BUNDLE"
echo ""
echo "   Press the globe key and approve microphone access when prompted."
echo ""
echo "3. Once permissions are granted, load the LaunchAgent:"
echo "   launchctl load ~/Library/LaunchAgents/com.hyprwhspr.agent.plist"
echo ""
echo "4. Check System Preferences > Security & Privacy > Privacy:"
echo "   - Microphone: You should see 'hyprwhspr' (not 'python')"
echo "   - Accessibility: Make sure 'hyprwhspr' is listed and checked"
echo ""
