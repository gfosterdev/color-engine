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
    
    def find_color(self, rgb: tuple, tolerance: int = 0) -> Optional[tuple]:
        """
        Find the first occurrence of an RGB color in the saved screenshot.
        
        Args:
            rgb: Tuple of (R, G, B) values to search for (0-255 each)
            tolerance: Color matching tolerance (0 = exact match, higher = more lenient)
            
        Returns:
            Tuple of (x, y) coordinates relative to window if found, None otherwise
        """
        if not self.screenshot:
            return None
        
        pixels = self.screenshot.load()
        if not pixels:
            return None
            
        width, height = self.screenshot.size
        
        for y in range(height):
            for x in range(width):
                pixel = pixels[x, y]
                # Handle both RGB and RGBA
                if isinstance(pixel, tuple):
                    pixel_rgb = pixel[:3] if len(pixel) >= 3 else pixel
                else:
                    continue  # Skip non-tuple pixels
                
                # Check if color matches within tolerance
                if tolerance == 0:
                    if pixel_rgb == rgb:
                        return (x, y)
                else:
                    if all(abs(pixel_rgb[i] - rgb[i]) <= tolerance for i in range(3)):
                        return (x, y)
        
        return None
