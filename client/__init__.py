"""
OSRS Client Package
Contains all client-side game interaction modules.
"""

from .osrs import OSRS
from .runelite_api import RuneLiteAPI
from .inventory import InventoryManager
from .interfaces import InterfaceDetector
from .interactions import KeyboardController
from .color_registry import ColorRegistry
from .navigation import Navigator
from .pathfinder import Pathfinder

__all__ = [
    'OSRS',
    'RuneLiteAPI',
    'InventoryManager',
    'InterfaceDetector',
    'KeyboardController',
    'ColorRegistry',
    'Navigator',
    'Pathfinder',
]
