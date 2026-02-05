"""
Item ID references for Old School RuneScape.

This module provides a centralized registry of all in-game item IDs used by the bot.
Item IDs are organized by category for easy lookup and maintenance.

Source: RuneLite ItemID.java
https://github.com/runelite/runelite/blob/master/runelite-api/src/main/java/net/runelite/api/ItemID.java

Usage:
    from config.items import Ores, Food, Potions
    
    # Access item ID
    iron_ore = Ores.IRON_ORE
    iron_ore_id = iron_ore.id
    iron_ore_name = iron_ore.name
    
    # Get all items in category
    all_ores = Ores.all()  # Returns List[Item]
    all_ore_ids = Ores.all_ids()  # Returns List[int]
    
    # Item works as int in comparisons
    if item_id == Ores.IRON_ORE:  # Uses __eq__ with id
        print(f"Found {Ores.IRON_ORE.name}")
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Item:
    """Represents an OSRS item with ID and display name."""
    id: int
    name: str
    
    def __int__(self) -> int:
        """Allow implicit conversion to int for backward compatibility."""
        return self.id
    
    def __eq__(self, other) -> bool:
        """Allow comparison with integers and other Items."""
        if isinstance(other, int):
            return self.id == other
        elif isinstance(other, Item):
            return self.id == other.id
        return False
    
    def __hash__(self) -> int:
        """Make Item hashable for use in sets/dicts."""
        return hash(self.id)


class ItemCategory:
    """Base class for item categories with helper methods."""
    
    @classmethod
    def all(cls) -> List[Item]:
        """Return all items in this category."""
        items = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, Item):
                    items.append(attr_value)
        return items
    
    @classmethod
    def all_ids(cls) -> List[int]:
        """Return all item IDs in this category."""
        return [item.id for item in cls.all()]
    
    @classmethod
    def find_by_id(cls, item_id: int) -> Optional[Item]:
        """Find an item by its ID."""
        for item in cls.all():
            if item.id == item_id:
                return item
        return None


# ============================================================================
# ORES & BARS
# ============================================================================

class Ores(ItemCategory):
    """Mining ore item IDs."""
    
    # Basic ores
    COPPER_ORE = Item(436, "Copper ore")
    TIN_ORE = Item(438, "Tin ore")
    IRON_ORE = Item(440, "Iron ore")
    COAL = Item(453, "Coal")
    
    # Clay
    CLAY = Item(434, "Clay")
    SOFT_CLAY = Item(1761, "Soft clay")
    
    # Precious metals
    SILVER_ORE = Item(442, "Silver ore")
    GOLD_ORE = Item(444, "Gold ore")
    
    # High-level ores
    MITHRIL_ORE = Item(447, "Mithril ore")
    ADAMANTITE_ORE = Item(449, "Adamantite ore")
    RUNITE_ORE = Item(451, "Runite ore")
    
    # Special ores
    SANDSTONE_1KG = Item(6971, "Sandstone (1kg)")
    SANDSTONE_2KG = Item(6973, "Sandstone (2kg)")
    SANDSTONE_5KG = Item(6975, "Sandstone (5kg)")
    SANDSTONE_10KG = Item(6977, "Sandstone (10kg)")
    GRANITE_500G = Item(6979, "Granite (500g)")
    GRANITE_2KG = Item(6981, "Granite (2kg)")
    GRANITE_5KG = Item(6983, "Granite (5kg)")
    AMETHYST = Item(21347, "Amethyst")
    
    # Gems from mining
    UNCUT_SAPPHIRE = Item(1623, "Uncut sapphire")
    UNCUT_EMERALD = Item(1621, "Uncut emerald")
    UNCUT_RUBY = Item(1619, "Uncut ruby")
    UNCUT_DIAMOND = Item(1617, "Uncut diamond")


class Bars(ItemCategory):
    """Smithing bar item IDs."""
    
    BRONZE_BAR = Item(2349, "Bronze bar")
    IRON_BAR = Item(2351, "Iron bar")
    STEEL_BAR = Item(2353, "Steel bar")
    SILVER_BAR = Item(2355, "Silver bar")
    GOLD_BAR = Item(2357, "Gold bar")
    MITHRIL_BAR = Item(2359, "Mithril bar")
    ADAMANTITE_BAR = Item(2361, "Adamantite bar")
    RUNITE_BAR = Item(2363, "Runite bar")


# ============================================================================
# LOGS & WOOD PRODUCTS
# ============================================================================

class Logs(ItemCategory):
    """Woodcutting log item IDs."""
    
    LOGS = Item(1511, "Logs")
    OAK_LOGS = Item(1521, "Oak logs")
    WILLOW_LOGS = Item(1519, "Willow logs")
    MAPLE_LOGS = Item(1517, "Maple logs")
    YEW_LOGS = Item(1515, "Yew logs")
    MAGIC_LOGS = Item(1513, "Magic logs")
    REDWOOD_LOGS = Item(19669, "Redwood logs")
    TEAK_LOGS = Item(6333, "Teak logs")
    MAHOGANY_LOGS = Item(6332, "Mahogany logs")


class Planks(ItemCategory):
    """Plank item IDs for construction."""
    
    PLANK = Item(960, "Plank")
    OAK_PLANK = Item(8778, "Oak plank")
    TEAK_PLANK = Item(8780, "Teak plank")
    MAHOGANY_PLANK = Item(8782, "Mahogany plank")


# ============================================================================
# FISH (RAW & COOKED)
# ============================================================================

class RawFish(ItemCategory):
    """Raw fish item IDs."""
    
    # Low level
    RAW_SHRIMPS = Item(317, "Raw shrimps")
    RAW_SARDINE = Item(327, "Raw sardine")
    RAW_HERRING = Item(345, "Raw herring")
    RAW_ANCHOVIES = Item(321, "Raw anchovies")
    RAW_MACKEREL = Item(353, "Raw mackerel")
    RAW_TROUT = Item(335, "Raw trout")
    RAW_COD = Item(341, "Raw cod")
    RAW_PIKE = Item(349, "Raw pike")
    RAW_SALMON = Item(331, "Raw salmon")
    
    # Mid level
    RAW_TUNA = Item(359, "Raw tuna")
    RAW_LOBSTER = Item(377, "Raw lobster")
    RAW_BASS = Item(363, "Raw bass")
    RAW_SWORDFISH = Item(371, "Raw swordfish")
    RAW_MONKFISH = Item(7944, "Raw monkfish")
    
    # High level
    RAW_SHARK = Item(383, "Raw shark")
    RAW_SEA_TURTLE = Item(395, "Raw sea turtle")
    RAW_MANTA_RAY = Item(389, "Raw manta ray")
    RAW_ANGLERFISH = Item(13439, "Raw anglerfish")
    
    # Special
    RAW_KARAMBWAN = Item(3142, "Raw karambwan")


class CookedFish(ItemCategory):
    """Cooked fish item IDs."""
    
    # Low level
    SHRIMPS = Item(315, "Shrimps")
    SARDINE = Item(325, "Sardine")
    HERRING = Item(347, "Herring")
    ANCHOVIES = Item(319, "Anchovies")
    MACKEREL = Item(355, "Mackerel")
    TROUT = Item(333, "Trout")
    COD = Item(339, "Cod")
    PIKE = Item(351, "Pike")
    SALMON = Item(329, "Salmon")
    
    # Mid level
    TUNA = Item(361, "Tuna")
    LOBSTER = Item(379, "Lobster")
    BASS = Item(365, "Bass")
    SWORDFISH = Item(373, "Swordfish")
    MONKFISH = Item(7946, "Monkfish")
    
    # High level
    SHARK = Item(385, "Shark")
    SEA_TURTLE = Item(397, "Sea turtle")
    MANTA_RAY = Item(391, "Manta ray")
    ANGLERFISH = Item(13441, "Anglerfish")
    
    # Special
    COOKED_KARAMBWAN = Item(3144, "Cooked karambwan")


# ============================================================================
# FOOD
# ============================================================================

class Food(ItemCategory):
    """General food item IDs."""
    
    # Bread and baked goods
    BREAD = Item(2309, "Bread")
    CAKE = Item(1891, "Cake")
    CHOCOLATE_CAKE = Item(1897, "Chocolate cake")
    MEAT_PIE = Item(2327, "Meat pie")
    
    # Cooked meats
    COOKED_CHICKEN = Item(2140, "Cooked chicken")
    COOKED_MEAT = Item(2142, "Cooked meat")
    
    # Pizza
    PLAIN_PIZZA = Item(2289, "Plain pizza")
    MEAT_PIZZA = Item(2293, "Meat pizza")
    ANCHOVY_PIZZA = Item(2297, "Anchovy pizza")
    PINEAPPLE_PIZZA = Item(2301, "Pineapple pizza")
    
    # Potatoes
    BAKED_POTATO = Item(6701, "Baked potato")
    POTATO_WITH_BUTTER = Item(6703, "Potato with butter")
    POTATO_WITH_CHEESE = Item(6705, "Potato with cheese")
    
    # Fruit
    BANANA = Item(1963, "Banana")
    STRAWBERRY = Item(5504, "Strawberry")
    PINEAPPLE = Item(2114, "Pineapple")
    
    # High-tier food
    SHARK = Item(385, "Shark")
    MANTA_RAY = Item(391, "Manta ray")
    ANGLERFISH = Item(13441, "Anglerfish")
    DARK_CRAB = Item(11936, "Dark crab")
    
    # Combo foods
    PURPLE_SWEETS = Item(10476, "Purple sweets")
    SARADOMIN_BREW4 = Item(6685, "Saradomin brew(4)")
    SUPER_RESTORE4 = Item(3024, "Super restore(4)")


# ============================================================================
# POTIONS
# ============================================================================

class Potions(ItemCategory):
    """Potion item IDs (4-dose versions)."""
    
    # Combat potions
    ATTACK_POTION4 = Item(2428, "Attack potion(4)")
    STRENGTH_POTION4 = Item(113, "Strength potion(4)")
    DEFENCE_POTION4 = Item(2432, "Defence potion(4)")
    RANGING_POTION4 = Item(2444, "Ranging potion(4)")
    MAGIC_POTION4 = Item(3040, "Magic potion(4)")
    
    # Super potions
    SUPER_ATTACK4 = Item(2436, "Super attack(4)")
    SUPER_STRENGTH4 = Item(2440, "Super strength(4)")
    SUPER_DEFENCE4 = Item(2442, "Super defence(4)")
    SUPER_RANGING4 = Item(2444, "Super ranging(4)")
    SUPER_MAGIC_POTION4 = Item(3024, "Super magic potion(4)")
    
    # Combat utility
    SUPER_COMBAT_POTION4 = Item(12695, "Super combat potion(4)")
    COMBAT_POTION4 = Item(9739, "Combat potion(4)")
    BASTION_POTION4 = Item(22461, "Bastion potion(4)")
    BATTLEMAGE_POTION4 = Item(22470, "Battlemage potion(4)")
    
    # Restoration
    RESTORE_POTION4 = Item(2430, "Restore potion(4)")
    SUPER_RESTORE4 = Item(3024, "Super restore(4)")
    PRAYER_POTION4 = Item(2434, "Prayer potion(4)")
    SANFEW_SERUM4 = Item(10925, "Sanfew serum(4)")
    
    # Utility
    ENERGY_POTION4 = Item(3008, "Energy potion(4)")
    SUPER_ENERGY4 = Item(3016, "Super energy(4)")
    STAMINA_POTION4 = Item(12625, "Stamina potion(4)")
    ANTIPOISON4 = Item(2446, "Antipoison(4)")
    SUPER_ANTIPOISON4 = Item(2448, "Super antipoison(4)")
    ANTIDOTE_PLUS_PLUS4 = Item(5952, "Antidote++(4)")
    ANTIFIRE_POTION4 = Item(2452, "Antifire potion(4)")
    SUPER_ANTIFIRE_POTION4 = Item(21987, "Super antifire potion(4)")
    EXTENDED_ANTIFIRE4 = Item(11951, "Extended antifire(4)")
    EXTENDED_SUPER_ANTIFIRE4 = Item(22209, "Extended super antifire(4)")
    
    # Saradomin brews
    SARADOMIN_BREW4 = Item(6685, "Saradomin brew(4)")
    SARADOMIN_BREW3 = Item(6687, "Saradomin brew(3)")
    SARADOMIN_BREW2 = Item(6689, "Saradomin brew(2)")
    SARADOMIN_BREW1 = Item(6691, "Saradomin brew(1)")


# ============================================================================
# HERBS & SECONDARY INGREDIENTS
# ============================================================================

class Herbs(ItemCategory):
    """Herb item IDs (grimy and clean)."""
    
    # Grimy herbs
    GRIMY_GUAM_LEAF = Item(199, "Grimy guam leaf")
    GRIMY_MARRENTILL = Item(201, "Grimy marrentill")
    GRIMY_TARROMIN = Item(203, "Grimy tarromin")
    GRIMY_HARRALANDER = Item(205, "Grimy harralander")
    GRIMY_RANARR_WEED = Item(207, "Grimy ranarr weed")
    GRIMY_IRIT_LEAF = Item(209, "Grimy irit leaf")
    GRIMY_AVANTOE = Item(211, "Grimy avantoe")
    GRIMY_KWUARM = Item(213, "Grimy kwuarm")
    GRIMY_CADANTINE = Item(215, "Grimy cadantine")
    GRIMY_DWARF_WEED = Item(217, "Grimy dwarf weed")
    GRIMY_TORSTOL = Item(219, "Grimy torstol")
    GRIMY_LANTADYME = Item(2485, "Grimy lantadyme")
    GRIMY_SNAPDRAGON = Item(3000, "Grimy snapdragon")
    
    # Clean herbs
    GUAM_LEAF = Item(249, "Guam leaf")
    MARRENTILL = Item(251, "Marrentill")
    TARROMIN = Item(253, "Tarromin")
    HARRALANDER = Item(255, "Harralander")
    RANARR_WEED = Item(257, "Ranarr weed")
    IRIT_LEAF = Item(259, "Irit leaf")
    AVANTOE = Item(261, "Avantoe")
    KWUARM = Item(263, "Kwuarm")
    CADANTINE = Item(265, "Cadantine")
    DWARF_WEED = Item(267, "Dwarf weed")
    TORSTOL = Item(269, "Torstol")
    LANTADYME = Item(2481, "Lantadyme")
    SNAPDRAGON = Item(3051, "Snapdragon")


class Seeds(ItemCategory):
    """Farming seed item IDs."""
    
    # Herbs
    GUAM_SEED = Item(5291, "Guam seed")
    MARRENTILL_SEED = Item(5292, "Marrentill seed")
    TARROMIN_SEED = Item(5293, "Tarromin seed")
    HARRALANDER_SEED = Item(5294, "Harralander seed")
    RANARR_SEED = Item(5295, "Ranarr seed")
    IRIT_SEED = Item(5297, "Irit seed")
    AVANTOE_SEED = Item(5298, "Avantoe seed")
    KWUARM_SEED = Item(5299, "Kwuarm seed")
    CADANTINE_SEED = Item(5301, "Cadantine seed")
    DWARF_WEED_SEED = Item(5303, "Dwarf weed seed")
    TORSTOL_SEED = Item(5304, "Torstol seed")
    LANTADYME_SEED = Item(5302, "Lantadyme seed")
    SNAPDRAGON_SEED = Item(5300, "Snapdragon seed")
    
    # Allotments
    POTATO_SEED = Item(5318, "Potato seed")
    ONION_SEED = Item(5319, "Onion seed")
    CABBAGE_SEED = Item(5324, "Cabbage seed")
    TOMATO_SEED = Item(5322, "Tomato seed")
    SWEETCORN_SEED = Item(5320, "Sweetcorn seed")
    STRAWBERRY_SEED = Item(5323, "Strawberry seed")
    WATERMELON_SEED = Item(5321, "Watermelon seed")
    
    # Trees
    ACORN = Item(5312, "Acorn")
    WILLOW_SEED = Item(5313, "Willow seed")
    MAPLE_SEED = Item(5314, "Maple seed")
    YEW_SEED = Item(5315, "Yew seed")
    MAGIC_SEED = Item(5316, "Magic seed")


# ============================================================================
# RUNES
# ============================================================================

class Runes(ItemCategory):
    """Rune item IDs."""
    
    # Elemental runes
    AIR_RUNE = Item(556, "Air rune")
    WATER_RUNE = Item(555, "Water rune")
    EARTH_RUNE = Item(557, "Earth rune")
    FIRE_RUNE = Item(554, "Fire rune")
    
    # Catalytic runes
    MIND_RUNE = Item(558, "Mind rune")
    BODY_RUNE = Item(559, "Body rune")
    COSMIC_RUNE = Item(564, "Cosmic rune")
    CHAOS_RUNE = Item(562, "Chaos rune")
    NATURE_RUNE = Item(561, "Nature rune")
    LAW_RUNE = Item(563, "Law rune")
    DEATH_RUNE = Item(560, "Death rune")
    BLOOD_RUNE = Item(565, "Blood rune")
    SOUL_RUNE = Item(566, "Soul rune")
    ASTRAL_RUNE = Item(9075, "Astral rune")
    WRATH_RUNE = Item(21880, "Wrath rune")
    
    # Combination runes
    MIST_RUNE = Item(4695, "Mist rune")
    DUST_RUNE = Item(4696, "Dust rune")
    MUD_RUNE = Item(4698, "Mud rune")
    SMOKE_RUNE = Item(4697, "Smoke rune")
    STEAM_RUNE = Item(4694, "Steam rune")
    LAVA_RUNE = Item(4699, "Lava rune")


# ============================================================================
# GEMS
# ============================================================================

class Gems(ItemCategory):
    """Gem item IDs."""
    
    # Uncut gems
    UNCUT_OPAL = Item(1625, "Uncut opal")
    UNCUT_JADE = Item(1627, "Uncut jade")
    UNCUT_RED_TOPAZ = Item(1629, "Uncut red topaz")
    UNCUT_SAPPHIRE = Item(1623, "Uncut sapphire")
    UNCUT_EMERALD = Item(1621, "Uncut emerald")
    UNCUT_RUBY = Item(1619, "Uncut ruby")
    UNCUT_DIAMOND = Item(1617, "Uncut diamond")
    UNCUT_DRAGONSTONE = Item(1631, "Uncut dragonstone")
    UNCUT_ONYX = Item(6571, "Uncut onyx")
    UNCUT_ZENYTE = Item(19496, "Uncut zenyte")
    
    # Cut gems
    OPAL = Item(1609, "Opal")
    JADE = Item(1611, "Jade")
    RED_TOPAZ = Item(1613, "Red topaz")
    SAPPHIRE = Item(1607, "Sapphire")
    EMERALD = Item(1605, "Emerald")
    RUBY = Item(1603, "Ruby")
    DIAMOND = Item(1601, "Diamond")
    DRAGONSTONE = Item(1615, "Dragonstone")
    ONYX = Item(6573, "Onyx")
    ZENYTE = Item(19501, "Zenyte")


# ============================================================================
# TOOLS
# ============================================================================

class Tools(ItemCategory):
    """Tool item IDs."""
    
    # Mining
    BRONZE_PICKAXE = Item(1265, "Bronze pickaxe")
    IRON_PICKAXE = Item(1267, "Iron pickaxe")
    STEEL_PICKAXE = Item(1269, "Steel pickaxe")
    MITHRIL_PICKAXE = Item(1273, "Mithril pickaxe")
    ADAMANT_PICKAXE = Item(1271, "Adamant pickaxe")
    RUNE_PICKAXE = Item(1275, "Rune pickaxe")
    DRAGON_PICKAXE = Item(11920, "Dragon pickaxe")
    CRYSTAL_PICKAXE = Item(23680, "Crystal pickaxe")
    
    # Woodcutting
    BRONZE_AXE = Item(1351, "Bronze axe")
    IRON_AXE = Item(1349, "Iron axe")
    STEEL_AXE = Item(1353, "Steel axe")
    MITHRIL_AXE = Item(1355, "Mithril axe")
    ADAMANT_AXE = Item(1357, "Adamant axe")
    RUNE_AXE = Item(1359, "Rune axe")
    DRAGON_AXE = Item(6739, "Dragon axe")
    CRYSTAL_AXE = Item(23677, "Crystal axe")
    
    # Fishing
    SMALL_FISHING_NET = Item(303, "Small fishing net")
    FISHING_ROD = Item(307, "Fishing rod")
    FLY_FISHING_ROD = Item(309, "Fly fishing rod")
    HARPOON = Item(311, "Harpoon")
    LOBSTER_POT = Item(301, "Lobster pot")
    BARBARIAN_ROD = Item(11323, "Barbarian rod")
    KARAMBWAN_VESSEL = Item(3157, "Karambwan vessel")
    
    # Other tools
    HAMMER = Item(2347, "Hammer")
    ROCK_HAMMER = Item(4162, "Rock hammer")
    SAW = Item(8794, "Saw")
    CHISEL = Item(1755, "Chisel")
    NEEDLE = Item(1733, "Needle")
    KNIFE = Item(946, "Knife")
    TINDERBOX = Item(590, "Tinderbox")


# ============================================================================
# WEAPONS
# ============================================================================

class Weapons(ItemCategory):
    """Weapon item IDs."""
    
    # Swords (rune tier as example)
    BRONZE_SWORD = Item(1277, "Bronze sword")
    IRON_SWORD = Item(1279, "Iron sword")
    STEEL_SWORD = Item(1281, "Steel sword")
    MITHRIL_SWORD = Item(1285, "Mithril sword")
    ADAMANT_SWORD = Item(1287, "Adamant sword")
    RUNE_SWORD = Item(1289, "Rune sword")
    
    # Scimitars
    BRONZE_SCIMITAR = Item(1321, "Bronze scimitar")
    IRON_SCIMITAR = Item(1323, "Iron scimitar")
    STEEL_SCIMITAR = Item(1325, "Steel scimitar")
    MITHRIL_SCIMITAR = Item(1329, "Mithril scimitar")
    ADAMANT_SCIMITAR = Item(1331, "Adamant scimitar")
    RUNE_SCIMITAR = Item(1333, "Rune scimitar")
    DRAGON_SCIMITAR = Item(4587, "Dragon scimitar")
    
    # Special weapons
    ABYSSAL_WHIP = Item(4151, "Abyssal whip")
    GRANITE_MAUL = Item(4153, "Granite maul")
    DRAGON_DAGGER = Item(1215, "Dragon dagger")
    DRAGON_CLAWS = Item(13652, "Dragon claws")
    ARMADYL_GODSWORD = Item(11802, "Armadyl godsword")
    SARADOMIN_GODSWORD = Item(11806, "Saradomin godsword")
    ZAMORAK_GODSWORD = Item(11808, "Zamorak godsword")
    BANDOS_GODSWORD = Item(11804, "Bandos godsword")
    
    # Ranged
    SHORTBOW = Item(841, "Shortbow")
    LONGBOW = Item(839, "Longbow")
    OAK_LONGBOW = Item(845, "Oak longbow")
    MAGIC_SHORTBOW = Item(861, "Magic shortbow")
    MAGIC_LONGBOW = Item(859, "Magic longbow")
    DARK_BOW = Item(11235, "Dark bow")
    TWISTED_BOW = Item(20997, "Twisted bow")
    TOXIC_BLOWPIPE = Item(12926, "Toxic blowpipe")
    
    # Staves
    STAFF_OF_AIR = Item(1381, "Staff of air")
    STAFF_OF_WATER = Item(1383, "Staff of water")
    STAFF_OF_EARTH = Item(1385, "Staff of earth")
    STAFF_OF_FIRE = Item(1387, "Staff of fire")
    ANCIENT_STAFF = Item(4675, "Ancient staff")


# ============================================================================
# ARMOR
# ============================================================================

class Armor(ItemCategory):
    """Armor item IDs (examples of common sets)."""
    
    # Rune armor
    RUNE_FULL_HELM = Item(1163, "Rune full helm")
    RUNE_PLATEBODY = Item(1127, "Rune platebody")
    RUNE_PLATELEGS = Item(1079, "Rune platelegs")
    RUNE_PLATESKIRT = Item(1093, "Rune plateskirt")
    RUNE_KITESHIELD = Item(1201, "Rune kiteshield")
    
    # Dragon armor
    DRAGON_FULL_HELM = Item(11335, "Dragon full helm")
    DRAGON_CHAINBODY = Item(3140, "Dragon chainbody")
    DRAGON_PLATELEGS = Item(4087, "Dragon platelegs")
    DRAGON_PLATESKIRT = Item(4585, "Dragon plateskirt")
    DRAGON_SQUARE_SHIELD = Item(1187, "Dragon square shield")
    
    # Barrows armor
    AHRIMS_HOOD = Item(4708, "Ahrim's hood")
    AHRIMS_ROBETOP = Item(4712, "Ahrim's robetop")
    AHRIMS_ROBESKIRT = Item(4714, "Ahrim's robeskirt")
    AHRIMS_STAFF = Item(4710, "Ahrim's staff")
    
    DHAROKS_HELM = Item(4716, "Dharok's helm")
    DHAROKS_PLATEBODY = Item(4720, "Dharok's platebody")
    DHAROKS_PLATELEGS = Item(4722, "Dharok's platelegs")
    DHAROKS_GREATAXE = Item(4718, "Dharok's greataxe")
    
    # God Wars armor
    BANDOS_CHESTPLATE = Item(11832, "Bandos chestplate")
    BANDOS_TASSETS = Item(11834, "Bandos tassets")
    ARMADYL_HELMET = Item(11826, "Armadyl helmet")
    ARMADYL_CHESTPLATE = Item(11828, "Armadyl chestplate")
    ARMADYL_CHAINSKIRT = Item(11830, "Armadyl chainskirt")


# ============================================================================
# JEWELRY
# ============================================================================

class Jewelry(ItemCategory):
    """Jewelry item IDs (amulets, rings, necklaces)."""
    
    # Amulets
    AMULET_OF_STRENGTH = Item(1725, "Amulet of strength")
    AMULET_OF_POWER = Item(1731, "Amulet of power")
    AMULET_OF_GLORY = Item(1712, "Amulet of glory(4)")
    AMULET_OF_FURY = Item(6585, "Amulet of fury")
    AMULET_OF_TORTURE = Item(19553, "Amulet of torture")
    
    # Necklaces
    NECKLACE_OF_ANGUISH = Item(19547, "Necklace of anguish")
    OCCULT_NECKLACE = Item(12002, "Occult necklace")
    
    # Rings
    RING_OF_WEALTH = Item(2572, "Ring of wealth(4)")
    RING_OF_DUELING = Item(2552, "Ring of dueling(8)")
    BERSERKER_RING = Item(6737, "Berserker ring")


# ============================================================================
# CURRENCY & VALUABLES
# ============================================================================

class Currency(ItemCategory):
    """Currency and valuable item IDs."""
    
    COINS = Item(995, "Coins")
    PLATINUM_TOKEN = Item(13204, "Platinum token")
    
    # Tokkul
    TOKKUL = Item(6529, "Tokkul")
    
    # Chaos/Death runes (often used as currency)
    CHAOS_RUNE = Item(562, "Chaos rune")
    DEATH_RUNE = Item(560, "Death rune")
    
    # Valuable items
    UNCUT_ONYX = Item(6571, "Uncut onyx")
    DRAGON_BONES = Item(536, "Dragon bones")
    SUPERIOR_DRAGON_BONES = Item(22124, "Superior dragon bones")


# ============================================================================
# SLAYER DROPS
# ============================================================================

class SlayerDrops(ItemCategory):
    """Valuable slayer monster drops."""
    
    # Gargoyle drops
    MYSTIC_ROBE_TOP_DARK = Item(4101, "Mystic robe top (dark)")
    MYSTIC_ROBE_BOTTOM_DARK = Item(4103, "Mystic robe bottom (dark)")
    RUNE_FULL_HELM = Item(1163, "Rune full helm")
    RUNE_PLATELEGS = Item(1079, "Rune platelegs")
    RUNE_BOOTS = Item(4131, "Rune boots")
    RUNE_PLATESKIRT = Item(1093, "Rune plateskirt")
    
    # Abyssal demon drops
    ABYSSAL_WHIP_DROP = Item(4151, "Abyssal whip")
    
    # Other valuable drops
    RANARR_SEED = Item(5295, "Ranarr seed")
    SNAPDRAGON_SEED = Item(5300, "Snapdragon seed")


# ============================================================================
# AMMUNITION
# ============================================================================

class Ammunition(ItemCategory):
    """Ammunition item IDs."""
    
    # Arrows
    BRONZE_ARROW = Item(882, "Bronze arrow")
    IRON_ARROW = Item(884, "Iron arrow")
    STEEL_ARROW = Item(886, "Steel arrow")
    MITHRIL_ARROW = Item(888, "Mithril arrow")
    ADAMANT_ARROW = Item(890, "Adamant arrow")
    RUNE_ARROW = Item(892, "Rune arrow")
    DRAGON_ARROW = Item(11212, "Dragon arrow")
    AMETHYST_ARROW = Item(21326, "Amethyst arrow")
    
    # Bolts
    BRONZE_BOLTS = Item(877, "Bronze bolts")
    IRON_BOLTS = Item(9140, "Iron bolts")
    STEEL_BOLTS = Item(9141, "Steel bolts")
    MITHRIL_BOLTS = Item(9142, "Mithril bolts")
    ADAMANT_BOLTS = Item(9143, "Adamant bolts")
    RUNITE_BOLTS = Item(9144, "Runite bolts")
    DRAGON_BOLTS = Item(21905, "Dragon bolts")
    
    # Javelins
    BRONZE_JAVELIN = Item(825, "Bronze javelin")
    IRON_JAVELIN = Item(826, "Iron javelin")
    STEEL_JAVELIN = Item(827, "Steel javelin")
    MITHRIL_JAVELIN = Item(828, "Mithril javelin")
    ADAMANT_JAVELIN = Item(829, "Adamant javelin")
    RUNE_JAVELIN = Item(830, "Rune javelin")
    DRAGON_JAVELIN = Item(19484, "Dragon javelin")


# ============================================================================
# BONES
# ============================================================================

class Bones(ItemCategory):
    """Bone item IDs for prayer training."""
    
    BONES = Item(526, "Bones")
    BURNT_BONES = Item(528, "Burnt bones")
    WOLF_BONES = Item(2859, "Wolf bones")
    BAT_BONES = Item(530, "Bat bones")
    BIG_BONES = Item(532, "Big bones")
    BABYDRAGON_BONES = Item(534, "Babydragon bones")
    DRAGON_BONES = Item(536, "Dragon bones")
    WYVERN_BONES = Item(6812, "Wyvern bones")
    DAGANNOTH_BONES = Item(6729, "Dagannoth bones")
    SUPERIOR_DRAGON_BONES = Item(22124, "Superior dragon bones")
    
    # Special bones
    OURG_BONES = Item(4834, "Ourg bones")
    HYDRA_BONES = Item(22783, "Hydra bones")


# ============================================================================
# HIDES
# ============================================================================

class Hides(ItemCategory):
    """Hide and leather item IDs."""
    
    COWHIDE = Item(1739, "Cowhide")
    LEATHER = Item(1741, "Leather")
    HARD_LEATHER = Item(1743, "Hard leather")


class BirdsNests(ItemCategory):
    """Birds nest item IDs (common woodcutting drops)."""
    
    # Seed nests
    BIRDS_NEST_SEEDS = Item(5070, "Bird nest")
    
    # Ring nests
    BIRDS_NEST_RING = Item(5071, "Bird nest")
    
    # Empty nests
    BIRDS_NEST_EMPTY = Item(5072, "Bird nest")
    
    # Specific content nests
    BIRDS_NEST_MARIGOLD = Item(5073, "Bird nest")
    BIRDS_NEST_WILLOW = Item(5074, "Bird nest")
    
    # Clue nest
    BIRDS_NEST_CLUE = Item(7413, "Bird nest")
    
    # God eggs (rare)
    BIRD_NEST_SARADOMIN = Item(22798, "Bird nest (Saradomin)")
    BIRD_NEST_GUTHIX = Item(22800, "Bird nest (Guthix)")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_item_category(item_id: int) -> Optional[str]:
    """
    Find which category an item ID belongs to.
    
    Args:
        item_id: Item ID to search for
        
    Returns:
        Category name (e.g., "Ores", "Food") or None if not found
    """
    categories = {
        "Ores": Ores,
        "Bars": Bars,
        "Logs": Logs,
        "Planks": Planks,
        "RawFish": RawFish,
        "CookedFish": CookedFish,
        "Food": Food,
        "Potions": Potions,
        "Herbs": Herbs,
        "Seeds": Seeds,
        "Runes": Runes,
        "Gems": Gems,
        "Tools": Tools,
        "Weapons": Weapons,
        "Armor": Armor,
        "Currency": Currency,
        "Ammunition": Ammunition,
        "Bones": Bones,
        "BirdsNests": BirdsNests,
    }
    
    for category_name, category_cls in categories.items():
        if item_id in category_cls.all_ids():
            return category_name
    
    return None


def find_item_name(item_id: int) -> Optional[str]:
    """
    Find the display name of an item by its ID.
    
    Args:
        item_id: Item ID to search for
        
    Returns:
        Item display name (e.g., "Iron ore", "Shark") or None if not found
    """
    categories = [
        Ores, Bars, Logs, Planks, RawFish, CookedFish, Food,
        Potions, Herbs, Seeds, Runes, Gems, Tools, Weapons,
        Armor, Jewelry, Currency, Ammunition, Bones, Hides, BirdsNests
    ]
    
    for category in categories:
        item = category.find_by_id(item_id)
        if item:
            return item.name
    
    return None


def find_item(item_id: int) -> Optional[Item]:
    """
    Find an Item object by its ID.
    
    Args:
        item_id: Item ID to search for
        
    Returns:
        Item object or None if not found
    """
    categories = [
        Ores, Bars, Logs, Planks, RawFish, CookedFish, Food,
        Potions, Herbs, Seeds, Runes, Gems, Tools, Weapons,
        Armor, Jewelry, Currency, Ammunition, Bones, Hides, BirdsNests
    ]
    
    for category in categories:
        item = category.find_by_id(item_id)
        if item:
            return item
    
    return None
