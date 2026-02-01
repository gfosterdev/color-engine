"""
Game location world coordinates for Old School RuneScape.

This module provides a centralized registry of important in-game locations using world coordinates.
Locations are organized by category for easy lookup and maintenance.

World coordinates in OSRS are represented as (x, y, z) tuples where:
- x: East-West position
- y: North-South position
- z: Plane/floor level (0 = ground floor, 1 = first floor, etc.)

Usage:
    from config.locations import BankLocations, MiningLocations, WoodcuttingLocations
    
    varrock_west_bank = BankLocations.VARROCK_WEST
    lumbridge_mine = MiningLocations.LUMBRIDGE_SWAMP_WEST
"""

from typing import Dict, List, Optional, Tuple, Any


# Type alias for world coordinates
WorldCoordinate = Tuple[int, int, int]  # (x, y, z)


class LocationCategory:
    """Base class for location categories with helper methods."""
    
    @classmethod
    def all(cls) -> Dict[str, WorldCoordinate]:
        """Return all locations in this category as a dictionary."""
        all_locations = {}
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, tuple) and len(attr_value) == 3:
                    all_locations[attr_name] = attr_value
        return all_locations
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional[WorldCoordinate]:
        """Find a location by its name."""
        name_upper = name.upper()
        if hasattr(cls, name_upper):
            attr_value = getattr(cls, name_upper)
            if isinstance(attr_value, tuple) and len(attr_value) == 3:
                return attr_value
        return None
    
    @classmethod
    def find_nearest(cls, x: int, y: int, z: int = 0) -> Optional[Tuple[str, WorldCoordinate, float]]:
        """
        Find the nearest location to the given coordinates.
        
        Returns:
            Tuple of (name, coordinates, distance) or None if no locations exist
        """
        all_locs = cls.all()
        if not all_locs:
            return None
        
        min_dist = float('inf')
        nearest_name = None
        nearest_coord = None
        
        for name, (loc_x, loc_y, loc_z) in all_locs.items():
            # Calculate 2D distance (ignoring z-plane unless same plane)
            if loc_z == z:
                dist = ((loc_x - x) ** 2 + (loc_y - y) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest_name = name
                    nearest_coord = (loc_x, loc_y, loc_z)
        
        if nearest_name and nearest_coord:
            return (nearest_name, nearest_coord, min_dist)
        return None


# ============================================================================
# BANK LOCATIONS
# ============================================================================

class BankLocations(LocationCategory):
    """World coordinates of bank locations."""
    
    # Varrock banks
    VARROCK_WEST = (3185, 3436, 0)
    VARROCK_EAST = (3253, 3420, 0)
    
    # Lumbridge banks
    LUMBRIDGE_CASTLE = (3208, 3220, 2)
    
    # Falador banks
    FALADOR_WEST = (2946, 3368, 0)
    FALADOR_EAST = (3013, 3355, 0)
    
    # Draynor bank
    DRAYNOR = (3092, 3243, 0)
    
    # Edgeville bank
    EDGEVILLE = (3094, 3492, 0)
    
    # Grand Exchange
    GRAND_EXCHANGE_NORTH = (3164, 3487, 0)
    GRAND_EXCHANGE_SOUTH = (3164, 3466, 0)
    
    # Ardougne banks
    ARDOUGNE_SOUTH = (2655, 3283, 0)
    ARDOUGNE_NORTH = (2616, 3332, 0)
    
    # Catherby bank
    CATHERBY = (2808, 3441, 0)
    
    # Seers' Village bank
    SEERS_VILLAGE = (2726, 3493, 0)
    
    # Al Kharid bank
    AL_KHARID = (3269, 3167, 0)
    
    # Duel Arena bank
    DUEL_ARENA = (3381, 3268, 0)
    
    # Shantay Pass bank
    SHANTAY_PASS = (3308, 3120, 0)


# ============================================================================
# MINING LOCATIONS
# ============================================================================

class MiningLocations(LocationCategory):
    """World coordinates of mining locations."""
    
    # Lumbridge area
    LUMBRIDGE_SWAMP_WEST = (3148, 3149, 0)  # Bronze (copper/tin)
    LUMBRIDGE_SWAMP_EAST = (3229, 3148, 0)  # Coal and mithril
    
    # Varrock area
    VARROCK_EAST_MINE = (3289, 3363, 0)  # Iron, tin, copper
    VARROCK_WEST_MINE = (3181, 3376, 0)  # Iron, tin, silver
    
    # Falador area
    DWARVEN_MINE_ENTRANCE = (3059, 3376, 0)
    MINING_GUILD_ENTRANCE = (3046, 3339, 0)
    
    # Al Kharid mine
    AL_KHARID_MINE = (3297, 3285, 0)  # Iron, copper, tin, silver, gold, mithril, adamantite
    
    # Motherlode Mine
    MOTHERLODE_MINE_ENTRANCE = (3759, 5666, 0)
    MOTHERLODE_MINE_CENTER = (3755, 5674, 0)
    
    # Rimmington mine
    RIMMINGTON_MINE = (2976, 3239, 0)  # Iron, tin, copper, clay, gold
    
    # Ardougne monastery
    ARDOUGNE_MONASTERY_MINE = (2610, 3222, 0)  # Coal
    
    # Heroes' Guild mine
    HEROES_GUILD_MINE = (2633, 9572, 0)  # Coal, adamantite, runite
    
    # Resource Area (Wilderness)
    WILDERNESS_RESOURCE_AREA = (3184, 3944, 0)


# ============================================================================
# WOODCUTTING LOCATIONS
# ============================================================================

class WoodcuttingLocations(LocationCategory):
    """World coordinates of woodcutting locations."""
    
    # Lumbridge area
    LUMBRIDGE_CASTLE_TREES = (3227, 3231, 0)  # Normal trees
    
    # Varrock area
    VARROCK_PALACE_TREES = (3227, 3457, 0)  # Yew trees
    
    # Draynor Village
    DRAYNOR_WILLOWS = (3086, 3234, 0)  # Willow trees
    
    # Grand Exchange
    GRAND_EXCHANGE_TREES = (3203, 3503, 0)  # Yew trees
    
    # Seers' Village
    SEERS_VILLAGE_MAPLES = (2730, 3502, 0)  # Maple trees
    SEERS_VILLAGE_YEWS = (2711, 3462, 0)  # Yew trees
    
    # Woodcutting Guild
    WOODCUTTING_GUILD_ENTRANCE = (1658, 3504, 0)
    WOODCUTTING_GUILD_REDWOODS = (1569, 3485, 0)
    
    # Falador area
    FALADOR_TREES = (3041, 3397, 0)  # Yew trees
    
    # Catherby area
    CATHERBY_TREES = (2768, 3437, 0)  # Yew trees
    
    # Port Sarim willows
    PORT_SARIM_WILLOWS = (3058, 3251, 0)


# ============================================================================
# FISHING LOCATIONS
# ============================================================================

class FishingLocations(LocationCategory):
    """World coordinates of fishing locations."""
    
    # Lumbridge area
    LUMBRIDGE_SWAMP_FISHING = (3239, 3147, 0)  # Net/Bait
    LUMBRIDGE_RIVER = (3239, 3244, 0)  # Lure/Bait
    
    # Draynor Village
    DRAYNOR_FISHING = (3085, 3228, 0)  # Net/Bait
    
    # Barbarian Village
    BARBARIAN_VILLAGE_FISHING = (3109, 3433, 0)  # Lure/Bait
    
    # Catherby
    CATHERBY_FISHING = (2835, 3432, 0)  # Cage/Harpoon
    
    # Fishing Guild
    FISHING_GUILD_ENTRANCE = (2610, 3391, 0)
    
    # Karamja
    KARAMJA_DOCKS = (2924, 3179, 0)  # Cage/Harpoon
    
    # Shilo Village
    SHILO_VILLAGE_FISHING = (2859, 2970, 0)  # Lure/Bait
    
    # Piscatoris
    PISCATORIS_FISHING_COLONY = (2339, 3697, 0)


# ============================================================================
# TRAINING LOCATIONS
# ============================================================================

class TrainingLocations(LocationCategory):
    """World coordinates of common training locations."""
    
    # Combat training
    LUMBRIDGE_COWS = (3257, 3267, 0)
    VARROCK_SEWERS_RATS = (3237, 9866, 0)
    EDGEVILLE_HILL_GIANTS = (3117, 9856, 0)
    STRONGHOLD_OF_SECURITY = (3081, 3421, 0)
    
    # Slayer
    SLAYER_TOWER_ENTRANCE = (3428, 3537, 0)
    CATACOMBS_OF_KOUREND = (1664, 10050, 0)
    
    # Wilderness
    CHAOS_ALTAR = (3236, 3635, 0)
    CHAOS_TEMPLE = (2948, 3820, 0)


# ============================================================================
# CITY/TOWN CENTER LOCATIONS
# ============================================================================

class CityLocations(LocationCategory):
    """World coordinates of major city centers and important landmarks."""
    
    # Major cities
    VARROCK_SQUARE = (3212, 3424, 0)
    FALADOR_SQUARE = (2965, 3380, 0)
    LUMBRIDGE_CASTLE_COURTYARD = (3222, 3218, 0)
    ARDOUGNE_MARKET = (2662, 3305, 0)
    YANILLE_CENTER = (2606, 3093, 0)
    
    # Important landmarks
    GRAND_EXCHANGE_CENTER = (3164, 3478, 0)
    WARRIORS_GUILD_ENTRANCE = (2876, 3546, 0)
    LEGENDS_GUILD_ENTRANCE = (2729, 3348, 0)
    CHAMPIONS_GUILD_ENTRANCE = (3190, 3355, 0)


# ============================================================================
# TELEPORT DESTINATIONS
# ============================================================================

class TeleportLocations(LocationCategory):
    """World coordinates of common teleport destinations."""
    
    # Standard spellbook
    LUMBRIDGE_HOME_TELEPORT = (3222, 3218, 0)
    VARROCK_TELEPORT = (3212, 3424, 0)
    FALADOR_TELEPORT = (2964, 3378, 0)
    CAMELOT_TELEPORT = (2757, 3477, 0)
    ARDOUGNE_TELEPORT = (2662, 3305, 0)
    
    # Ancient spellbook
    EDGEVILLE_HOME_TELEPORT_ANCIENT = (3087, 3496, 0)
    PADDEWWA_TELEPORT = (3098, 9882, 0)
    SENNTISTEN_TELEPORT = (3322, 3336, 0)
    
    # Lunar spellbook
    LUNAR_ISLE_HOME_TELEPORT = (2100, 3914, 0)
    MOONCLAN_TELEPORT = (2111, 3915, 0)
    WATERBIRTH_TELEPORT = (2527, 3740, 0)
    
    # Arceuus spellbook
    ARCEUUS_HOME_TELEPORT = (1700, 3882, 0)


# ============================================================================
# QUEST LOCATIONS
# ============================================================================

class QuestLocations(LocationCategory):
    """World coordinates of common quest start points and important quest areas."""
    
    # Tutorial Island
    TUTORIAL_ISLAND_START = (3094, 3107, 0)
    
    # Lumbridge area quests
    COOKS_ASSISTANT_START = (3207, 3214, 0)
    SHEEP_SHEARER_START = (3189, 3273, 0)
    
    # Varrock area quests
    ROMEO_AND_JULIET_START = (3211, 3422, 0)
    DEMON_SLAYER_START = (3203, 3392, 0)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_location_category(coord: WorldCoordinate) -> Optional[str]:
    """
    Find which category a coordinate belongs to.
    
    Args:
        coord: World coordinate tuple (x, y, z)
        
    Returns:
        Category name or None if not found
    """
    categories = {
        "BankLocations": BankLocations,
        "MiningLocations": MiningLocations,
        "WoodcuttingLocations": WoodcuttingLocations,
        "FishingLocations": FishingLocations,
        "TrainingLocations": TrainingLocations,
        "CityLocations": CityLocations,
        "TeleportLocations": TeleportLocations,
        "QuestLocations": QuestLocations,
    }
    
    for category_name, category_cls in categories.items():
        all_locs = category_cls.all()
        if coord in all_locs.values():
            return category_name
    
    return None


def find_location_name(coord: WorldCoordinate) -> Optional[str]:
    """
    Find the specific name of a location by its coordinates.
    
    Args:
        coord: World coordinate tuple (x, y, z)
        
    Returns:
        Location name or None if not found
    """
    categories = [
        BankLocations,
        MiningLocations,
        WoodcuttingLocations,
        FishingLocations,
        TrainingLocations,
        CityLocations,
        TeleportLocations,
        QuestLocations,
    ]
    
    for category in categories:
        all_locs = category.all()
        for name, location in all_locs.items():
            if location == coord:
                return name
    
    return None


def find_nearest_location(x: int, y: int, z: int = 0) -> Optional[Tuple[str, str, WorldCoordinate, float]]:
    """
    Find the nearest location across all categories.
    
    Args:
        x: X coordinate
        y: Y coordinate
        z: Z coordinate (plane level)
        
    Returns:
        Tuple of (category_name, location_name, coordinates, distance) or None
    """
    categories = {
        "BankLocations": BankLocations,
        "MiningLocations": MiningLocations,
        "WoodcuttingLocations": WoodcuttingLocations,
        "FishingLocations": FishingLocations,
        "TrainingLocations": TrainingLocations,
        "CityLocations": CityLocations,
        "TeleportLocations": TeleportLocations,
        "QuestLocations": QuestLocations,
    }
    
    min_dist = float('inf')
    nearest_category = None
    nearest_name = None
    nearest_coord = None
    
    for category_name, category_cls in categories.items():
        result = category_cls.find_nearest(x, y, z)
        if result:
            name, coord, dist = result
            if dist < min_dist:
                min_dist = dist
                nearest_category = category_name
                nearest_name = name
                nearest_coord = coord
    
    if nearest_category and nearest_name and nearest_coord:
        return (nearest_category, nearest_name, nearest_coord, min_dist)
    return None
