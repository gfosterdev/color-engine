"""
Navigation system for OSRS bot using minimap and coordinate-based movement.

Implements coordinate reading, minimap clicking with yaw rotation, path chunking
for long distances, movement validation with stuck detection, and variance-based
pathfinding with collision awareness.
"""

import math
import time
import random
from typing import Optional, Tuple, List, Dict, Any, cast
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
from config.timing import TIMING
from core.config import DEBUG
from .runelite_api import RuneLiteAPI

# Lazy imports for pathfinding (only loaded when needed)
_collision_map = None
_pathfinder = None


class NavigationManager:
    """
    Manages coordinate-based navigation using the minimap.
    
    Features:
    - Reads world/scene coordinates from RuneLite overlay via OCR
    - Reads camera yaw angle (0-2048 units) for rotation handling
    - Clicks minimap with yaw-adjusted offsets for directional movement
    - Variance-based pathfinding with collision awareness (Dijkstra + random edge weights)
    - Path caching with execution randomness for anti-detection
    - Validates arrival with 2-tile tolerance
    - Detects stuck players and triggers re-pathing
    - Dynamic re-pathing (20% chance mid-journey)
    """
    
    def __init__(self, window: Window, profile_config: Optional[dict] = None):
        """
        Initialize navigation manager.
        
        Args:
            window: Window instance for screen capture and interaction
            profile_config: Optional profile configuration dict with pathfinding settings
        """
        self.window = window

        self.api = RuneLiteAPI()
        
        # Minimap scale: pixels per tile (estimated, calibratable later)
        self.minimap_scale = 4.0
        
        # Movement validation tracking
        self._position_history = deque(maxlen=4)  # Last 4 positions with timestamps
        self._last_check_time = 0
        
        # Pathfinding configuration (lazy-loaded)
        self._pathfinding_enabled = False
        self._pathfinding_config = self._init_pathfinding_config(profile_config)
        
        # Track stuck detection for re-pathing
        self._stuck_count = 0
        self._last_stuck_position = None
    
    def _init_pathfinding_config(self, profile_config: Optional[dict] = None) -> dict:
        """
        Initialize pathfinding configuration from profile.
        
        Args:
            profile_config: Profile configuration dictionary
            
        Returns:
            Pathfinding configuration dict with defaults
        """
        default_config = {
            "variance_level": "moderate",  # conservative, moderate, aggressive
            "repathing_chance": 0.05,       # 20% chance to re-path mid-journey
            "path_cache_size": 100,         # Max cached paths
            "region_cache_size": 50,        # Max cached collision regions
            "enable_pathfinding": True      # Use collision-aware pathfinding
        }
        
        if profile_config and "pathfinding" in profile_config:
            default_config.update(profile_config["pathfinding"])
        
        return default_config
    
    def _ensure_pathfinding_loaded(self) -> bool:
        """
        Lazy-load pathfinding modules when first needed.
        
        Returns:
            True if pathfinding loaded successfully, False otherwise
        """
        global _collision_map, _pathfinder
        
        if not self._pathfinding_config.get("enable_pathfinding", True):
            return False
        
        if _collision_map is not None and _pathfinder is not None:
            return True
        
        try:
            from util.collision_util import CollisionMap
            from client.pathfinder import VariancePathfinder
            
            if DEBUG:
                print("Loading collision map and pathfinder...")
            # CollisionMap singleton - parameters are correct despite type checker warning
            _collision_map = CollisionMap(
                zip_path=None,  # type: ignore[call-arg]
                max_cache_size=self._pathfinding_config.get("region_cache_size", 50)  # type: ignore[call-arg]
            )
            _pathfinder = VariancePathfinder(
                collision_map=_collision_map,
                max_cache_size=self._pathfinding_config.get("path_cache_size", 100)
            )
            
            self._pathfinding_enabled = True
            if DEBUG:
                print("✓ Pathfinding system loaded")
            return True
            
        except FileNotFoundError as e:
            print(f"Pathfinding disabled: {e}")
            print("Run: python scripts/download_collision_data.py")
            self._pathfinding_enabled = False
            return False
        except Exception as e:
            print(f"Error loading pathfinding: {e}")
            self._pathfinding_enabled = False
            return False
        
    def read_world_coordinates(self) -> Optional[Tuple[int, int]]:
        """
        Read world coordinates from RuneLite API

        Returns:
            Tuple of (x, y) world coordinates, or None if reading failed
        """

        data = self.api.get_coords()
        if data and "world" in data:
            world = data["world"]
            return (world.get("x", 0), world.get("y", 0))
        return None
    
    def read_scene_coordinates(self) -> Optional[Tuple[int, int]]:
        """
        Read scene coordinates from RuneLite API.

        Returns:
            Tuple of (x, y) scene coordinates, or None if reading failed
        """

        data = self.api.get_coords()
        if data and "local" in data:
            local = data["local"]
            return (local.get("sceneX", 0), local.get("sceneY", 0))
        return None

    def read_camera_yaw(self) -> Optional[int]:
        """
        Read current camera yaw angle from RuneLite API.

        Returns:
            Yaw angle as integer (0-2048), or None if reading failed
        """

        data = self.api.get_camera()
        if data and "yaw" in data:
            return data["yaw"]
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
        
        if DEBUG:
            print("Clicking minimap compass to reset to north...")
        
        # Ensure we have a fresh capture
        self.window.capture()
        
        # Click random point within compass region
        compass_point = MINIMAP_COMPASS_REGION.random_point()
        self.window.click_at(*compass_point)
        
        # Camera snaps instantly, just brief pause for click to register
        time.sleep(random.uniform(*TIMING.INTERFACE_TRANSITION))
        
        # Verify it worked
        yaw = self.read_camera_yaw()
        if yaw is not None and yaw < 100:  # Should be close to 0
            if DEBUG:
                print(f"✓ Compass clicked, camera at north (yaw: {yaw})")
            return True
        else:
            if DEBUG:
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
            if DEBUG:
                print("Warning: Could not read camera yaw, clicking compass to reset to north")
            if self.click_compass_to_north():
                yaw = 0  # Compass resets to north
            else:
                print("Error: Failed to reset compass, cannot proceed with navigation")
                return False
        
        # Convert yaw (0-2048) to radians
        # 0 = north, 512 = east, 1024 = south, 1536 = west
        yaw_radians = yaw * 2 * math.pi / 2048
        
        # Apply inverse rotation matrix to convert world offsets to minimap offsets
        # We rotate by -yaw to counter the camera rotation
        # Rotation by -θ: [cos(θ), sin(θ); -sin(θ), cos(θ)]
        rotated_dx = dx * math.cos(yaw_radians) + dy * math.sin(yaw_radians)
        rotated_dy = -dx * math.sin(yaw_radians) + dy * math.cos(yaw_radians)
        
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
            if DEBUG:
                print(f"Warning: Click target ({target_x:.1f}, {target_y:.1f}) outside minimap circle")
                print(f"  Distance from center: {distance_from_center:.1f}px, radius: {minimap_radius:.1f}px")
            return False
        
        # Execute click (mouse movement has built-in delay)
        self.window.move_mouse_to((int(target_x), int(target_y)))
        self.window.click()
        
        return True
    
    def walk_to_tile(self, world_x: int, world_y: int, plane: int = 0, use_pathfinding: bool = True) -> bool:
        """
        Walk to target world coordinates using minimap clicks.
        
        If pathfinding is enabled and collision data is available, uses variance-based
        pathfinding with collision avoidance. Otherwise falls back to linear interpolation.
        
        Long distances are automatically chunked into waypoints.
        
        Args:
            world_x: Target world x coordinate
            world_y: Target world y coordinate
            plane: Plane/height level (default: 0)
            use_pathfinding: Whether to use pathfinding (default: True)
            
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
        
        if DEBUG:
            print(f"Walking from ({current_x}, {current_y}) to ({world_x}, {world_y})")
            print(f"Distance: {distance:.1f} tiles")
        
        # Check if already at target (within tolerance)
        if distance <= 2:
            if DEBUG:
                print("Already at target location")
            return True
        
        # Try to use pathfinding if enabled
        waypoints = None
        if use_pathfinding and self._ensure_pathfinding_loaded():
            try:
                if DEBUG:
                    print("Using collision-aware pathfinding...")
                start = (current_x, current_y, plane)
                goal = (world_x, world_y, plane)
                variance_level = self._pathfinding_config.get("variance_level", "moderate")
                
                if _pathfinder is not None:
                    waypoints = _pathfinder.find_path(start, goal, variance_level=variance_level)
                else:
                    waypoints = None
                
                if waypoints:
                    if DEBUG:
                        print(f"✓ Path found: {len(waypoints)} tiles")
                    # Convert to simpler format and chunk for minimap range
                    waypoints = [(x, y) for x, y, z in waypoints]
                else:
                    if DEBUG:
                        print("No path found, falling back to linear navigation")
                    
            except Exception as e:
                if DEBUG:
                    print(f"Pathfinding error: {e}, falling back to linear navigation")
                waypoints = None
        
        # Fallback: Generate linear waypoints if pathfinding unavailable or failed
        if waypoints is None:
            if DEBUG:
                print("Using linear path navigation...")
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
        
        # Chunk waypoints for minimap range (max 12 tiles per click)
        # At this point waypoints is always List[Tuple[int, int]]
        waypoints_2d = cast(List[Tuple[int, int]], waypoints)
        chunked_waypoints = self._chunk_waypoints_for_minimap(waypoints_2d, current_pos)
        
        if DEBUG:
            print(f"Executing path: {len(chunked_waypoints)} waypoint(s)")
        
        # Navigate through waypoints
        for i, (wp_x, wp_y) in enumerate(chunked_waypoints):
            if DEBUG:
                print(f"\nWaypoint {i+1}/{len(chunked_waypoints)}: ({wp_x}, {wp_y})")
            
            # Random re-pathing chance (anti-ban)
            if i > 0 and random.random() < self._pathfinding_config.get("repathing_chance", 0.05):
                if DEBUG:
                    print("  ↻ Dynamic re-pathing triggered")
                # Re-calculate remaining path with new random seed
                return self.walk_to_tile(world_x, world_y, plane, use_pathfinding=True)
            
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
            
            if DEBUG:
                print(f"  Current: ({current_x}, {current_y})")
                print(f"  Offset: ({wp_dx:+d}, {wp_dy:+d}) = {wp_distance:.1f} tiles")
            
            # Click minimap
            if not self._click_minimap_offset(wp_dx, wp_dy):
                print("Error: Minimap click failed (out of bounds)")
                return False
            
            # Wait for arrival with stuck detection
            time.sleep(random.uniform(*TIMING.GAME_TICK))  # Wait full game tick for movement to register in API
            
            if not self.wait_until_arrived(wp_x, wp_y, plane=plane, tolerance=2, timeout=30):
                # Check if we're stuck
                if self._is_stuck():
                    if DEBUG:
                        print("  ⚠ Stuck detected, attempting re-path...")
                    self._stuck_count += 1
                    self._last_stuck_position = (current_x, current_y)
                    
                    # Clear path cache to force new calculation
                    if _pathfinder:
                        _pathfinder.clear_cache()
                    
                    # Retry navigation with fresh path
                    if self._stuck_count < 3:
                        return self.walk_to_tile(world_x, world_y, plane, use_pathfinding=True)
                    else:
                        print("  ✗ Failed after 3 re-path attempts")
                        return False
                else:
                    print(f"Failed to reach waypoint {i+1}")
                    return False
            
            # Reset stuck counter on successful waypoint
            self._stuck_count = 0
            if DEBUG:
                print(f"  ✓ Reached waypoint {i+1}")
        
        if DEBUG:
            print("\n✓ Successfully reached target")
        return True
    
    def _chunk_waypoints_for_minimap(
        self,
        waypoints: List[Tuple[int, int]],
        current_pos: Tuple[int, int],
        max_distance: int = 12
    ) -> List[Tuple[int, int]]:
        """
        Intelligently select waypoints to maximize minimap click distance.
        Uses greedy algorithm to skip intermediate waypoints when possible,
        resulting in fewer total clicks for more human-like navigation.
        
        Searches backwards from max_distance to prioritize furthest reachable waypoints.
        
        Args:
            waypoints: Full list of path waypoints
            current_pos: Current player position
            max_distance: Maximum tiles per minimap click (default: 12)
            
        Returns:
            Optimized waypoints list with maximum spacing
        """
        if not waypoints:
            return []
        
        # If only one waypoint, just return it
        if len(waypoints) == 1:
            return waypoints
        
        chunked = []
        last_pos = current_pos
        i = 0
        min_useful_distance = 3  # Skip waypoints closer than 3 tiles
        
        while i < len(waypoints):
            farthest_index = i
            farthest_distance = 0.0
            
            # Search backwards from max_distance to find furthest reachable waypoint
            # This ensures we always try to maximize click distance first
            for j in range(len(waypoints) - 1, i - 1, -1):
                dx = waypoints[j][0] - last_pos[0]
                dy = waypoints[j][1] - last_pos[1]
                dist = math.sqrt(dx**2 + dy**2)
                
                # Found a waypoint within range - take it if it's the furthest so far
                if dist <= max_distance:
                    if dist > farthest_distance:
                        farthest_index = j
                        farthest_distance = dist
                        # If we found a good distant waypoint, use it
                        if dist >= min_useful_distance:
                            break
            
            # If no waypoint was found beyond minimum distance, take the closest valid one
            if farthest_distance < min_useful_distance and farthest_index == i:
                # Search forward for first waypoint within range
                for j in range(i, len(waypoints)):
                    dx = waypoints[j][0] - last_pos[0]
                    dy = waypoints[j][1] - last_pos[1]
                    dist = math.sqrt(dx**2 + dy**2)
                    
                    if dist <= max_distance:
                        farthest_index = j
                        farthest_distance = dist
                        break
            
            # Add the selected waypoint
            selected_wp = waypoints[farthest_index]
            chunked.append(selected_wp)
            if DEBUG:
                print(f"  → Selected waypoint at distance: {farthest_distance:.1f} tiles")
            
            last_pos = selected_wp
            
            # Move to next segment (skip all intermediate waypoints)
            i = farthest_index + 1
        
        return chunked
    
    def is_moving(self) -> bool:
        """
        Check if player is currently moving via API.
        """
        animation = self.api.get_animation()
        if animation and animation.get("isMoving", False):
            return True
        return False
    
    def wait_until_stopped(self, timeout: float = 5.0) -> bool:
        """
        Wait until player stops moving using API animation check.
        
        Args:
            timeout: Maximum wait time in seconds (default: 5)
            
        Returns:
            True if player stopped moving, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.is_moving():
                # Confirm with second check to avoid animation lag
                time.sleep(random.uniform(*TIMING.GAME_TICK))
                if not self.is_moving():
                    return True
            time.sleep(random.uniform(*TIMING.API_POLL_INTERVAL))
        
        return False

    def wait_until_arrived(self, target_x: int, target_y: int, plane: int = 0, tolerance: int = 2, timeout: float = 15.0) -> bool:
        """
        Wait until player arrives at target coordinates.
        
        Strategy: Wait for movement to complete (player stops), then check if arrived.
        This is more logical since a single click will always result in stopping eventually.
        
        Args:
            target_x: Target world x coordinate
            target_y: Target world y coordinate
            plane: Target plane/height level (default: 0)
            tolerance: Distance tolerance in tiles (default: 2)
            timeout: Maximum wait time for movement to stop (default: 15s for ~12 tile click)
            
        Returns:
            True if arrived within tolerance and correct plane, False if stopped elsewhere or timeout
        """
        # Wait for player to stop moving from the minimap click
        # Max distance ~12 tiles at ~0.6s/tile = ~7-8s typical, 15s timeout is safe
        if not self.wait_until_stopped(timeout=timeout):
            if DEBUG:
                print(f"  ⚠ Player still moving after {timeout}s timeout (possible API/game issue)")
            return False
        
        # Movement complete - check if we arrived at destination
        coords = self.api.get_coords()
        if coords is None or "world" not in coords:
            if DEBUG:
                print("  ⚠ Could not read coordinates after movement stopped")
            return False
        
        world = coords["world"]
        current_x = world.get("x", 0)
        current_y = world.get("y", 0)
        current_plane = world.get("plane", 0)
        
        # Check plane first - must be exact match
        if current_plane != plane:
            if DEBUG:
                print(f"  ⚠ Stopped at wrong plane: {current_plane} (expected: {plane})")
            return False
        
        # Check x/y distance
        distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
        
        if distance <= tolerance:
            return True
        else:
            if DEBUG:
                print(f"  ⚠ Stopped at ({current_x}, {current_y}, plane {current_plane}) - distance from target: {distance:.1f} tiles")
            return False
    
    def is_player_moving(self) -> bool:
        """
        Check if player is currently moving by comparing coordinates over time.
        Uses API first, falls back to position polling if needed.
        
        Returns:
            True if player position changed in last 0.3-0.6 seconds
        """
        # Try API first (faster and more reliable)
        if self.is_moving():
            return True
        
        # Fallback: position polling (sometimes animation state lags)
        pos1 = self.read_world_coordinates()
        if pos1 is None:
            return False
        
        time.sleep(random.uniform(*TIMING.SMALL_DELAY))
        
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
    
    def get_animation_state(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed animation state from API.
        
        Returns:
            Dictionary with animationId, poseAnimation, isAnimating, isMoving
            or None if API call failed
        """
        return self.api.get_animation()
    
    def is_animating(self) -> bool:
        """
        Check if player is performing any animation (combat, skilling, emote, etc).
        Different from is_moving() which only checks movement.
        
        Returns:
            True if player is animating
        """
        animation = self.api.get_animation()
        if animation and animation.get("isAnimating", False):
            return True
        return False
    
    def get_pathfinding_stats(self) -> dict:
        """
        Get pathfinding system statistics for monitoring.
        
        Returns:
            Dictionary with collision map and path cache statistics
        """
        stats = {
            "pathfinding_enabled": self._pathfinding_enabled,
            "variance_level": self._pathfinding_config.get("variance_level", "N/A")
        }
        
        if _collision_map:
            stats["collision_map"] = _collision_map.get_cache_stats()
        
        if _pathfinder:
            stats["pathfinder"] = _pathfinder.get_cache_stats()
        
        return stats
    
    def clear_path_cache(self):
        """Clear pathfinding cache (useful for testing or forcing new paths)."""
        if _pathfinder:
            _pathfinder.clear_cache()
            if DEBUG:
                print("Path cache cleared")
    
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
        if DEBUG:
            print("Minimap scale calibration not yet implemented")
            print(f"Current scale: {self.minimap_scale} pixels/tile")
            print("To calibrate: walk a known distance and measure pixel displacement")
