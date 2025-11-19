# Troubleshooting Globe/Fn Key on macOS

If the globe/fn key isn't working, follow these steps:

## Step 1: Verify Accessibility Permissions

**This is the most common issue!**

1. Open **System Preferences** (or **System Settings** on macOS 13+)
2. Go to **Security & Privacy** > **Privacy** tab
3. Select **Accessibility** from the left sidebar
4. Click the 🔒 lock icon and enter your password
5. Look for your terminal app (Terminal, iTerm2, etc.) or Python
6. If it's not in the list, click **+** and add it
7. **Make sure the checkbox next to it is CHECKED**
8. If it was already there, try:
   - Unchecking it, then checking it again
   - Removing it and re-adding it
9. Close System Preferences
10. **Restart hyprwhspr**

## Step 2: Run the Diagnostic Tool

We've included a diagnostic tool to help identify the issue:

```bash
cd /path/to/hyprwhspr

# If using the virtual environment
source ~/.local/share/hyprwhspr/venv/bin/activate

# Run the diagnostic
python3 scripts/test-macos-globe-key.py
```

This will:
- Check if accessibility permissions are granted
- Monitor keyboard events
- Show you the keycode when you press the globe/fn key
- Help identify if the key is being detected

**What to do:**
1. Run the script
2. Press various keys including the globe/fn key
3. Look for output showing the keycode
4. Take note of what keycode appears when you press globe/fn

## Step 3: Check Your Keyboard Type

Different Mac keyboards have different keys:

### Newer Macs (M1/M2, 2021+)
- Have a **🌐 globe key** in the bottom left
- This replaced the traditional Fn key
- Should be keycode **63 (0x3F)**

### Older Macs (Intel, pre-2021)
- Have a traditional **fn key** in the bottom left
- Should be keycode **63 (0x3F)**

### External/Third-party Keyboards
- May not have a globe/fn key at all
- Consider using a different key combination (see Step 4)

## Step 4: Try a Different Key Combination

If the globe key isn't working, you can use any other key combination.

Edit `~/.config/hyprwhspr/config.json`:

```json
{
    "primary_shortcut": "cmd+shift+d"
}
```

**Popular alternatives:**
- `"cmd+shift+d"` - Command+Shift+D
- `"f12"` - F12 key
- `"cmd+shift+space"` - Command+Shift+Space
- `"ctrl+option+d"` - Control+Option+D

Then restart hyprwhspr.

## Step 5: Verify hyprwhspr is Running

Check if the process is running:

```bash
ps aux | grep hyprwhspr
```

If you see it running, you should see output like:
```
you    12345  ...  python3 .../hyprwhspr/lib/main.py
```

If not running, start it:
```bash
~/.local/share/hyprwhspr/hyprwhspr-launch.sh
```

Check the logs for errors:
```bash
tail -f ~/Library/Logs/hyprwhspr.log
```

## Step 6: Check Python Version

Make sure you're using Python 3.8 or later:

```bash
python3 --version
```

Should show: `Python 3.8.x` or higher

## Step 7: Verify PyObjC Installation

The macOS modules require PyObjC:

```bash
source ~/.local/share/hyprwhspr/venv/bin/activate
pip list | grep pyobjc
```

You should see:
```
pyobjc-core             9.x.x
pyobjc-framework-Cocoa  9.x.x
pyobjc-framework-Quartz 9.x.x
```

If missing, reinstall:
```bash
pip install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz
```

## Common Issues and Solutions

### Issue: "Event tap not created"
**Solution:** Grant accessibility permissions (see Step 1)

### Issue: Globe key presses not detected
**Solutions:**
1. Run diagnostic tool (Step 2)
2. Try holding the key for 1 second
3. Try a different key combination (Step 4)
4. Check if your keyboard actually has a globe/fn key

### Issue: Text doesn't appear after speaking
**Solutions:**
1. Make sure you press globe key TWICE (once to start, once to stop)
2. Check that the target app accepts paste (Cmd+V)
3. Check logs: `tail -f ~/Library/Logs/hyprwhspr.log`

### Issue: "No module named 'Cocoa'" or "No module named 'Quartz'"
**Solution:** Install PyObjC (see Step 7)

### Issue: hyprwhspr won't start
**Solutions:**
1. Check logs: `tail -f ~/Library/Logs/hyprwhspr-error.log`
2. Try running manually to see errors:
   ```bash
   source ~/.local/share/hyprwhspr/venv/bin/activate
   cd ~/.local/share/hyprwhspr
   python3 lib/main.py
   ```
3. Check Python version (Step 6)
4. Reinstall: `./scripts/install-macos.sh`

## Still Not Working?

If you've tried all the above and it's still not working:

1. **Collect diagnostic info:**
   ```bash
   # System info
   sw_vers

   # Python version
   python3 --version

   # Run diagnostic and save output
   python3 scripts/test-macos-globe-key.py > diagnostic-output.txt 2>&1

   # Get logs
   tail -100 ~/Library/Logs/hyprwhspr.log > hyprwhspr-recent.log
   ```

2. **Open an issue** on GitHub with:
   - Your macOS version
   - Python version
   - Output from diagnostic tool
   - Any error messages from logs
   - Keyboard model/type

## Quick Test Without Globe Key

To quickly test if everything else works, use F12 as the toggle:

```bash
# Edit config
nano ~/.config/hyprwhspr/config.json
# Change "primary_shortcut" to "f12"

# Restart
pkill -f hyprwhspr
~/.local/share/hyprwhspr/hyprwhspr-launch.sh
```

Then press F12 to toggle dictation. If this works, the issue is specifically with globe key detection.
