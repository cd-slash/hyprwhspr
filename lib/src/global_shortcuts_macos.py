"""
Global shortcuts handler for hyprwhspr on macOS
Manages system-wide keyboard shortcuts using Quartz Event Taps
Supports the globe/fn key for toggling dictation
"""

import threading
import time
from typing import Callable, Optional, Set
from Cocoa import (
    NSEvent,
    NSEventMaskKeyDown,
    NSEventMaskKeyUp,
    NSEventMaskFlagsChanged,
)
from Quartz import (
    CGEventTapCreate,
    CGEventTapEnable,
    CGEventTapLocation,
    CGEventType,
    kCGEventKeyDown,
    kCGEventKeyUp,
    kCGEventFlagsChanged,
    kCGHeadInsertEventTap,
    kCGSessionEventTap,
    CGEventGetIntegerValueField,
    kCGKeyboardEventKeycode,
    CGEventGetFlags,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
    kCGEventFlagMaskAlternate,
    kCGEventFlagMaskSecondaryFn,
    CFMachPortCreateRunLoopSource,
    CFRunLoopAddSource,
    CFRunLoopRun,
    CFRunLoopStop,
    CFRunLoopGetCurrent,
    kCFRunLoopCommonModes,
)


# macOS key code constants
class KeyCode:
    """macOS virtual key codes"""
    # Function keys
    F1 = 0x7A
    F2 = 0x78
    F3 = 0x63
    F4 = 0x76
    F5 = 0x60
    F6 = 0x61
    F7 = 0x62
    F8 = 0x64
    F9 = 0x65
    F10 = 0x6D
    F11 = 0x67
    F12 = 0x6F
    F13 = 0x69
    F14 = 0x6B
    F15 = 0x71
    F16 = 0x6A
    F17 = 0x40
    F18 = 0x4F
    F19 = 0x50
    F20 = 0x5A

    # Special keys
    ESCAPE = 0x35
    TAB = 0x30
    SPACE = 0x31
    RETURN = 0x24
    DELETE = 0x33
    FORWARD_DELETE = 0x75

    # Globe/Fn key
    FUNCTION = 0x3F  # 63 decimal

    # Letters
    A = 0x00
    B = 0x0B
    C = 0x08
    D = 0x02
    E = 0x0E
    F = 0x03
    G = 0x05
    H = 0x04
    I = 0x22
    J = 0x26
    K = 0x28
    L = 0x25
    M = 0x2E
    N = 0x2D
    O = 0x1F
    P = 0x23
    Q = 0x0C
    R = 0x0F
    S = 0x01
    T = 0x11
    U = 0x20
    V = 0x09
    W = 0x0D
    X = 0x07
    Y = 0x10
    Z = 0x06

    # Numbers
    NUM_0 = 0x1D
    NUM_1 = 0x12
    NUM_2 = 0x13
    NUM_3 = 0x14
    NUM_4 = 0x15
    NUM_5 = 0x17
    NUM_6 = 0x16
    NUM_7 = 0x1A
    NUM_8 = 0x1C
    NUM_9 = 0x19


# Key aliases mapping to macOS key codes
KEY_ALIASES = {
    # Modifiers (handled separately via flags)
    'cmd': 'COMMAND',
    'command': 'COMMAND',
    'super': 'COMMAND',
    'ctrl': 'CONTROL',
    'control': 'CONTROL',
    'alt': 'OPTION',
    'option': 'OPTION',
    'shift': 'SHIFT',

    # Globe/Fn key
    'fn': 'FUNCTION',
    'function': 'FUNCTION',
    'globe': 'FUNCTION',

    # Function keys
    'f1': 'F1', 'f2': 'F2', 'f3': 'F3', 'f4': 'F4',
    'f5': 'F5', 'f6': 'F6', 'f7': 'F7', 'f8': 'F8',
    'f9': 'F9', 'f10': 'F10', 'f11': 'F11', 'f12': 'F12',
    'f13': 'F13', 'f14': 'F14', 'f15': 'F15', 'f16': 'F16',
    'f17': 'F17', 'f18': 'F18', 'f19': 'F19', 'f20': 'F20',

    # Special keys
    'esc': 'ESCAPE', 'escape': 'ESCAPE',
    'tab': 'TAB',
    'space': 'SPACE', 'spacebar': 'SPACE',
    'return': 'RETURN', 'enter': 'RETURN',
    'delete': 'DELETE', 'backspace': 'DELETE',
    'forwarddelete': 'FORWARD_DELETE', 'del': 'FORWARD_DELETE',

    # Letters
    'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F',
    'g': 'G', 'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K', 'l': 'L',
    'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R',
    's': 'S', 't': 'T', 'u': 'U', 'v': 'V', 'w': 'W', 'x': 'X',
    'y': 'Y', 'z': 'Z',

    # Numbers
    '0': 'NUM_0', '1': 'NUM_1', '2': 'NUM_2', '3': 'NUM_3', '4': 'NUM_4',
    '5': 'NUM_5', '6': 'NUM_6', '7': 'NUM_7', '8': 'NUM_8', '9': 'NUM_9',
}


class GlobalShortcuts:
    """Handles global keyboard shortcuts using macOS Quartz Event Taps"""

    def __init__(self, primary_key: str = 'fn', callback: Optional[Callable] = None):
        self.primary_key = primary_key.lower()
        self.callback = callback

        # Event tap and run loop
        self.event_tap = None
        self.run_loop_source = None
        self.run_loop = None
        self.listener_thread = None
        self.is_running = False
        self.stop_event = threading.Event()

        # State tracking
        self.pressed_keys = set()
        self.pressed_modifiers = set()
        self.last_trigger_time = 0
        self.debounce_time = 0.3  # 300ms debounce

        # Parse the primary key combination
        self.target_keycode, self.target_modifiers = self._parse_key_combination(primary_key)

        print(f"Global shortcuts initialized with key: {primary_key}")
        print(f"Parsed: keycode={self.target_keycode}, modifiers={self.target_modifiers}")

    def _parse_key_combination(self, key_string: str):
        """Parse a key combination string into keycode and modifiers"""
        modifiers = set()
        keycode = None

        key_lower = key_string.lower().strip()
        key_lower = key_lower.replace('<', '').replace('>', '')

        # Split into parts for modifier + key combinations
        parts = [p.strip() for p in key_lower.split('+')]

        for part in parts:
            alias = KEY_ALIASES.get(part, part.upper())

            # Check if it's a modifier
            if alias in ['COMMAND', 'CONTROL', 'OPTION', 'SHIFT']:
                modifiers.add(alias)
            elif alias == 'FUNCTION':
                # Fn key is special - it can be both a modifier and a key
                # For toggle on single Fn press, we'll treat it as a keycode
                keycode = KeyCode.FUNCTION
            else:
                # Try to get the keycode
                try:
                    keycode = getattr(KeyCode, alias)
                except AttributeError:
                    print(f"Warning: Unknown key '{part}'")

        # Default to Fn key if nothing parsed
        if keycode is None and not modifiers:
            keycode = KeyCode.FUNCTION

        return keycode, modifiers

    def _create_event_tap_callback(self):
        """Create the event tap callback function"""
        def callback(proxy, event_type, event, refcon):
            try:
                # Get key code
                keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)

                # Get modifier flags
                flags = CGEventGetFlags(event)
                current_modifiers = set()

                if flags & kCGEventFlagMaskCommand:
                    current_modifiers.add('COMMAND')
                if flags & kCGEventFlagMaskControl:
                    current_modifiers.add('CONTROL')
                if flags & kCGEventFlagMaskAlternate:
                    current_modifiers.add('OPTION')
                if flags & kCGEventFlagMaskShift:
                    current_modifiers.add('SHIFT')
                if flags & kCGEventFlagMaskSecondaryFn:
                    current_modifiers.add('FUNCTION')

                # Handle key down
                if event_type == kCGEventKeyDown:
                    self.pressed_keys.add(keycode)
                    self._check_shortcut_combination(keycode, current_modifiers)

                # Handle key up
                elif event_type == kCGEventKeyUp:
                    self.pressed_keys.discard(keycode)

                # Handle flags changed (for modifier keys including Fn)
                elif event_type == kCGEventFlagsChanged:
                    # On macOS, Fn key presses come as flags changed events
                    # Check if this is an Fn key event
                    if keycode == KeyCode.FUNCTION:
                        if flags & kCGEventFlagMaskSecondaryFn:
                            # Fn key pressed
                            self.pressed_keys.add(keycode)
                            self._check_shortcut_combination(keycode, current_modifiers)
                        else:
                            # Fn key released
                            self.pressed_keys.discard(keycode)

                # Always pass through the event
                return event

            except Exception as e:
                print(f"Error in event tap callback: {e}")
                return event

        return callback

    def _check_shortcut_combination(self, keycode, modifiers):
        """Check if current key combination matches target"""
        # Check if keycode matches (if target has a keycode)
        keycode_matches = (self.target_keycode is None or
                          self.target_keycode == keycode)

        # Check if modifiers match
        modifiers_match = self.target_modifiers == modifiers

        if keycode_matches and modifiers_match:
            current_time = time.time()

            # Implement debouncing
            if current_time - self.last_trigger_time > self.debounce_time:
                self.last_trigger_time = current_time
                self._trigger_callback()

    def _trigger_callback(self):
        """Trigger the callback function"""
        if self.callback:
            try:
                print(f"Global shortcut triggered: {self.primary_key}")
                # Run callback in a separate thread to avoid blocking the event tap
                callback_thread = threading.Thread(target=self.callback, daemon=True)
                callback_thread.start()
            except Exception as e:
                print(f"Error calling shortcut callback: {e}")

    def _event_loop(self):
        """Main event loop for processing keyboard events"""
        try:
            # Create event tap
            event_mask = (
                (1 << kCGEventKeyDown) |
                (1 << kCGEventKeyUp) |
                (1 << kCGEventFlagsChanged)
            )

            tap_callback = self._create_event_tap_callback()

            self.event_tap = CGEventTapCreate(
                kCGSessionEventTap,  # Tap location
                kCGHeadInsertEventTap,  # Place at head
                0,  # Active filter (0 = passive)
                event_mask,  # Event mask
                tap_callback,  # Callback
                None  # User data
            )

            if not self.event_tap:
                print("ERROR: Failed to create event tap. Accessibility permissions required.")
                print("Go to System Preferences > Security & Privacy > Privacy > Accessibility")
                print("and grant permission to Terminal or your Python app.")
                return

            # Create run loop source
            self.run_loop_source = CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
            self.run_loop = CFRunLoopGetCurrent()

            CFRunLoopAddSource(self.run_loop, self.run_loop_source, kCFRunLoopCommonModes)
            CGEventTapEnable(self.event_tap, True)

            print("Event tap created successfully, starting run loop...")

            # Run the event loop
            CFRunLoopRun()

        except Exception as e:
            print(f"Error in keyboard event loop: {e}")
            import traceback
            traceback.print_exc()

    def start(self) -> bool:
        """Start listening for global shortcuts"""
        if self.is_running:
            return True

        try:
            self.stop_event.clear()
            self.listener_thread = threading.Thread(target=self._event_loop, daemon=True)
            self.listener_thread.start()
            self.is_running = True

            print(f"Global shortcuts started, listening for {self.primary_key}")

            # Give the thread a moment to start
            time.sleep(0.5)

            # Check if event tap was created successfully
            if self.event_tap is None:
                print("WARNING: Event tap not created. Check accessibility permissions.")
                return False

            return True

        except Exception as e:
            print(f"Failed to start global shortcuts: {e}")
            import traceback
            traceback.print_exc()
            return False

    def stop(self):
        """Stop listening for global shortcuts"""
        if not self.is_running:
            return

        try:
            self.stop_event.set()

            # Stop the run loop
            if self.run_loop:
                CFRunLoopStop(self.run_loop)

            # Wait for thread to finish
            if self.listener_thread and self.listener_thread.is_alive():
                self.listener_thread.join(timeout=1.0)

            self.is_running = False
            self.pressed_keys.clear()
            self.pressed_modifiers.clear()

            print("Global shortcuts stopped")

        except Exception as e:
            print(f"Error stopping global shortcuts: {e}")

    def is_active(self) -> bool:
        """Check if global shortcuts are currently active"""
        return self.is_running and self.listener_thread and self.listener_thread.is_alive()

    def set_callback(self, callback: Callable):
        """Set the callback function for shortcut activation"""
        self.callback = callback

    def update_shortcut(self, new_key: str) -> bool:
        """Update the shortcut key combination"""
        try:
            # Parse the new key combination
            new_keycode, new_modifiers = self._parse_key_combination(new_key)

            # Update the configuration
            self.primary_key = new_key.lower()
            self.target_keycode = new_keycode
            self.target_modifiers = new_modifiers

            print(f"Updated global shortcut to: {new_key}")
            return True

        except Exception as e:
            print(f"Failed to update shortcut: {e}")
            return False

    def get_status(self) -> dict:
        """Get the current status of global shortcuts"""
        return {
            'is_running': self.is_running,
            'is_active': self.is_active(),
            'primary_key': self.primary_key,
            'target_keycode': self.target_keycode,
            'target_modifiers': list(self.target_modifiers),
            'pressed_keys': list(self.pressed_keys),
        }

    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.stop()
        except:
            pass


def check_accessibility_permissions() -> bool:
    """Check if the app has accessibility permissions"""
    try:
        # Try to create a simple event tap to test permissions
        event_mask = (1 << kCGEventKeyDown)

        def dummy_callback(proxy, event_type, event, refcon):
            return event

        test_tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            0,
            event_mask,
            dummy_callback,
            None
        )

        if test_tap:
            print("✓ Accessibility permissions granted")
            return True
        else:
            print("✗ Accessibility permissions NOT granted")
            print("\nTo enable:")
            print("1. Open System Preferences > Security & Privacy > Privacy")
            print("2. Select 'Accessibility' from the list")
            print("3. Add Terminal (or your Python app) and check the box")
            print("4. Restart this application")
            return False

    except Exception as e:
        print(f"Error checking accessibility permissions: {e}")
        return False


if __name__ == "__main__":
    # Test functionality
    print("Testing macOS Global Shortcuts")
    print("=" * 50)

    # Check permissions first
    if not check_accessibility_permissions():
        print("\nCannot continue without accessibility permissions.")
        exit(1)

    def test_callback():
        print("🎤 Globe/Fn key pressed! Dictation toggled.")

    shortcuts = GlobalShortcuts('fn', test_callback)

    if shortcuts.start():
        print("\n✓ Press the Globe/Fn key to test")
        print("✓ Press Ctrl+C to exit")
        print("-" * 50)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
    else:
        print("\n✗ Failed to start global shortcuts")

    shortcuts.stop()
