"""
Camera control system for positioning camera to make target tiles visible.

Uses API-based calculations with combined diagonal mouse drags and scroll wheel zoom
for natural-looking camera adjustments with closed-loop verification.
"""

import time
import random
import math
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from client.osrs import OSRS


class CameraController:
    """
    Manages camera positioning to make target world tiles visible in viewport.
    
    Uses the RuneLite API to calculate optimal camera angles and zoom, then
    performs combined yaw+pitch adjustments via diagonal middle-mouse drags
    and zoom adjustments via scroll wheel.
    """
    
    # Conversion ratios from API empirical measurements
    YAW_PIXEL_RATIO = 260 / 512    # 260 pixels ≈ 512 yaw units (90 degrees)
    PITCH_PIXEL_RATIO = 65 / 128   # 65 pixels ≈ 128 pitch units
    
    # Scale (zoom) bounds
    MIN_SCALE = 300  # Maximum zoom out
    MAX_SCALE = 650  # Maximum zoom in
    
    # Minimum scale delta to warrant adjustment
    SCALE_THRESHOLD = 5
    
    def __init__(self, osrs: 'OSRS'):
        """
        Initialize camera controller.
        
        Args:
            osrs: OSRS client instance with API and window access
        """
        self.osrs = osrs
        self.api = osrs.api
        self.window = osrs.window
    
    def set_camera_to_tile(self, world_x: int, world_y: int, plane: int = 0, 
                          max_attempts: int = 5) -> bool:
        """
        Position camera to make target world tile visible in viewport.
        
        Uses closed-loop control: adjusts camera, verifies visibility, retries if needed.
        Adjusts scale first (if needed), then performs combined yaw+pitch rotation.
        Early-exits if tile becomes visible at any point.
        
        Args:
            world_x: Target tile world X coordinate
            world_y: Target tile world Y coordinate
            plane: Target tile plane (default 0)
            max_attempts: Maximum adjustment attempts before giving up (default 5)
        
        Returns:
            True if tile is visible in viewport, False if failed after all attempts
        """
        # Get initial camera state to check if scale adjustment needed
        rotation_data = self.api.get_camera_rotation(world_x, world_y, plane)
        
        if not rotation_data:
            print(f"[CameraController] Failed to get initial rotation data")
            return False
        
        # Early exit if already visible
        if rotation_data.get('visible', False):
            print(f"[CameraController] Tile already visible")
            return True
        
        # Adjust scale ONCE before rotation attempts (zoom before rotating)
        current_scale = rotation_data.get('currentScale', 512)
        
        # Always target zoomed-out scale (< 330) for better visibility
        target_scale = random.randint(305, 325)
        
        # Override API suggestion if current scale is too zoomed in
        if current_scale >= 330:
            scale_delta = target_scale - current_scale
            print(f"[CameraController] Current scale too zoomed in ({current_scale}), forcing zoom out to {target_scale}")
        else:
            # Already zoomed out enough, maintain current scale
            target_scale = current_scale
            scale_delta = 0
        
        if abs(scale_delta) > self.SCALE_THRESHOLD:
            print(f"[CameraController] Adjusting scale: {current_scale} -> {target_scale} (delta: {scale_delta})")
            
            self._adjust_scale(target_scale, current_scale, world_x, world_y, plane)
            
            # Early exit check if tile visible after scale adjustment
            rotation_data = self.api.get_camera_rotation(world_x, world_y, plane)
            if rotation_data and rotation_data.get('visible', False):
                print(f"[CameraController] Tile visible after scale adjustment")
                return True
        
        # Now perform rotation attempts (scale is already adjusted)
        last_yaw = None
        last_pitch = None
        stuck_count = 0
        
        for attempt in range(max_attempts):
            # Get current camera state for this attempt
            rotation_data = self.api.get_camera_rotation(world_x, world_y, plane)
            
            if not rotation_data:
                print(f"[CameraController] Failed to get rotation data (attempt {attempt + 1}/{max_attempts})")
                time.sleep(random.uniform(0.4, 0.6))
                continue
            
            # Early exit if visible
            if rotation_data.get('visible', False):
                print(f"[CameraController] Tile visible (attempt {attempt + 1})")
                return True
            
            # Detect if camera is stuck (not moving between attempts)
            current_yaw = rotation_data.get('currentYaw')
            current_pitch = rotation_data.get('currentPitch')
            
            if last_yaw is not None and current_yaw == last_yaw and current_pitch == last_pitch:
                stuck_count += 1
                print(f"[CameraController] Camera hasn't moved (stuck count: {stuck_count})")
                if stuck_count >= 3:
                    print(f"[CameraController] Camera stuck after 3 attempts, aborting")
                    return False
            else:
                stuck_count = 0  # Reset if camera moved
            
            last_yaw = current_yaw
            last_pitch = current_pitch
            
            # Perform combined yaw+pitch adjustment (diagonal drag)
            if not rotation_data:
                print(f"[CameraController] Failed to get rotation data, retrying...")
                time.sleep(random.uniform(0.5, 0.8))
                continue
                
            drag_x = rotation_data.get('dragPixelsX', 0)
            drag_y = rotation_data.get('dragPixelsY', 0)
            yaw_distance = abs(rotation_data.get('yawDistance', 0))
            
            # Debug: show what API returned
            print(f"[CameraController] API returned: dragX={drag_x}, dragY={drag_y}, yawDist={yaw_distance}")
            print(f"[CameraController] Raw rotation data: {rotation_data}")
            
            # Skip if adjustments are below game's threshold (empirically, < 5px doesn't move camera)
            if abs(drag_x) < 5 and abs(drag_y) < 5:
                print(f"[CameraController] Drags too small to execute (< 5px, game threshold)")
                print(f"[CameraController] Tile at screen position but not marked visible by API")
                # If we're this close, consider it a success even if API says not visible
                return True
            
            print(f"[CameraController] Adjusting camera: dx={drag_x}, dy={drag_y}")
            self._adjust_camera_combined(drag_x, drag_y)
            
            # Wait for camera adjustment to complete
            time.sleep(random.uniform(0.4, 0.6))
            
            # Verify if tile is now visible
            rotation_data = self.api.get_camera_rotation(world_x, world_y, plane)
            if rotation_data and rotation_data.get('visible', False):
                print(f"[CameraController] Success! Tile visible after adjustment (attempt {attempt + 1})")
                return True
            
            # If not last attempt, add delay before retry
            if attempt < max_attempts - 1:
                print(f"[CameraController] Tile not visible, retrying... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(random.uniform(0.4, 0.6))
        
        print(f"[CameraController] Failed to make tile visible after {max_attempts} attempts")
        return False
    
    def _adjust_scale(self, target_scale: int, current_scale: int, world_x: int, world_y: int, plane: int, max_retries: int = 2):
        """
        Adjust camera zoom using scroll wheel with verification.
        
        Args:
            target_scale: Desired zoom level
            current_scale: Current zoom level
            world_x: Target world X coordinate for verification
            world_y: Target world Y coordinate for verification
            plane: Target plane for verification
            max_retries: Maximum retry attempts if scale doesn't reach target (default 2)
        """
        for attempt in range(max_retries):
            # Calculate scroll delta needed
            scale_delta = target_scale - current_scale
            
            # Convert OSRS scale delta to Windows scroll units (120 = 1 click)
            # Use 50x multiplier to ensure significant zoom change (scale range is 300-650)
            # Each scale unit should be ~4 scroll wheel clicks for visible effect
            scroll_delta = scale_delta * 50
            print(f"[CameraController] Scrolling {scroll_delta} units (scale {current_scale} -> {target_scale}) [attempt {attempt + 1}/{max_retries}]")
            
            # Apply ±10% randomization to make it less predictable
            variance = random.uniform(-0.10, 0.10)
            randomized_delta = int(scroll_delta * (1 + variance))
            
            # Clamp to reasonable bounds (±600 = ~5 scroll clicks max)
            randomized_delta = max(-600, min(600, randomized_delta))
            
            if randomized_delta == 0:
                print(f"[CameraController] No scroll needed, scale already at target")
                return
            
            # Move mouse to center of viewport for scroll to work
            # Scroll wheel only affects the area under the mouse cursor
            if not self.window.window:
                print("[CameraController] Window not found, cannot position mouse for scroll")
                return
                
            viewport_center_x = self.window.window['x'] + self.window.window['width'] // 2
            viewport_center_y = self.window.window['y'] + self.window.window['height'] // 2
            self.window.mouse.move_to(viewport_center_x, viewport_center_y)
            time.sleep(0.1)  # Brief pause for mouse to settle
            
            # Perform scroll wheel adjustment
            duration = random.uniform(0.25, 0.4)
            self.window.mouse.scroll_wheel(randomized_delta, duration)
            
            # Wait for scale adjustment to complete
            time.sleep(random.uniform(1.2, 1.8))
            
            # Verify scale adjustment
            rotation_data = self.api.get_camera_rotation(world_x, world_y, plane)
            if rotation_data:
                new_scale = rotation_data.get('currentScale', 512)
                if new_scale < 330:
                    print(f"[CameraController] Scale adjustment successful: {new_scale}")
                    return
                else:
                    print(f"[CameraController] Scale still too zoomed in ({new_scale}), target was < 330")
                    if attempt < max_retries - 1:
                        print(f"[CameraController] Retrying scale adjustment...")
                        current_scale = new_scale  # Update for next attempt
                    else:
                        print(f"[CameraController] WARNING: Failed to reach target scale after {max_retries} attempts")
            else:
                print(f"[CameraController] WARNING: Could not verify scale adjustment")
                return
    
    def _adjust_camera_combined(self, dx_pixels: int, dy_pixels: int):
        """
        Perform combined yaw+pitch adjustment using diagonal middle-mouse drag.
        
        Args:
            dx_pixels: Horizontal drag distance (positive=right, negative=left)
            dy_pixels: Vertical drag distance (positive=down, negative=up)
        """
        # Apply ±7% variance to both components for human-like behavior
        variance_x = random.uniform(-0.07, 0.07)
        variance_y = random.uniform(-0.07, 0.07)
        
        adjusted_dx = int(dx_pixels * (1 + variance_x))
        adjusted_dy = int(dy_pixels * (1 + variance_y))
        
        # Calculate distance to ensure meaningful drag
        distance = math.sqrt(adjusted_dx ** 2 + adjusted_dy ** 2)
        
        # Skip if drag distance too small
        if distance < 5:
            return
        
        # Perform the precise camera drag
        self._perform_camera_drag(adjusted_dx, adjusted_dy)
    
    def _perform_camera_drag(self, dx: int, dy: int):
        """
        Perform precise middle-mouse drag for camera adjustment.
        
        Splits large drags into multiple segments to avoid hitting game area boundaries.
        
        Args:
            dx: Horizontal pixel distance (positive=right, negative=left)
            dy: Vertical pixel distance (positive=down, negative=up)
        """
        from config.regions import GAME_AREA
        
        # Get window position for screen coordinate conversion
        window_info = self.window.window
        if not window_info:
            print("[CameraController] Window not found for camera drag")
            return
        
        window_x = window_info['x']
        window_y = window_info['y']
        
        # Calculate how many segments needed to avoid boundaries
        # Max safe drag is ~200 pixels to stay well within game area
        max_safe_drag = 200
        drag_distance = math.sqrt(dx**2 + dy**2)
        num_segments = max(1, int(math.ceil(drag_distance / max_safe_drag)))
        
        # Divide total drag into segments
        segment_dx = dx / num_segments
        segment_dy = dy / num_segments
        
        print(f"[CameraController] Splitting drag ({dx}, {dy}) into {num_segments} segments")
        
        # Perform each segment
        for i in range(num_segments):
            # Find valid start point within game area (center with randomization)
            game_center_x = GAME_AREA.x + GAME_AREA.width // 2
            game_center_y = GAME_AREA.y + GAME_AREA.height // 2
            
            # Add small randomization to start point (±20 pixels from center)
            start_x = game_center_x + random.randint(-20, 20)
            start_y = game_center_y + random.randint(-20, 20)
            
            # Calculate end point for this segment
            end_x = start_x + int(segment_dx)
            end_y = start_y + int(segment_dy)
            
            # Clamp end point to stay within game area bounds
            end_x = max(GAME_AREA.x, min(GAME_AREA.x + GAME_AREA.width, end_x))
            end_y = max(GAME_AREA.y, min(GAME_AREA.y + GAME_AREA.height, end_y))
            
            # Convert to screen coordinates
            screen_start_x = window_x + start_x
            screen_start_y = window_y + start_y
            screen_end_x = window_x + end_x
            screen_end_y = window_y + end_y
            
            # Move to start position
            self.window.mouse.move_to(
                screen_start_x, 
                screen_start_y, 
                duration=random.uniform(0.08, 0.15),
                curve_intensity=random.uniform(0.3, 0.5)
            )
            
            time.sleep(random.uniform(0.03, 0.06))
            
            # Perform middle-mouse drag to end position
            drag_duration = random.uniform(0.2, 0.35)
            drag_curve = random.uniform(0.3, 0.6)
            
            self.window.mouse.drag_middle_mouse(
                screen_end_x,
                screen_end_y,
                duration=drag_duration,
                curve_intensity=drag_curve
            )
            
            # Small delay between segments (except after last segment)
            if i < num_segments - 1:
                time.sleep(random.uniform(0.1, 0.2))
