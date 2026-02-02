"""
Resource management system for gathering skills.
Handles resource node finding, prioritization, and depletion tracking.
"""

from typing import Optional, Dict, List
import time
import math


class ResourceManager:
    """
    Manages resource nodes for gathering skills (mining, woodcutting, fishing, etc.).
    
    Features:
    - World-coordinate-based distance sorting
    - Depletion memory tracking
    - Respawn time estimation
    - Multi-node support with automatic fallback
    """
    
    def __init__(self, osrs, resource_object_ids: list[int], respawn_time: tuple[float, float] = (5, 10)):
        """
        Initialize resource manager.
        
        Args:
            osrs: OSRS instance for API access
            resource_object_ids: List of game object IDs to track
            respawn_time: Tuple of (min, max) respawn time in seconds
        """
        self.osrs = osrs
        self.api = osrs.api
        self.resource_object_ids = resource_object_ids
        self.respawn_time = respawn_time
        
        # Depletion tracking: {(x, y): timestamp}
        self.depleted_nodes: Dict[tuple[int, int], float] = {}
        
        # Cleanup interval for depleted nodes
        self.last_cleanup = time.time()
        self.cleanup_interval = 30  # seconds
    
    def find_nearest_node(self, exclude_depleted: bool = True, rotate_360: bool = True) -> Optional[Dict]:
        """
        Find the nearest resource node based on world coordinates.
        Automatically rotates camera 360° to search if not found in current view.
        
        Args:
            exclude_depleted: If True, exclude recently depleted nodes
            rotate_360: If True, rotates camera 360° to search for resources
        
        Returns:
            Game object dict with distance info, or None if no nodes found
        """
        # Cleanup old depleted nodes periodically
        self._cleanup_depleted_nodes()
        
        # Get player position
        coords = self.api.get_coords()
        if not coords or 'world' not in coords:
            print("✗ Failed to get player coordinates")
            return None
        
        player_pos = coords['world']
        player_x, player_y = player_pos['x'], player_pos['y']
        
        # Use find_in_viewport to search (with optional camera rotation)
        resource_nodes = self.osrs.find_in_viewport(
            entity_ids=self.resource_object_ids,
            entity_type="object",
            rotate_360=rotate_360
        )
        
        if not resource_nodes:
            print("✗ No resource nodes found in viewport")
            return None
        
        # Filter out depleted nodes if requested
        if exclude_depleted:
            resource_nodes = [
                node for node in resource_nodes
                if (node['x'], node['y']) not in self.depleted_nodes
            ]
        
        if not resource_nodes:
            print("✗ All visible nodes are depleted")
            return None
        
        # Calculate distances and find nearest
        for node in resource_nodes:
            node_x, node_y = node['x'], node['y']
            distance = math.sqrt((node_x - player_x)**2 + (node_y - player_y)**2)
            node['distance'] = distance
        
        # Sort by distance
        resource_nodes.sort(key=lambda n: n['distance'])
        nearest = resource_nodes[0]
        
        print(f"Found {len(resource_nodes)} nodes, nearest at distance {nearest['distance']:.1f}")
        return nearest
    
    def mark_node_depleted(self, x: int, y: int):
        """
        Mark a node as depleted at specific world coordinates.
        
        Args:
            x: World X coordinate
            y: World Y coordinate
        """
        self.depleted_nodes[(x, y)] = time.time()
        print(f"Marked node at ({x}, {y}) as depleted")
    
    def is_node_depleted(self, x: int, y: int) -> bool:
        """
        Check if a node at given coordinates is marked as depleted.
        
        Args:
            x: World X coordinate
            y: World Y coordinate
        
        Returns:
            True if node is in depleted list, False otherwise
        """
        return (x, y) in self.depleted_nodes
    
    def clear_depleted_node(self, x: int, y: int):
        """
        Remove a node from depleted list (when it respawns).
        
        Args:
            x: World X coordinate
            y: World Y coordinate
        """
        if (x, y) in self.depleted_nodes:
            del self.depleted_nodes[(x, y)]
            print(f"Cleared depletion marker for node at ({x}, {y})")
    
    def get_depleted_count(self) -> int:
        """Get number of currently tracked depleted nodes."""
        return len(self.depleted_nodes)
    
    def _cleanup_depleted_nodes(self):
        """Remove depleted nodes that have likely respawned."""
        current_time = time.time()
        
        # Only cleanup periodically
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        max_respawn = self.respawn_time[1]
        nodes_to_remove = [
            pos for pos, timestamp in self.depleted_nodes.items()
            if current_time - timestamp > max_respawn
        ]
        
        for pos in nodes_to_remove:
            del self.depleted_nodes[pos]
        
        if nodes_to_remove:
            print(f"Cleaned up {len(nodes_to_remove)} old depleted nodes")
        
        self.last_cleanup = current_time
    
    def get_all_visible_nodes(self) -> List[Dict]:
        """
        Get all visible resource nodes sorted by distance.
        
        Returns:
            List of game object dicts with distance info
        """
        coords = self.api.get_coords()
        if not coords or 'world' not in coords:
            return []
        
        player_pos = coords['world']
        player_x, player_y = player_pos['x'], player_pos['y']
        
        all_objects = self.api.get_game_objects_in_viewport()
        resource_nodes = [
            obj for obj in all_objects 
            if obj.get('id') in self.resource_object_ids
        ]
        
        # Calculate distances
        for node in resource_nodes:
            node_x, node_y = node['x'], node['y']
            distance = math.sqrt((node_x - player_x)**2 + (node_y - player_y)**2)
            node['distance'] = distance
            node['is_depleted'] = (node_x, node_y) in self.depleted_nodes
        
        # Sort by distance
        resource_nodes.sort(key=lambda n: n['distance'])
        
        return resource_nodes
