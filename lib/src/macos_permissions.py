"""
macOS permissions checker for hyprwhspr
Checks and requests microphone and accessibility permissions
"""

import subprocess
import sys
from typing import Tuple


def check_microphone_permission() -> bool:
    """
    Check if the app has microphone access permission

    Returns:
        bool: True if permission granted, False otherwise
    """
    try:
        # Try to import AVFoundation for permission checking
        from AVFoundation import AVCaptureDevice, AVMediaTypeAudio, AVAuthorizationStatusAuthorized

        auth_status = AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeAudio)

        if auth_status == AVAuthorizationStatusAuthorized:
            print("✓ Microphone permissions granted")
            return True
        else:
            print("✗ Microphone permissions NOT granted")
            return False

    except ImportError:
        # Fallback method using sounddevice - if it can list devices, we likely have permission
        try:
            import sounddevice as sd
            devices = sd.query_devices()

            # Check if we can actually access input devices
            input_devices = [d for d in devices if d['max_input_channels'] > 0]

            if input_devices:
                print("✓ Microphone access appears to be available")
                return True
            else:
                print("⚠️  No input devices found - permissions may be required")
                return False

        except Exception as e:
            print(f"⚠️  Could not check microphone permissions: {e}")
            return False


def request_microphone_permission() -> bool:
    """
    Request microphone permission from the user

    Returns:
        bool: True if permission granted, False otherwise
    """
    try:
        from AVFoundation import AVCaptureDevice, AVMediaTypeAudio
        from PyObjCTools import AppHelper
        import time

        print("Requesting microphone permission...")

        # Request permission
        def permission_callback(granted):
            print(f"Microphone permission: {'granted' if granted else 'denied'}")

        AVCaptureDevice.requestAccessForMediaType_completionHandler_(
            AVMediaTypeAudio,
            permission_callback
        )

        # Give it a moment to process
        time.sleep(1)

        # Check the result
        return check_microphone_permission()

    except ImportError:
        print("⚠️  AVFoundation not available - cannot request permissions")
        return False
    except Exception as e:
        print(f"⚠️  Error requesting microphone permission: {e}")
        return False


def open_system_preferences_microphone():
    """Open System Preferences to the Microphone privacy settings"""
    try:
        # macOS Ventura and later
        subprocess.run([
            "open",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"
        ])
    except Exception as e:
        print(f"Error opening preferences: {e}")
        # Fallback to general preferences
        subprocess.run(["open", "/System/Applications/System Preferences.app"])


def check_all_permissions() -> Tuple[bool, bool]:
    """
    Check both accessibility and microphone permissions

    Returns:
        Tuple[bool, bool]: (accessibility_ok, microphone_ok)
    """
    from global_shortcuts_macos import check_accessibility_permissions

    accessibility_ok = check_accessibility_permissions()
    microphone_ok = check_microphone_permission()

    return accessibility_ok, microphone_ok


if __name__ == "__main__":
    print("Checking macOS permissions...")
    print("=" * 50)

    accessibility_ok, microphone_ok = check_all_permissions()

    print("\nPermissions Status:")
    print(f"  Accessibility: {'✓ Granted' if accessibility_ok else '✗ NOT granted'}")
    print(f"  Microphone:    {'✓ Granted' if microphone_ok else '✗ NOT granted'}")

    if not microphone_ok:
        print("\nWould you like to request microphone permission? (y/n)")
        response = input().lower()
        if response == 'y':
            request_microphone_permission()
