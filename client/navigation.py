"""
Navigation system for OSRS bot using minimap and coordinate-based movement.

Implements coordinate reading, minimap clicking with yaw rotation, path chunking
for long distances, and movement validation with stuck detection.
"""

import math
import time
import random
from typing import Optional, Tuple, List
from collections import deque
from util import Window
from config.regions import (
    COORD_WORLD_REGION,
    COORD_SCENE_REGION,
    CAMERA_YAW_REGION,
    MINIMAP_REGION,
    MINIMAP_CENTER,
    MINIMAP_COMPASS_REGION
)


class NavigationManager:
    """
    Manages coordinate-based navigation using the minimap.
    
    Features:
    - Reads world/scene coordinates from RuneLite overlay via OCR
    - Reads camera yaw angle (0-2048 units) for rotation handling
    - Clicks minimap with yaw-adjusted offsets for directional movement
    - Chunks long paths into multiple waypoints (linear interpolation)
    - Validates arrival with 2-tile tolerance
    - Detects stuck players (no movement for 3+ seconds)
    
    Future Enhancements:
    - A* pathfinding with collision detection (currently uses linear paths)
    - Minimap scale calibration for accuracy tuning
    - Game area clicking (extended from minimap system)
    """
    
    def __init__(self, window: Window):
        """
        Initialize navigation manager.
        
        Args:
            window: Window instance for screen capture and interaction
        """
        self.window = window
        
        # Minimap scale: pixels per tile (estimated, calibratable later)
        self.minimap_scale = 4.0
        
        # Movement validation tracking
        self._position_history = deque(maxlen=4)  # Last 4 positions with timestamps
        self._last_check_time = 0
        
    def read_world_coordinates(self) -> Optional[Tuple[int, int]]:
        """
        Read current world coordinates from RuneLite overlay.
        
        Returns:
            Tuple of (x, y) world coordinates, or None if reading failed
        """
        if not self.window.window:
            return None
        
        self.window.capture()
        text = self.window.read_text(COORD_WORLD_REGION, debug=False)
        
        if not text:
            return None
        
        try:
            # Expected format: "3222, 3218" or "3222,3218"
            parts = text.replace(" ", "").split(",")
            if len(parts) == 2:
                x = int(parts[0])
                y = int(parts[1])
                return (x, y)
        except (ValueError, IndexError):
            pass
        
        return None
    
    def read_scene_coordinates(self) -> Optional[Tuple[int, int]]:
        """
        Read current scene coordinates from RuneLite overlay.
        
        Returns:
            Tuple of (x, y) scene coordinates, or None if reading failed
        """
        if not self.window.window:
            return None
        
        self.window.capture()
        text = self.window.read_text(COORD_SCENE_REGION, debug=False)
        
        if not text:
            return None
        
        try:
            # Expected format: "52, 48" or "52,48"
            parts = text.replace(" ", "").split(",")
            if len(parts) == 2:
                x = int(parts[0])
                y = int(parts[1])
                return (x, y)
        except (ValueError, IndexError):
            pass
        
        return None
    
    def read_camera_yaw(self) -> Optional[int]:
        """
        Read current camera yaw angle from RuneLite overlay.
        
        RuneLite yaw format: 0-2048 units (0 = north, counter-clockwise)
        Corrected mapping: 0=N, 512=W, 1024=S, 1536=E
        
        Returns:
            Yaw angle as integer (0-2048), or None if reading failed
        """
        if not self.window.window:
            return None
        
        self.window.capture()
        text = self.window.read_text(CAMERA_YAW_REGION, debug=False)
        
        if not text:
            return None
        
        try:
            # Expected format: "1024" or similar integer
            yaw = int(text.strip())
            # Validate range
            if 0 <= yaw <= 2048:
                return yaw
        except ValueError:
            pass
        
        return None
    
    def get_cardinal_direction(self, yaw: Optional[int] = None) -> str:
        """
        Convert yaw angle to 8-direction cardinal direction string.
        
        Args:
            yaw: Yaw angle (0-2048), or None to read current yaw
            
        Returns:
            Cardinal direction: N, NE, E, SE, S, SW, W, NW, or "Unknown"
        """
        if yaw is None:
            yaw = self.read_camera_yaw()
        
        if yaw is None:
            return "Unknown"
        
        # 8 directions, each spanning 256 units (2048/8)
        # Corrected: counter-clockwise from north
        # Add 128 to center each direction, then modulo to handle wraparound
        adjusted = (yaw + 128) % 2048
        octant = adjusted // 256
        
        directions = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
        return directions[octant]
    
    def click_compass_to_north(self) -> bool:
        """
        Click the minimap compass to reset camera to true north (yaw = 0).
        
        This is useful as a fallback when yaw reading fails or as a way to
        standardize camera orientation before navigation.
        
        Returns:
            True if compass was clicked successfully
        """
        if not self.window.window:
            return False
        
        print("Clicking minimap compass to reset to north...")
        
        # Ensure we have a fresh capture
        self.window.capture()
        
        # Click random point within compass region
        compass_point = MINIMAP_COMPASS_REGION.random_point()
        self.window.click_at(compass_point)
        
        # Camera snaps instantly, just brief pause for click to register
        time.sleep(random.uniform(0.2, 0.3))
        
        # Verify it worked
        yaw = self.read_camera_yaw()
        if yaw is not None and yaw < 100:  # Should be close to 0
            print(f"✓ Compass clicked, camera at north (yaw: {yaw})")
            return True
        else:
            print(f"Warning: Compass clicked but yaw reading unclear (yaw: {yaw})")
            return True  # Still return True since we clicked it
    
    def _click_minimap_offset(self, dx: int, dy: int) -> bool:
        """
        Click the minimap at an offset from current position, accounting for camera yaw.
        
        Args:
            dx: Tile offset in x direction (positive = east)
            dy: Tile offset in y direction (positive = north)
            
        Returns:
            True if click executed successfully, False if out of bounds
        """
        if not self.window.window:
            return False
        
        # Read camera yaw for rotation
        yaw = self.read_camera_yaw()
        if yaw is None:
            print("Warning: Could not read camera yaw, clicking compass to reset to north")
            if self.click_compass_to_north():
                yaw = 0  # Compass resets to north
            else:
                print("Error: Failed to reset compass, cannot proceed with navigation")
                return False
        
        # Convert yaw (0-2048) to radians
        # 0 = north, 512 = east, 1024 = south, 1536 = west
        yaw_radians = yaw * 2 * math.pi / 2048
        
        # Apply rotation matrix to tile delta
        # Rotation: [cos(θ), -sin(θ); sin(θ), cos(θ)]
        rotated_dx = dx * math.cos(yaw_radians) - dy * math.sin(yaw_radians)
        rotated_dy = dx * math.sin(yaw_radians) + dy * math.cos(yaw_radians)
        
        # Convert to minimap pixels
        pixel_dx = rotated_dx * self.minimap_scale
        pixel_dy = -rotated_dy * self.minimap_scale  # Negative because screen y increases downward
        
        # Calculate target position from minimap center
        center = MINIMAP_CENTER.center()
        target_x = center[0] + pixel_dx
        target_y = center[1] + pixel_dy
        
        # Add random jitter (2-3 pixels)
        target_x += random.uniform(-2.5, 2.5)
        target_y += random.uniform(-2.5, 2.5)
        
        # Boundary check: ensure click is within minimap circle
        # The minimap is circular, not rectangular, so we need to check distance from center
        minimap_radius = MINIMAP_REGION.width / 2.0  # Assumes square region
        distance_from_center = math.sqrt((target_x - center[0])**2 + (target_y - center[1])**2)
        
        if distance_from_center > minimap_radius:
            print(f"Warning: Click target ({target_x:.1f}, {target_y:.1f}) outside minimap circle")
            print(f"  Distance from center: {distance_from_center:.1f}px, radius: {minimap_radius:.1f}px")
            return False
        
        # Execute click
        self.window.move_mouse_to((int(target_x), int(target_y)))
        time.sleep(random.uniform(0.05, 0.15))
        self.window.click()
        
        return True
    
    def walk_to_tile(self, world_x: int, world_y: int) -> bool:
        """
        Walk to target world coordinates using minimap clicks.
        
        Long distances are automatically chunked into waypoints every 10-12 tiles.
        Uses linear interpolation for pathfinding (no obstacle avoidance yet).
        
        Args:
            world_x: Target world x coordinate
            world_y: Target world y coordinate
            
        Returns:
            True if successfully reached target (within 2 tiles), False otherwise
        """
        if not self.window.window:
            return False
        
        # Read current position
        current_pos = self.read_world_coordinates()
        if current_pos is None:
            print("Error: Could not read current coordinates")
            return False
        
        current_x, current_y = current_pos
        
        # Calculate total distance
        dx = world_x - current_x
        dy = world_y - current_y
        distance = math.sqrt(dx**2 + dy**2)
        
        print(f"Walking from ({current_x}, {current_y}) to ({world_x}, {world_y})")
        print(f"Distance: {distance:.1f} tiles")
        
        # Check if already at target (within tolerance)
        if distance <= 2:
            print("Already at target location")
            return True
        
        # Generate waypoints if distance > 12 tiles
        waypoints = []
        if distance > 12:
            # Chunk into segments of 10-12 tiles (randomized)
            num_segments = math.ceil(distance / 11)
            for i in range(1, num_segments):
                progress = i / num_segments
                wp_x = int(current_x + dx * progress)
                wp_y = int(current_y + dy * progress)
                waypoints.append((wp_x, wp_y))
        
        # Add final target
        waypoints.append((world_x, world_y))
        
        print(f"Path: {len(waypoints)} waypoint(s)")
        
        # Navigate through waypoints
        for i, (wp_x, wp_y) in enumerate(waypoints):
            print(f"\nWaypoint {i+1}/{len(waypoints)}: ({wp_x}, {wp_y})")
            
            # Re-read current position for accuracy
            current_pos = self.read_world_coordinates()
            if current_pos is None:
                print("Error: Lost coordinate tracking")
                return False
            
            current_x, current_y = current_pos
            
            # Calculate offset to waypoint
            wp_dx = wp_x - current_x
            wp_dy = wp_y - current_y
            wp_distance = math.sqrt(wp_dx**2 + wp_dy**2)
            
            print(f"  Current: ({current_x}, {current_y})")
            print(f"  Offset: ({wp_dx:+d}, {wp_dy:+d}) = {wp_distance:.1f} tiles")
            
            # Click minimap
            if not self._click_minimap_offset(wp_dx, wp_dy):
                print("Error: Minimap click failed (out of bounds)")
                return False
            
            # Wait for arrival
            time.sleep(random.uniform(0.8, 1.2))  # Initial movement delay
            
            if not self.wait_until_arrived(wp_x, wp_y, tolerance=2, timeout=10):
                print(f"Failed to reach waypoint {i+1}")
                return False
            
            print(f"  ✓ Reached waypoint {i+1}")
        
        print("\n✓ Successfully reached target")
        return True
    
    def wait_until_arrived(self, target_x: int, target_y: int, tolerance: int = 2, timeout: float = 10.0) -> bool:
        """
        Wait until player arrives at target coordinates or gets stuck.
        
        Args:
            target_x: Target world x coordinate
            target_y: Target world y coordinate
            tolerance: Distance tolerance in tiles (default: 2)
            timeout: Maximum wait time in seconds (default: 10)
            
        Returns:
            True if arrived within tolerance, False if timeout or stuck
        """
        start_time = time.time()
        last_stuck_check = start_time
        distance = float('inf')  # Initialize distance
        
        while time.time() - start_time < timeout:
            # Read current position
            current_pos = self.read_world_coordinates()
            if current_pos is None:
                print("Warning: Could not read coordinates during arrival check")
                time.sleep(random.uniform(0.5, 0.8))
                continue
            
            current_x, current_y = current_pos
            
            # Check if arrived
            distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
            if distance <= tolerance:
                return True
            
            # Check for stuck condition every 3 seconds
            if time.time() - last_stuck_check >= 3.0:
                if self._is_stuck():
                    print("Player appears stuck (no movement detected)")
                    return False
                last_stuck_check = time.time()
            
            # Wait before next check
            time.sleep(random.uniform(0.8, 1.2))
        
        print(f"Timeout waiting for arrival (still {distance:.1f} tiles away)")
        return False
    
    def is_player_moving(self) -> bool:
        """
        Check if player is currently moving by comparing coordinates over time.
        
        Returns:
            True if player position changed in last 0.6 seconds
        """
        pos1 = self.read_world_coordinates()
        if pos1 is None:
            return False
        
        time.sleep(0.6)
        
        pos2 = self.read_world_coordinates()
        if pos2 is None:
            return False
        
        return pos1 != pos2
    
    def _is_stuck(self) -> bool:
        """
        Detect if player is stuck (not moving for 3+ seconds).
        
        Maintains a history of recent positions with timestamps.
        Returns True if all recent positions are identical.
        
        Returns:
            True if player appears stuck, False otherwise
        """
        current_pos = self.read_world_coordinates()
        if current_pos is None:
            return False
        
        current_time = time.time()
        
        # Add current position to history
        self._position_history.append((current_pos, current_time))
        
        # Need at least 3 samples to determine stuck status
        if len(self._position_history) < 3:
            return False
        
        # Check if all positions are identical
        positions = [pos for pos, _ in self._position_history]
        if len(set(positions)) > 1:
            # Movement detected, clear history
            self._position_history.clear()
            return False
        
        # All positions identical - check time span
        oldest_time = self._position_history[0][1]
        time_span = current_time - oldest_time
        
        # Stuck if no movement for 3+ seconds
        return time_span >= 3.0
    
    def calibrate_minimap_scale(self):
        """
        Calibrate minimap scale by walking a known distance and measuring pixels.
        
        TODO: Implementation
        
        Approach:
        1. Record current world coordinates and minimap center
        2. Click minimap at known offset (e.g., 10 tiles north)
        3. Wait for arrival
        4. Measure actual pixel displacement on minimap
        5. Calculate pixels/tile ratio: pixel_distance / tile_distance
        6. Update self.minimap_scale with calibrated value
        
        This method is deferred for future implementation when scale accuracy
        becomes critical for precise navigation tasks.
        """
        print("Minimap scale calibration not yet implemented")
        print(f"Current scale: {self.minimap_scale} pixels/tile")
        print("To calibrate: walk a known distance and measure pixel displacement")
