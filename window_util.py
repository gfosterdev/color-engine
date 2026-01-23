import ctypes
from ctypes import wintypes
from typing import Optional, Dict
import cv2
import numpy as np
from PIL import ImageGrab
from mouse_util import MouseMover


class Window:
    """Find and interact with a window by title."""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.window: Optional[Dict] = None
        self.screenshot: Optional[np.ndarray] = None
        self.mouse = MouseMover()
    
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
    
    def capture(self, debug=False) -> Optional[np.ndarray]:
        """
        Capture a screenshot of the found window and store it in memory as OpenCV image.
        
        Returns:
            OpenCV numpy array (RGB format) if successful, None if no window found
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
        
        pil_image = ImageGrab.grab(bbox=bbox)
        # Convert PIL image to OpenCV numpy array (RGB format)
        self.screenshot = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        if debug and self.screenshot is not None:
            cv2.imwrite('screenshot.png', self.screenshot)
        
        return self.screenshot
    
    def find_color(self, rgb: tuple, tolerance: int = 0, debug: bool = False) -> Optional[tuple]:
        """
        Find the first occurrence of an RGB color in the saved screenshot using OpenCV.
        
        Args:
            rgb: Tuple of (R, G, B) values to search for (0-255 each)
            tolerance: Color matching tolerance (0 = exact match, higher = more lenient)
            debug: If True, print debug information about pixels being checked
            
        Returns:
            Tuple of (x, y) coordinates relative to window if found, None otherwise
        """
        if self.screenshot is None:
            return None
        
        height, width = self.screenshot.shape[:2]
        
        # Convert RGB to BGR for OpenCV
        bgr = (rgb[2], rgb[1], rgb[0])
        
        if tolerance == 0:
            # Exact match using OpenCV - convert tuple to numpy array
            bgr_array = np.array(bgr, dtype=np.uint8)
            mask = cv2.inRange(self.screenshot, bgr_array, bgr_array)
        else:
            # Match with tolerance
            lower = np.array([max(0, bgr[i] - tolerance) for i in range(3)], dtype=np.uint8)
            upper = np.array([min(255, bgr[i] + tolerance) for i in range(3)], dtype=np.uint8)
            mask = cv2.inRange(self.screenshot, lower, upper)
        
        # Find first non-zero pixel in mask
        coords = cv2.findNonZero(mask)
        
        if coords is not None and len(coords) > 0:
            x, y = coords[0][0]
            if debug:
                pixel_bgr = self.screenshot[y, x]
                pixel_rgb = (pixel_bgr[2], pixel_bgr[1], pixel_bgr[0])
                print(f"Found match at ({x}, {y}): RGB {pixel_rgb}")
            return (int(x), int(y))
        
        if debug:
            print("Color not found in image")
        return None
    
    def move_mouse_to(self, coords: tuple[int, int], duration: float = 0.5, 
                      curve_intensity: float = 1.0) -> bool:
        """
        Move mouse to coordinates relative to the found window.
        
        Args:
            coords: Tuple of (x, y) coordinates relative to window (0, 0 = top-left corner)
            duration: Time to complete movement in seconds
            curve_intensity: How curved the path should be
            
        Returns:
            True if successful, False if no window found
        """
        if not self.window:
            return False
        
        x, y = coords
        
        # Convert window-relative coordinates to screen coordinates
        screen_x = self.window['x'] + x
        screen_y = self.window['y'] + y
        
        self.mouse.move_to(screen_x, screen_y, duration, curve_intensity)
        return True
    
    def click_at(self, x: int, y: int, duration: float = 0.5, 
                 button: str = 'left') -> bool:
        """
        Move to coordinates relative to window and click.
        
        Args:
            x: X coordinate relative to window
            y: Y coordinate relative to window
            duration: Time to move to position
            button: 'left' or 'right'
            
        Returns:
            True if successful, False if no window found
        """
        if not self.window:
            return False
        
        # Convert window-relative coordinates to screen coordinates
        screen_x = self.window['x'] + x
        screen_y = self.window['y'] + y
        
        self.mouse.click(screen_x, screen_y, duration, button)
        return True
    
    def get_color_at_mouse(self) -> Optional[tuple]:
        """
        Get the RGB color at the current mouse position using OpenCV.
        
        Returns:
            Tuple of (R, G, B) if mouse is over the window and screenshot exists, None otherwise
        """
        if not self.window or self.screenshot is None:
            return None
        
        # Get current mouse position
        mouse_x, mouse_y = self.mouse.get_position()
        
        # Check if mouse is within window bounds
        if (mouse_x < self.window['x'] or 
            mouse_x >= self.window['x'] + self.window['width'] or
            mouse_y < self.window['y'] or 
            mouse_y >= self.window['y'] + self.window['height']):
            return None
        
        # Convert screen coordinates to window-relative coordinates
        rel_x = mouse_x - self.window['x']
        rel_y = mouse_y - self.window['y']
        
        # Get pixel from OpenCV image (BGR format)
        pixel_bgr = self.screenshot[rel_y, rel_x]
        
        # Convert BGR to RGB
        return (int(pixel_bgr[2]), int(pixel_bgr[1]), int(pixel_bgr[0]))
