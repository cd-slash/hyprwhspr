#!/bin/bash
#
# hyprwhspr installation script for macOS
# This script sets up hyprwhspr for voice dictation with globe/fn key toggle
#

set -e  # Exit on error

echo "=================================="
echo "hyprwhspr macOS Installation"
echo "=================================="
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
echo "Installation directory: $REPO_DIR"
echo ""

# Create installation directories
INSTALL_DIR="$HOME/.local/share/hyprwhspr"
CONFIG_DIR="$HOME/.config/hyprwhspr"
MODEL_DIR="$HOME/.local/share/pywhispercpp/models"

echo "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$MODEL_DIR"
mkdir -p "$INSTALL_DIR/temp"

echo -e "${GREEN}✓${NC} Directories created"

# Copy application files
echo ""
echo "Copying application files..."
cp -r "$REPO_DIR/lib" "$INSTALL_DIR/"
cp -r "$REPO_DIR/share" "$INSTALL_DIR/" 2>/dev/null || true

echo -e "${GREEN}✓${NC} Application files copied"

# Create and activate virtual environment
echo ""
echo "Setting up Python virtual environment..."
VENV_DIR="$INSTALL_DIR/venv"

if [ -d "$VENV_DIR" ]; then
    echo "Removing existing virtual environment..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo -e "${GREEN}✓${NC} Virtual environment created"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r "$REPO_DIR/requirements.txt"

echo -e "${GREEN}✓${NC} Dependencies installed"

# Download Whisper model
echo ""
echo "Checking for Whisper model..."
MODEL_FILE="$MODEL_DIR/ggml-base.en.bin"

if [ -f "$MODEL_FILE" ]; then
    echo -e "${GREEN}✓${NC} Whisper model already exists"
else
    echo "Downloading Whisper base.en model (~148MB)..."
    curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin" \
         -o "$MODEL_FILE" \
         --progress-bar

    if [ -f "$MODEL_FILE" ]; then
        echo -e "${GREEN}✓${NC} Model downloaded successfully"
    else
        echo -e "${YELLOW}WARNING: Failed to download model${NC}"
        echo "You can manually download it later with:"
        echo "  curl -L 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin' -o '$MODEL_FILE'"
    fi
fi

# Create default config
echo ""
echo "Creating configuration..."
CONFIG_FILE="$CONFIG_DIR/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
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
EOF
    echo -e "${GREEN}✓${NC} Configuration file created"
else
    echo -e "${GREEN}✓${NC} Configuration file already exists"
fi

# Create launch script
echo ""
echo "Creating launch script..."
LAUNCH_SCRIPT="$INSTALL_DIR/hyprwhspr-launch.sh"

cat > "$LAUNCH_SCRIPT" << 'EOF'
#!/bin/bash
# hyprwhspr launcher for macOS

INSTALL_DIR="$HOME/.local/share/hyprwhspr"
VENV_DIR="$INSTALL_DIR/venv"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run hyprwhspr
cd "$INSTALL_DIR"
python3 "$INSTALL_DIR/lib/main.py"
EOF

chmod +x "$LAUNCH_SCRIPT"
echo -e "${GREEN}✓${NC} Launch script created"

# Create LaunchAgent plist for auto-start (optional)
LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENT_DIR/com.hyprwhspr.agent.plist"

mkdir -p "$LAUNCH_AGENT_DIR"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hyprwhspr.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$LAUNCH_SCRIPT</string>
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

echo -e "${GREEN}✓${NC} LaunchAgent plist created"

# Installation complete
echo ""
echo "=================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=================================="
echo ""
echo "Important: Accessibility Permissions Required"
echo ""
echo "To use hyprwhspr, you need to grant accessibility permissions:"
echo ""
echo "  1. Open System Preferences > Security & Privacy > Privacy"
echo "  2. Select 'Accessibility' from the left sidebar"
echo "  3. Click the lock icon to make changes"
echo "  4. Add Terminal (or your terminal app) to the list"
echo "  5. Check the box next to it"
echo ""
echo "Usage:"
echo ""
echo "  Start manually:"
echo "    $LAUNCH_SCRIPT"
echo ""
echo "  Start automatically on login:"
echo "    launchctl load $PLIST_FILE"
echo ""
echo "  Stop auto-start:"
echo "    launchctl unload $PLIST_FILE"
echo ""
echo "Configuration file:"
echo "  $CONFIG_FILE"
echo ""
echo "Default toggle key: Globe/Fn key"
echo ""
echo "To change the toggle key, edit the config file and set 'primary_shortcut'"
echo "Examples:"
echo "  - 'fn' or 'globe' - Globe/Fn key (default)"
echo "  - 'f12' - F12 key"
echo "  - 'cmd+shift+d' - Command+Shift+D"
echo ""
echo -e "${GREEN}Press the Globe/Fn key to toggle dictation on/off!${NC}"
echo ""
