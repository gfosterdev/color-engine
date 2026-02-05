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
            runEnergy, specialAttack, weight, isAnimating, animationId, interactingWith
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
            Dictionary with:
            - inCombat: bool - Whether player is in combat
            - combatLevel: int - Player combat level
            - autoRetaliate: bool - Auto-retaliate setting (True = enabled)
            - isPoisoned: bool - Whether player is poisoned
            - isVenomed: bool - Whether player is venomed
            - poisonDamage: int - Poison damage value
            - venomDamage: int - Venom damage value
            - target: dict - Current target info (name, id, combatLevel, health, maxHealth, isDying)
        """
        result = self._get("combat")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_auto_retaliate(self) -> Optional[bool]:
        """
        Get auto-retaliate status.
        
        Returns:
            True if auto-retaliate is enabled, False if disabled, None on error
        """
        combat_data = self.get_combat()
        if combat_data:
            return combat_data.get('autoRetaliate')
        return None
    
    def get_poison_status(self) -> Optional[Dict[str, Any]]:
        """
        Get poison/venom status.
        
        Returns:
            Dictionary with:
            - isPoisoned: bool - Whether player is poisoned
            - isVenomed: bool - Whether player is venomed
            - poisonDamage: int - Poison damage value
            - venomDamage: int - Venom damage value
            Returns None on error
        """
        combat_data = self.get_combat()
        if combat_data:
            return {
                'isPoisoned': combat_data.get('isPoisoned', False),
                'isVenomed': combat_data.get('isVenomed', False),
                'poisonDamage': combat_data.get('poisonDamage', 0),
                'venomDamage': combat_data.get('venomDamage', 0)
            }
        return None
    
    def get_animation(self) -> Optional[Dict[str, Any]]:
        """
        Get current animation state.
        
        Returns:
            Dictionary with animationId, poseAnimation, isAnimating, isMoving
        """
        result = self._get("animation")
        return cast(Optional[Dict[str, Any]], result)
    
    # Magic & Spellbook
    def get_selected_widget(self) -> Optional[Dict[str, Any]]:
        """
        Get currently selected widget (for spell selection detection).
        
        Returns:
            Dictionary with selectedSpellId, selectedWidgetId for detecting
            active spells awaiting targets (alchemy, telegrab, etc.)
        """
        result = self._get("selected_widget")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_magic_level(self) -> Optional[int]:
        """
        Get player's current magic level (boosted).
        
        Returns:
            Magic level as integer, None if unavailable
        """
        stats = self.get_stats()
        if stats:
            magic_stat = next((s for s in stats if s['stat'] == 'Magic'), None)
            if magic_stat:
                return magic_stat.get('boostedLevel', magic_stat.get('level', 1))
        return None
    
    # Inventory & Equipment
    def get_inventory(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get inventory items.
        
        Returns:
            List of item dictionaries with id, quantity, slot
        """
        result = self._get("inv")
        return cast(Optional[List[Dict[str, Any]]], result)
    
    def get_inventory_slot(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        Get inventory slot information.
        
        Returns:
            Dictionary with requestedSlot, empty, itemId, quantity
        """
        result = self._get(f"inv/{slot}")
        return cast(Optional[Dict[str, Any]], result)

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
    
    def get_bank_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Get bank item information by item ID.

        Returns:
            Dictionary with id, quantity, slot, x, y, width, height, accessible (can click), hidden (not visible), name (<col=ff9040>Name</col>)
        """
        result = self._get(f"bank?itemId={item_id}")
        return cast(Optional[Dict[str, Any]], result)

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
    
    def get_ground_items(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        plane: Optional[int] = None,
        radius: Optional[int] = None,
        item_id: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get ground items, optionally filtered by location.
        
        Args:
            x: Target world X coordinate (optional)
            y: Target world Y coordinate (optional)
            plane: Target plane (optional, defaults to player's current plane)
            radius: Search radius in tiles (optional, defaults to exact match if x/y provided)
            item_id: Filter by specific item ID (optional)
        
        Returns:
            List of ground item dictionaries with id, quantity, position
            
        Examples:
            # Get all items in scene
            items = api.get_ground_items()
            
            # Get items at specific tile
            items = api.get_ground_items(x=3222, y=3218)
            
            # Get items within 5 tiles of coordinate
            items = api.get_ground_items(x=3222, y=3218, radius=5)
            
            # Get all iron ore (item ID 440) within 10 tiles of NPC death location
            items = api.get_ground_items(x=npc_x, y=npc_y, radius=10, item_id=440)
        """
        params = []
        if x is not None:
            params.append(f"x={x}")
        if y is not None:
            params.append(f"y={y}")
        if plane is not None:
            params.append(f"plane={plane}")
        if radius is not None:
            params.append(f"radius={radius}")
        if item_id is not None:
            params.append(f"item_id={item_id}")
        
        endpoint = "grounditems"
        if params:
            endpoint += "?" + "&".join(params)
        
        result = self._get(endpoint)
        print(result)
        return cast(Optional[List[Dict[str, Any]]], result)
    
    # Game State
    def get_camera(self) -> Optional[Dict[str, Any]]:
        """
        Get camera position and rotation.
        
        Returns:
            Dictionary with yaw, pitch, scale, x, y, z
        """
        result = self._get("camera")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_camera_rotation(self, world_x: int, world_y: int, plane: int = 0) -> Optional[Dict[str, Any]]:
        """
        Get camera rotation calculations to make a target tile visible.
        
        Args:
            world_x: Target tile world X coordinate
            world_y: Target tile world Y coordinate
            plane: Target tile plane (default: 0)
        
        Returns:
            Dictionary with:
            - visible: bool - whether tile is currently visible
            - currentYaw, currentPitch, currentScale: current camera state
            - targetYaw, targetPitch, targetScale: target camera state
            - yawDistance, pitchDistance, scaleDelta: adjustment amounts
            - dragPixelsX, dragPixelsY: signed pixel drag distances
            - screenX, screenY: tile screen coordinates (if visible)
        """
        result = self._get(f"camera_rotation?x={world_x}&y={world_y}&plane={plane}")
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

        Example return value:
            {
                "isOpen": True,
                "size": 5,
                "x": 400,
                "y": 300,
                "width": 150,
                "height": 120,
                "entries": [
                    {"option": "Walk here", "target": "", "type": 0},
                    {"option": "Examine", "target": "Tree", "type": 100},
                ]
            }
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
    
    def get_sidebar_tabs(self) -> Optional[Dict[str, bool]]:
        """
        Get sidebar tab states.
        
        Returns:
            Dictionary with inventory, music, prayer, equipment etc
        """
        result = self._get("sidebar")
        return cast(Optional[Dict[str, bool]], result)

    def get_sidebar_tab(self, tab_name: str) -> Optional[Dict[str, bool]]:
        """
        Get specific sidebar tab state.
        
        Args:
            tab_name: Name of the sidebar tab (e.g. inventory, music, prayer)
        
        Returns:
            True if tab is open, False if closed, None if unknown
        """
        result = self._get(f"sidebar/{tab_name}")
        return cast(Optional[Dict[str, bool]], result)

    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get request performance metrics.
        
        Returns:
            Dictionary mapping endpoint names to request times in milliseconds
        """
        return self.last_request_time.copy()

    def get_npcs_in_viewport(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all NPCs currently visible in the viewport with enhanced Actor data.
        
        Returns:
            List of NPC dictionaries with:
            - name: str - NPC name
            - id: int - NPC ID
            - worldX, worldY: int - World coordinates
            - x, y: int - Screen coordinates
            - combatLevel: int - Combat level
            - interactingWith: str|None - Name of entity NPC is interacting with
            - isDying: bool - Whether NPC is dying
            - animation: int - Current animation ID
            - graphicId: int - Current graphic ID
            - overheadText: str|None - Overhead text if any
            - overheadIcon: str|None - Prayer protection icon (MELEE, RANGED, MAGIC, etc.)
            - healthRatio: int - Current health ratio (if available)
            - healthScale: int - Max health scale (if available)
            - hull: dict - Convex hull polygon data with points array
        """
        result = self._get("npcs_in_viewport")
        return cast(Optional[List[Dict[str, Any]]], result)

    def get_entity_in_viewport(self, entity_ids: Union[int, List[int]], entity_type: str, world_x: Optional[int] = None, world_y: Optional[int] = None, selection: str = "random", filterNpcInteracting: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get entity (NPC or game object) in viewport if it exists.
        If more than one exists and no coordinates provided, returns based on selection mode.
        If coordinates are provided, returns the entity at that location.
        
        Args:
            entity_ids: Entity ID or list of entity IDs to search for (NPC ID or game object ID)
            entity_type: Type of entity - either "npc" or "object"
            world_x: Optional world X coordinate to filter by
            world_y: Optional world Y coordinate to filter by
            selection: Selection mode - "random" (default) or "nearest"

        Returns:
            Dictionary with id, name, x, y, hull or None if not found
        """
        if entity_type not in ["npc", "object"]:
            raise ValueError(f"entity_type must be 'npc' or 'object', got '{entity_type}'")
        
        if selection not in ["random", "nearest"]:
            raise ValueError(f"selection must be 'random' or 'nearest', got '{selection}'")
        
        # Normalize to list
        if isinstance(entity_ids, int):
            entity_ids = [entity_ids]
        
        # Get appropriate viewport data based on entity type
        if entity_type == "npc":
            result = self._get("npcs_in_viewport")
        else:  # object
            result = self._get("objects_in_viewport")
        
        result = cast(Optional[List[Dict[str, Any]]], result)
        if result and len(result) > 0:
            filtered = [entity for entity in result if entity.get('id') in entity_ids]
            print(filtered)
            # If filtering NPCs by interacting target
            if filterNpcInteracting and entity_type == "npc":
                player = self.get_player()
                player_name = player.get('name') if player else None
                filtered = [entity for entity in filtered if entity.get('interactingWith') == player_name or entity.get('interactingWith') is None]
            
            # If coordinates provided, filter by exact location
            if world_x is not None and world_y is not None:
                filtered = [entity for entity in filtered if entity.get('worldX') == world_x and entity.get('worldY') == world_y]
            
            if len(filtered) > 0:
                if selection == "nearest":
                    return self.get_nearest_entity_from_list(filtered)
                else:  # random
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

    def get_viewport_data(self) -> Optional[Dict[str, Any]]:
        """
        Get viewport data

        Returns:
            Dictionary with width, height, xOffset, yOffset, canvasMouseX, canvasMouseY
        """

        result = self._get("viewport")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_camera_rotation_to_tile(self, world_x: int, world_y: int, plane: int = 0) -> Optional[Dict[str, Any]]:
        """
        Calculate camera rotation required to make a world tile visible in viewport.
        
        Args:
            world_x: Target tile world X coordinate
            world_y: Target tile world Y coordinate
            plane: Target tile plane (default: 0)
            
        Returns:
            Dictionary with:
                - visible (bool): Whether tile is currently visible
                - currentYaw (int): Current camera yaw (0-2048)
                - currentPitch (int): Current camera pitch (128-512)
                - targetYaw (int): Required yaw to face tile
                - targetPitch (int): Recommended pitch for distance
                - yawDistance (int): Rotation distance in yaw units
                - pitchDistance (int): Rotation distance in pitch units
                - direction (str): "left" or "right" for yaw rotation
                - pitchDirection (str): "up" or "down" for pitch adjustment
                - yawPixels (int): Approximate pixel drag distance for yaw
                - pitchPixels (int): Approximate pixel drag distance for pitch
                - screenX (int): Screen X coordinate if visible
                - screenY (int): Screen Y coordinate if visible
        """
        result = self._get(f"camera_rotation?x={world_x}&y={world_y}&plane={plane}")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_nearest_by_id(self, entity_ids: Union[int, List[int]], entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Find the nearest game object or NPC by ID(s) and return its world coordinates.
        
        Args:
            entity_ids: The game object ID(s) or NPC ID(s) to search for (single int or list)
            entity_type: Type of entity to search for - either "npc" or "object"
            
        Returns:
            Dictionary with:
                - found (bool): Whether entity was found
                - searchIds (list): The IDs that were searched for
                - searchType (str): The type that was searched ("npc" or "object")
                - type (str): "npc" or "object" if found
                - name (str): Entity name (NPCs only)
                - id (int): The ID of the found entity
                - worldX (int): World X coordinate
                - worldY (int): World Y coordinate
                - plane (int): World plane
                - distance (int): Distance from player in tiles
            
            Returns None if request fails, or dict with found=False if not found.
        """
        if entity_type not in ["npc", "object"]:
            raise ValueError(f"entity_type must be 'npc' or 'object', got '{entity_type}'")
        
        # Normalize to list
        if isinstance(entity_ids, int):
            entity_ids = [entity_ids]
        
        # Convert list to comma-separated string for query parameter
        ids_str = ','.join(map(str, entity_ids))
        
        result = self._get(f"find_nearest?ids={ids_str}&type={entity_type}")
        return cast(Optional[Dict[str, Any]], result)
    
    def get_nearest_entity_from_list(self, entities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the nearest entity from a list of entity dictionaries.
        Calculates distance from player coordinates to each entity.
        
        Args:
            entities: List of entity dictionaries (must contain 'worldX' and 'worldY' or 'x' and 'y')
            
        Returns:
            The nearest entity dict with 'distance' field added, or None if list is empty or player coords unavailable
        """
        if not entities:
            return None
        
        # Get player coordinates
        coords = self.get_coords()
        if not coords or 'world' not in coords:
            return None
        
        px, py = coords['world']['x'], coords['world']['y']
        
        # Calculate distances for each entity
        import math
        for entity in entities:
            # Support both 'worldX/worldY' and 'x/y' field names
            ex = entity.get('worldX', entity.get('x'))
            ey = entity.get('worldY', entity.get('y'))
            
            if ex is None or ey is None:
                continue
            
            dx = ex - px
            dy = ey - py
            entity['distance'] = math.sqrt(dx*dx + dy*dy)
        
        # Filter out entities without distance (missing coordinates)
        entities_with_distance = [e for e in entities if 'distance' in e]
        
        if not entities_with_distance:
            return None
        
        # Return nearest
        return min(entities_with_distance, key=lambda e: e['distance'])