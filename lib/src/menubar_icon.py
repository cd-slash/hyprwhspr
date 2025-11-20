"""
Menubar icon for hyprwhspr on macOS
Provides visual status and control through the system menubar
"""

import sys
import subprocess
from pathlib import Path
from typing import Callable, Optional
import objc
from AppKit import (
    NSApplication,
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSImage,
    NSVariableStatusItemLength,
    NSAlert,
    NSAlertFirstButtonReturn,
)
from Foundation import NSObject, NSTimer


class MenuBarApp(NSObject):
    """macOS menubar application controller"""

    def init(self):
        self = objc.super(MenuBarApp, self).init()
        if self is None:
            return None

        self.statusbar = None
        self.menu = None
        self.is_recording = False
        self.permissions_ok = False
        self.toggle_callback = None
        self.quit_callback = None

        return self

    def setup_menubar(
        self,
        toggle_callback: Optional[Callable] = None,
        quit_callback: Optional[Callable] = None,
        accessibility_ok: bool = False,
        microphone_ok: bool = False
    ):
        """Setup the menubar icon and menu"""
        self.toggle_callback = toggle_callback
        self.quit_callback = quit_callback
        self.accessibility_ok = accessibility_ok
        self.microphone_ok = microphone_ok

        # Create status bar item
        self.statusbar = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )

        # Set initial icon
        self.update_icon(False)

        # Create menu
        self.menu = NSMenu.alloc().init()

        # Add menu items
        status_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "hyprwhspr - Voice Dictation", None, ""
        )
        self.menu.addItem_(status_item)

        self.menu.addItem_(NSMenuItem.separatorItem())

        # Recording status
        self.status_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Status: Idle", None, ""
        )
        self.menu.addItem_(self.status_item)

        self.menu.addItem_(NSMenuItem.separatorItem())

        # Toggle recording
        toggle_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Toggle Recording (fn)", "toggleRecording:", ""
        )
        toggle_item.setTarget_(self)
        self.menu.addItem_(toggle_item)

        # Permissions status
        if not accessibility_ok or not microphone_ok:
            self.menu.addItem_(NSMenuItem.separatorItem())

            if not accessibility_ok:
                acc_perm_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    "⚠️  Accessibility Permissions Required", None, ""
                )
                self.menu.addItem_(acc_perm_item)

                open_acc_prefs_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    "Open Accessibility Settings...", "openAccessibilityPrefs:", ""
                )
                open_acc_prefs_item.setTarget_(self)
                self.menu.addItem_(open_acc_prefs_item)

                if not microphone_ok:
                    self.menu.addItem_(NSMenuItem.separatorItem())

            if not microphone_ok:
                mic_perm_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    "⚠️  Microphone Permissions Required", None, ""
                )
                self.menu.addItem_(mic_perm_item)

                open_mic_prefs_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    "Open Microphone Settings...", "openMicrophonePrefs:", ""
                )
                open_mic_prefs_item.setTarget_(self)
                self.menu.addItem_(open_mic_prefs_item)

        self.menu.addItem_(NSMenuItem.separatorItem())

        # About
        about_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "About hyprwhspr", "showAbout:", ""
        )
        about_item.setTarget_(self)
        self.menu.addItem_(about_item)

        # Quit
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "terminate:", ""
        )
        quit_item.setTarget_(self)
        self.menu.addItem_(quit_item)

        # Set the menu
        self.statusbar.setMenu_(self.menu)

    def update_icon(self, is_recording):
        """Update the menubar icon based on recording state"""
        self.is_recording = is_recording

        # Use emoji as icon (fallback if no image)
        if is_recording:
            self.statusbar.setTitle_("🔴")  # Red circle when recording
        else:
            self.statusbar.setTitle_("🎤")  # Microphone when idle

    def update_status(self, is_recording):
        """Update the recording status in the menu"""
        self.is_recording = is_recording
        self.update_icon(is_recording)

        if is_recording:
            self.status_item.setTitle_("Status: ⏺ Recording...")
        else:
            self.status_item.setTitle_("Status: Idle")

    def toggleRecording_(self, sender):
        """Handle toggle recording menu item"""
        if self.toggle_callback:
            self.toggle_callback()

    def openAccessibilityPrefs_(self, sender):
        """Open System Preferences to Accessibility settings"""
        try:
            # macOS Ventura and later
            subprocess.run([
                "open",
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
            ])
        except Exception as e:
            print(f"Error opening preferences: {e}")
            # Fallback to general preferences
            subprocess.run(["open", "/System/Applications/System Preferences.app"])

    def openMicrophonePrefs_(self, sender):
        """Open System Preferences to Microphone settings"""
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

    def showAbout_(self, sender):
        """Show about dialog"""
        alert = NSAlert.alloc().init()
        alert.setMessageText_("hyprwhspr")
        alert.setInformativeText_(
            "Voice dictation application for macOS\n\n"
            "Press the fn (globe) key to start/stop recording\n"
            "Transcribed text will be automatically typed\n\n"
            "Repository: github.com/cd-slash/hyprwhspr"
        )
        alert.addButtonWithTitle_("OK")
        alert.runModal()

    def terminate_(self, sender):
        """Quit the application"""
        if self.quit_callback:
            self.quit_callback()
        NSApplication.sharedApplication().terminate_(sender)


class MenuBarController:
    """Controller for the menubar icon"""

    def __init__(
        self,
        toggle_callback: Optional[Callable] = None,
        quit_callback: Optional[Callable] = None,
        accessibility_ok: bool = False,
        microphone_ok: bool = False
    ):
        self.app = NSApplication.sharedApplication()
        self.delegate = MenuBarApp.alloc().init()
        self.delegate.setup_menubar(toggle_callback, quit_callback, accessibility_ok, microphone_ok)

    def update_recording_status(self, is_recording: bool):
        """Update the recording status"""
        self.delegate.update_status(is_recording)

    def run(self):
        """Start the menubar application"""
        # Note: This will be called from the main thread
        # The app is already running, we just need to keep it alive
        pass


def create_menubar(
    toggle_callback: Optional[Callable] = None,
    quit_callback: Optional[Callable] = None,
    accessibility_ok: bool = False,
    microphone_ok: bool = False
) -> MenuBarController:
    """
    Create and return a menubar controller

    Args:
        toggle_callback: Function to call when user clicks toggle recording
        quit_callback: Function to call when user quits
        accessibility_ok: Whether accessibility permissions are granted
        microphone_ok: Whether microphone permissions are granted

    Returns:
        MenuBarController instance
    """
    return MenuBarController(toggle_callback, quit_callback, accessibility_ok, microphone_ok)
