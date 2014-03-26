"""Some useful functions for accessing and manipulating the clipboard"""

from dragonfly.windows.clipboard import Clipboard

# For temporarily storing clipboard contents
clip = ""


def save_to_clipboard(text):
    """Stores text to the clipboard"""
    clipboard = Clipboard(from_system=True)
    clipboard.set_text(text)
    clipboard.copy_to_system()


def save_clip():
    """Stores the most recent clipboard item"""
    global clip
    clip = Clipboard(from_system=True).get_text()


def restore_clip():
    """Restores the most recent clipboard item"""
    global clip
    clipboard = Clipboard(from_system=True)
    clipboard.set_text(clip)
    clipboard.copy_to_system()

def text_clip():
    """Gets the most recent item from the clipboard as text"""
    return Clipboard(from_system=True).get_text()


def reverse_clip():
    """Reverses the most recent clipboard item"""
    clip = text_clip()
    clipboard = Clipboard(from_system=True)
    clipboard.set_text(clip[::-1])
    clipboard.copy_to_system()
