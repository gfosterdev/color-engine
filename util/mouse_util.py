import ctypes
import time
import random
import math
from typing import Tuple, Optional


class MouseMover:
    """Smoothly move the mouse to emulate human-like movement."""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        
        point = POINT()
        self.user32.GetCursorPos(ctypes.byref(point))
        return (point.x, point.y)
    
    def set_position(self, x: int, y: int) -> None:
        """Set mouse position."""
        self.user32.SetCursorPos(int(x), int(y))
    
    def bezier_curve(self, start: Tuple[float, float], end: Tuple[float, float], 
                     control1: Tuple[float, float], control2: Tuple[float, float], 
                     t: float) -> Tuple[float, float]:
        """
        Calculate point on cubic Bezier curve.
        
        Args:
            start: Starting point (x, y)
            end: Ending point (x, y)
            control1: First control point (x, y)
            control2: Second control point (x, y)
            t: Parameter from 0 to 1
            
        Returns:
            Point on curve (x, y)
        """
        # Cubic Bezier formula: B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        t2 = t * t
        t3 = t2 * t
        
        x = (mt3 * start[0] + 
             3 * mt2 * t * control1[0] + 
             3 * mt * t2 * control2[0] + 
             t3 * end[0])
        
        y = (mt3 * start[1] + 
             3 * mt2 * t * control1[1] + 
             3 * mt * t2 * control2[1] + 
             t3 * end[1])
        
        return (x, y)
    
    def move_to(self, target_x: int, target_y: int, duration: float = 0.25, 
                curve_intensity: float = 1.0) -> None:
        """
        Move mouse to target position with smooth, human-like movement.
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            duration: Time to complete movement in seconds (default 0.25)
            curve_intensity: How curved the path should be (0=straight, 1=moderate, 2=very curved)
        """
        start_x, start_y = self.get_position()
        start = (float(start_x), float(start_y))
        end = (float(target_x), float(target_y))
        
        # Calculate distance
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        
        # Adjust duration based on distance to make it feel more natural
        # Longer distances should take proportionally more time
        # adjusted_duration = max(duration, distance / 1000.0)
        adjusted_duration = duration
        
        # Generate control points for Bezier curve
        # Add some randomness to make movement less predictable
        offset_range = distance * 0.2 * curve_intensity
        
        # Random perpendicular offset for control points
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        perp_angle = angle + math.pi / 2
        
        offset1 = random.uniform(-offset_range, offset_range)
        offset2 = random.uniform(-offset_range, offset_range)
        
        control1 = (
            start[0] + (end[0] - start[0]) * 0.33 + math.cos(perp_angle) * offset1,
            start[1] + (end[1] - start[1]) * 0.33 + math.sin(perp_angle) * offset1
        )
        
        control2 = (
            start[0] + (end[0] - start[0]) * 0.66 + math.cos(perp_angle) * offset2,
            start[1] + (end[1] - start[1]) * 0.66 + math.sin(perp_angle) * offset2
        )
        
        # Number of steps based on duration and desired smoothness
        steps = max(int(adjusted_duration * 60), 10)  # 60 FPS target
        
        # Move along the curve
        for i in range(steps + 1):
            t = i / steps
            
            # Apply easing function for more natural acceleration/deceleration
            # Using ease-in-out for smooth start and end
            eased_t = self._ease_in_out_quad(t)
            
            x, y = self.bezier_curve(start, end, control1, control2, eased_t)
            self.set_position(int(x), int(y))
            
            # Add slight random delays to simulate human imperfection
            delay = (adjusted_duration / steps) * random.uniform(0.8, 1.2)
            time.sleep(delay)
    
    def _ease_in_out_quad(self, t: float) -> float:
        """
        Quadratic ease-in-out function for smooth acceleration/deceleration.
        
        Args:
            t: Input value from 0 to 1
            
        Returns:
            Eased value from 0 to 1
        """
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - pow(-2 * t + 2, 2) / 2
    
    def move_relative(self, dx: int, dy: int, duration: float = 0.25, 
                      curve_intensity: float = 1.0) -> None:
        """
        Move mouse relative to current position.
        
        Args:
            dx: X offset from current position
            dy: Y offset from current position
            duration: Time to complete movement in seconds
            curve_intensity: How curved the path should be
        """
        current_x, current_y = self.get_position()
        self.move_to(current_x + dx, current_y + dy, duration, curve_intensity)
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, duration: float = 0.25, 
              button: str = 'left') -> None:
        """
        Move to position and click.
        
        Args:
            x: X coordinate (if None, click at current position)
            y: Y coordinate (if None, click at current position)
            duration: Time to move to position
            button: 'left' or 'right'
        """
        if x is not None and y is not None:
            self.move_to(x, y, duration)
        
        # Small random delay before clicking (human-like)
        time.sleep(random.uniform(0.05, 0.15))
        
        if button == 'left':
            self.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
            time.sleep(random.uniform(0.05, 0.12))
            self.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
        elif button == 'right':
            self.user32.mouse_event(0x0008, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTDOWN
            time.sleep(random.uniform(0.05, 0.12))
            self.user32.mouse_event(0x0010, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTUP
    
    def drag_middle_mouse(self, target_x: int, target_y: int, duration: float = 0.25, 
                          curve_intensity: float = 1.0) -> None:
        """
        Hold middle mouse button and drag to target position with smooth movement.
        Useful for camera rotation in games like OSRS.
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            duration: Time to complete drag in seconds (default 0.25)
            curve_intensity: How curved the path should be (0=straight, 1=moderate, 2=very curved)
        """
        # Press middle mouse button down
        self.user32.mouse_event(0x0020, 0, 0, 0, 0)  # MOUSEEVENTF_MIDDLEDOWN
        
        # Small delay to ensure button press registers
        time.sleep(random.uniform(0.02, 0.05))
        
        # Move to target while holding button
        self.move_to(target_x, target_y, duration, curve_intensity)
        
        # Small delay before releasing
        time.sleep(random.uniform(0.02, 0.05))
        
        # Release middle mouse button
        self.user32.mouse_event(0x0040, 0, 0, 0, 0)  # MOUSEEVENTF_MIDDLEUP
    
    def scroll_wheel(self, delta: int, duration: float = 0.3):
        """
        Scroll the mouse wheel smoothly.
        
        Args:
            delta: Amount to scroll (positive=up/zoom in, negative=down/zoom out)
                   120 units = 1 "click" of scroll wheel
            duration: Time to spread scroll events over (default 0.3s)
        """
        # Split large deltas into multiple smaller scroll events for smoothness
        num_events = min(max(3, abs(delta) // 60), 5)  # 3-5 scroll events
        delta_per_event = delta // num_events
        remainder = delta % num_events
        
        # Calculate delay between each scroll event
        delay_between = duration / num_events if num_events > 1 else 0
        
        for i in range(num_events):
            # Add remainder to last event to reach exact target
            current_delta = delta_per_event + (remainder if i == num_events - 1 else 0)
            
            # Perform scroll event using MOUSEEVENTF_WHEEL (0x0800)
            self.user32.mouse_event(0x0800, 0, 0, current_delta, 0)
            
            # Random delay between events (except after last one)
            if i < num_events - 1:
                time.sleep(delay_between + random.uniform(-0.02, 0.02))
