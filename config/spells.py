"""
Spell configurations for Old School RuneScape magic system.

This module provides spell definitions for the standard spellbook including
spell requirements, rune costs, and widget positions.

Usage:
    from config.spells import StandardSpells, Spell
    
    # Access spell data
    high_alch = StandardSpells.HIGH_LEVEL_ALCHEMY
    level = high_alch.level_required
    runes = high_alch.runes_required
    
    # Get all spells in category
    teleports = StandardSpells.all_teleports()
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from config.items import Runes


@dataclass(frozen=True)
class Spell:
    """Represents a spell with its requirements and properties."""
    id: int
    name: str
    level_required: int
    runes_required: Dict[int, int]  # {rune_item_id: quantity}
    widget_id: Optional[int] = None
    requires_target: bool = False  # True for alchemy, telegrab, etc.
    
    def __eq__(self, other) -> bool:
        """Allow comparison with integers and other Spells."""
        if isinstance(other, int):
            return self.id == other
        elif isinstance(other, Spell):
            return self.id == other.id
        return False
    
    def __hash__(self) -> int:
        """Make Spell hashable for use in sets/dicts."""
        return hash(self.id)


class StandardSpells:
    """Standard spellbook spell definitions."""
    
    # ============================================================================
    # COMBAT SPELLS
    # ============================================================================
    
    WIND_STRIKE = Spell(
        id=1152,
        name="Wind Strike",
        level_required=1,
        runes_required={
            Runes.AIR_RUNE.id: 1,
            Runes.MIND_RUNE.id: 1
        },
        widget_id=14286850
    )
    
    WATER_STRIKE = Spell(
        id=1154,
        name="Water Strike",
        level_required=5,
        runes_required={
            Runes.WATER_RUNE.id: 1,
            Runes.AIR_RUNE.id: 1,
            Runes.MIND_RUNE.id: 1
        },
        widget_id=14286851
    )
    
    EARTH_STRIKE = Spell(
        id=1156,
        name="Earth Strike",
        level_required=9,
        runes_required={
            Runes.EARTH_RUNE.id: 2,
            Runes.AIR_RUNE.id: 1,
            Runes.MIND_RUNE.id: 1
        },
        widget_id=14286852
    )
    
    FIRE_STRIKE = Spell(
        id=1158,
        name="Fire Strike",
        level_required=13,
        runes_required={
            Runes.FIRE_RUNE.id: 3,
            Runes.AIR_RUNE.id: 2,
            Runes.MIND_RUNE.id: 1
        },
        widget_id=14286853
    )
    
    WIND_BOLT = Spell(
        id=1160,
        name="Wind Bolt",
        level_required=17,
        runes_required={
            Runes.AIR_RUNE.id: 2,
            Runes.CHAOS_RUNE.id: 1
        },
        widget_id=14286854
    )
    
    WATER_BOLT = Spell(
        id=1163,
        name="Water Bolt",
        level_required=23,
        runes_required={
            Runes.WATER_RUNE.id: 2,
            Runes.AIR_RUNE.id: 2,
            Runes.CHAOS_RUNE.id: 1
        },
        widget_id=14286855
    )
    
    EARTH_BOLT = Spell(
        id=1166,
        name="Earth Bolt",
        level_required=29,
        runes_required={
            Runes.EARTH_RUNE.id: 3,
            Runes.AIR_RUNE.id: 2,
            Runes.CHAOS_RUNE.id: 1
        },
        widget_id=14286856
    )
    
    FIRE_BOLT = Spell(
        id=1169,
        name="Fire Bolt",
        level_required=35,
        runes_required={
            Runes.FIRE_RUNE.id: 4,
            Runes.AIR_RUNE.id: 3,
            Runes.CHAOS_RUNE.id: 1
        },
        widget_id=14286857
    )
    
    WIND_BLAST = Spell(
        id=1172,
        name="Wind Blast",
        level_required=41,
        runes_required={
            Runes.AIR_RUNE.id: 3,
            Runes.DEATH_RUNE.id: 1
        },
        widget_id=14286858
    )
    
    WATER_BLAST = Spell(
        id=1175,
        name="Water Blast",
        level_required=47,
        runes_required={
            Runes.WATER_RUNE.id: 3,
            Runes.AIR_RUNE.id: 3,
            Runes.DEATH_RUNE.id: 1
        },
        widget_id=14286859
    )
    
    EARTH_BLAST = Spell(
        id=1177,
        name="Earth Blast",
        level_required=53,
        runes_required={
            Runes.EARTH_RUNE.id: 4,
            Runes.AIR_RUNE.id: 3,
            Runes.DEATH_RUNE.id: 1
        },
        widget_id=14286860
    )
    
    FIRE_BLAST = Spell(
        id=1181,
        name="Fire Blast",
        level_required=59,
        runes_required={
            Runes.FIRE_RUNE.id: 5,
            Runes.AIR_RUNE.id: 4,
            Runes.DEATH_RUNE.id: 1
        },
        widget_id=14286861
    )
    
    WIND_WAVE = Spell(
        id=1183,
        name="Wind Wave",
        level_required=62,
        runes_required={
            Runes.AIR_RUNE.id: 5,
            Runes.BLOOD_RUNE.id: 1
        },
        widget_id=14286862
    )
    
    WATER_WAVE = Spell(
        id=1185,
        name="Water Wave",
        level_required=65,
        runes_required={
            Runes.WATER_RUNE.id: 7,
            Runes.AIR_RUNE.id: 5,
            Runes.BLOOD_RUNE.id: 1
        },
        widget_id=14286863
    )
    
    EARTH_WAVE = Spell(
        id=1188,
        name="Earth Wave",
        level_required=70,
        runes_required={
            Runes.EARTH_RUNE.id: 7,
            Runes.AIR_RUNE.id: 5,
            Runes.BLOOD_RUNE.id: 1
        },
        widget_id=14286864
    )
    
    FIRE_WAVE = Spell(
        id=1189,
        name="Fire Wave",
        level_required=75,
        runes_required={
            Runes.FIRE_RUNE.id: 7,
            Runes.AIR_RUNE.id: 5,
            Runes.BLOOD_RUNE.id: 1
        },
        widget_id=14286865
    )
    
    # ============================================================================
    # TELEPORT SPELLS
    # ============================================================================
    
    HOME_TELEPORT = Spell(
        id=1164,
        name="Home Teleport",
        level_required=1,
        runes_required={},  # No runes required
        widget_id=14286850
    )
    
    VARROCK_TELEPORT = Spell(
        id=1164,
        name="Varrock Teleport",
        level_required=25,
        runes_required={
            Runes.FIRE_RUNE.id: 1,
            Runes.AIR_RUNE.id: 3,
            Runes.LAW_RUNE.id: 1
        },
        widget_id=14286871
    )
    
    LUMBRIDGE_TELEPORT = Spell(
        id=1167,
        name="Lumbridge Teleport",
        level_required=31,
        runes_required={
            Runes.EARTH_RUNE.id: 1,
            Runes.AIR_RUNE.id: 3,
            Runes.LAW_RUNE.id: 1
        },
        widget_id=14286872
    )
    
    FALADOR_TELEPORT = Spell(
        id=1170,
        name="Falador Teleport",
        level_required=37,
        runes_required={
            Runes.WATER_RUNE.id: 1,
            Runes.AIR_RUNE.id: 3,
            Runes.LAW_RUNE.id: 1
        },
        widget_id=14286873
    )
    
    CAMELOT_TELEPORT = Spell(
        id=1174,
        name="Camelot Teleport",
        level_required=45,
        runes_required={
            Runes.AIR_RUNE.id: 5,
            Runes.LAW_RUNE.id: 1
        },
        widget_id=14286875
    )
    
    ARDOUGNE_TELEPORT = Spell(
        id=1234,
        name="Ardougne Teleport",
        level_required=51,
        runes_required={
            Runes.WATER_RUNE.id: 2,
            Runes.LAW_RUNE.id: 2
        },
        widget_id=14286876
    )
    
    WATCHTOWER_TELEPORT = Spell(
        id=1236,
        name="Watchtower Teleport",
        level_required=58,
        runes_required={
            Runes.EARTH_RUNE.id: 2,
            Runes.LAW_RUNE.id: 2
        },
        widget_id=14286877
    )
    
    TROLLHEIM_TELEPORT = Spell(
        id=1238,
        name="Trollheim Teleport",
        level_required=61,
        runes_required={
            Runes.FIRE_RUNE.id: 2,
            Runes.LAW_RUNE.id: 2
        },
        widget_id=14286878
    )
    
    # ============================================================================
    # UTILITY SPELLS
    # ============================================================================
    
    LOW_LEVEL_ALCHEMY = Spell(
        id=1162,
        name="Low Level Alchemy",
        level_required=21,
        runes_required={
            Runes.FIRE_RUNE.id: 3,
            Runes.NATURE_RUNE.id: 1
        },
        widget_id=14286869,
        requires_target=True
    )
    
    HIGH_LEVEL_ALCHEMY = Spell(
        id=1178,
        name="High Level Alchemy",
        level_required=55,
        runes_required={
            Runes.FIRE_RUNE.id: 5,
            Runes.NATURE_RUNE.id: 1
        },
        widget_id=14286880,
        requires_target=True
    )
    
    TELEKINETIC_GRAB = Spell(
        id=1168,
        name="Telekinetic Grab",
        level_required=33,
        runes_required={
            Runes.AIR_RUNE.id: 1,
            Runes.LAW_RUNE.id: 1
        },
        widget_id=14286874,
        requires_target=True
    )
    
    SUPERHEAT_ITEM = Spell(
        id=1173,
        name="Superheat Item",
        level_required=43,
        runes_required={
            Runes.FIRE_RUNE.id: 4,
            Runes.NATURE_RUNE.id: 1
        },
        widget_id=14286879,
        requires_target=True
    )
    
    ENCHANT_SAPPHIRE = Spell(
        id=1155,
        name="Lvl-1 Enchant",
        level_required=7,
        runes_required={
            Runes.WATER_RUNE.id: 1,
            Runes.COSMIC_RUNE.id: 1
        },
        widget_id=14286866,
        requires_target=True
    )
    
    ENCHANT_EMERALD = Spell(
        id=1165,
        name="Lvl-2 Enchant",
        level_required=27,
        runes_required={
            Runes.AIR_RUNE.id: 3,
            Runes.COSMIC_RUNE.id: 1
        },
        widget_id=14286867,
        requires_target=True
    )
    
    ENCHANT_RUBY = Spell(
        id=1176,
        name="Lvl-3 Enchant",
        level_required=49,
        runes_required={
            Runes.FIRE_RUNE.id: 5,
            Runes.COSMIC_RUNE.id: 1
        },
        widget_id=14286868,
        requires_target=True
    )
    
    ENCHANT_DIAMOND = Spell(
        id=1180,
        name="Lvl-4 Enchant",
        level_required=57,
        runes_required={
            Runes.EARTH_RUNE.id: 10,
            Runes.COSMIC_RUNE.id: 1
        },
        widget_id=14286881,
        requires_target=True
    )
    
    ENCHANT_DRAGONSTONE = Spell(
        id=1187,
        name="Lvl-5 Enchant",
        level_required=68,
        runes_required={
            Runes.EARTH_RUNE.id: 15,
            Runes.WATER_RUNE.id: 15,
            Runes.COSMIC_RUNE.id: 1
        },
        widget_id=14286882,
        requires_target=True
    )
    
    ENCHANT_ONYX = Spell(
        id=6003,
        name="Lvl-6 Enchant",
        level_required=87,
        runes_required={
            Runes.EARTH_RUNE.id: 20,
            Runes.FIRE_RUNE.id: 20,
            Runes.COSMIC_RUNE.id: 1
        },
        widget_id=14286883,
        requires_target=True
    )
    
    BONES_TO_BANANAS = Spell(
        id=1159,
        name="Bones to Bananas",
        level_required=15,
        runes_required={
            Runes.EARTH_RUNE.id: 2,
            Runes.WATER_RUNE.id: 2,
            Runes.NATURE_RUNE.id: 1
        },
        widget_id=14286870
    )
    
    BONES_TO_PEACHES = Spell(
        id=1171,
        name="Bones to Peaches",
        level_required=60,
        runes_required={
            Runes.EARTH_RUNE.id: 4,
            Runes.WATER_RUNE.id: 4,
            Runes.NATURE_RUNE.id: 2
        },
        widget_id=14286884
    )
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    @classmethod
    def all(cls) -> List[Spell]:
        """Return all spells in standard spellbook."""
        spells = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, Spell):
                    spells.append(attr_value)
        return spells
    
    @classmethod
    def all_combat(cls) -> List[Spell]:
        """Return all combat spells."""
        combat_keywords = ['STRIKE', 'BOLT', 'BLAST', 'WAVE']
        return [s for s in cls.all() if any(k in s.name.upper() for k in combat_keywords)]
    
    @classmethod
    def all_teleports(cls) -> List[Spell]:
        """Return all teleport spells."""
        return [s for s in cls.all() if 'TELEPORT' in s.name.upper()]
    
    @classmethod
    def all_utility(cls) -> List[Spell]:
        """Return all utility spells (alchemy, enchant, etc)."""
        all_spells = cls.all()
        combat = cls.all_combat()
        teleports = cls.all_teleports()
        return [s for s in all_spells if s not in combat and s not in teleports]
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional[Spell]:
        """Find a spell by name (case-insensitive)."""
        name_lower = name.lower()
        for spell in cls.all():
            if spell.name.lower() == name_lower:
                return spell
        return None
    
    @classmethod
    def find_by_id(cls, spell_id: int) -> Optional[Spell]:
        """Find a spell by its ID."""
        for spell in cls.all():
            if spell.id == spell_id:
                return spell
        return None
