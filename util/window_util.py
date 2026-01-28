import os
# Set environment variable before any PaddlePaddle imports to disable OneDNN
os.environ['PADDLE_DISABLE_ONEDNN'] = '1'

from time import sleep
import ctypes
from ctypes import wintypes
from typing import Optional, Dict
import cv2
import numpy as np
from PIL import ImageGrab, Image
from .mouse_util import MouseMover
import random
import math
import subprocess


class Region:
    """Helper class for storing and working with regions (can be non-rectangular shapes)."""
    
    def __init__(self, x: int, y: int, width: int, height: int, mask: Optional[np.ndarray] = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mask = mask  # Binary mask of filled shape within bounding box
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Region':
        """Create a Region from a dictionary with x, y, width, height keys."""
        return cls(data['x'], data['y'], data['width'], data['height'])
    
    def to_dict(self) -> Dict:
        """Convert Region to dictionary."""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
    
    def center(self) -> tuple[int, int]:
        """
        Get the center point of the region.
        If mask exists, returns centroid of filled shape.
        
        Returns:
            Tuple of (x, y) coordinates at the center
        """
        if self.mask is not None:
            # Calculate centroid of the filled shape
            moments = cv2.moments(self.mask)
            if moments['m00'] != 0:
                cx = int(moments['m10'] / moments['m00'])
                cy = int(moments['m01'] / moments['m00'])
                return (self.x + cx, self.y + cy)
        
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def random_point(self) -> tuple[int, int]:
        """
        Get a random point within the inner 80% of the region.
        If mask exists, ensures point is within filled shape.
        This creates a 10% margin based on the actual shape extent for more natural clicking.
        
        Returns:
            Tuple of (x, y) coordinates at a random position within the inner 80%
        """
        if self.mask is not None:
            # Get all filled coordinates from the mask
            valid_coords = cv2.findNonZero(self.mask)
            
            if valid_coords is not None and len(valid_coords) > 0:
                # Flatten to (N, 2) array
                valid_coords = valid_coords.reshape(-1, 2)
                
                # Calculate actual extent of the shape (not bounding box)
                min_x = valid_coords[:, 0].min()
                max_x = valid_coords[:, 0].max()
                min_y = valid_coords[:, 1].min()
                max_y = valid_coords[:, 1].max()
                
                shape_width = max_x - min_x
                shape_height = max_y - min_y
                
                # Calculate 10% margin based on shape extent
                margin_x = int(shape_width * 0.1)
                margin_y = int(shape_height * 0.1)
                
                # Filter to inner 80% of the actual shape
                inner_coords = valid_coords[
                    (valid_coords[:, 0] >= min_x + margin_x) & 
                    (valid_coords[:, 0] <= max_x - margin_x) &
                    (valid_coords[:, 1] >= min_y + margin_y) & 
                    (valid_coords[:, 1] <= max_y - margin_y)
                ]
                
                # Use inner coords if available, otherwise use all valid coords
                coords_to_use = inner_coords if len(inner_coords) > 0 else valid_coords
                
                # Pick random coordinate
                idx = random.randint(0, len(coords_to_use) - 1)
                rel_x, rel_y = coords_to_use[idx]
                return (self.x + int(rel_x), self.y + int(rel_y))
        
        # Fallback to simple random point if no mask
        margin_x = int(self.width * 0.1)
        margin_y = int(self.height * 0.1)
        inner_width = max(1, self.width - 2 * margin_x)
        inner_height = max(1, self.height - 2 * margin_y)
        
        rand_x = self.x + margin_x + random.randint(0, inner_width - 1)
        rand_y = self.y + margin_y + random.randint(0, inner_height - 1)
        return (rand_x, rand_y)
    
    def contains(self, x: int, y: int) -> bool:
        """
        Check if a point is within the region.
        If mask exists, checks if point is within filled shape.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            True if point is within bounds (and filled shape if mask exists), False otherwise
        """
        # Check bounding box first
        if not (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height):
            return False
        
        # If mask exists, check if point is within filled shape
        if self.mask is not None:
            mask_x = x - self.x
            mask_y = y - self.y
            
            if (0 <= mask_x < self.mask.shape[1] and 
                0 <= mask_y < self.mask.shape[0]):
                return self.mask[mask_y, mask_x] > 0
            return False
        
        return True
    
    def setX(self, x: int):
        self.x = x
    
    def setY(self, y: int):
        self.y = y

    def setWidth(self, width: int):
        self.width = width

    def setHeight(self, height: int):
        self.height = height

    def __repr__(self) -> str:
        return f"Region(x={self.x}, y={self.y}, width={self.width}, height={self.height})"


class Window:
    """Find and interact with a window by title."""

    ROTATE_DURATION_MIN = 0.1
    ROTATE_DURATION_MAX = 0.25
    ROTATE_CURVE_INTENSITY_MIN = 0.3
    ROTATE_CURVE_INTENSITY_MAX = 0.7
    CANVAS_OFFSET = {
        'x': 12,
        'y': 28
    }
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.window: Optional[Dict] = None
        self._game_area = None
        self.screenshot: Optional[np.ndarray] = None
        self.mouse = MouseMover()
    
    @property
    def GAME_AREA(self) -> Region:
        """Lazy load GAME_AREA from config to avoid circular import."""
        if self._game_area is None:
            from config.regions import GAME_AREA
            self._game_area = GAME_AREA
            from client.runelite_api import RuneLiteAPI
            api = RuneLiteAPI()

            # Update to API viewport width/height
            viewport = api.get_viewport_data()
            if viewport:
                self._game_area.setWidth(viewport.get('width', self._game_area.width))
                self._game_area.setHeight(viewport.get('height', self._game_area.height))
        return self._game_area
    
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
    
    def find_color_region(self, rgb: tuple, tolerance: int = 0, debug: bool = False) -> Optional[Region]:
        """
        Find a block of color and return its bounding box as a Region.
        
        Args:
            rgb: Tuple of (R, G, B) values to search for (0-255 each)
            tolerance: Color matching tolerance (0 = exact match, higher = more lenient)
            debug: If True, save a debug image showing the detected region
            
        Returns:
            Region object with x, y, width, height of the color block, None if not found
        """
        if self.screenshot is None:
            return None
        
        # Convert RGB to BGR for OpenCV
        bgr = (rgb[2], rgb[1], rgb[0])
        
        if tolerance == 0:
            bgr_array = np.array(bgr, dtype=np.uint8)
            mask = cv2.inRange(self.screenshot, bgr_array, bgr_array)
        else:
            lower = np.array([max(0, bgr[i] - tolerance) for i in range(3)], dtype=np.uint8)
            upper = np.array([min(255, bgr[i] + tolerance) for i in range(3)], dtype=np.uint8)
            mask = cv2.inRange(self.screenshot, lower, upper)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Create filled mask using fillPoly
        filled_mask = np.zeros((h, w), dtype=np.uint8)
        # Offset contour to bounding box coordinates
        contour_offset = largest_contour - [x, y]
        cv2.fillPoly(filled_mask, [contour_offset], (255,))
        
        if debug:
            debug_img = self.screenshot.copy()
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Draw filled contour in blue with transparency
            overlay = debug_img.copy()
            cv2.fillPoly(overlay, [largest_contour], (255, 0, 0))
            cv2.addWeighted(overlay, 0.3, debug_img, 0.7, 0, debug_img)
            cv2.imwrite('color_region_debug.png', debug_img)
            print(f"Found color region at ({x}, {y}) with size {w}x{h}")
            print(f"Filled mask has {cv2.countNonZero(filled_mask)} valid pixels")
        
        return Region(int(x), int(y), int(w), int(h), filled_mask)
    
    def move_mouse_to(self, coords: tuple[int, int], in_canvas: bool = True, duration: float = 0.25, 
                      curve_intensity: float = 1.0) -> bool:
        """
        Move mouse to coordinates relative to the found window.
        
        Args:
            coords: Tuple of (x, y) coordinates relative to window (0, 0 = top-left corner)
            in_canvas: If True, coordinates are relative to the game canvas within the window
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
        if in_canvas:
            screen_x += self.CANVAS_OFFSET['x']
            screen_y += self.CANVAS_OFFSET['y']
        
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
    
    def click(self, button: str = 'left') -> bool:
        """
        Click at the current mouse position.
        
        Args:
            button: 'left' or 'right' mouse button (default: 'left')
            
        Returns:
            True if successful, False if no window found
        """
        if not self.window:
            return False

        self.mouse.click(x=None, y=None, duration=0.0, button=button)
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

    def print_mouse_position(self) -> bool:
        """
        Print the current mouse position relative to the window.
        
        Returns:
            True if successful, False if no window found
        """
        if not self.window:
            return False
        
        # Get current mouse position
        mouse_x, mouse_y = self.mouse.get_position()
        
        # Convert screen coordinates to window-relative coordinates
        rel_x = mouse_x - self.window['x']
        rel_y = mouse_y - self.window['y']
        
        print(f"Mouse position: ({rel_x}, {rel_y})")
        return True

    def read_text(self, region=None, debug=False):
        """
        Extract text using PaddleOCR (better for game text with colored/stylized fonts).
        PaddleOCR is more robust than Tesseract for OSRS text and requires no preprocessing.
        
        Args:
            region: Optional Region object or tuple (x, y, w, h) to specify a sub-region
            debug: If True, save the input image to 'paddle_debug_input.png'
        Returns:
            Extracted text as a string
        """
        self.capture()
        
        if self.screenshot is None:
            return ""
        
        if region:
            # Handle both Region objects and tuples
            if isinstance(region, Region):
                x, y, w, h = region.x, region.y, region.width, region.height
            else:
                x, y, w, h = region
            cropped = self.screenshot[y:y+h, x:x+w]
        else:
            cropped = self.screenshot.copy()
        
        # PaddleOCR works with BGR (OpenCV format) directly
        if debug:
            cv2.imwrite('paddle_debug_input.png', cropped)
        
        # Initialize PaddleOCR if not already done (lazy loading)
        if not hasattr(self, 'paddle_ocr'):
            from paddleocr import PaddleOCR
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        
        # Run OCR (v2.x API uses ocr method)
        result = self.paddle_ocr.ocr(cropped, cls=True)
        
        # Extract all text
        if result and result[0]:
            texts = [line[1][0] for line in result[0]]
            return ' '.join(texts)
        
        return ""
    
    def search(self, rgb: tuple, tolerance: int = 0, rotation_amount: int = 100, 
               max_attempts: int = 8, debug: bool = False) -> Optional[Region]:
        """
        Search for a color by rotating the camera until found.
        Useful for finding objects in the game world when they may not be visible initially.
        
        Args:
            rgb: Tuple of (R, G, B) values to search for (0-255 each)
            tolerance: Color matching tolerance (0 = exact match, higher = more lenient)
            rotation_amount: Minimum drag distance in pixels for camera rotation (default 100)
            max_attempts: Maximum number of camera rotations before giving up (default 8)
            debug: If True, save debug images for each attempt
            
        Returns:
            Region object if color found, None if not found after max_attempts
        """
        if not self.window:
            return None
        
        for attempt in range(max_attempts):
            # Capture current screen
            self.capture(debug=debug)
            
            # Try to find the color
            found = self.find_color_region(rgb, tolerance=tolerance, debug=debug)
            
            if found:
                if debug:
                    print(f"Found color on attempt {attempt + 1}")
                return found
            
            # Not found, rotate camera
            if debug:
                print(f"Attempt {attempt + 1}/{max_attempts}: Color not found, rotating camera...")
            
            # Rotate camera using rotate_camera method
            self.rotate_camera(rotation_amount)
            
            # Small delay to let camera settle
            sleep(0.1)
        
        if debug:
            print(f"Color not found after {max_attempts} attempts")
        
        return None

    def is_in_game_area(self, x: int, y: int) -> bool:
        """
        Check if a point is within the GAME_AREA region.
        Args:
            x: X coordinate relative to window
            y: Y coordinate relative to window
        
        Returns:
            True if point is within GAME_AREA, False otherwise
        """
        return self.GAME_AREA.contains(x, y)

    def rotate_camera(self, min_drag_distance: int) -> bool:
        """
        Rotate camera by dragging middle mouse from a random point in any random direction.
        The drag distance is at least min_drag_distance pixels, and the end point stays within the GAME_AREA.
        Duration and curve_intensity are randomized within class-defined bounds for natural movement.
        
        Args:
            min_drag_distance: Minimum drag distance in pixels
            
        Returns:
            True if successful, False if no window found or invalid parameters
        """
        if not self.window:
            return False
        
        if min_drag_distance <= 0:
            return False
        
        # Randomize duration and curve intensity for natural movement
        duration = random.uniform(self.ROTATE_DURATION_MIN, self.ROTATE_DURATION_MAX)
        curve_intensity = random.uniform(self.ROTATE_CURVE_INTENSITY_MIN, self.ROTATE_CURVE_INTENSITY_MAX)
        
        # Use GAME_AREA bounds for camera rotation
        game_area = self.GAME_AREA
        min_x = game_area.x
        min_y = game_area.y
        max_x = game_area.x + game_area.width - 1
        max_y = game_area.y + game_area.height - 1
        
        # Try to find a valid start/end point combination
        max_tries = 100
        for _ in range(max_tries):
            # Pick a random starting point within GAME_AREA
            start_x = random.randint(min_x, max_x)
            start_y = random.randint(min_y, max_y)
            
            # Pick a random angle (0-360 degrees)
            angle = random.uniform(0, 2 * math.pi)
            
            # Calculate end point based on angle and min distance
            # Try with the minimum distance first
            drag_distance = min_drag_distance
            
            # Calculate potential end point
            end_x = start_x + int(drag_distance * math.cos(angle))
            end_y = start_y + int(drag_distance * math.sin(angle))
            
            # Check if end point is within GAME_AREA bounds
            if min_x <= end_x <= max_x and min_y <= end_y <= max_y:
                # Valid combination found
                # Convert window-relative coordinates to screen coordinates
                screen_start_x = self.window['x'] + start_x
                screen_start_y = self.window['y'] + start_y
                screen_end_x = self.window['x'] + end_x
                screen_end_y = self.window['y'] + end_y
                
                # Move mouse to start position first
                self.mouse.move_to(screen_start_x, screen_start_y, duration=0.1, curve_intensity=0.5)
                sleep(0.05)
                
                # Perform the drag
                self.mouse.drag_middle_mouse(screen_end_x, screen_end_y, duration, curve_intensity)
                
                return True
            else:
                # End point is out of bounds, try to adjust distance
                # Calculate maximum distance we can go in this direction
                max_distance_x = (max_x - start_x) / math.cos(angle) if math.cos(angle) != 0 else float('inf')
                max_distance_y = (max_y - start_y) / math.sin(angle) if math.sin(angle) != 0 else float('inf')
                
                # Handle negative directions
                if math.cos(angle) < 0:
                    max_distance_x = (start_x - min_x) / abs(math.cos(angle))
                if math.sin(angle) < 0:
                    max_distance_y = (start_y - min_y) / abs(math.sin(angle))
                
                # Take the minimum of the two constraints
                max_distance = min(abs(max_distance_x), abs(max_distance_y))
                
                # Check if we can meet minimum distance requirement
                if max_distance >= min_drag_distance:
                    # Use minimum distance
                    end_x = start_x + int(min_drag_distance * math.cos(angle))
                    end_y = start_y + int(min_drag_distance * math.sin(angle))
                    
                    # Clamp to ensure we're within GAME_AREA bounds (floating point safety)
                    end_x = max(min_x, min(max_x, end_x))
                    end_y = max(min_y, min(max_y, end_y))
                    
                    # Convert to screen coordinates
                    screen_start_x = self.window['x'] + start_x
                    screen_start_y = self.window['y'] + start_y
                    screen_end_x = self.window['x'] + end_x
                    screen_end_y = self.window['y'] + end_y
                    
                    # Move mouse to start position first
                    self.mouse.move_to(screen_start_x, screen_start_y, duration=0.1, curve_intensity=0.5)
                    sleep(0.05)
                    
                    # Perform the drag
                    self.mouse.drag_middle_mouse(screen_end_x, screen_end_y, duration, curve_intensity)
                    
                    return True
        
        # Couldn't find valid combination after max tries
        return False
