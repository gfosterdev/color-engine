"""
Game object ID references for Old School RuneScape.

This module provides a centralized registry of all in-game object IDs used by the bot.
Object IDs are organized by category for easy lookup and maintenance.

Source: RuneLite ObjectID.java
https://github.com/runelite/runelite/blob/master/runelite-api/src/main/java/net/runelite/api/ObjectID.java

Usage:
    from config.game_objects import BankObjects, OreRocks, Trees
    
    # Access game object
    iron_rock = OreRocks.IRON_ORE_ROCK
    iron_ids = iron_rock.ids  # List[int]
    iron_name = iron_rock.name  # str
    
    # Get all objects in category
    all_rocks = OreRocks.all()  # Returns List[GameObject]
    all_rock_ids = OreRocks.all_ids()  # Returns List[int]
    
    # GameObject supports list-like operations
    if object_id in OreRocks.IRON_ORE_ROCK:  # Uses __contains__
        print(f"Found {OreRocks.IRON_ORE_ROCK.name}")
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class GameObject:
    """Represents a game object type with all its ID variations."""
    name: str
    ids: List[int]
    category: str
    description: str = ""
    
    def __contains__(self, item: int) -> bool:
        """Allow 'id in GameObject' syntax."""
        return item in self.ids
    
    def __len__(self) -> int:
        """Return number of ID variations."""
        return len(self.ids)
    
    def __iter__(self):
        """Allow iteration over IDs."""
        return iter(self.ids)
    
    def __getitem__(self, index):
        """Allow indexing like a list."""
        return self.ids[index]


class ObjectCategory:
    """Base class for game object categories with helper methods."""
    
    @classmethod
    def all(cls) -> List[GameObject]:
        """Return all game objects in this category."""
        objects = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, GameObject):
                    objects.append(attr_value)
        return objects
    
    @classmethod
    def all_ids(cls) -> List[int]:
        """Return all object IDs in this category (flattened)."""
        all_ids = []
        for obj in cls.all():
            all_ids.extend(obj.ids)
        return all_ids
    
    @classmethod
    def find_by_id(cls, obj_id: int) -> Optional[GameObject]:
        """Find a game object by any of its ID variations."""
        for obj in cls.all():
            if obj_id in obj.ids:
                return obj
        return None


# ============================================================================
# BANKING OBJECTS
# ============================================================================

class BankObjects(ObjectCategory):
    """All bank-related object IDs."""
    
    # Bank booths (common in cities)
    BANK_BOOTH = GameObject(
        name="Bank booth",
        ids=[10355, 10356, 10357, 10583, 6084, 6083, 11744, 11758, 12798, 12799, 12800, 12801, 14367, 14368, 18491, 18492, 27291,
             24347],
        category="banking",
        description="Bank booths found in cities"
    )
    
    # Bank chests (common in resource areas)
    BANK_CHEST = GameObject(
        name="Bank chest",
        ids=[4483, 24101, 27663, 34752, 2693, 4485, 8981, 12308, 14382, 14383, 14886, 16700, 19230, 21301, 24914, 27253, 28594, 28861, 34755, 35647, 36196, 36197, 36198],
        category="banking",
        description="Bank chests in resource areas"
    )
    
    # Deposit boxes (quick deposit only, no withdrawal)
    DEPOSIT_BOX = GameObject(
        name="Bank deposit box",
        ids=[25937, 26969, 32924, 34755, 36788, 39830],
        category="banking",
        description="Deposit boxes for quick deposits"
    )
    
    @classmethod
    def all_interactive(cls) -> List[int]:
        """Get all bank object IDs that can be opened (booths + chests, no deposit boxes)."""
        return cls.BANK_BOOTH.ids + cls.BANK_CHEST.ids


# ============================================================================
# MINING OBJECTS
# ============================================================================

class OreRocks(ObjectCategory):
    """Mining rock object IDs."""
    
    # Essential ores
    COPPER_ORE_ROCK = GameObject("Copper ore rock", [10079, 10943, 11161, 31080, 31081, 31082], "mining")
    TIN_ORE_ROCK = GameObject("Tin ore rock", [10080, 11360, 11361, 11933], "mining")
    IRON_ORE_ROCK = GameObject("Iron ore rock", [11364, 11365, 36203, 37307, 37308, 37309], "mining")
    COAL_ROCK = GameObject("Coal rock", [4676, 11366, 11367, 36204, 37304, 37305, 37306], "mining")
    
    # Clay
    CLAY_ROCK = GameObject("Clay rock", [11362, 11363, 15503, 15504, 15505], "mining")
    SOFT_CLAY_ROCK = GameObject("Soft clay rock", [34956, 34957, 36210], "mining")
    
    # Precious metals
    SILVER_ORE_ROCK = GameObject("Silver ore rock", [11368, 11369, 36205], "mining")
    GOLD_ORE_ROCK = GameObject("Gold ore rock", [11370, 11371, 36206, 37310, 37311], "mining")
    
    # High-level ores
    MITHRIL_ORE_ROCK = GameObject("Mithril ore rock", [11372, 11373, 36207, 37313, 37314, 37315], "mining")
    ADAMANTITE_ORE_ROCK = GameObject("Adamantite ore rock", [11374, 11375, 36208, 37316, 37317, 37318], "mining")
    RUNITE_ORE_ROCK = GameObject("Runite ore rock", [11376, 11377, 36209, 31917, 37319, 37320, 37321], "mining")
    
    # Special ores
    SANDSTONE_ROCK = GameObject("Sandstone rock", [11386, 11387], "mining")
    GRANITE_ROCK = GameObject("Granite rock", [11388, 11389, 11390, 11391], "mining")
    GEM_ROCK = GameObject("Gem rock", [11380, 11381], "mining")
    AMETHYST_CRYSTAL = GameObject("Amethyst crystal", [33254], "mining")
    
    # Motherlode Mine
    ORE_VEIN = GameObject("Ore vein", [26661, 26662, 26663, 26664], "mining", "Motherlode Mine ore veins")
    
    # Volcanic Mine
    BOULDER = GameObject("Boulder", [30842, 30843, 30844], "mining", "Volcanic Mine boulders")


# ============================================================================
# WOODCUTTING OBJECTS
# ============================================================================

class Trees(ObjectCategory):
    """Woodcutting tree object IDs."""
    
    # Normal trees
    TREE = GameObject(
        name="Tree",
        ids=[1276, 1277, 1278, 1279, 1280, 1282, 1283, 1284, 1285, 1286, 1289, 1290, 1291, 1315, 1316, 1318, 1319, 1330, 1331, 1332, 1365, 1383, 1384, 4820, 4821, 4822, 4823, 5902, 5903, 5904, 14308, 14309, 14310, 14311],
        category="woodcutting"
    )
    DEAD_TREE = GameObject(
        name="Dead tree",
        ids=[1282, 1283, 1284, 1285, 1286, 1289, 1290, 1291, 1365, 1383, 1384],
        category="woodcutting"
    )
    EVERGREEN = GameObject(
        name="Evergreen",
        ids=[1318, 1319],
        category="woodcutting"
    )
    
    # Oak trees
    OAK_TREE = GameObject("Oak tree", [10820, 37477, 37478, 38760], "woodcutting")
    
    # Willow trees
    WILLOW_TREE = GameObject("Willow tree", [10829, 10831, 10833, 37473, 37474, 38755], "woodcutting")
    
    # Maple trees
    MAPLE_TREE = GameObject("Maple tree", [10832, 36681, 37478, 38766], "woodcutting")
    
    # Yew trees
    YEW_TREE = GameObject("Yew tree", [10822, 36683, 37479, 38764], "woodcutting")
    
    # Magic trees
    MAGIC_TREE = GameObject("Magic tree", [10834, 37823], "woodcutting")
    
    # Special trees
    REDWOOD_TREE = GameObject("Redwood tree", [29668, 29670], "woodcutting")
    TEAK_TREE = GameObject("Teak tree", [9036, 15062, 36686], "woodcutting")
    MAHOGANY_TREE = GameObject("Mahogany tree", [9034, 36688], "woodcutting")
    
    # Fruit trees
    APPLE_TREE = GameObject("Apple tree", [1278], "woodcutting")
    BANANA_TREE = GameObject(
        name="Banana tree",
        ids=[2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2091],
        category="woodcutting"
    )
    
    # Tree stumps (after cutting)
    TREE_STUMP = GameObject(
        name="Tree stump",
        ids=[1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 4821, 4822, 4823, 10821],
        category="woodcutting",
        description="Stumps remaining after trees are cut"
    )


# ============================================================================
# FISHING OBJECTS
# ============================================================================

class FishingSpots(ObjectCategory):
    """Fishing spot NPC IDs (these are NPCs, not objects)."""
    
    # Net/Bait spots
    NET_BAIT_SPOT = GameObject(
        name="Fishing spot (net/bait)",
        ids=[1518, 1521, 1522, 1523, 1524, 1525, 1528, 3317, 3418, 3419, 3657, 3913, 4316, 4476, 5820, 5821, 7155, 7459, 7460, 7467, 7468, 7469, 7470],
        category="fishing"
    )
    
    # Lure/Bait spots
    LURE_BAIT_SPOT = GameObject(
        name="Fishing spot (lure/bait)",
        ids=[1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 3417, 3418, 3419, 3420, 5820, 5821, 7155, 7459, 7460, 7467, 7468, 7469, 7470],
        category="fishing"
    )
    
    # Cage/Harpoon spots
    CAGE_HARPOON_SPOT = GameObject(
        name="Fishing spot (cage/harpoon)",
        ids=[1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1528, 3317, 3418, 3419, 3657, 3913, 4316, 4476, 5820, 5821, 7155, 7459, 7460, 7467, 7468, 7469, 7470],
        category="fishing"
    )


# ============================================================================
# UTILITY OBJECTS
# ============================================================================

class UtilityObjects(ObjectCategory):
    """Utility objects like furnaces, anvils, ranges, etc."""
    
    # Metalworking
    ANVIL = GameObject("Anvil", [2031, 2097, 4306, 6150, 26814, 37622], "utility", "Metalworking anvil")
    FURNACE = GameObject(
        name="Furnace",
        ids=[2030, 2966, 3294, 4304, 11010, 11666, 12100, 12809, 16469, 18497, 18525, 24009, 26814, 30510, 36956, 37651],
        category="utility",
        description="Smelting furnace"
    )
    
    # Cooking
    RANGE = GameObject(
        name="Range",
        ids=[2728, 2729, 2730, 2731, 2859, 3039, 4172, 5249, 5275, 6150, 9682, 11666, 12269, 12539, 12540, 21302, 24283, 24284, 25014, 25440, 26815, 26817, 29165, 31633, 34547, 34546, 34544, 36972],
        category="utility",
        description="Cooking range"
    )
    FIRE = GameObject(
        name="Fire",
        ids=[26185, 26186, 26187, 26188, 26189, 26190, 26191, 26192, 26193, 26194, 26195, 26196, 26197, 26198, 26199, 26200, 26201, 26202, 26203, 26204, 26205, 26206, 26207, 26208, 26209, 26210, 26211, 26212, 26213, 26214],
        category="utility",
        description="Cooking fire"
    )
    
    # Crafting
    SPINNING_WHEEL = GameObject("Spinning wheel", [2644, 4309, 8748, 14889, 21304, 34497], "utility")
    POTTERY_WHEEL = GameObject("Pottery wheel", [2642, 4310, 14887, 25484], "utility")
    POTTERY_OVEN = GameObject("Pottery oven", [2643, 4308, 11601, 14888, 25485], "utility")
    LOOM = GameObject("Loom", [2644, 8748], "utility")
    
    # Altars
    ALTAR = GameObject(
        name="Altar",
        ids=[2640, 4008, 13179, 13180, 13181, 13182, 13183, 13184, 13185, 13186, 13187, 13188, 13189, 13190, 13191, 13192, 13193, 13194, 13195, 13196, 13197, 13198, 13199, 13200, 13201, 13202, 13203, 13204, 13205, 13206, 13207, 13208, 13209, 13210, 13211, 13212, 13213, 13214, 13215, 13216, 13217, 13218, 13219, 13220, 13221, 13222, 13223, 13224, 13225, 13226, 13227, 13228, 13229, 13230, 13231, 13232, 13233, 13234, 13235, 13236, 13237, 13238, 13239, 13240, 13241, 13242, 13243, 13244, 13245, 13246, 13247, 13248],
        category="utility",
        description="Prayer altar"
    )
    
    # Training dummies
    TRAINING_DUMMY = GameObject(
        name="Training dummy",
        ids=[23921, 23922, 23923, 23924, 23925, 23926, 23927, 23928, 23929, 23930, 23931, 23932, 23933, 23934, 23935, 23936, 23937, 23938, 23939, 23940, 23941, 23942, 23943, 23944, 23945, 23946, 23947, 23948, 23949, 23950, 23951, 23952, 23953, 23954, 23955, 23956, 23957, 23958, 23959, 23960, 23961, 23962, 23963, 23964, 23965, 23966, 23967, 23968, 23969, 23970, 23971, 23972, 23973, 23974, 23975, 23976, 23977, 23978, 23979, 23980, 23981, 23982, 23983, 23984, 23985, 23986, 23987, 23988, 23989, 23990, 23991, 23992, 23993, 23994, 23995, 23996, 23997, 23998, 23999],
        category="utility",
        description="Combat training dummy"
    )


# ============================================================================
# DOORS & GATES
# ============================================================================

class DoorsAndGates(ObjectCategory):
    """Door and gate object IDs."""
    
    # Generic doors (closed)
    DOOR_CLOSED = GameObject(
        name="Door (closed)",
        ids=[1516, 1519, 1530, 1531, 1533, 1534, 3014, 3015, 3017, 3018, 3019, 3020, 11712, 11714, 11716, 11718],
        category="doors"
    )
    
    # Generic doors (open)
    DOOR_OPEN = GameObject(
        name="Door (open)",
        ids=[1517, 1520, 1531, 1532, 1534, 1535, 3014, 3016, 3017, 3019, 3020, 3021, 11713, 11715, 11717, 11719],
        category="doors"
    )
    
    # Gates (closed)
    GATE_CLOSED = GameObject("Gate (closed)", [1551, 1553, 2514, 2515, 9470, 9472], "doors")
    
    # Gates (open)
    GATE_OPEN = GameObject("Gate (open)", [1552, 1554, 2514, 2516, 9471, 9473], "doors")
    
    # Lumbridge cow pen gate (placeholder IDs - user will verify)
    LUMBRIDGE_COW_PEN_GATE = GameObject(
        name="Gate",
        ids=[1567, 1558, 1559, 1560],
        category="doors",
        description="Lumbridge cow pen gate"
    )

    SLAYER_TOWER_DOOR = GameObject(
        name="Slayer tower door",
        ids=[2109, 2110],
        category="doors",
        description="Door to enter/exit Slayer tower"
    )

    SLAYER_TOWER_BLOODVELD_DOOR = GameObject(
        name="Slayer tower bloodveld door",
        ids=[2106],
        category="doors",
        description="Door to bloodveld room in Slayer tower"
    )


# ============================================================================
# STAIRS & LADDERS
# ============================================================================

class StairsAndLadders(ObjectCategory):
    """Stairs and ladder object IDs for vertical navigation."""
    
    # Lumbridge castle stairs (placeholder IDs - user will verify)
    LUMBRIDGE_CASTLE_STAIRS = GameObject(
        name="Staircase",
        ids=[56230, 16672, 56231],
        category="stairs",
        description="Lumbridge castle stairs for climbing up/down"
    )
    
    # Slayer tower stairs
    SLAYER_TOWER_STAIRS = GameObject(
        name="Staircase",
        ids=[2114, 2119],
        category="stairs",
        description="Slayer tower staircases for climbing between floors"
    )
    
    # Slayer tower chain (acts like stairs/ladder)
    SLAYER_TOWER_CHAIN = GameObject(
        name="Chain",
        ids=[4495],
        category="stairs",
        description="Slayer tower chain for climbing up/down"
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_object_category(obj_id: int) -> Optional[str]:
    """
    Find which category an object ID belongs to.
    
    Args:
        obj_id: Object ID to search for
        
    Returns:
        Category name (e.g., "BankObjects", "OreRocks") or None if not found
    """
    categories = {
        "BankObjects": BankObjects,
        "OreRocks": OreRocks,
        "Trees": Trees,
        "FishingSpots": FishingSpots,
        "UtilityObjects": UtilityObjects,
        "DoorsAndGates": DoorsAndGates,
        "StairsAndLadders": StairsAndLadders,
    }
    
    for category_name, category_cls in categories.items():
        if obj_id in category_cls.all_ids():
            return category_name
    
    return None


def find_object_name(obj_id: int) -> Optional[str]:
    """
    Find the display name of an object by its ID.
    
    Args:
        obj_id: Object ID to search for
        
    Returns:
        Object display name (e.g., "Iron ore rock", "Bank booth") or None if not found
    """
    categories = [BankObjects, OreRocks, Trees, FishingSpots, UtilityObjects, DoorsAndGates, StairsAndLadders]
    
    for category in categories:
        obj = category.find_by_id(obj_id)
        if obj:
            return obj.name
    
    return None


def find_game_object(obj_id: int) -> Optional[GameObject]:
    """
    Find a GameObject by its ID.
    
    Args:
        obj_id: Object ID to search for
        
    Returns:
        GameObject object or None if not found
    """
    categories = [BankObjects, OreRocks, Trees, FishingSpots, UtilityObjects, DoorsAndGates, StairsAndLadders]
    
    for category in categories:
        obj = category.find_by_id(obj_id)
        if obj:
            return obj
    
    return None
