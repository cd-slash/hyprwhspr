#!/usr/bin/env python3
"""
Wrapper script for hyprwhspr that properly sets up environment
This ensures the process shows as hyprwhspr, not python
"""

import os
import sys
from pathlib import Path

# Set up environment
home = Path.home()
install_dir = home / ".local/share/hyprwhspr"
venv_dir = install_dir / "venv"

# Activate virtual environment by modifying sys.path
venv_site_packages = venv_dir / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
if venv_site_packages.exists():
    sys.path.insert(0, str(venv_site_packages))

# Change to install directory
os.chdir(install_dir)

# Set environment variables
os.environ['VIRTUAL_ENV'] = str(venv_dir)
if 'PYTHONHOME' in os.environ:
    del os.environ['PYTHONHOME']

# Add lib directory to path
sys.path.insert(0, str(install_dir / "lib"))

# Import and run main
os.chdir(install_dir / "lib")
with open(install_dir / "lib" / "main.py") as f:
    code = compile(f.read(), "main.py", 'exec')
    exec(code)
