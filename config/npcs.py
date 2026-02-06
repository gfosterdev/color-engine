"""
NPC ID references for Old School RuneScape.

This module provides a centralized registry of all in-game NPC IDs used by the bot.
NPC IDs are organized by category for easy lookup and maintenance.

Source: RuneLite NpcID.java
https://github.com/runelite/runelite/blob/master/runelite-api/src/main/java/net/runelite/api/NpcID.java

Usage:
    from config.npcs import Bankers, Guards, FishingSpots
    
    # Access NPC
    banker = Bankers.BANKER
    banker_ids = banker.ids  # List[int]
    banker_name = banker.name  # str
    
    # Get all NPCs in category
    all_bankers = Bankers.all()  # Returns List[NPC]
    all_banker_ids = Bankers.all_ids()  # Returns List[int]
    
    # NPC supports list-like operations
    if npc_id in Bankers.BANKER:  # Uses __contains__
        print(f"Found {Bankers.BANKER.name}")
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class NPC:
    """Represents an NPC type with all its ID variations."""
    name: str
    ids: List[int]
    category: str
    description: str = ""
    combat_level: Optional[int] = None
    
    def __contains__(self, item: int) -> bool:
        """Allow 'id in NPC' syntax."""
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


class NPCCategory:
    """Base class for NPC categories with helper methods."""
    
    @classmethod
    def all(cls) -> List[NPC]:
        """Return all NPCs in this category."""
        npcs = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, NPC):
                    npcs.append(attr_value)
        return npcs
    
    @classmethod
    def all_ids(cls) -> List[int]:
        """Return all NPC IDs in this category (flattened)."""
        all_ids = []
        for npc in cls.all():
            all_ids.extend(npc.ids)
        return all_ids
    
    @classmethod
    def find_by_id(cls, npc_id: int) -> Optional[NPC]:
        """Find an NPC by any of its ID variations."""
        for npc in cls.all():
            if npc_id in npc.ids:
                return npc
        return None


# ============================================================================
# BANKERS
# ============================================================================

class Bankers(NPCCategory):
    """Banker NPC IDs."""
    
    # Generic bankers
    BANKER = NPC(
        name="Banker",
        ids=[44, 45, 166, 494, 495, 496, 497, 498, 499, 553, 1036, 1360, 1702, 2163, 2164, 2354, 2355, 2568, 2569, 2570, 3046, 3198, 3199, 5257, 5258, 5259, 5260, 5488, 5489, 5777, 5901, 6200, 6362, 6532, 6533, 6534, 6535, 7049, 7050, 7605, 8948, 9710, 14923, 14924],
        category="banker",
        description="Generic bankers found at banks"
    )
    
    # Specialized bankers
    BANK_TUTOR = NPC("Bank tutor", [4907], "banker", "Tutorial island banker")
    GHOST_BANKER = NPC("Ghost banker", [4519], "banker", "Ectofuntus ghost banker")


# ============================================================================
# SHOPS & MERCHANTS
# ============================================================================

class Merchants(NPCCategory):
    """Shop keeper and merchant NPC IDs."""
    
    # Generic shop keepers
    SHOP_KEEPER = NPC(
        name="Shop keeper",
        ids=[520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 1301, 2820, 3166, 3167],
        category="merchant"
    )
    SHOP_ASSISTANT = NPC("Shop assistant", [534, 2820], "merchant")
    
    # General stores
    GENERAL_STORE_OWNER = NPC("General store owner", [519], "merchant")


# ============================================================================
# FISHING SPOTS
# ============================================================================

class FishingSpots(NPCCategory):
    """Fishing spot NPC IDs."""
    
    # Net/Bait fishing spots
    FISHING_SPOT_NET_BAIT = NPC(
        name="Fishing spot",
        ids=[1518, 1521, 1522, 1523, 1524, 1525, 1528, 3417, 3418, 3419],
        category="fishing",
        description="Net and bait fishing spots"
    )
    
    # Lure/Bait fishing spots
    FISHING_SPOT_LURE_BAIT = NPC(
        name="Fishing spot",
        ids=[1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517],
        category="fishing",
        description="Lure and bait fishing spots"
    )
    
    # Cage/Harpoon fishing spots
    FISHING_SPOT_CAGE_HARPOON = NPC(
        name="Fishing spot",
        ids=[1518, 1519, 1520, 1521, 1522, 1523, 1524, 1525, 1528],
        category="fishing",
        description="Cage and harpoon fishing spots"
    )
    
    # Rod fishing spots
    FISHING_SPOT_ROD = NPC(
        name="Fishing spot",
        ids=[1526, 1527, 1544, 3417, 3418, 3419, 3657, 4316, 4476, 5820, 5821, 7155, 7459, 7460, 7467, 7468, 7469, 7470],
        category="fishing",
        description="Rod fishing spots"
    )
    
    # Special fishing spots
    FISHING_SPOT_MONKFISH = NPC("Fishing spot", [4316], "fishing", "Monkfish fishing spot")
    FISHING_SPOT_KARAMBWAN = NPC("Fishing spot", [4705], "fishing", "Karambwan fishing spot")
    FISHING_SPOT_ANGLERFISH = NPC("Fishing spot", [6825], "fishing", "Anglerfish fishing spot")
    FISHING_SPOT_SACRED_EEL = NPC("Fishing spot", [6488, 6489], "fishing", "Sacred eel fishing spot")
    FISHING_SPOT_INFERNAL_EEL = NPC("Fishing spot", [7495, 7496], "fishing", "Infernal eel fishing spot")


# ============================================================================
# GUARDS & COMBAT
# ============================================================================

class Guards(NPCCategory):
    """Guard and city protection NPC IDs."""
    
    # Generic guards
    GUARD = NPC(
        name="Guard",
        ids=[9, 32, 206, 297, 298, 299, 368, 516, 812, 1010, 1011, 1012, 1013, 1152, 1153, 1154, 2699, 2700, 3010, 3231, 3232, 3233, 3241, 3242, 5919, 5920, 7233, 7234],
        category="guard",
        combat_level=21
    )
    
    # Specific guard types
    PALACE_GUARD = NPC("Palace guard", [4367, 4368], "guard", combat_level=42)
    GNOME_GUARD = NPC("Gnome guard", [160, 161, 166, 2249], "guard", combat_level=44)


# ============================================================================
# COMBAT - LOW LEVEL
# ============================================================================

class LowLevelMonsters(NPCCategory):
    """Low level combat monster NPC IDs (level 1-50)."""
    
    # Chickens
    CHICKEN = NPC("Chicken", [1017, 2639, 2640, 2641], "monster_low", "Common low-level monster", combat_level=1)
    ROOSTER = NPC("Rooster", [1017, 2693, 2694], "monster_low", "Male chicken variant", combat_level=1)
    
    # Cows
    COW = NPC("Cow", [2790, 2791, 2792, 2793, 2794, 2795, 2801], "monster_low", "Common low-level monster", combat_level=2)
    COW_CALF = NPC("Cow calf", [2792, 2794, 2801], "monster_low", "Young cow", combat_level=2)
    
    # Goblins
    GOBLIN = NPC("Goblin", [4279, 4280, 4281, 4282, 4283, 4284, 4285, 4286, 4287, 4288, 4289, 4290, 4291, 4292, 4293, 4294, 4295, 4296, 4297], "monster_low", "Common goblin variants", combat_level=5)
    
    # Rats
    RAT = NPC("Rat", [2854, 2855, 4397, 4398, 4399, 5198, 5199, 5200, 5201, 5202, 5203, 5204], "monster_low", "Small rat", combat_level=1)
    GIANT_RAT = NPC("Giant rat", [2856, 2857, 2858, 2859, 2860], "monster_low", "Larger rat variant", combat_level=6)
    
    # Spiders
    SPIDER = NPC("Spider", [59, 60, 61, 62, 63, 1009], "monster_low", "Small spider", combat_level=2)
    GIANT_SPIDER = NPC("Giant spider", [59, 60, 61, 62, 63], "monster_low", "Larger spider variant", combat_level=5)
    
    # Scorpions
    SCORPION = NPC("Scorpion", [107, 108, 109, 110, 111, 112, 113, 114], "monster_low", "Desert scorpion", combat_level=14)
    
    # Imps
    IMP = NPC("Imp", [708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724], "monster_low", "Small demon creature", combat_level=7)
    
    # Minotaurs
    MINOTAUR = NPC("Minotaur", [3404, 3405, 3406, 3407, 3408], "monster_low", "Bull-headed monster", combat_level=12)
    
    # Rock crabs
    ROCK_CRAB = NPC("Rock crab", [1265, 1266, 1267, 1268, 1269], "monster_low", "AFK training monster", combat_level=13)
    SAND_CRAB = NPC("Sand crab", [1265], "monster_low", "Beach training monster", combat_level=15)
    AMMONITE_CRAB = NPC("Ammonite crab", [7796, 7797, 7798, 7799, 7800], "monster_low", "Fossil Island training monster", combat_level=25)


# ============================================================================
# COMBAT - MID LEVEL
# ============================================================================

class MidLevelMonsters(NPCCategory):
    """Mid level combat monster NPC IDs (level 50-100)."""
    
    # Hill giants
    HILL_GIANT = NPC("Hill giant", [2098, 2099, 2100, 2101, 2102, 4686, 4687], "monster_mid", "Popular training monster", combat_level=28)
    
    # Fire giants
    FIRE_GIANT = NPC("Fire giant", [2075, 2076, 2077, 2078, 2079], "monster_mid", "High HP training monster", combat_level=86)
    
    # Moss giants
    MOSS_GIANT = NPC("Moss giant", [2039, 2040, 2041, 2042, 4530, 4531], "monster_mid", "Green giant variant", combat_level=42)
    
    # Ice giants
    ICE_GIANT = NPC("Ice giant", [2084, 2085, 2086, 2087], "monster_mid", "Cold region giant", combat_level=53)
    
    # Lesser demons
    LESSER_DEMON = NPC("Lesser demon", [82, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443], "monster_mid", "Weaker demon type", combat_level=82)
    
    # Greater demons
    GREATER_DEMON = NPC("Greater demon", [82, 83, 84, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 3133, 3134, 3135, 3136], "monster_mid", "Common demon type", combat_level=92)
    
    # Black demons
    BLACK_DEMON = NPC("Black demon", [84, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 7243, 7244, 7245, 7246], "monster_mid", "Powerful demon variant", combat_level=172)
    
    # Hellhounds
    HELLHOUND = NPC("Hellhound", [49, 50, 51, 6369, 7848], "monster_mid", "Demonic hound", combat_level=122)
    
    # Ankous
    ANKOU = NPC("Ankou", [2514, 2515, 2516], "monster_mid", "Undead skeletal monster", combat_level=75)
    
    # Abyssal demons
    ABYSSAL_DEMON = NPC("Abyssal demon", [415, 7241, 7242], "monster_mid", "Slayer monster with whip drop", combat_level=124)


# ============================================================================
# COMBAT - HIGH LEVEL
# ============================================================================

class HighLevelMonsters(NPCCategory):
    """High level combat monster NPC IDs (level 100+)."""
    
    # Dragons
    GREEN_DRAGON = NPC("Green dragon", [941, 4677, 4678, 4679, 4680, 4681, 4682, 4683, 4684], "monster_high", "Wilderness dragon", combat_level=79)
    BLUE_DRAGON = NPC("Blue dragon", [55, 4681, 4682, 4683, 4684, 4685], "monster_high", "Mid-tier dragon", combat_level=111)
    RED_DRAGON = NPC("Red dragon", [53, 4669, 4670, 4671, 4672, 4673, 4674, 4675, 4676], "monster_high", "High-tier dragon", combat_level=152)
    BLACK_DRAGON = NPC("Black dragon", [54, 4673, 4674, 4675, 4676], "monster_high", "Powerful dragon variant", combat_level=227)
    BRUTAL_BLACK_DRAGON = NPC("Brutal black dragon", [8616, 8617], "monster_high", "Elite dragon variant", combat_level=318)
    
    # Metal dragons
    BRONZE_DRAGON = NPC("Bronze dragon", [1590, 1591, 1592, 4655, 4656], "monster_high", "Weakest metal dragon", combat_level=131)
    IRON_DRAGON = NPC("Iron dragon", [1591, 1592, 4655, 4656, 4657, 4658], "monster_high", "Mid-tier metal dragon", combat_level=189)
    STEEL_DRAGON = NPC("Steel dragon", [1592, 4656, 4657, 4658, 4659, 4660], "monster_high", "Strong metal dragon", combat_level=246)
    MITHRIL_DRAGON = NPC("Mithril dragon", [5363, 5364, 5365], "monster_high", "Powerful metal dragon", combat_level=304)
    ADAMANT_DRAGON = NPC("Adamant dragon", [8090, 8091], "monster_high", "Very strong metal dragon", combat_level=338)
    RUNE_DRAGON = NPC("Rune dragon", [8031, 8032], "monster_high", "Strongest metal dragon", combat_level=380)
    
    # Demons
    ABYSSAL_DEMON = NPC("Abyssal demon", [415, 7241, 7242], "monster_high", "Popular slayer monster", combat_level=124)
    DEMONIC_GORILLA = NPC("Demonic gorilla", [7144, 7145, 7146, 7147, 7148, 7149], "monster_high", "MM2 post-quest monster", combat_level=275)
    
    # Slayer monsters
    DARK_BEAST = NPC("Dark beast", [2783, 2784, 2785], "monster_high", "High level slayer monster", combat_level=182)
    SMOKE_DEVIL = NPC("Smoke devil", [498, 499, 7406], "monster_high", "Slayer monster in smoke dungeon", combat_level=160)
    CAVE_KRAKEN = NPC("Cave kraken", [493, 494, 496], "monster_high", "Underwater slayer monster", combat_level=127)
    KRAKEN = NPC("Kraken", [496], "monster_high", "Kraken boss variant", combat_level=291)


# ============================================================================
# SLAYER MONSTERS
# ============================================================================

class SlayerMonsters(NPCCategory):
    """Slayer-specific monster NPC IDs."""
    
    # Low level slayer
    CRAWLING_HAND = NPC("Crawling hand", [448, 449, 450, 451], "slayer", "Level 5 slayer required", combat_level=7)
    CAVE_BUG = NPC("Cave bug", [1832, 1833, 1834, 5750], "slayer", "Level 7 slayer required", combat_level=6)
    CAVE_CRAWLER = NPC("Cave crawler", [1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607], "slayer", "Level 10 slayer required", combat_level=53)
    BANSHEE = NPC("Banshee", [1612, 1613, 6369], "slayer", "Level 15 slayer required", combat_level=23)
    CAVE_SLIME = NPC("Cave slime", [1831], "slayer", "Level 17 slayer required", combat_level=23)
    ROCKSLUG = NPC("Rockslug", [1622, 1623, 1624, 4363], "slayer", "Level 20 slayer required", combat_level=29)
    COCKATRICE = NPC("Cockatrice", [1620, 1621, 4227], "slayer", "Level 25 slayer required", combat_level=37)
    PYREFIEND = NPC("Pyrefiend", [1633, 1634, 1635, 1636], "slayer", "Level 30 slayer required", combat_level=43)
    BASILISK = NPC("Basilisk", [1616, 1617, 6369], "slayer", "Level 40 slayer required", combat_level=61)
    INFERNAL_MAGE = NPC("Infernal mage", [1643, 1644, 1645, 1646], "slayer", "Level 45 slayer required", combat_level=66)
    BLOODVELD = NPC("Bloodveld", [1618, 1619, 6369, 6369], "slayer", "Level 50 slayer required", combat_level=76)
    
    # Mid level slayer
    JELLY = NPC("Jelly", [1637, 1638, 1639], "slayer", "Level 52 slayer required", combat_level=78)
    TUROTH = NPC("Turoth", [1626, 1627, 1628, 1629, 1630, 1631, 1632], "slayer", "Level 55 slayer required", combat_level=83)
    KURASK = NPC("Kurask", [1608, 1609, 4227], "slayer", "Level 70 slayer required", combat_level=106)
    GARGOYLE = NPC("Gargoyle", [412], "slayer", "Level 75 slayer required", combat_level=111)
    NECHRYAEL = NPC("Nechryael", [1613, 1614, 1615, 7278, 7279], "slayer", "Level 80 slayer required", combat_level=115)
    ABYSSAL_DEMON = NPC("Abyssal demon", [415, 7241, 7242], "slayer", "Level 85 slayer required", combat_level=124)
    
    # High level slayer
    CAVE_KRAKEN = NPC("Cave kraken", [493, 494, 496], "slayer", "Level 87 slayer required", combat_level=127)
    KRAKEN = NPC("Kraken", [496], "slayer", "Kraken boss variant", combat_level=291)
    SMOKE_DEVIL = NPC("Smoke devil", [498, 499, 7406], "slayer", "Level 93 slayer required", combat_level=160)
    CERBERUS = NPC("Cerberus", [5862, 5863, 5866], "slayer", "Level 91 slayer boss", combat_level=318)
    THERMONUCLEAR_SMOKE_DEVIL = NPC("Thermonuclear smoke devil", [7406], "slayer", "Smoke devil boss", combat_level=301)
    DARK_BEAST = NPC("Dark beast", [2783, 2784, 2785], "slayer", "Level 90 slayer required", combat_level=182)
    
    # Superior slayers
    CRUSHING_HAND = NPC("Crushing hand", [7388], "slayer", "Superior crawling hand", combat_level=32)
    CHASM_CRAWLER = NPC("Chasm crawler", [7389], "slayer", "Superior cave crawler", combat_level=82)
    SCREAMING_BANSHEE = NPC("Screaming banshee", [7390], "slayer", "Superior banshee", combat_level=95)
    GIANT_ROCKSLUG = NPC("Giant rockslug", [7392], "slayer", "Superior rockslug", combat_level=67)
    COCKATHRICE = NPC("Cockathrice", [7393], "slayer", "Superior cockatrice", combat_level=89)
    FLAMING_PYRELORD = NPC("Flaming pyrelord", [7394], "slayer", "Superior pyrefiend", combat_level=104)
    MONSTROUS_BASILISK = NPC("Monstrous basilisk", [7395], "slayer", "Superior basilisk", combat_level=135)
    MALEVOLENT_MAGE = NPC("Malevolent mage", [7396], "slayer", "Superior infernal mage", combat_level=104)
    INSATIABLE_BLOODVELD = NPC("Insatiable bloodveld", [7397], "slayer", "Superior bloodveld", combat_level=120)
    VITREOUS_JELLY = NPC("Vitreous jelly", [7399], "slayer", "Superior jelly", combat_level=140)
    CAVE_ABOMINATION = NPC("Cave abomination", [7401], "slayer", "Superior cave horror", combat_level=150)
    ABHORRENT_SPECTRE = NPC("Abhorrent spectre", [7402], "slayer", "Superior aberrant spectre", combat_level=142)
    REPUGNANT_SPECTRE = NPC("Repugnant spectre", [7403], "slayer", "Superior deviant spectre", combat_level=142)
    CHOKE_DEVIL = NPC("Choke devil", [7404], "slayer", "Superior dust devil", combat_level=150)
    KING_KURASK = NPC("King kurask", [7405], "slayer", "Superior kurask", combat_level=180)
    MARBLE_GARGOYLE = NPC("Marble gargoyle", [7408], "slayer", "Superior gargoyle", combat_level=182)
    NECHRYARCH = NPC("Nechryarch", [7411], "slayer", "Superior nechryael", combat_level=200)
    GREATER_ABYSSAL_DEMON = NPC("Greater abyssal demon", [7410], "slayer", "Superior abyssal demon", combat_level=342)
    NIGHT_BEAST = NPC("Night beast", [7409], "slayer", "Superior dark beast", combat_level=310)


# ============================================================================
# BOSSES
# ============================================================================

class Bosses(NPCCategory):
    """Boss NPC IDs."""
    
    # God Wars Dungeon
    GENERAL_GRAARDOR = NPC("General Graardor", [6260, 6261, 6263, 6265], "boss", "Bandos GWD boss", combat_level=624)
    KRIL_TSUTSAROTH = NPC("K'ril Tsutsaroth", [6203, 6204, 6206, 6208], "boss", "Zamorak GWD boss", combat_level=650)
    COMMANDER_ZILYANA = NPC("Commander Zilyana", [6247, 6248, 6250, 6252], "boss", "Saradomin GWD boss", combat_level=596)
    KREEARRA = NPC("Kree'arra", [6222, 6223, 6225, 6227], "boss", "Armadyl GWD boss", combat_level=580)
    
    # Wilderness bosses
    CALLISTO = NPC("Callisto", [6609], "boss", "Wilderness bear boss", combat_level=470)
    VENENATIS = NPC("Venenatis", [6610], "boss", "Wilderness spider boss", combat_level=464)
    VETION = NPC("Vet'ion", [6611, 6612], "boss", "Wilderness skeleton boss", combat_level=454)
    SCORPIA = NPC("Scorpia", [6615], "boss", "Wilderness scorpion boss", combat_level=225)
    CRAZY_ARCHAEOLOGIST = NPC("Crazy archaeologist", [6618], "boss", "Wilderness demi-boss", combat_level=204)
    CHAOS_FANATIC = NPC("Chaos fanatic", [6619], "boss", "Wilderness demi-boss", combat_level=202)
    
    # Slayer bosses
    KRAKEN = NPC("Kraken", [496], "boss", "Level 87 slayer boss", combat_level=291)
    THERMONUCLEAR_SMOKE_DEVIL = NPC("Thermonuclear smoke devil", [7406], "boss", "Level 93 slayer boss", combat_level=301)
    CERBERUS = NPC("Cerberus", [5862, 5863, 5866], "boss", "Level 91 slayer boss", combat_level=318)
    ABYSSAL_SIRE = NPC("Abyssal sire", [5886, 5887, 5888, 5889, 5890, 5891], "boss", "Level 85 slayer boss", combat_level=350)
    
    # Raid bosses
    GREAT_OLM = NPC("Great Olm", [7554, 7555], "boss", "Chambers of Xeric final boss", combat_level=1043)
    VERZIK_VITUR = NPC("Verzik Vitur", [8370, 8371, 8372, 8373, 8374, 8375], "boss", "Theatre of Blood final boss", combat_level=1040)
    
    # Demi-bosses
    DEMONIC_GORILLA = NPC("Demonic gorilla", [7144, 7145, 7146, 7147, 7148, 7149], "boss", "MM2 end-game monster", combat_level=275)
    VORKATH = NPC("Vorkath", [8059, 8060, 8061], "boss", "Undead dragon boss", combat_level=732)
    ZULRAH = NPC("Zulrah", [2042, 2043, 2044], "boss", "Snake boss with rotations", combat_level=725)
    
    # Other bosses
    CORPOREAL_BEAST = NPC("Corporeal Beast", [319], "boss", "Spirit shield boss", combat_level=785)
    KALPHITE_QUEEN = NPC("Kalphite Queen", [963, 965], "boss", "Desert insect boss", combat_level=333)
    KING_BLACK_DRAGON = NPC("King Black Dragon", [50, 2642, 6636], "boss", "Three-headed dragon", combat_level=276)
    DAGANNOTH_PRIME = NPC("Dagannoth Prime", [2881], "boss", "Mage dagannoth king", combat_level=303)
    DAGANNOTH_REX = NPC("Dagannoth Rex", [2883], "boss", "Melee dagannoth king", combat_level=303)
    DAGANNOTH_SUPREME = NPC("Dagannoth Supreme", [2882], "boss", "Ranged dagannoth king", combat_level=303)


# ============================================================================
# SKILLING NPCS
# ============================================================================

class SkillingNPCs(NPCCategory):
    """Skilling-related NPC IDs."""
    
    # Tree spirits (woodcutting randoms)
    TREE_SPIRIT = NPC("Tree spirit", [437, 438, 439, 440, 441, 442, 443], "skilling", "Woodcutting random event", combat_level=159)
    
    # Rock golems (mining randoms)
    ROCK_GOLEM = NPC("Rock golem", [413, 414, 415, 416, 417, 418, 419], "skilling", "Mining random event", combat_level=159)
    
    # Fishing spots covered in FishingSpots class
    
    # Farmers
    FARMER = NPC("Farmer", [3257, 3258, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3267, 3268, 3269, 3270, 3271, 3272], "skilling", "Farming patch NPC")


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
        if npc_id in category_cls.all_ids():
            return category_name
    
    return None


def find_npc_name(npc_id: int) -> Optional[str]:
    """
    Find the display name of an NPC by its ID.
    
    Args:
        npc_id: NPC ID to search for
        
    Returns:
        NPC display name (e.g., "Banker", "Guard") or None if not found
    """
    categories = [
        Bankers, Merchants, FishingSpots, Guards,
        LowLevelMonsters, MidLevelMonsters, HighLevelMonsters,
        SlayerMonsters, Bosses, SkillingNPCs
    ]
    
    for category in categories:
        npc = category.find_by_id(npc_id)
        if npc:
            return npc.name
    
    return None


def find_npc(npc_id: int) -> Optional[NPC]:
    """
    Find an NPC object by its ID.
    
    Args:
        npc_id: NPC ID to search for
        
    Returns:
        NPC object or None if not found
    """
    categories = [
        Bankers, Merchants, FishingSpots, Guards,
        LowLevelMonsters, MidLevelMonsters, HighLevelMonsters,
        SlayerMonsters, Bosses, SkillingNPCs
    ]
    
    for category in categories:
        npc = category.find_by_id(npc_id)
        if npc:
            return npc
    
    return None
