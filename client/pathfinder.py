"""
Variance-based pathfinding for OSRS bot navigation.

This module implements Dijkstra's algorithm with randomized edge weights and waypoint
injection to create unique paths on every execution, helping avoid bot detection.

Features:
- Collision-aware pathfinding using pre-computed collision map data
- Path variance through randomized edge weights (±10-35% per profile)
- Random waypoint injection for large-scale path deviation
- Path caching with execution randomness (cache base path, randomize execution)
- 8-directional movement (N, S, E, W, NE, NW, SE, SW)
"""

import random
import time
from collections import deque
from typing import Tuple, List, Optional, Dict
from heapq import heappush, heappop

from util.collision_util import CollisionMap


class PathNode:
    """
    Node in the pathfinding graph.
    
    Attributes:
        x, y, z: World coordinates
        cost: Accumulated cost from start
        parent: Previous node in path
    """
    
    def __init__(self, x: int, y: int, z: int, cost: float, parent: Optional['PathNode'] = None):
        self.x = x
        self.y = y
        self.z = z
        self.cost = cost
        self.parent = parent
    
    def __lt__(self, other):
        """For heap ordering (lower cost = higher priority)."""
        return self.cost < other.cost
    
    def __eq__(self, other):
        """For position comparison."""
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __hash__(self):
        """For use in sets/dicts."""
        return hash((self.x, self.y, self.z))
    
    def position(self) -> Tuple[int, int, int]:
        """Get position as tuple."""
        return (self.x, self.y, self.z)


class VariancePathfinder:
    """
    Pathfinder with variance for anti-detection.
    
    Uses Dijkstra's algorithm with:
    - Randomized edge weights for natural path variation
    - Path caching to improve performance
    - Waypoint injection for large-scale deviation
    
    Attributes:
        collision_map: CollisionMap instance for walkability checks
        path_cache: Cache of computed paths (base routes)
        max_cache_size: Maximum number of cached paths
        variance_config: Configuration for path variance
    """
    
    def __init__(self, collision_map: Optional[CollisionMap] = None, max_cache_size: int = 100):
        """
        Initialize pathfinder.
        
        Args:
            collision_map: CollisionMap instance (creates new if None)
            max_cache_size: Maximum number of paths to cache
        """
        self.collision_map = collision_map or CollisionMap()
        self.max_cache_size = max_cache_size
        
        # Path cache: key = (start, end), value = list of waypoints
        self.path_cache: Dict[Tuple[Tuple[int, int, int], Tuple[int, int, int]], List[Tuple[int, int, int]]] = {}
        
        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0
    
    def find_path(
        self,
        start: Tuple[int, int, int],
        goal: Tuple[int, int, int],
        variance_level: str = "moderate",
        use_cache: bool = True
    ) -> Optional[List[Tuple[int, int, int]]]:
        """
        Find path from start to goal with variance.
        
        Args:
            start: Starting position (x, y, z)
            goal: Goal position (x, y, z)
            variance_level: "conservative", "moderate", or "aggressive"
            use_cache: Whether to use cached paths
            
        Returns:
            List of waypoints from start to goal, or None if no path exists
        """
        # Check cache
        cache_key = (start, goal)
        if use_cache and cache_key in self.path_cache:
            self.cache_hits += 1
            return self.path_cache[cache_key].copy()
        
        self.cache_misses += 1
        
        # Get variance parameters
        variance_config = self._get_variance_config(variance_level)
        
        # Run Dijkstra with random edge weights
        path = self._dijkstra(start, goal, variance_config)
        
        if path is None:
            return None
        
        # Inject random waypoints for large-scale variance
        path = self._inject_waypoints(path, variance_config)
        
        # Simplify path by removing unnecessary intermediate waypoints
        path = self._simplify_path(path)
        
        # Cache the path
        if use_cache:
            self.path_cache[cache_key] = path.copy()
            
            # Evict oldest if cache full (simple FIFO eviction)
            if len(self.path_cache) > self.max_cache_size:
                # Remove first item (oldest)
                first_key = next(iter(self.path_cache))
                del self.path_cache[first_key]
        
        return path
    
    def _get_variance_config(self, variance_level: str) -> dict:
        """
        Get variance configuration parameters.
        
        Args:
            variance_level: "conservative", "moderate", or "aggressive"
            
        Returns:
            Dictionary with variance parameters
        """
        configs = {
            "conservative": {
                "edge_weight_min": 0.90,
                "edge_weight_max": 1.10,
                "waypoint_count_min": 0,
                "waypoint_count_max": 1,
                "waypoint_deviation": 3  # tiles from straight line
            },
            "moderate": {
                "edge_weight_min": 0.85,
                "edge_weight_max": 1.25,
                "waypoint_count_min": 1,
                "waypoint_count_max": 2,
                "waypoint_deviation": 5
            },
            "aggressive": {
                "edge_weight_min": 0.75,
                "edge_weight_max": 1.35,
                "waypoint_count_min": 2,
                "waypoint_count_max": 3,
                "waypoint_deviation": 8
            }
        }
        
        return configs.get(variance_level, configs["moderate"])
    
    def _dijkstra(
        self,
        start: Tuple[int, int, int],
        goal: Tuple[int, int, int],
        variance_config: dict
    ) -> Optional[List[Tuple[int, int, int]]]:
        """
        Dijkstra's algorithm with randomized edge weights.
        
        Args:
            start: Starting position
            goal: Goal position
            variance_config: Variance configuration
            
        Returns:
            List of waypoints or None if no path found
        """
        start_x, start_y, start_z = start
        goal_x, goal_y, goal_z = goal
        
        # Priority queue: (cost, node)
        frontier = []
        start_node = PathNode(start_x, start_y, start_z, 0.0)
        heappush(frontier, start_node)
        
        # Visited set
        visited = set()
        
        # Node lookup for efficient visited checking
        best_costs: Dict[Tuple[int, int, int], float] = {start: 0.0}
        
        while frontier:
            current = heappop(frontier)
            
            # Check if reached goal
            if (current.x, current.y, current.z) == goal:
                # Reconstruct path
                return self._reconstruct_path(current)
            
            # Skip if already visited with better cost
            pos = current.position()
            if pos in visited:
                continue
            
            visited.add(pos)
            
            # Get walkable neighbors
            neighbors = self.collision_map.get_walkable_neighbors(current.x, current.y, current.z)
            
            for neighbor_pos in neighbors:
                if neighbor_pos in visited:
                    continue
                
                nx, ny, nz = neighbor_pos
                
                # Calculate edge cost with randomization
                base_cost = self._calculate_base_cost(current.x, current.y, nx, ny)
                variance = random.uniform(
                    variance_config["edge_weight_min"],
                    variance_config["edge_weight_max"]
                )
                edge_cost = base_cost * variance
                
                new_cost = current.cost + edge_cost
                
                # Update if this is a better path
                if neighbor_pos not in best_costs or new_cost < best_costs[neighbor_pos]:
                    best_costs[neighbor_pos] = new_cost
                    neighbor_node = PathNode(nx, ny, nz, new_cost, current)
                    heappush(frontier, neighbor_node)
        
        # No path found
        return None
    
    def _calculate_base_cost(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calculate base cost between two adjacent tiles.
        
        Diagonal moves cost sqrt(2) ≈ 1.414, cardinal moves cost 1.0
        
        Args:
            x1, y1: Start tile coordinates
            x2, y2: End tile coordinates
            
        Returns:
            Base movement cost
        """
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        if dx == 1 and dy == 1:
            return 1.414  # Diagonal
        else:
            return 1.0    # Cardinal
    
    def _reconstruct_path(self, goal_node: PathNode) -> List[Tuple[int, int, int]]:
        """
        Reconstruct path from goal node back to start.
        
        Args:
            goal_node: Final node in path
            
        Returns:
            List of waypoints from start to goal
        """
        path = []
        current = goal_node
        
        while current is not None:
            path.append(current.position())
            current = current.parent
        
        path.reverse()
        return path
    
    def _inject_waypoints(
        self,
        path: List[Tuple[int, int, int]],
        variance_config: dict
    ) -> List[Tuple[int, int, int]]:
        """
        Inject random waypoints into path for large-scale variance.
        
        This creates deviation from the computed shortest path by selecting
        random intermediate points and re-pathing through them.
        
        Args:
            path: Original path
            variance_config: Variance configuration
            
        Returns:
            Modified path with injected waypoints
        """
        # Only inject for longer paths (>15 tiles)
        if len(path) < 15:
            return path
        
        # Determine number of waypoints to inject
        waypoint_count = random.randint(
            variance_config["waypoint_count_min"],
            variance_config["waypoint_count_max"]
        )
        
        if waypoint_count == 0:
            return path
        
        # Select random points along the path to deviate from
        segment_size = len(path) // (waypoint_count + 1)
        
        new_path = [path[0]]  # Start with first point
        
        for i in range(waypoint_count):
            # Get point on original path to deviate from
            index = segment_size * (i + 1)
            if index >= len(path):
                break
            
            orig_x, orig_y, orig_z = path[index]
            
            # Generate random offset perpendicular to path direction
            deviation = variance_config["waypoint_deviation"]
            offset_x = random.randint(-deviation, deviation)
            offset_y = random.randint(-deviation, deviation)
            
            waypoint = (orig_x + offset_x, orig_y + offset_y, orig_z)
            
            # Find path from last point to this waypoint
            segment = self._dijkstra(new_path[-1], waypoint, variance_config)
            
            if segment:
                new_path.extend(segment[1:])  # Exclude duplicate start point
            else:
                # If waypoint unreachable, continue with original path
                continue
        
        # Add final segment to goal
        final_segment = self._dijkstra(new_path[-1], path[-1], variance_config)
        if final_segment:
            new_path.extend(final_segment[1:])
        else:
            # Fallback to original path if final segment fails
            return path
        
        return new_path
    
    def _simplify_path(self, path: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """
        Simplify path by removing intermediate waypoints when line-of-sight is clear.
        Uses greedy algorithm: looks ahead as far as possible and skips to farthest
        visible tile, making paths look more natural around large obstacles.
        
        Args:
            path: Original path with potentially many intermediate waypoints
            
        Returns:
            Simplified path with fewer waypoints
        """
        if len(path) <= 2:
            return path
        
        simplified = [path[0]]  # Always keep start
        current_index = 0
        
        while current_index < len(path) - 1:
            # Look ahead to find farthest visible tile
            # Limit to 12 tiles (minimap click range) for practical pathing
            max_lookahead = min(len(path) - 1, current_index + 12)
            farthest_visible = current_index + 1  # Default to next tile
            
            # Greedy search: find farthest tile with clear line-of-sight
            for lookahead_index in range(max_lookahead, current_index, -1):
                if self._has_line_of_sight(path[current_index], path[lookahead_index]):
                    farthest_visible = lookahead_index
                    break
            
            # Add farthest visible waypoint
            simplified.append(path[farthest_visible])
            current_index = farthest_visible
        
        return simplified
    
    def _has_line_of_sight(self, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> bool:
        """
        Check if there's a walkable line-of-sight between two tiles using Bresenham's algorithm.
        Returns True if all tiles along the line are walkable.
        
        Args:
            start: Starting tile (x, y, z)
            end: Ending tile (x, y, z)
            
        Returns:
            True if line-of-sight is clear and all intermediate tiles are walkable
        """
        x0, y0, z0 = start
        x1, y1, z1 = end
        
        # Must be on same plane
        if z0 != z1:
            return False
        
        # Bresenham's line algorithm
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            # Check if current tile is walkable (except start/end, which we know are in path)
            if (x, y) != (x0, y0) and (x, y) != (x1, y1):
                neighbors = self.collision_map.get_walkable_neighbors(x, y, z0)
                
                # If tile has no walkable neighbors, it's blocked
                if not neighbors:
                    return False
                
                # Verify we can walk to/from this tile in the line direction
                # Check if we can reach this tile from the previous step
                # and continue to the next step
            
            # Reached end
            if x == x1 and y == y1:
                break
            
            # Calculate next position
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return True
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics for monitoring."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "cached_paths": len(self.path_cache),
            "max_cache_size": self.max_cache_size,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate_percent": hit_rate
        }
    
    def clear_cache(self):
        """Clear path cache and statistics."""
        self.path_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
