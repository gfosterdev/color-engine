"""
NPC ID references for Old School RuneScape.

This module provides a centralized registry of all in-game NPC IDs used by the bot.
NPC IDs are organized by category for easy lookup and maintenance.

Source: RuneLite NpcID.java
https://github.com/runelite/runelite/blob/master/runelite-api/src/main/java/net/runelite/api/NpcID.java

Usage:
    from config.npcs import Bankers, Guards, FishingSpots
    
    banker_ids = Bankers.all()
    guard_ids = Guards.GUARD
"""

from typing import List, Optional


class NPCCategory:
    """Base class for NPC categories with helper methods."""
    
    @classmethod
    def all(cls) -> List[int]:
        """Return all NPC IDs in this category."""
        all_ids = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, list):
                    all_ids.extend(attr_value)
        return all_ids
    
    @classmethod
    def find_by_id(cls, npc_id: int) -> Optional[str]:
        """Find the name of an NPC by its ID."""
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, list) and npc_id in attr_value:
                    return attr_name
        return None


# ============================================================================
# BANKERS
# ============================================================================

class Bankers(NPCCategory):
    """Banker NPC IDs."""
    
    # Generic bankers
    BANKER = [44, 45, 166, 494, 495, 496, 497, 498, 499, 553, 1036, 1360, 1702, 2163, 2164, 2354, 2355, 2568, 2569, 2570, 3046, 3198, 3199, 5257, 5258, 5259, 5260, 5488, 5489, 5777, 5901, 6200, 6362, 6532, 6533, 6534, 6535, 7049, 7050, 7605, 8948, 9710, 14923, 14924]
    
    # Specialized bankers
    BANK_TUTOR = [4907]
    GHOST_BANKER = [4519]


# ============================================================================
# SHOPS & MERCHANTS
# ============================================================================

class Merchants(NPCCategory):
    """Shop keeper and merchant NPC IDs."""
    
    # Generic shop keepers
    SHOP_KEEPER = [520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 1301, 2820, 3166, 3167]
    SHOP_ASSISTANT = [534, 2820]
    
    # General stores
    GENERAL_STORE_OWNER = [519]


# ============================================================================
# FISHING SPOTS
# ============================================================================

class FishingSpots(NPCCategory):
    """Fishing spot NPC IDs."""
    
    # Net/Bait fishing spots
    FISHING_SPOT_NET_BAIT = [1518, 1521, 1522, 1523, 1524, 1525, 1528, 3417, 3418, 3419]
    
    # Lure/Bait fishing spots
    FISHING_SPOT_LURE_BAIT = [1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517]
    
    # Cage/Harpoon fishing spots
    FISHING_SPOT_CAGE_HARPOON = [1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1528]
    
    # Rod fishing spots
    FISHING_SPOT_ROD = [1526, 1527, 1544, 3417, 3418, 3419, 3657, 4316, 4476, 5820, 5821, 7155, 7459, 7460, 7467, 7468, 7469, 7470]
    
    # Special fishing spots
    FISHING_SPOT_MONKFISH = [4316]
    FISHING_SPOT_KARAMBWAN = [4705]
    FISHING_SPOT_ANGLERFISH = [6825]
    FISHING_SPOT_SACRED_EEL = [6488, 6489]
    FISHING_SPOT_INFERNAL_EEL = [7495, 7496]


# ============================================================================
# GUARDS & COMBAT
# ============================================================================

class Guards(NPCCategory):
    """Guard and city protection NPC IDs."""
    
    # Generic guards
    GUARD = [9, 32, 206, 297, 298, 299, 368, 516, 812, 1010, 1011, 1012, 1013, 1152, 1153, 1154, 2699, 2700, 3010, 3231, 3232, 3233, 3241, 3242, 5919, 5920, 7233, 7234]
    
    # Specific guard types
    PALACE_GUARD = [4367, 4368]
    GNOME_GUARD = [160, 161, 166, 2249]


# ============================================================================
# COMBAT - LOW LEVEL
# ============================================================================

class LowLevelMonsters(NPCCategory):
    """Low level combat monster NPC IDs (level 1-50)."""
    
    # Chickens
    CHICKEN = [1017, 2639, 2640, 2641]
    ROOSTER = [1017, 2693, 2694]
    
    # Cows
    COW = [81, 397, 955, 1766, 1767, 1768, 2310, 3309, 3311]
    COW_CALF = [1766, 1767, 1768]
    
    # Goblins
    GOBLIN = [4279, 4280, 4281, 4282, 4283, 4284, 4285, 4286, 4287, 4288, 4289, 4290, 4291, 4292, 4293, 4294, 4295, 4296, 4297]
    
    # Rats
    RAT = [2854, 2855, 4397, 4398, 4399, 5198, 5199, 5200, 5201, 5202, 5203, 5204]
    GIANT_RAT = [2856, 2857, 2858, 2859, 2860]
    
    # Spiders
    SPIDER = [59, 60, 61, 62, 63, 1009]
    GIANT_SPIDER = [59, 60, 61, 62, 63]
    
    # Scorpions
    SCORPION = [107, 108, 109, 110, 111, 112, 113, 114]
    
    # Imps
    IMP = [708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724]
    
    # Minotaurs
    MINOTAUR = [3404, 3405, 3406, 3407, 3408]
    
    # Rock crabs
    ROCK_CRAB = [1265, 1266, 1267, 1268, 1269]
    SAND_CRAB = [1265]
    AMMONITE_CRAB = [7796, 7797, 7798, 7799, 7800]


# ============================================================================
# COMBAT - MID LEVEL
# ============================================================================

class MidLevelMonsters(NPCCategory):
    """Mid level combat monster NPC IDs (level 50-100)."""
    
    # Hill giants
    HILL_GIANT = [2098, 2099, 2100, 2101, 2102, 4686, 4687]
    
    # Fire giants
    FIRE_GIANT = [2075, 2076, 2077, 2078, 2079]
    
    # Moss giants
    MOSS_GIANT = [2039, 2040, 2041, 2042, 4530, 4531]
    
    # Ice giants
    ICE_GIANT = [2084, 2085, 2086, 2087]
    
    # Lesser demons
    LESSER_DEMON = [82, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443]
    
    # Greater demons
    GREATER_DEMON = [82, 83, 84, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 3133, 3134, 3135, 3136]
    
    # Black demons
    BLACK_DEMON = [84, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 7243, 7244, 7245, 7246]
    
    # Hellhounds
    HELLHOUND = [49, 50, 51, 6369, 7848]
    
    # Ankous
    ANKOU = [2514, 2515, 2516]
    
    # Abyssal demons
    ABYSSAL_DEMON = [415, 7241, 7242]


# ============================================================================
# COMBAT - HIGH LEVEL
# ============================================================================

class HighLevelMonsters(NPCCategory):
    """High level combat monster NPC IDs (level 100+)."""
    
    # Dragons
    GREEN_DRAGON = [941, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4684]
    BLUE_DRAGON = [55, 4681, 4682, 4683, 4684, 4685]
    RED_DRAGON = [53, 4669, 4670, 4671, 4672, 4673, 4674, 4675, 4676]
    BLACK_DRAGON = [54, 4673, 4674, 4675, 4676]
    BRUTAL_BLACK_DRAGON = [8616, 8617]
    
    # Metal dragons
    BRONZE_DRAGON = [1590, 1591, 1592, 4655, 4656]
    IRON_DRAGON = [1591, 1592, 4655, 4656, 4657, 4658]
    STEEL_DRAGON = [1592, 4656, 4657, 4658, 4659, 4660]
    MITHRIL_DRAGON = [5363, 5364, 5365]
    ADAMANT_DRAGON = [8090, 8091]
    RUNE_DRAGON = [8031, 8032]
    
    # Demons
    ABYSSAL_DEMON = [415, 7241, 7242]
    DEMONIC_GORILLA = [7144, 7145, 7146, 7147, 7148, 7149]
    
    # Slayer monsters
    DARK_BEAST = [2783, 2784, 2785]
    SMOKE_DEVIL = [498, 499, 7406]
    CAVE_KRAKEN = [493, 494, 496]
    KRAKEN = [496]


# ============================================================================
# SLAYER MONSTERS
# ============================================================================

class SlayerMonsters(NPCCategory):
    """Slayer-specific monster NPC IDs."""
    
    # Low level slayer
    CRAWLING_HAND = [448, 449, 450, 451]
    CAVE_BUG = [1832, 1833, 1834, 5750]
    CAVE_CRAWLER = [1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607]
    BANSHEE = [1612, 1613, 6369]
    CAVE_SLIME = [1831]
    ROCKSLUG = [1622, 1623, 1624, 4363]
    COCKATRICE = [1620, 1621, 4227]
    PYREFIEND = [1633, 1634, 1635, 1636]
    BASILISK = [1616, 1617, 6369]
    INFERNAL_MAGE = [1643, 1644, 1645, 1646]
    BLOODVELD = [1618, 1619, 6369, 6369]
    
    # Mid level slayer
    JELLY = [1637, 1638, 1639]
    TUROTH = [1626, 1627, 1628, 1629, 1630, 1631, 1632]
    KURASK = [1608, 1609, 4227]
    GARGOYLE = [1610, 1611, 4227]
    NECHRYAEL = [1613, 1614, 1615, 7278, 7279]
    ABYSSAL_DEMON = [415, 7241, 7242]
    
    # High level slayer
    CAVE_KRAKEN = [493, 494, 496]
    KRAKEN = [496]
    SMOKE_DEVIL = [498, 499, 7406]
    CERBERUS = [5862, 5863, 5866]
    THERMONUCLEAR_SMOKE_DEVIL = [7406]
    DARK_BEAST = [2783, 2784, 2785]
    
    # Superior slayers
    CRUSHING_HAND = [7388]
    CHASM_CRAWLER = [7389]
    SCREAMING_BANSHEE = [7390]
    GIANT_ROCKSLUG = [7392]
    COCKATHRICE = [7393]
    FLAMING_PYRELORD = [7394]
    MONSTROUS_BASILISK = [7395]
    MALEVOLENT_MAGE = [7396]
    INSATIABLE_BLOODVELD = [7397]
    VITREOUS_JELLY = [7399]
    CAVE_ABOMINATION = [7401]
    ABHORRENT_SPECTRE = [7402]
    REPUGNANT_SPECTRE = [7403]
    CHOKE_DEVIL = [7404]
    KING_KURASK = [7405]
    MARBLE_GARGOYLE = [7408]
    NECHRYARCH = [7411]
    GREATER_ABYSSAL_DEMON = [7410]
    NIGHT_BEAST = [7409]


# ============================================================================
# BOSSES
# ============================================================================

class Bosses(NPCCategory):
    """Boss NPC IDs."""
    
    # God Wars Dungeon
    GENERAL_GRAARDOR = [6260, 6261, 6263, 6265]
    KRIL_TSUTSAROTH = [6203, 6204, 6206, 6208]
    COMMANDER_ZILYANA = [6247, 6248, 6250, 6252]
    KREEARRA = [6222, 6223, 6225, 6227]
    
    # Wilderness bosses
    CALLISTO = [6609]
    VENENATIS = [6610]
    VETION = [6611, 6612]
    SCORPIA = [6615]
    CRAZY_ARCHAEOLOGIST = [6618]
    CHAOS_FANATIC = [6619]
    
    # Slayer bosses
    KRAKEN = [496]
    THERMONUCLEAR_SMOKE_DEVIL = [7406]
    CERBERUS = [5862, 5863, 5866]
    ABYSSAL_SIRE = [5886, 5887, 5888, 5889, 5890, 5891]
    
    # Raid bosses
    GREAT_OLM = [7554, 7555]
    VERZIK_VITUR = [8370, 8371, 8372, 8373, 8374, 8375]
    
    # Demi-bosses
    DEMONIC_GORILLA = [7144, 7145, 7146, 7147, 7148, 7149]
    VORKATH = [8059, 8060, 8061]
    ZULRAH = [2042, 2043, 2044]
    
    # Other bosses
    CORPOREAL_BEAST = [319]
    KALPHITE_QUEEN = [963, 965]
    KING_BLACK_DRAGON = [50, 2642, 6636]
    DAGANNOTH_PRIME = [2881]
    DAGANNOTH_REX = [2883]
    DAGANNOTH_SUPREME = [2882]


# ============================================================================
# SKILLING NPCS
# ============================================================================

class SkillingNPCs(NPCCategory):
    """Skilling-related NPC IDs."""
    
    # Tree spirits (woodcutting randoms)
    TREE_SPIRIT = [437, 438, 439, 440, 441, 442, 443]
    
    # Rock golems (mining randoms)
    ROCK_GOLEM = [413, 414, 415, 416, 417, 418, 419]
    
    # Fishing spots covered in FishingSpots class
    
    # Farmers
    FARMER = [3257, 3258, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3267, 3268, 3269, 3270, 3271, 3272]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_npc_category(npc_id: int) -> Optional[str]:
    """
    Find which category an NPC ID belongs to.
    
    Args:
        npc_id: NPC ID to search for
        
    Returns:
        Category name (e.g., "Bankers", "Guards") or None if not found
    """
    categories = {
        "Bankers": Bankers,
        "Merchants": Merchants,
        "FishingSpots": FishingSpots,
        "Guards": Guards,
        "LowLevelMonsters": LowLevelMonsters,
        "MidLevelMonsters": MidLevelMonsters,
        "HighLevelMonsters": HighLevelMonsters,
        "SlayerMonsters": SlayerMonsters,
        "Bosses": Bosses,
        "SkillingNPCs": SkillingNPCs,
    }
    
    for category_name, category_cls in categories.items():
        if npc_id in category_cls.all():
            return category_name
    
    return None


def find_npc_name(npc_id: int) -> Optional[str]:
    """
    Find the specific name of an NPC by its ID.
    
    Args:
        npc_id: NPC ID to search for
        
    Returns:
        NPC name (e.g., "BANKER", "GUARD") or None if not found
    """
    categories = [
        Bankers, Merchants, FishingSpots, Guards,
        LowLevelMonsters, MidLevelMonsters, HighLevelMonsters,
        SlayerMonsters, Bosses, SkillingNPCs
    ]
    
    for category in categories:
        name = category.find_by_id(npc_id)
        if name:
            return name
    
    return None
