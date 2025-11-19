#!/usr/bin/env python3
"""
Diagnostic tool to test globe/fn key detection on macOS
This helps debug why the globe key might not be working
"""

import sys
import time

print("=" * 60)
print("Globe/Fn Key Diagnostic Tool for macOS")
print("=" * 60)
print()

# Check if we're on macOS
import platform
if platform.system() != 'Darwin':
    print("ERROR: This diagnostic tool is for macOS only")
    sys.exit(1)

print("✓ Running on macOS")
print()

# Try to import the required modules
print("Checking dependencies...")
try:
    from Cocoa import NSEvent
    print("✓ Cocoa framework available")
except ImportError:
    print("✗ Cocoa framework NOT available")
    print("  Install with: pip install pyobjc-framework-Cocoa")
    sys.exit(1)

try:
    from Quartz import (
        CGEventTapCreate,
        kCGSessionEventTap,
        kCGHeadInsertEventTap,
        kCGEventKeyDown,
        kCGEventKeyUp,
        kCGEventFlagsChanged,
        CGEventGetIntegerValueField,
        kCGKeyboardEventKeycode,
        CGEventGetFlags,
        kCGEventFlagMaskSecondaryFn,
    )
    print("✓ Quartz framework available")
except ImportError:
    print("✗ Quartz framework NOT available")
    print("  Install with: pip install pyobjc-framework-Quartz")
    sys.exit(1)

print()

# Check accessibility permissions
print("Checking accessibility permissions...")
print()

def check_accessibility_permissions():
    """Check if the app has accessibility permissions"""
    try:
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
            print("✓ Accessibility permissions GRANTED")
            print()
            return True
        else:
            print("✗ Accessibility permissions NOT GRANTED")
            print()
            print("To enable accessibility permissions:")
            print("  1. Open System Preferences")
            print("  2. Go to Security & Privacy > Privacy > Accessibility")
            print("  3. Click the lock icon and enter your password")
            print("  4. Add Python (or Terminal) to the list")
            print("  5. Make sure it's checked")
            print("  6. Restart this script")
            print()
            return False

    except Exception as e:
        print(f"✗ Error checking permissions: {e}")
        return False

if not check_accessibility_permissions():
    sys.exit(1)

# Now test for actual key events
print("Starting keyboard event monitoring...")
print()
print("Press ANY key to see its keycode (including the globe/fn key)")
print("Press Ctrl+C to exit")
print()
print("-" * 60)

from Quartz import (
    CFMachPortCreateRunLoopSource,
    CFRunLoopAddSource,
    CFRunLoopRun,
    CFRunLoopStop,
    CFRunLoopGetCurrent,
    kCFRunLoopCommonModes,
    CGEventTapEnable,
)

detected_globe = False

def create_event_callback():
    """Create callback to monitor all keyboard events"""
    def callback(proxy, event_type, event, refcon):
        global detected_globe

        try:
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            flags = CGEventGetFlags(event)

            # Check for Fn flag
            has_fn = bool(flags & kCGEventFlagMaskSecondaryFn)

            # Event type names
            event_name = {
                kCGEventKeyDown: "KeyDown",
                kCGEventKeyUp: "KeyUp",
                kCGEventFlagsChanged: "FlagsChanged",
            }.get(event_type, f"Unknown({event_type})")

            # Print event info
            if event_type == kCGEventFlagsChanged:
                # This is where Fn key events come through
                print(f"{event_name}: keycode={keycode} (0x{keycode:02X}), Fn={has_fn}")
                if keycode == 63 or keycode == 0x3F:
                    detected_globe = True
                    print("  ^^^^^ THIS IS THE GLOBE/FN KEY! ^^^^^")
            elif event_type in (kCGEventKeyDown, kCGEventKeyUp):
                # Regular key events
                print(f"{event_name}: keycode={keycode} (0x{keycode:02X}), Fn={has_fn}")

        except Exception as e:
            print(f"Error in callback: {e}")

        # Always pass through the event
        return event

    return callback

# Create event tap
event_mask = (
    (1 << kCGEventKeyDown) |
    (1 << kCGEventKeyUp) |
    (1 << kCGEventFlagsChanged)
)

tap_callback = create_event_callback()

event_tap = CGEventTapCreate(
    kCGSessionEventTap,
    kCGHeadInsertEventTap,
    0,  # Passive filter
    event_mask,
    tap_callback,
    None
)

if not event_tap:
    print("ERROR: Failed to create event tap!")
    print("Make sure accessibility permissions are granted.")
    sys.exit(1)

# Create run loop source
run_loop_source = CFMachPortCreateRunLoopSource(None, event_tap, 0)
run_loop = CFRunLoopGetCurrent()

CFRunLoopAddSource(run_loop, run_loop_source, kCFRunLoopCommonModes)
CGEventTapEnable(event_tap, True)

print("Event tap created successfully!")
print()
print("Now press keys to see their codes...")
print()

try:
    CFRunLoopRun()
except KeyboardInterrupt:
    print()
    print()
    if detected_globe:
        print("✓ Globe/Fn key WAS detected!")
        print("  The globe key is working correctly.")
    else:
        print("✗ Globe/Fn key was NOT detected")
        print()
        print("Troubleshooting tips:")
        print("  1. Try pressing and holding the Fn/globe key")
        print("  2. Check if you have a physical Fn key or the newer globe key")
        print("  3. On some keyboards, Fn might be keycode 63 (0x3F)")
        print("  4. The globe key might have a different keycode")
        print()
        print("If you saw ANY 'FlagsChanged' events when pressing the globe key,")
        print("note the keycode and update the configuration.")
    print()
    print("Exiting...")
