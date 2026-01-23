import ctypes
from ctypes import wintypes
from typing import Optional, Dict


def find_window(title: str, exact_match: bool = True) -> Optional[Dict]:
    """
    Find a window by title and return its properties.
    
    Args:
        title: The window title to search for
        exact_match: If True, requires exact title match. If False, does partial match.
        
    Returns:
        Dictionary with window properties:
        - hwnd: Window handle
        - title: Window title
        - x: X coordinate of top-left corner
        - y: Y coordinate of top-left corner
        - width: Window width
        - height: Window height
        
        Returns None if window not found
    """
    user32 = ctypes.windll.user32
    hwnd = None
    
    if exact_match:
        hwnd = user32.FindWindowW(None, title)
    else:
        # For partial match, enumerate all windows
        result = {'hwnd': None}
        
        def enum_callback(hwnd, lParam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    window_title = buffer.value
                    if title.lower() in window_title.lower():
                        result['hwnd'] = hwnd
                        return False  # Stop enumeration
            return True  # Continue enumeration
        
        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        callback = WNDENUMPROC(enum_callback)
        user32.EnumWindows(callback, 0)
        hwnd = result['hwnd']
    
    if not hwnd:
        return None
    
    # Get window rectangle
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    
    # Get actual window title
    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    window_title = buffer.value
    
    return {
        'hwnd': hwnd,
        'title': window_title,
        'x': rect.left,
        'y': rect.top,
        'width': rect.right - rect.left,
        'height': rect.bottom - rect.top
    }
