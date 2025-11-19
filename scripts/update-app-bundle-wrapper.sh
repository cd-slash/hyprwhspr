#!/bin/bash
#
# Update the app bundle to use Python wrapper instead of bash script
#

set -e

APP_BUNDLE="$HOME/Applications/hyprwhspr.app"
MACOS_DIR="$APP_BUNDLE/Contents/MacOS"
INSTALL_DIR="$HOME/.local/share/hyprwhspr"
VENV_PYTHON="$INSTALL_DIR/venv/bin/python3"

echo "Updating app bundle wrapper..."

# Create the wrapper using the venv python
cat > "$MACOS_DIR/hyprwhspr" << 'EOF'
#!/usr/bin/env python3
"""
Wrapper for hyprwhspr app bundle
"""
import os
import sys
from pathlib import Path

# Set up paths
home = Path.home()
install_dir = home / ".local/share/hyprwhspr"
venv_python = install_dir / "venv" / "bin" / "python3"

# Use venv python to run with proper environment
os.execv(str(venv_python), [str(venv_python), str(install_dir / "lib" / "main.py")])
EOF

chmod +x "$MACOS_DIR/hyprwhspr"

# Update the shebang to use the venv python
sed -i '' "1s|.*|#!$VENV_PYTHON|" "$MACOS_DIR/hyprwhspr"

echo "✅ App bundle updated"
echo ""
echo "Test it:"
echo "  open -a $APP_BUNDLE"
