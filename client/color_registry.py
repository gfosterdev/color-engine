"""
Color Registry - Database of game object colors for RuneLite color markers.

This module maintains mappings between game objects and their unique RGB color markers
configured in RuneLite plugins (Object Markers, NPC Indicators, Ground Items, etc.).
"""

from typing import Dict, Tuple, Optional
from enum import Enum


# Type alias for RGB color tuples
RGB = Tuple[int, int, int]


class ObjectType(Enum):
    """Categories of game objects."""
    ORE = "ore"
    TREE = "tree"
    FISHING_SPOT = "fishing_spot"
    NPC = "npc"
    ITEM = "item"
    INTERACTIVE = "interactive"
    BANK = "bank"


class ColorRegistry:
    """
    Central registry for game object color mappings.
    
    Usage:
        registry = ColorRegistry()
        iron_color = registry.get_color("iron_ore")
        obj_name = registry.get_object_by_color((255, 100, 50))
    """
    
    def __init__(self):
        """Initialize the color registry with default mappings."""
        self._color_to_object: Dict[RGB, str] = {}
        self._object_to_color: Dict[str, RGB] = {}
        self._object_types: Dict[str, ObjectType] = {}
        
        # Load default color mappings
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default color mappings for common game objects."""
        
        # Banks
        self.register("bank_booth", (190, 25, 25), ObjectType.BANK)
        self.register("bank_chest", (200, 30, 30), ObjectType.BANK)
        
        # Mining - Ores
        self.register("copper_ore", (184, 115, 51), ObjectType.ORE)
        self.register("tin_ore", (128, 128, 128), ObjectType.ORE)
        self.register("iron_ore", (150, 75, 50), ObjectType.ORE)
        self.register("coal", (50, 50, 50), ObjectType.ORE)
        self.register("gold_ore", (255, 215, 0), ObjectType.ORE)
        self.register("mithril_ore", (100, 149, 237), ObjectType.ORE)
        self.register("adamantite_ore", (144, 238, 144), ObjectType.ORE)
        self.register("runite_ore", (0, 255, 255), ObjectType.ORE)
        
        # Woodcutting - Trees
        self.register("tree", (101, 67, 33), ObjectType.TREE)
        self.register("oak_tree", (139, 90, 43), ObjectType.TREE)
        self.register("willow_tree", (154, 205, 50), ObjectType.TREE)
        self.register("maple_tree", (210, 105, 30), ObjectType.TREE)
        self.register("yew_tree", (34, 139, 34), ObjectType.TREE)
        self.register("magic_tree", (138, 43, 226), ObjectType.TREE)
        
        # Fishing
        self.register("fishing_spot_net", (70, 130, 180), ObjectType.FISHING_SPOT)
        self.register("fishing_spot_bait", (65, 105, 225), ObjectType.FISHING_SPOT)
        self.register("fishing_spot_lure", (100, 149, 237), ObjectType.FISHING_SPOT)
        self.register("fishing_spot_cage", (30, 144, 255), ObjectType.FISHING_SPOT)
        self.register("fishing_spot_harpoon", (0, 191, 255), ObjectType.FISHING_SPOT)
        
        # Common NPCs (examples)
        self.register("chicken", (255, 228, 196), ObjectType.NPC)
        self.register("cow", (160, 82, 45), ObjectType.NPC)
        self.register("goblin", (34, 139, 34), ObjectType.NPC)
        
        # Interactive objects
        self.register("door", (165, 42, 42), ObjectType.INTERACTIVE)
        self.register("ladder_up", (218, 165, 32), ObjectType.INTERACTIVE)
        self.register("ladder_down", (184, 134, 11), ObjectType.INTERACTIVE)
        self.register("gate", (139, 69, 19), ObjectType.INTERACTIVE)
    
    def register(self, object_name: str, color: RGB, object_type: ObjectType):
        """
        Register a new object-color mapping.
        
        Args:
            object_name: Unique identifier for the game object (e.g., "iron_ore")
            color: RGB tuple representing the color marker
            object_type: Category of the object
        """
        object_name = object_name.lower()
        self._object_to_color[object_name] = color
        self._color_to_object[color] = object_name
        self._object_types[object_name] = object_type
    
    def get_color(self, object_name: str) -> Optional[RGB]:
        """
        Get the color for a registered object.
        
        Args:
            object_name: Name of the game object
            
        Returns:
            RGB tuple or None if not found
        """
        return self._object_to_color.get(object_name.lower())
    
    def get_object_by_color(self, color: RGB) -> Optional[str]:
        """
        Get the object name for a given color.
        
        Args:
            color: RGB tuple
            
        Returns:
            Object name or None if not found
        """
        return self._color_to_object.get(color)
    
    def get_object_type(self, object_name: str) -> Optional[ObjectType]:
        """
        Get the type category for a registered object.
        
        Args:
            object_name: Name of the game object
            
        Returns:
            ObjectType enum or None if not found
        """
        return self._object_types.get(object_name.lower())
    
    def get_all_by_type(self, object_type: ObjectType) -> Dict[str, RGB]:
        """
        Get all objects of a specific type.
        
        Args:
            object_type: Category to filter by
            
        Returns:
            Dictionary mapping object names to colors
        """
        return {
            name: color
            for name, color in self._object_to_color.items()
            if self._object_types.get(name) == object_type
        }
    
    def remove(self, object_name: str) -> bool:
        """
        Remove an object from the registry.
        
        Args:
            object_name: Name of the object to remove
            
        Returns:
            True if removed, False if not found
        """
        object_name = object_name.lower()
        if object_name in self._object_to_color:
            color = self._object_to_color[object_name]
            del self._object_to_color[object_name]
            del self._color_to_object[color]
            del self._object_types[object_name]
            return True
        return False
    
    def list_all(self) -> Dict[str, Tuple[RGB, ObjectType]]:
        """
        Get all registered objects with their colors and types.
        
        Returns:
            Dictionary mapping object names to (color, type) tuples
        """
        return {
            name: (color, self._object_types[name])
            for name, color in self._object_to_color.items()
        }


# Global registry instance
_registry = ColorRegistry()


def get_registry() -> ColorRegistry:
    """Get the global ColorRegistry instance."""
    return _registry


# Convenience functions for common operations
def get_color(object_name: str) -> Optional[RGB]:
    """Get color for an object from the global registry."""
    return _registry.get_color(object_name)


def register_color(object_name: str, color: RGB, object_type: ObjectType):
    """Register a color in the global registry."""
    _registry.register(object_name, color, object_type)
