"""
Text injector for hyprwhspr on macOS
Handles injecting transcribed text using Cocoa APIs and pasteboard
"""

import time
import threading
import subprocess
from typing import Optional
from AppKit import NSPasteboard, NSStringPboardType
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    CGEventSetFlags,
    kCGEventKeyDown,
    kCGEventKeyUp,
    kCGHIDEventTap,
    kCGEventFlagMaskCommand,
)


class TextInjector:
    """Handles injecting text into focused applications on macOS"""

    def __init__(self, config_manager=None):
        # Configuration
        self.config_manager = config_manager

        # macOS keycodes
        self.KEY_V = 0x09  # V key

        print("✓ macOS text injector initialized")

    def _clear_clipboard(self):
        """Clear the clipboard by setting it to empty content"""
        try:
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            print("📋 Clipboard cleared")
        except Exception as e:
            print(f"Warning: Could not clear clipboard: {e}")

    def _schedule_clipboard_clear(self, delay: float):
        """Schedule clipboard clearing after the specified delay"""
        def clear_after_delay():
            time.sleep(delay)
            self._clear_clipboard()
            print(f"📋 Clipboard cleared after {delay}s delay")

        # Run in a separate thread to avoid blocking
        clear_thread = threading.Thread(target=clear_after_delay, daemon=True)
        clear_thread.start()

    # ------------------------ Public API ------------------------

    def inject_text(self, text: str) -> bool:
        """
        Inject text into the currently focused application

        Args:
            text: Text to inject

        Returns:
            True if successful, False otherwise
        """
        if not text or text.strip() == "":
            print("No text to inject (empty or whitespace)")
            return True

        # Preprocess and add trailing space
        processed_text = self._preprocess_text(text).rstrip("\r\n") + ' '

        try:
            # Use clipboard + paste method
            success = self._inject_via_clipboard_and_paste(processed_text)

            # Check if clipboard clearing is enabled
            if success and self.config_manager:
                clipboard_behavior = self.config_manager.get_setting('clipboard_behavior', False)
                if clipboard_behavior:
                    clear_delay = self.config_manager.get_setting('clipboard_clear_delay', 5.0)
                    self._schedule_clipboard_clear(clear_delay)

            return success

        except Exception as e:
            print(f"Text injection failed: {e}")
            return False

    # ------------------------ Helpers ------------------------

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text to handle common speech-to-text corrections
        """
        import re

        # Normalize line breaks to spaces to avoid unintended "Enter"
        processed = text.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')

        # Apply user-defined overrides first
        processed = self._apply_word_overrides(processed)

        # Built-in speech-to-text replacements
        replacements = {
            r'\bperiod\b': '.',
            r'\bcomma\b': ',',
            r'\bquestion mark\b': '?',
            r'\bexclamation mark\b': '!',
            r'\bcolon\b': ':',
            r'\bsemicolon\b': ';',
            r'\bnew line\b': '\n',
            r'\btab\b': '\t',
            r'\bdash\b': '-',
            r'\bunderscore\b': '_',
            r'\bopen paren\b': '(',
            r'\bclose paren\b': ')',
            r'\bopen bracket\b': '[',
            r'\bclose bracket\b': ']',
            r'\bopen brace\b': '{',
            r'\bclose brace\b': '}',
            r'\bat symbol\b': '@',
            r'\bhash\b': '#',
            r'\bdollar sign\b': '$',
            r'\bpercent\b': '%',
            r'\bcaret\b': '^',
            r'\bampersand\b': '&',
            r'\basterisk\b': '*',
            r'\bplus\b': '+',
            r'\bequals\b': '=',
            r'\bless than\b': '<',
            r'\bgreater than\b': '>',
            r'\bslash\b': '/',
            r'\bbackslash\b': r'\\',
            r'\bpipe\b': '|',
            r'\btilde\b': '~',
            r'\bgrave\b': '`',
            r'\bquote\b': '"',
            r'\bapostrophe\b': "'",
        }

        for pattern, replacement in replacements.items():
            processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)

        # Collapse runs of whitespace, preserve intentional newlines
        processed = re.sub(r'[ \t]+', ' ', processed)
        processed = re.sub(r' *\n *', '\n', processed)
        processed = processed.strip()

        return processed

    def _apply_word_overrides(self, text: str) -> str:
        """Apply user-defined word overrides to the text"""
        import re

        if not self.config_manager:
            return text

        word_overrides = self.config_manager.get_word_overrides()
        if not word_overrides:
            return text

        processed = text
        for original, replacement in word_overrides.items():
            if original and replacement:
                pattern = r'\b' + re.escape(original) + r'\b'
                processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)

        return processed

    # ------------------------ macOS-specific backends ------------------------

    def _inject_via_clipboard_and_paste(self, text: str) -> bool:
        """Copy text to clipboard and simulate Cmd+V to paste"""
        try:
            # 1) Copy text to clipboard using NSPasteboard
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            pasteboard.setString_forType_(text, NSStringPboardType)

            # Small delay to ensure clipboard is updated
            time.sleep(0.1)

            # 2) Simulate Cmd+V keystroke using Quartz
            self._press_cmd_v()

            print(f"✅ Text injected via clipboard+paste")
            return True

        except Exception as e:
            print(f"Clipboard+paste injection failed: {e}")
            # Try AppleScript fallback
            return self._inject_via_applescript(text)

    def _press_cmd_v(self):
        """Simulate pressing Cmd+V using Quartz CGEvent"""
        try:
            # Create key down event for V
            key_down = CGEventCreateKeyboardEvent(None, self.KEY_V, True)
            # Set Command flag
            CGEventSetFlags(key_down, kCGEventFlagMaskCommand)
            # Post the key down event
            CGEventPost(kCGHIDEventTap, key_down)

            # Small delay between down and up
            time.sleep(0.05)

            # Create key up event for V
            key_up = CGEventCreateKeyboardEvent(None, self.KEY_V, False)
            CGEventSetFlags(key_up, kCGEventFlagMaskCommand)
            CGEventPost(kCGHIDEventTap, key_up)

        except Exception as e:
            print(f"Error simulating Cmd+V: {e}")
            raise

    def _inject_via_applescript(self, text: str) -> bool:
        """Fallback method using AppleScript to paste text"""
        try:
            # Escape quotes and backslashes for AppleScript
            escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')

            # AppleScript to set clipboard and paste
            applescript = f'''
            set the clipboard to "{escaped_text}"
            tell application "System Events"
                keystroke "v" using command down
            end tell
            '''

            # Run AppleScript
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print("✅ Text injected via AppleScript")
                return True
            else:
                print(f"AppleScript injection failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("ERROR: AppleScript command timed out")
            return False
        except Exception as e:
            print(f"ERROR: AppleScript injection failed: {e}")
            return False

    def _inject_via_applescript_keystroke(self, text: str) -> bool:
        """Type text character by character using AppleScript (slow but reliable)"""
        try:
            # Escape for AppleScript
            escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')

            applescript = f'''
            tell application "System Events"
                keystroke "{escaped_text}"
            end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=30  # Longer timeout for typing
            )

            if result.returncode == 0:
                print("✅ Text typed via AppleScript")
                return True
            else:
                print(f"AppleScript typing failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"ERROR: AppleScript typing failed: {e}")
            return False


def test_text_injection():
    """Test the text injector"""
    print("Testing macOS Text Injector")
    print("=" * 50)

    injector = TextInjector()

    test_text = "Hello from hyprwhspr on macOS!"
    print(f"Injecting test text: {test_text}")
    print("Switch to another app (like TextEdit) within 3 seconds...")

    time.sleep(3)

    success = injector.inject_text(test_text)

    if success:
        print("✓ Text injection successful")
    else:
        print("✗ Text injection failed")


if __name__ == "__main__":
    test_text_injection()
