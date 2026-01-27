"""
OSRS Client Package
Contains all client-side game interaction modules.
"""

from .osrs import OSRS
from .runelite_api import RuneLiteAPI
from .inventory import InventoryManager
from .interfaces import InterfaceDetector
from .interactions import KeyboardInput
from .color_registry import ColorRegistry
from .navigation import NavigationManager
from .pathfinder import VariancePathfinder

__all__ = [
    'OSRS',
    'RuneLiteAPI',
    'InventoryManager',
    'InterfaceDetector',
    'KeyboardInput',
    'ColorRegistry',
    'NavigationManager',
    'VariancePathfinder',
]
