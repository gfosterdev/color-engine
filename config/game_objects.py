"""
Game object ID references for Old School RuneScape.

This module provides a centralized registry of all in-game object IDs used by the bot.
Object IDs are organized by category for easy lookup and maintenance.

Source: RuneLite ObjectID.java
https://github.com/runelite/runelite/blob/master/runelite-api/src/main/java/net/runelite/api/ObjectID.java

Usage:
    from config.game_objects import BankObjects, OreRocks, Trees
    
    bank_ids = BankObjects.all()
    iron_rock_ids = OreRocks.IRON
"""

from typing import Dict, List, Optional


class ObjectCategory:
    """Base class for game object categories with helper methods."""
    
    @classmethod
    def all(cls) -> List[int]:
        """Return all object IDs in this category."""
        all_ids = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, list):
                    all_ids.extend(attr_value)
        return all_ids
    
    @classmethod
    def find_by_id(cls, obj_id: int) -> Optional[str]:
        """Find the name of an object by its ID."""
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, list) and obj_id in attr_value:
                    return attr_name
        return None


# ============================================================================
# BANKING OBJECTS
# ============================================================================

class BankObjects(ObjectCategory):
    """All bank-related object IDs."""
    
    # Bank booths (common in cities)
    BOOTHS = [10355, 10356, 10357, 10583, 6084, 6083, 11744, 11758, 12798, 12799, 12800, 12801, 14367, 14368]
    
    # Bank chests (common in resource areas)
    CHESTS = [4483, 24101, 27663, 34752, 2693, 4485, 8981, 12308, 14382, 14383, 14886, 16700, 19230, 21301, 24914, 27253, 28594, 28861, 34755, 35647, 36196, 36197, 36198]
    
    # Deposit boxes (quick deposit only, no withdrawal)
    DEPOSIT_BOXES = [25937, 26969, 32924, 34755, 36788, 39830]
    
    @classmethod
    def all_interactive(cls) -> List[int]:
        """Get all bank objects that can be opened (booths + chests, no deposit boxes)."""
        return cls.BOOTHS + cls.CHESTS


# ============================================================================
# MINING OBJECTS
# ============================================================================

class OreRocks(ObjectCategory):
    """Mining rock object IDs."""
    
    # Essential ores
    COPPER = [10079, 10943, 11161, 31080, 31081, 31082]
    TIN = [10080, 11360, 11361, 11933]
    IRON = [11364, 11365, 36203, 37307, 37308, 37309]
    COAL = [4676, 11366, 11367, 36204, 37304, 37305, 37306]
    
    # Clay
    CLAY = [11362, 11363, 15503, 15504, 15505]
    SOFT_CLAY = [34956, 34957, 36210]
    
    # Precious metals
    SILVER = [11368, 11369, 36205]
    GOLD = [11370, 11371, 36206, 37310, 37311]
    
    # High-level ores
    MITHRIL = [11372, 11373, 36207, 37313, 37314, 37315]
    ADAMANTITE = [11374, 11375, 36208, 37316, 37317, 37318]
    RUNITE = [11376, 11377, 36209, 31917, 37319, 37320, 37321]
    
    # Special ores
    SANDSTONE = [11386, 11387]
    GRANITE = [11388, 11389, 11390, 11391]
    GEM_ROCK = [11380, 11381]
    AMETHYST = [33254]
    
    # Motherlode Mine
    ORE_VEIN = [26661, 26662, 26663, 26664]
    
    # Volcanic Mine
    BOULDER = [30842, 30843, 30844]


# ============================================================================
# WOODCUTTING OBJECTS
# ============================================================================

class Trees(ObjectCategory):
    """Woodcutting tree object IDs."""
    
    # Normal trees
    TREE = [1276, 1277, 1278, 1279, 1280, 1282, 1283, 1284, 1285, 1286, 1289, 1290, 1291, 1315, 1316, 1318, 1319, 1330, 1331, 1332, 1365, 1383, 1384, 4820, 4821, 4822, 4823, 5902, 5903, 5904, 14308, 14309, 14310, 14311]
    DEAD_TREE = [1282, 1283, 1284, 1285, 1286, 1289, 1290, 1291, 1365, 1383, 1384]
    EVERGREEN = [1318, 1319]
    
    # Oak trees
    OAK = [10820, 37477, 37478, 38760]
    
    # Willow trees
    WILLOW = [10829, 10831, 10833, 37473, 37474, 38755]
    
    # Maple trees
    MAPLE = [10832, 36681, 37478, 38766]
    
    # Yew trees
    YEW = [10822, 36683, 37479, 38764]
    
    # Magic trees
    MAGIC = [10834, 37823]
    
    # Special trees
    REDWOOD = [29668, 29670]
    TEAK = [9036, 15062, 36686]
    MAHOGANY = [9034, 36688]
    
    # Fruit trees
    APPLE_TREE = [1278]
    BANANA_TREE = [2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2091]
    
    # Tree stumps (after cutting)
    STUMPS = [1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 4821, 4822, 4823, 10821]


# ============================================================================
# FISHING OBJECTS
# ============================================================================

class FishingSpots(ObjectCategory):
    """Fishing spot NPC IDs (these are NPCs, not objects)."""
    
    # Net/Bait spots
    NET_BAIT = [1518, 1521, 1522, 1523, 1524, 1525, 1528, 3317, 3418, 3419, 3657, 3913, 4316, 4476, 5820, 5821, 7155, 7459, 7460, 7467, 7468, 7469, 7470]
    
    # Lure/Bait spots
    LURE_BAIT = [1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517, 3417, 3418, 3419, 3420, 5820, 5821, 7155, 7459, 7460, 7467, 7468, 7469, 7470]
    
    # Cage/Harpoon spots
    CAGE_HARPOON = [1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1528, 3317, 3418, 3419, 3657, 3913, 4316, 4476, 5820, 5821, 7155, 7459, 7460, 7467, 7468, 7469, 7470]


# ============================================================================
# UTILITY OBJECTS
# ============================================================================

class UtilityObjects(ObjectCategory):
    """Utility objects like furnaces, anvils, ranges, etc."""
    
    # Metalworking
    ANVIL = [2031, 2097, 4306, 6150, 26814, 37622]
    FURNACE = [2030, 2966, 3294, 4304, 11010, 11666, 12100, 12809, 16469, 18497, 18525, 24009, 26814, 30510, 36956, 37651]
    
    # Cooking
    RANGE = [2728, 2729, 2730, 2731, 2859, 3039, 4172, 5249, 5275, 6150, 9682, 11666, 12269, 12539, 12540, 21302, 24283, 24284, 25014, 25440, 26815, 26817, 29165, 31633, 34547, 34546, 34544, 36972]
    FIRE = [26185, 26186, 26187, 26188, 26189, 26190, 26191, 26192, 26193, 26194, 26195, 26196, 26197, 26198, 26199, 26200, 26201, 26202, 26203, 26204, 26205, 26206, 26207, 26208, 26209, 26210, 26211, 26212, 26213, 26214]
    
    # Crafting
    SPINNING_WHEEL = [2644, 4309, 8748, 14889, 21304, 34497]
    POTTERY_WHEEL = [2642, 4310, 14887, 25484]
    POTTERY_OVEN = [2643, 4308, 11601, 14888, 25485]
    LOOM = [2644, 8748]
    
    # Altars
    ALTAR = [2640, 4008, 13179, 13180, 13181, 13182, 13183, 13184, 13185, 13186, 13187, 13188, 13189, 13190, 13191, 13192, 13193, 13194, 13195, 13196, 13197, 13198, 13199, 13200, 13201, 13202, 13203, 13204, 13205, 13206, 13207, 13208, 13209, 13210, 13211, 13212, 13213, 13214, 13215, 13216, 13217, 13218, 13219, 13220, 13221, 13222, 13223, 13224, 13225, 13226, 13227, 13228, 13229, 13230, 13231, 13232, 13233, 13234, 13235, 13236, 13237, 13238, 13239, 13240, 13241, 13242, 13243, 13244, 13245, 13246, 13247, 13248]
    
    # Training dummies
    DUMMY = [23921, 23922, 23923, 23924, 23925, 23926, 23927, 23928, 23929, 23930, 23931, 23932, 23933, 23934, 23935, 23936, 23937, 23938, 23939, 23940, 23941, 23942, 23943, 23944, 23945, 23946, 23947, 23948, 23949, 23950, 23951, 23952, 23953, 23954, 23955, 23956, 23957, 23958, 23959, 23960, 23961, 23962, 23963, 23964, 23965, 23966, 23967, 23968, 23969, 23970, 23971, 23972, 23973, 23974, 23975, 23976, 23977, 23978, 23979, 23980, 23981, 23982, 23983, 23984, 23985, 23986, 23987, 23988, 23989, 23990, 23991, 23992, 23993, 23994, 23995, 23996, 23997, 23998, 23999]


# ============================================================================
# DOORS & GATES
# ============================================================================

class DoorsAndGates(ObjectCategory):
    """Door and gate object IDs."""
    
    # Generic doors (closed)
    DOOR_CLOSED = [1516, 1519, 1530, 1531, 1533, 1534, 3014, 3015, 3017, 3018, 3019, 3020, 11712, 11714, 11716, 11718]
    
    # Generic doors (open)
    DOOR_OPEN = [1517, 1520, 1531, 1532, 1534, 1535, 3014, 3016, 3017, 3019, 3020, 3021, 11713, 11715, 11717, 11719]
    
    # Gates (closed)
    GATE_CLOSED = [1551, 1553, 2514, 2515, 9470, 9472]
    
    # Gates (open)
    GATE_OPEN = [1552, 1554, 2514, 2516, 9471, 9473]


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
    }
    
    for category_name, category_cls in categories.items():
        if obj_id in category_cls.all():
            return category_name
    
    return None


def find_object_name(obj_id: int) -> Optional[str]:
    """
    Find the specific name of an object by its ID.
    
    Args:
        obj_id: Object ID to search for
        
    Returns:
        Object name (e.g., "IRON", "BOOTHS") or None if not found
    """
    categories = [BankObjects, OreRocks, Trees, FishingSpots, UtilityObjects, DoorsAndGates]
    
    for category in categories:
        name = category.find_by_id(obj_id)
        if name:
            return name
    
    return None
