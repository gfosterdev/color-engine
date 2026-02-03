"""
Collision detection utilities for OSRS pathfinding.

This module provides collision map data parsing and querying capabilities using
the pre-built collision-map.zip file from the RuneLite shortest-path plugin.

The collision map uses a bit-packed format where each tile has 2 flags:
- Flag 0: Can walk North/South (0 = blocked, 1 = open)
- Flag 1: Can walk East/West (0 = blocked, 1 = open)

Regions are lazy-loaded from the ZIP file with LRU caching to minimize memory usage.
"""

import os
import zipfile
import struct
from collections import OrderedDict
from pathlib import Path
from typing import Tuple, Optional
from core.config import DEBUG


class CollisionMap:
    """
    Lazy-loading collision map with LRU caching for memory efficiency.
    
    Attributes:
        zip_path: Path to collision-map.zip file
        region_cache: LRU cache of recently accessed regions (max 50 regions ~10MB RAM)
        max_cache_size: Maximum number of regions to keep in memory
    """
    
    # Region dimensions (each region is 64x64 tiles)
    REGION_SIZE = 64
    
    # Number of planes (z-levels: 0, 1, 2, 3)
    PLANE_COUNT = 4
    
    # Flag indices for directional movement
    FLAG_NORTH = 0
    FLAG_SOUTH = 0  # Same as North (checked on adjacent tile)
    FLAG_EAST = 1
    FLAG_WEST = 1   # Same as East (checked on adjacent tile)
    
    _instance = None
    _initialized = False
    
    def __new__(cls, zip_path: Optional[str] = None, max_cache_size: int = 50):
        """Singleton pattern to ensure only one collision map instance."""
        if cls._instance is None:
            cls._instance = super(CollisionMap, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, zip_path: Optional[str] = None, max_cache_size: int = 50):
        """
        Initialize collision map with lazy loading.
        
        Args:
            zip_path: Path to collision-map.zip (default: util/data/collision-map.zip)
            max_cache_size: Maximum number of regions to cache (default: 50)
        """
        # Only initialize once (singleton pattern)
        if self._initialized:
            return
        
        if zip_path is None:
            # Default path relative to this file
            util_dir = Path(__file__).parent
            zip_path = str(util_dir / "data" / "collision-map.zip")
        
        self.zip_path = Path(zip_path)
        self.max_cache_size = max_cache_size
        
        # LRU cache: OrderedDict maintains insertion order
        # Most recent accesses are moved to end
        self.region_cache: OrderedDict[Tuple[int, int, int], bytes] = OrderedDict()
        
        # Verify collision map file exists
        if not self.zip_path.exists():
            raise FileNotFoundError(
                f"Collision map not found at {self.zip_path}\n"
                f"Please run: python scripts/download_collision_data.py"
            )
        
        self._initialized = True
        if DEBUG:
            print(f"CollisionMap initialized: {self.zip_path}")
    
    def _load_region(self, region_x: int, region_y: int, plane: int) -> Optional[bytes]:
        """
        Load a region from the ZIP file.
        
        Args:
            region_x: Region X coordinate
            region_y: Region Y coordinate
            plane: Plane (z-level) 0-3
            
        Returns:
            Raw byte data for the region, or None if not found
        """
        try:
            # Region filename format in ZIP: "x_y" (plane data is within the file)
            filename = f"{region_x}_{region_y}"
            
            with zipfile.ZipFile(self.zip_path, 'r') as zf:
                # Check if file exists in ZIP
                if filename not in zf.namelist():
                    return None
                
                # Read compressed data
                data = zf.read(filename)
                return data
                
        except Exception as e:
            if DEBUG:
                print(f"Error loading region ({region_x}, {region_y}, {plane}): {e}")
            return None
    
    def _get_region_data(self, region_x: int, region_y: int, plane: int) -> Optional[bytes]:
        """
        Get region data with LRU caching.
        
        Args:
            region_x: Region X coordinate
            region_y: Region Y coordinate
            plane: Plane (z-level) 0-3
            
        Returns:
            Raw byte data for the region, or None if not found
        """
        cache_key = (region_x, region_y, plane)
        
        # Check cache
        if cache_key in self.region_cache:
            # Move to end (most recently used)
            self.region_cache.move_to_end(cache_key)
            return self.region_cache[cache_key]
        
        # Load from ZIP
        data = self._load_region(region_x, region_y, plane)
        
        if data is not None:
            # Add to cache
            self.region_cache[cache_key] = data
            
            # Evict least recently used if cache is full
            if len(self.region_cache) > self.max_cache_size:
                self.region_cache.popitem(last=False)  # Remove oldest (first item)
        
        return data
    
    def _get_tile_flag(self, x: int, y: int, z: int, flag: int) -> bool:
        """
        Get walkability flag for a specific tile and direction.
        
        Args:
            x: World X coordinate
            y: World Y coordinate
            z: Plane (z-level) 0-3
            flag: Direction flag (0=North/South, 1=East/West)
            
        Returns:
            True if walkable in that direction, False if blocked
        """
        # Calculate region coordinates
        region_x = x // self.REGION_SIZE
        region_y = y // self.REGION_SIZE
        
        # Calculate tile coordinates within region
        tile_x = x % self.REGION_SIZE
        tile_y = y % self.REGION_SIZE
        
        # Get region data
        data = self._get_region_data(region_x, region_y, z)
        
        if data is None:
            # Region not found - assume blocked for safety
            return False
        
        # Calculate bit index
        # Each region has 64x64 tiles, each tile has 2 flags (bits)
        tile_index = tile_y * self.REGION_SIZE + tile_x
        bit_index = tile_index * 2 + flag
        
        # Get byte and bit within byte
        byte_index = bit_index // 8
        bit_in_byte = bit_index % 8
        
        if byte_index >= len(data):
            return False
        
        # Extract bit value
        byte_val = data[byte_index]
        return bool((byte_val >> bit_in_byte) & 1)
    
    # Public API for checking movement directions
    
    def can_move_north(self, x: int, y: int, z: int) -> bool:
        """Check if can move north from tile."""
        return self._get_tile_flag(x, y, z, self.FLAG_NORTH)
    
    def can_move_south(self, x: int, y: int, z: int) -> bool:
        """Check if can move south from tile (check tile to the south)."""
        return self._get_tile_flag(x, y - 1, z, self.FLAG_NORTH)
    
    def can_move_east(self, x: int, y: int, z: int) -> bool:
        """Check if can move east from tile."""
        return self._get_tile_flag(x, y, z, self.FLAG_EAST)
    
    def can_move_west(self, x: int, y: int, z: int) -> bool:
        """Check if can move west from tile (check tile to the west)."""
        return self._get_tile_flag(x - 1, y, z, self.FLAG_EAST)
    
    def can_move_northeast(self, x: int, y: int, z: int) -> bool:
        """Check if can move northeast (both north and east must be clear)."""
        return (self.can_move_north(x, y, z) and 
                self.can_move_east(x, y + 1, z) and
                self.can_move_east(x, y, z) and
                self.can_move_north(x + 1, y, z))
    
    def can_move_northwest(self, x: int, y: int, z: int) -> bool:
        """Check if can move northwest (both north and west must be clear)."""
        return (self.can_move_north(x, y, z) and 
                self.can_move_west(x, y + 1, z) and
                self.can_move_west(x, y, z) and
                self.can_move_north(x - 1, y, z))
    
    def can_move_southeast(self, x: int, y: int, z: int) -> bool:
        """Check if can move southeast (both south and east must be clear)."""
        return (self.can_move_south(x, y, z) and 
                self.can_move_east(x, y - 1, z) and
                self.can_move_east(x, y, z) and
                self.can_move_south(x + 1, y, z))
    
    def can_move_southwest(self, x: int, y: int, z: int) -> bool:
        """Check if can move southwest (both south and west must be clear)."""
        return (self.can_move_south(x, y, z) and 
                self.can_move_west(x, y - 1, z) and
                self.can_move_west(x, y, z) and
                self.can_move_south(x - 1, y, z))
    
    def is_tile_blocked(self, x: int, y: int, z: int) -> bool:
        """
        Check if tile is completely blocked (no movement in any direction).
        
        Args:
            x: World X coordinate
            y: World Y coordinate
            z: Plane (z-level) 0-3
            
        Returns:
            True if tile is blocked in all directions
        """
        return not (self.can_move_north(x, y, z) or 
                   self.can_move_south(x, y, z) or
                   self.can_move_east(x, y, z) or
                   self.can_move_west(x, y, z))
    
    def get_walkable_neighbors(self, x: int, y: int, z: int) -> list[Tuple[int, int, int]]:
        """
        Get all walkable neighbor tiles (8 directions).
        
        Args:
            x: World X coordinate
            y: World Y coordinate
            z: Plane (z-level) 0-3
            
        Returns:
            List of (x, y, z) tuples for walkable neighbors
        """
        neighbors = []
        
        # Check all 8 directions
        if self.can_move_north(x, y, z):
            neighbors.append((x, y + 1, z))
        if self.can_move_south(x, y, z):
            neighbors.append((x, y - 1, z))
        if self.can_move_east(x, y, z):
            neighbors.append((x + 1, y, z))
        if self.can_move_west(x, y, z):
            neighbors.append((x - 1, y, z))
        if self.can_move_northeast(x, y, z):
            neighbors.append((x + 1, y + 1, z))
        if self.can_move_northwest(x, y, z):
            neighbors.append((x - 1, y + 1, z))
        if self.can_move_southeast(x, y, z):
            neighbors.append((x + 1, y - 1, z))
        if self.can_move_southwest(x, y, z):
            neighbors.append((x - 1, y - 1, z))
        
        return neighbors
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics for debugging/monitoring."""
        return {
            "cached_regions": len(self.region_cache),
            "max_cache_size": self.max_cache_size,
            "cache_utilization": len(self.region_cache) / self.max_cache_size * 100
        }
    
    def clear_cache(self):
        """Clear the region cache (useful for testing or memory management)."""
        self.region_cache.clear()
