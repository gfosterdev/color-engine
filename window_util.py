import ctypes
from ctypes import wintypes
from typing import Optional, Dict
from PIL import Image, ImageGrab


class Window:
    """Find and interact with a window by title."""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.window: Optional[Dict] = None
        self.screenshot: Optional[Image.Image] = None
    
    def find(self, title: str, exact_match: bool = True) -> bool:
        """
        Find a window by title and store its properties.
        
        Args:
            title: The window title to search for
            exact_match: If True, requires exact title match. If False, does partial match.
            
        Returns:
            True if window found, False otherwise
        """
        hwnd = None
        
        if exact_match:
            hwnd = self.user32.FindWindowW(None, title)
        else:
            # For partial match, enumerate all windows
            result = {'hwnd': None}
            
            def enum_callback(hwnd, lParam):
                if self.user32.IsWindowVisible(hwnd):
                    length = self.user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        self.user32.GetWindowTextW(hwnd, buffer, length + 1)
                        window_title = buffer.value
                        if title.lower() in window_title.lower():
                            result['hwnd'] = hwnd
                            return False  # Stop enumeration
                return True  # Continue enumeration
            
            WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            callback = WNDENUMPROC(enum_callback)
            self.user32.EnumWindows(callback, 0)
            hwnd = result['hwnd']
        
        if not hwnd:
            self.window = None
            return False
        
        # Get window rectangle
        rect = wintypes.RECT()
        if not self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            self.window = None
            return False
        
        # Get actual window title
        length = self.user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buffer, length + 1)
        window_title = buffer.value
        
        self.window = {
            'hwnd': hwnd,
            'title': window_title,
            'x': rect.left,
            'y': rect.top,
            'width': rect.right - rect.left,
            'height': rect.bottom - rect.top
        }
        
        return True
    
    def capture(self, debug=False) -> Optional[Image.Image]:
        """
        Capture a screenshot of the found window and store it in memory.
        
        Returns:
            PIL Image object if successful, None if no window found
        """
        if not self.window:
            return None
        
        # Capture the window area
        bbox = (
            self.window['x'],
            self.window['y'],
            self.window['x'] + self.window['width'],
            self.window['y'] + self.window['height']
        )
        
        self.screenshot = ImageGrab.grab(bbox=bbox)
        if debug and self.screenshot:
            self.screenshot.save('screenshot.png')
        return self.screenshot
