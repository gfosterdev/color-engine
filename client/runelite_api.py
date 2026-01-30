"""
RuneLite HTTP Server Plugin API Wrapper
Provides complete interface to all RuneLite HTTP endpoints.

The RuneLite HTTP Server plugin exposes game data via REST API endpoints.
This wrapper provides typed access to all available endpoints with automatic
request timing and error handling.

Usage:
    from client.runelite_api import RuneLiteAPI
    
    api = RuneLiteAPI()
    player = api.get_player()
    stats = api.get_stats()
    coords = api.get_coords()

Endpoints:
    - Player Data: stats, player, coords, combat, animation
    - Inventory: inv, equip, bank
    - World Data: npcs, players, objects, grounditems
    - Game State: camera, game, menu, widgets
"""

import requests
import time
from util.window_util import Region
from typing import Any, Dict, List, Optional, Union, cast


class RuneLiteAPI:
    """Complete API wrapper for all RuneLite HTTP Server endpoints."""
    
    def __init__(self, host='localhost', port=8080):
        """
        Initialize RuneLite API connection.
        
        Args:
            host: RuneLite HTTP server host (default: localhost)
            port: RuneLite HTTP server port (default: 8080)
        """
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.last_request_time = {}
        
    def _get(self, endpoint: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
        """
        Make GET request to API endpoint with timing tracking.
        
        Args:
            endpoint: API endpoint path (without leading slash)
            
        Returns:
            JSON response data or None on error
        """
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", timeout=2)
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            self.last_request_time[endpoint] = elapsed
            
            response.raise_for_status()
            
            if not response.text or response.text.strip() == '':
                return None
            
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"❌ JSON Error on /{endpoint}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error on /{endpoint}: {e}")
            return None
    
    # Player Data Endpoints
    def get_stats(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all skill stats with XP calculations.
        
        Returns:
            List of skill dictionaries with stat, level, boostedLevel, xp, xpToNextLevel
        """
        result = self._get("stats")
        return cast(Optional[List[Dict[str, Any]]], result)
    
    def get_player(self) -> Optional[Dict[str, Any]]:
        """
        Get player state (health, prayer, energy, etc).
        
        Returns:
            Dictionary with name, combatLevel, health, maxHealth, prayer, maxPrayer,
            runEnergy, specialAttack, weight, isAnimating, interactingWith
        """
        result = self._get("player")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_coords(self) -> Optional[Dict[str, Any]]:
        """
        Get world and local coordinates.
        
        Returns:
            Dictionary with world (x, y, plane, regionID, regionX, regionY) and
            local (sceneX, sceneY) coordinates
        """
        result = self._get("coords")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_combat(self) -> Optional[Dict[str, Any]]:
        """
        Get combat state and target info.
        
        Returns:
            Dictionary with inCombat, autoRetaliate, and target information
        """
        result = self._get("combat")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_animation(self) -> Optional[Dict[str, Any]]:
        """
        Get current animation state.
        
        Returns:
            Dictionary with animationId, poseAnimation, isAnimating, isMoving
        """
        result = self._get("animation")
        return cast(Optional[Dict[str, Any]], result)
    
    # Inventory & Equipment
    def get_inventory(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get inventory items.
        
        Returns:
            List of item dictionaries with id, quantity, slot
        """
        result = self._get("inv")
        return cast(Optional[List[Dict[str, Any]]], result)
    
    def get_equipment(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get equipped items.
        
        Returns:
            List of equipped item dictionaries with id, quantity, slot
        """
        result = self._get("equip")
        return cast(Optional[List[Dict[str, Any]]], result)
    
    def get_bank(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get bank items (only when bank is open).
        
        Returns:
            List of bank item dictionaries with id, quantity, slot
        """
        result = self._get("bank")
        return cast(Optional[List[Dict[str, Any]]], result)
    
    # World Data
    def get_npcs(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all NPCs in scene.
        
        Returns:
            List of NPC dictionaries with name, id, combatLevel, distanceFromPlayer,
            worldX, worldY, plane
        """
        result = self._get("npcs")
        return cast(Optional[List[Dict[str, Any]]], result)
    
    def get_players(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all other players in scene.
        
        Returns:
            List of player dictionaries with name, combatLevel, worldX, worldY, plane
        """
        result = self._get("players")
        return cast(Optional[List[Dict[str, Any]]], result)
    
    def get_objects(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all game objects in scene.
        
        Returns:
            List of object dictionaries with id, name, worldX, worldY, plane
        """
        result = self._get("objects")
        return cast(Optional[List[Dict[str, Any]]], result)
    
    def get_ground_items(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all ground items in scene.
        
        Returns:
            List of ground item dictionaries with id, quantity, worldX, worldY, plane
        """
        result = self._get("grounditems")
        return cast(Optional[List[Dict[str, Any]]], result)
    
    # Game State
    def get_camera(self) -> Optional[Dict[str, Any]]:
        """
        Get camera position and rotation.
        
        Returns:
            Dictionary with yaw, pitch, x, y, z
        """
        result = self._get("camera")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_game_state(self) -> Optional[Dict[str, Any]]:
        """
        Get game state info.
        
        Returns:
            Dictionary with state, isLoggedIn, world, gameCycle, tickCount, fps
        """
        result = self._get("game")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_menu(self) -> Optional[Dict[str, Any]]:
        """
        Get current menu state.
        
        Returns:
            Dictionary with isOpen, size, x, y, width, height, entries
        """
        result = self._get("menu")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_menu_region(self) -> Optional[Region]:
        """
        Get right click menu Region.

        Returns:
            Region object with x, y, width, height
        """
        menu_data = self.get_menu()
        if menu_data and menu_data.get('isOpen'):
            x = menu_data.get('x', 0)
            y = menu_data.get('y', 0)
            width = menu_data.get('width', 0)
            height = menu_data.get('height', 0)
            return Region(x, y, width, height)
        return None

    def get_widgets(self) -> Optional[Dict[str, Any]]:
        """
        Get interface/widget states.
        
        Returns:
            Dictionary with isBankOpen, isShopOpen, isDialogueOpen, isInventoryOpen,
        """
        result = self._get("widgets")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get request performance metrics.
        
        Returns:
            Dictionary mapping endpoint names to request times in milliseconds
        """
        return self.last_request_time.copy()

    def get_npcs_in_viewport(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all NPCs currently visible in the viewport.
        
        Returns:
            List of NPC dictionaries with name, id, combatLevel, distanceFromPlayer,
            worldX, worldY, plane
        """
        result = self._get("npcs_in_viewport")
        return cast(Optional[List[Dict[str, Any]]], result)

    def get_npc_in_viewport(self, npc_id) -> Optional[Dict[str, Any]]:
        """
        Get npc in viewport if it exists

        Returns:
            Dictionary with name, id, x, y, hull
        """
        result = self._get("npcs_in_viewport")
        result = cast(Optional[List[Dict[str, Any]]], result)
        if result and len(result) > 0:
            filtered = [npc for npc in result if npc.get('id') == npc_id]
            if len(filtered) > 0:
                import random
                return random.choice(filtered)
        return None

    def get_game_objects_in_viewport(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all game objects currently visible in the viewport.
        
        Returns:
            List of object dictionaries with id, name, worldX, worldY, plane
        """
        result = self._get("objects_in_viewport")
        return cast(Optional[List[Dict[str, Any]]], result)

    def get_game_object_in_viewport(self, obj_id) -> Optional[Dict[str, Any]]:
        """
        Get game object if it exists in the viewport.
        If more than one exists, returns a random one.
        
        Returns:
            Dictionary with id, name, x, y or None if not found
        """
        result = self._get("objects_in_viewport")
        result = cast(Optional[List[Dict[str, Any]]], result)
        if result and len(result) > 0:
            filtered = [obj for obj in result if obj.get('id') == obj_id]
            if len(filtered) > 0:
                import random
                return random.choice(filtered)
        return None

    def get_viewport_data(self) -> Optional[Dict[str, Any]]:
        """
        Get viewport data

        Returns:
            Dictionary with width, height, xOffset, yOffset, canvasMousePosition
        """

        result = self._get("viewport")
        return cast(Optional[Dict[str, Any]], result)