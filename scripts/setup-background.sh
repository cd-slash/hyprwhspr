#!/bin/bash
#
# Quick setup script to install hyprwhspr for background running
#

set -e

echo "Setting up hyprwhspr for background operation..."

# Get the repo directory (where this script is)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Repository: $REPO_DIR"
echo "Home: $HOME"

# Create directories
INSTALL_DIR="$HOME/.local/share/hyprwhspr"
CONFIG_DIR="$HOME/.config/hyprwhspr"

echo ""
echo "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$HOME/Library/Logs"

# Copy application files
echo "Copying application files..."
cp -r "$REPO_DIR/lib" "$INSTALL_DIR/"
cp -r "$REPO_DIR/share" "$INSTALL_DIR/" 2>/dev/null || echo "No share directory, skipping"

# Create launch script
echo "Creating launch script..."
cat > "$INSTALL_DIR/hyprwhspr-launch.sh" << 'EOF'
#!/bin/bash
# hyprwhspr launcher for macOS

INSTALL_DIR="$HOME/.local/share/hyprwhspr"
cd "$INSTALL_DIR"

# Activate virtual environment if it exists, otherwise use system python
if [ -d "$INSTALL_DIR/venv" ]; then
    source "$INSTALL_DIR/venv/bin/activate"
fi

# Run hyprwhspr
exec python3 "$INSTALL_DIR/lib/main.py"
EOF

chmod +x "$INSTALL_DIR/hyprwhspr-launch.sh"

# Create LaunchAgent plist
echo "Creating LaunchAgent..."
cat > "$HOME/Library/LaunchAgents/com.hyprwhspr.agent.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hyprwhspr.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$INSTALL_DIR/hyprwhspr-launch.sh</string>
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

# Create config if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    echo "Creating default config..."
    cat > "$CONFIG_DIR/config.json" << 'CONFIGEOF'
{
  "primary_shortcut": "fn",
  "model": "base.en",
  "threads": 4,
  "language": null,
  "word_overrides": {},
  "whisper_prompt": "Transcribe with proper capitalization, including sentence beginnings, proper nouns, titles, and standard English capitalization rules.",
  "clipboard_behavior": false,
  "clipboard_clear_delay": 5.0,
  "paste_mode": "super",
  "audio_feedback": true,
  "start_sound_volume": 0.3,
  "stop_sound_volume": 0.3
}
CONFIGEOF
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "To start now:"
echo "  launchctl load ~/Library/LaunchAgents/com.hyprwhspr.agent.plist"
echo ""
echo "Or run manually:"
echo "  $INSTALL_DIR/hyprwhspr-launch.sh"
echo ""
echo "View logs:"
echo "  tail -f ~/Library/Logs/hyprwhspr.log"
