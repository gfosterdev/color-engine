"""
Item ID references for Old School RuneScape.

This module provides a centralized registry of all in-game item IDs used by the bot.
Item IDs are organized by category for easy lookup and maintenance.

Source: RuneLite ItemID.java
https://github.com/runelite/runelite/blob/master/runelite-api/src/main/java/net/runelite/api/ItemID.java

Usage:
    from config.items import Ores, Food, Potions
    
    ore_ids = Ores.all()
    iron_ore_id = Ores.IRON_ORE
    shark_id = Food.SHARK
"""

from typing import List, Optional


class ItemCategory:
    """Base class for item categories with helper methods."""
    
    @classmethod
    def all(cls) -> List[int]:
        """Return all item IDs in this category."""
        all_ids = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, (int, list)):
                    if isinstance(attr_value, int):
                        all_ids.append(attr_value)
                    else:
                        all_ids.extend(attr_value)
        return all_ids
    
    @classmethod
    def find_by_id(cls, item_id: int) -> Optional[str]:
        """Find the name of an item by its ID."""
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, int) and attr_value == item_id:
                    return attr_name
                elif isinstance(attr_value, list) and item_id in attr_value:
                    return attr_name
        return None


# ============================================================================
# ORES & BARS
# ============================================================================

class Ores(ItemCategory):
    """Mining ore item IDs."""
    
    # Basic ores
    COPPER_ORE = 436
    TIN_ORE = 438
    IRON_ORE = 440
    COAL = 453
    
    # Clay
    CLAY = 434
    SOFT_CLAY = 1761
    
    # Precious metals
    SILVER_ORE = 442
    GOLD_ORE = 444
    
    # High-level ores
    MITHRIL_ORE = 447
    ADAMANTITE_ORE = 449
    RUNITE_ORE = 451
    
    # Special ores
    SANDSTONE_1KG = 6971
    SANDSTONE_2KG = 6973
    SANDSTONE_5KG = 6975
    SANDSTONE_10KG = 6977
    GRANITE_500G = 6979
    GRANITE_2KG = 6981
    GRANITE_5KG = 6983
    AMETHYST = 21347
    
    # Gems from mining
    UNCUT_SAPPHIRE = 1623
    UNCUT_EMERALD = 1621
    UNCUT_RUBY = 1619
    UNCUT_DIAMOND = 1617


class Bars(ItemCategory):
    """Smithing bar item IDs."""
    
    BRONZE_BAR = 2349
    IRON_BAR = 2351
    STEEL_BAR = 2353
    SILVER_BAR = 2355
    GOLD_BAR = 2357
    MITHRIL_BAR = 2359
    ADAMANTITE_BAR = 2361
    RUNITE_BAR = 2363


# ============================================================================
# LOGS & WOOD PRODUCTS
# ============================================================================

class Logs(ItemCategory):
    """Woodcutting log item IDs."""
    
    LOGS = 1511
    OAK_LOGS = 1521
    WILLOW_LOGS = 1519
    MAPLE_LOGS = 1517
    YEW_LOGS = 1515
    MAGIC_LOGS = 1513
    REDWOOD_LOGS = 19669
    TEAK_LOGS = 6333
    MAHOGANY_LOGS = 6332


class Planks(ItemCategory):
    """Plank item IDs for construction."""
    
    PLANK = 960
    OAK_PLANK = 8778
    TEAK_PLANK = 8780
    MAHOGANY_PLANK = 8782


# ============================================================================
# FISH (RAW & COOKED)
# ============================================================================

class RawFish(ItemCategory):
    """Raw fish item IDs."""
    
    # Low level
    RAW_SHRIMPS = 317
    RAW_SARDINE = 327
    RAW_HERRING = 345
    RAW_ANCHOVIES = 321
    RAW_MACKEREL = 353
    RAW_TROUT = 335
    RAW_COD = 341
    RAW_PIKE = 349
    RAW_SALMON = 331
    
    # Mid level
    RAW_TUNA = 359
    RAW_LOBSTER = 377
    RAW_BASS = 363
    RAW_SWORDFISH = 371
    RAW_MONKFISH = 7944
    
    # High level
    RAW_SHARK = 383
    RAW_SEA_TURTLE = 395
    RAW_MANTA_RAY = 389
    RAW_ANGLERFISH = 13439
    
    # Special
    RAW_KARAMBWAN = 3142


class CookedFish(ItemCategory):
    """Cooked fish item IDs."""
    
    # Low level
    SHRIMPS = 315
    SARDINE = 325
    HERRING = 347
    ANCHOVIES = 319
    MACKEREL = 355
    TROUT = 333
    COD = 339
    PIKE = 351
    SALMON = 329
    
    # Mid level
    TUNA = 361
    LOBSTER = 379
    BASS = 365
    SWORDFISH = 373
    MONKFISH = 7946
    
    # High level
    SHARK = 385
    SEA_TURTLE = 397
    MANTA_RAY = 391
    ANGLERFISH = 13441
    
    # Special
    COOKED_KARAMBWAN = 3144


# ============================================================================
# FOOD
# ============================================================================

class Food(ItemCategory):
    """General food item IDs."""
    
    # Bread and baked goods
    BREAD = 2309
    CAKE = 1891
    CHOCOLATE_CAKE = 1897
    MEAT_PIE = 2327
    
    # Cooked meats
    COOKED_CHICKEN = 2140
    COOKED_MEAT = 2142
    
    # Pizza
    PLAIN_PIZZA = 2289
    MEAT_PIZZA = 2293
    ANCHOVY_PIZZA = 2297
    PINEAPPLE_PIZZA = 2301
    
    # Potatoes
    BAKED_POTATO = 6701
    POTATO_WITH_BUTTER = 6703
    POTATO_WITH_CHEESE = 6705
    
    # Fruit
    BANANA = 1963
    STRAWBERRY = 5504
    PINEAPPLE = 2114
    
    # High-tier food
    SHARK = 385
    MANTA_RAY = 391
    ANGLERFISH = 13441
    DARK_CRAB = 11936
    
    # Combo foods
    PURPLE_SWEETS = 10476
    SARADOMIN_BREW4 = 6685
    SUPER_RESTORE4 = 3024


# ============================================================================
# POTIONS
# ============================================================================

class Potions(ItemCategory):
    """Potion item IDs (4-dose versions)."""
    
    # Combat potions
    ATTACK_POTION4 = 2428
    STRENGTH_POTION4 = 113
    DEFENCE_POTION4 = 2432
    RANGING_POTION4 = 2444
    MAGIC_POTION4 = 3040
    
    # Super potions
    SUPER_ATTACK4 = 2436
    SUPER_STRENGTH4 = 2440
    SUPER_DEFENCE4 = 2442
    SUPER_RANGING4 = 2444
    SUPER_MAGIC_POTION4 = 3024
    
    # Combat utility
    SUPER_COMBAT_POTION4 = 12695
    COMBAT_POTION4 = 9739
    BASTION_POTION4 = 22461
    BATTLEMAGE_POTION4 = 22470
    
    # Restoration
    RESTORE_POTION4 = 2430
    SUPER_RESTORE4 = 3024
    PRAYER_POTION4 = 2434
    SANFEW_SERUM4 = 10925
    
    # Utility
    ENERGY_POTION4 = 3008
    SUPER_ENERGY4 = 3016
    STAMINA_POTION4 = 12625
    ANTIPOISON4 = 2446
    SUPER_ANTIPOISON4 = 2448
    ANTIDOTE_PLUS_PLUS4 = 5952
    ANTIFIRE_POTION4 = 2452
    SUPER_ANTIFIRE_POTION4 = 21987
    EXTENDED_ANTIFIRE4 = 11951
    EXTENDED_SUPER_ANTIFIRE4 = 22209
    
    # Saradomin brews
    SARADOMIN_BREW4 = 6685
    SARADOMIN_BREW3 = 6687
    SARADOMIN_BREW2 = 6689
    SARADOMIN_BREW1 = 6691


# ============================================================================
# HERBS & SECONDARY INGREDIENTS
# ============================================================================

class Herbs(ItemCategory):
    """Herb item IDs (grimy and clean)."""
    
    # Grimy herbs
    GRIMY_GUAM_LEAF = 199
    GRIMY_MARRENTILL = 201
    GRIMY_TARROMIN = 203
    GRIMY_HARRALANDER = 205
    GRIMY_RANARR_WEED = 207
    GRIMY_IRIT_LEAF = 209
    GRIMY_AVANTOE = 211
    GRIMY_KWUARM = 213
    GRIMY_CADANTINE = 215
    GRIMY_DWARF_WEED = 217
    GRIMY_TORSTOL = 219
    GRIMY_LANTADYME = 2485
    GRIMY_SNAPDRAGON = 3000
    
    # Clean herbs
    GUAM_LEAF = 249
    MARRENTILL = 251
    TARROMIN = 253
    HARRALANDER = 255
    RANARR_WEED = 257
    IRIT_LEAF = 259
    AVANTOE = 261
    KWUARM = 263
    CADANTINE = 265
    DWARF_WEED = 267
    TORSTOL = 269
    LANTADYME = 2481
    SNAPDRAGON = 3051


class Seeds(ItemCategory):
    """Farming seed item IDs."""
    
    # Herbs
    GUAM_SEED = 5291
    MARRENTILL_SEED = 5292
    TARROMIN_SEED = 5293
    HARRALANDER_SEED = 5294
    RANARR_SEED = 5295
    IRIT_SEED = 5297
    AVANTOE_SEED = 5298
    KWUARM_SEED = 5299
    CADANTINE_SEED = 5301
    DWARF_WEED_SEED = 5303
    TORSTOL_SEED = 5304
    LANTADYME_SEED = 5302
    SNAPDRAGON_SEED = 5300
    
    # Allotments
    POTATO_SEED = 5318
    ONION_SEED = 5319
    CABBAGE_SEED = 5324
    TOMATO_SEED = 5322
    SWEETCORN_SEED = 5320
    STRAWBERRY_SEED = 5323
    WATERMELON_SEED = 5321
    
    # Trees
    ACORN = 5312
    WILLOW_SEED = 5313
    MAPLE_SEED = 5314
    YEW_SEED = 5315
    MAGIC_SEED = 5316


# ============================================================================
# RUNES
# ============================================================================

class Runes(ItemCategory):
    """Rune item IDs."""
    
    # Elemental runes
    AIR_RUNE = 556
    WATER_RUNE = 555
    EARTH_RUNE = 557
    FIRE_RUNE = 554
    
    # Catalytic runes
    MIND_RUNE = 558
    BODY_RUNE = 559
    COSMIC_RUNE = 564
    CHAOS_RUNE = 562
    NATURE_RUNE = 561
    LAW_RUNE = 563
    DEATH_RUNE = 560
    BLOOD_RUNE = 565
    SOUL_RUNE = 566
    ASTRAL_RUNE = 9075
    WRATH_RUNE = 21880
    
    # Combination runes
    MIST_RUNE = 4695
    DUST_RUNE = 4696
    MUD_RUNE = 4698
    SMOKE_RUNE = 4697
    STEAM_RUNE = 4694
    LAVA_RUNE = 4699


# ============================================================================
# GEMS
# ============================================================================

class Gems(ItemCategory):
    """Gem item IDs."""
    
    # Uncut gems
    UNCUT_OPAL = 1625
    UNCUT_JADE = 1627
    UNCUT_RED_TOPAZ = 1629
    UNCUT_SAPPHIRE = 1623
    UNCUT_EMERALD = 1621
    UNCUT_RUBY = 1619
    UNCUT_DIAMOND = 1617
    UNCUT_DRAGONSTONE = 1631
    UNCUT_ONYX = 6571
    UNCUT_ZENYTE = 19496
    
    # Cut gems
    OPAL = 1609
    JADE = 1611
    RED_TOPAZ = 1613
    SAPPHIRE = 1607
    EMERALD = 1605
    RUBY = 1603
    DIAMOND = 1601
    DRAGONSTONE = 1615
    ONYX = 6573
    ZENYTE = 19501


# ============================================================================
# TOOLS
# ============================================================================

class Tools(ItemCategory):
    """Tool item IDs."""
    
    # Mining
    BRONZE_PICKAXE = 1265
    IRON_PICKAXE = 1267
    STEEL_PICKAXE = 1269
    MITHRIL_PICKAXE = 1273
    ADAMANT_PICKAXE = 1271
    RUNE_PICKAXE = 1275
    DRAGON_PICKAXE = 11920
    CRYSTAL_PICKAXE = 23680
    
    # Woodcutting
    BRONZE_AXE = 1351
    IRON_AXE = 1349
    STEEL_AXE = 1353
    MITHRIL_AXE = 1355
    ADAMANT_AXE = 1357
    RUNE_AXE = 1359
    DRAGON_AXE = 6739
    CRYSTAL_AXE = 23677
    
    # Fishing
    SMALL_FISHING_NET = 303
    FISHING_ROD = 307
    FLY_FISHING_ROD = 309
    HARPOON = 311
    LOBSTER_POT = 301
    BARBARIAN_ROD = 11323
    KARAMBWAN_VESSEL = 3157
    
    # Other tools
    HAMMER = 2347
    SAW = 8794
    CHISEL = 1755
    NEEDLE = 1733
    KNIFE = 946
    TINDERBOX = 590


# ============================================================================
# WEAPONS
# ============================================================================

class Weapons(ItemCategory):
    """Weapon item IDs."""
    
    # Swords (rune tier as example)
    BRONZE_SWORD = 1277
    IRON_SWORD = 1279
    STEEL_SWORD = 1281
    MITHRIL_SWORD = 1285
    ADAMANT_SWORD = 1287
    RUNE_SWORD = 1289
    
    # Scimitars
    BRONZE_SCIMITAR = 1321
    IRON_SCIMITAR = 1323
    STEEL_SCIMITAR = 1325
    MITHRIL_SCIMITAR = 1329
    ADAMANT_SCIMITAR = 1331
    RUNE_SCIMITAR = 1333
    DRAGON_SCIMITAR = 4587
    
    # Special weapons
    ABYSSAL_WHIP = 4151
    DRAGON_DAGGER = 1215
    DRAGON_CLAWS = 13652
    ARMADYL_GODSWORD = 11802
    SARADOMIN_GODSWORD = 11806
    ZAMORAK_GODSWORD = 11808
    BANDOS_GODSWORD = 11804
    
    # Ranged
    SHORTBOW = 841
    LONGBOW = 839
    MAGIC_SHORTBOW = 861
    MAGIC_LONGBOW = 859
    DARK_BOW = 11235
    TWISTED_BOW = 20997
    TOXIC_BLOWPIPE = 12926
    
    # Staves
    STAFF_OF_AIR = 1381
    STAFF_OF_WATER = 1383
    STAFF_OF_EARTH = 1385
    STAFF_OF_FIRE = 1387
    ANCIENT_STAFF = 4675


# ============================================================================
# ARMOR
# ============================================================================

class Armor(ItemCategory):
    """Armor item IDs (examples of common sets)."""
    
    # Rune armor
    RUNE_FULL_HELM = 1163
    RUNE_PLATEBODY = 1127
    RUNE_PLATELEGS = 1079
    RUNE_PLATESKIRT = 1093
    RUNE_KITESHIELD = 1201
    
    # Dragon armor
    DRAGON_FULL_HELM = 11335
    DRAGON_CHAINBODY = 3140
    DRAGON_PLATELEGS = 4087
    DRAGON_PLATESKIRT = 4585
    DRAGON_SQUARE_SHIELD = 1187
    
    # Barrows armor
    AHRIMS_HOOD = 4708
    AHRIMS_ROBETOP = 4712
    AHRIMS_ROBESKIRT = 4714
    AHRIMS_STAFF = 4710
    
    DHAROKS_HELM = 4716
    DHAROKS_PLATEBODY = 4720
    DHAROKS_PLATELEGS = 4722
    DHAROKS_GREATAXE = 4718
    
    # God Wars armor
    BANDOS_CHESTPLATE = 11832
    BANDOS_TASSETS = 11834
    ARMADYL_HELMET = 11826
    ARMADYL_CHESTPLATE = 11828
    ARMADYL_CHAINSKIRT = 11830


# ============================================================================
# CURRENCY & VALUABLES
# ============================================================================

class Currency(ItemCategory):
    """Currency and valuable item IDs."""
    
    COINS = 995
    PLATINUM_TOKEN = 13204
    
    # Tokkul
    TOKKUL = 6529
    
    # Chaos/Death runes (often used as currency)
    CHAOS_RUNE = 562
    DEATH_RUNE = 560
    
    # Valuable items
    UNCUT_ONYX = 6571
    DRAGON_BONES = 536
    SUPERIOR_DRAGON_BONES = 22124


# ============================================================================
# AMMUNITION
# ============================================================================

class Ammunition(ItemCategory):
    """Ammunition item IDs."""
    
    # Arrows
    BRONZE_ARROW = 882
    IRON_ARROW = 884
    STEEL_ARROW = 886
    MITHRIL_ARROW = 888
    ADAMANT_ARROW = 890
    RUNE_ARROW = 892
    DRAGON_ARROW = 11212
    AMETHYST_ARROW = 21326
    
    # Bolts
    BRONZE_BOLTS = 877
    IRON_BOLTS = 9140
    STEEL_BOLTS = 9141
    MITHRIL_BOLTS = 9142
    ADAMANT_BOLTS = 9143
    RUNITE_BOLTS = 9144
    DRAGON_BOLTS = 21905
    
    # Javelins
    BRONZE_JAVELIN = 825
    IRON_JAVELIN = 826
    STEEL_JAVELIN = 827
    MITHRIL_JAVELIN = 828
    ADAMANT_JAVELIN = 829
    RUNE_JAVELIN = 830
    DRAGON_JAVELIN = 19484


# ============================================================================
# BONES
# ============================================================================

class Bones(ItemCategory):
    """Bone item IDs for prayer training."""
    
    BONES = 526
    BURNT_BONES = 528
    WOLF_BONES = 2859
    BAT_BONES = 530
    BIG_BONES = 532
    BABYDRAGON_BONES = 534
    DRAGON_BONES = 536
    WYVERN_BONES = 6812
    DAGANNOTH_BONES = 6729
    SUPERIOR_DRAGON_BONES = 22124
    
    # Special bones
    OURG_BONES = 4834
    HYDRA_BONES = 22783


class BirdsNests(ItemCategory):
    """Birds nest item IDs (common woodcutting drops)."""
    
    # Seed nests
    BIRDS_NEST_SEEDS = 5070
    
    # Ring nests
    BIRDS_NEST_RING = 5071
    
    # Empty nests
    BIRDS_NEST_EMPTY = 5072
    
    # Specific content nests
    BIRDS_NEST_MARIGOLD = 5073
    BIRDS_NEST_WILLOW = 5074
    
    # Clue nest
    BIRDS_NEST_CLUE = 7413
    
    # God eggs (rare)
    BIRD_NEST_SARADOMIN = 22798
    BIRD_NEST_GUTHIX = 22800


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
        if item_id in category_cls.all():
            return category_name
    
    return None


def find_item_name(item_id: int) -> Optional[str]:
    """
    Find the specific name of an item by its ID.
    
    Args:
        item_id: Item ID to search for
        
    Returns:
        Item name (e.g., "IRON_ORE", "SHARK") or None if not found
    """
    categories = [
        Ores, Bars, Logs, Planks, RawFish, CookedFish, Food,
        Potions, Herbs, Seeds, Runes, Gems, Tools, Weapons,
        Armor, Currency, Ammunition, Bones, BirdsNests
    ]
    
    for category in categories:
        name = category.find_by_id(item_id)
        if name:
            return name
    
    return None
