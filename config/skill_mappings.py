"""
Centralized skill resource mappings for gathering skills.
Maps skill resources to their game object IDs, item IDs, names, and animation IDs.
"""

from config.game_objects import OreRocks, Trees
from config.items import Ores, Logs, Tools


# =============================================================================
# MINING RESOURCES
# =============================================================================

MINING_RESOURCES = {
    'copper': {
        'object_ids': OreRocks.COPPER_ORE_ROCK.ids,
        'item_id': Ores.COPPER_ORE.id,
        'display_name': 'Copper',
        'mining_animation_id': 628,
        'respawn_time': (2, 3)  # seconds
    },
    'tin': {
        'object_ids': OreRocks.TIN_ORE_ROCK.ids,
        'item_id': Ores.TIN_ORE.id,
        'display_name': 'Tin',
        'mining_animation_id': 628,
        'respawn_time': (2, 3)
    },
    'iron': {
        'object_ids': OreRocks.IRON_ORE_ROCK.ids,
        'item_id': Ores.IRON_ORE.id,
        'display_name': 'Iron',
        'mining_animation_id': 628,
        'respawn_time': (4, 6)
    },
    'coal': {
        'object_ids': OreRocks.COAL_ROCK.ids,
        'item_id': Ores.COAL.id,
        'display_name': 'Coal',
        'mining_animation_id': 628,
        'respawn_time': (30, 40)
    },
    'silver': {
        'object_ids': OreRocks.SILVER_ORE_ROCK.ids,
        'item_id': Ores.SILVER_ORE.id,
        'display_name': 'Silver',
        'mining_animation_id': 628,
        'respawn_time': (60, 100)
    },
    'gold': {
        'object_ids': OreRocks.GOLD_ORE_ROCK.ids,
        'item_id': Ores.GOLD_ORE.id,
        'display_name': 'Gold',
        'mining_animation_id': 628,
        'respawn_time': (60, 100)
    },
    'mithril': {
        'object_ids': OreRocks.MITHRIL_ORE_ROCK.ids,
        'item_id': Ores.MITHRIL_ORE.id,
        'display_name': 'Mithril',
        'mining_animation_id': 628,
        'respawn_time': (120, 180)
    },
    'adamantite': {
        'object_ids': OreRocks.ADAMANTITE_ORE_ROCK.ids,
        'item_id': Ores.ADAMANTITE_ORE.id,
        'display_name': 'Adamantite',
        'mining_animation_id': 628,
        'respawn_time': (180, 240)
    },
    'runite': {
        'object_ids': OreRocks.RUNITE_ORE_ROCK.ids,
        'item_id': Ores.RUNITE_ORE.id,
        'display_name': 'Runite',
        'mining_animation_id': 628,
        'respawn_time': (720, 900)
    }
}

MINING_TOOLS = {
    'bronze_pickaxe': Tools.BRONZE_PICKAXE.id,
    'iron_pickaxe': Tools.IRON_PICKAXE.id,
    'steel_pickaxe': Tools.STEEL_PICKAXE.id,
    'mithril_pickaxe': Tools.MITHRIL_PICKAXE.id,
    'adamant_pickaxe': Tools.ADAMANT_PICKAXE.id,
    'rune_pickaxe': Tools.RUNE_PICKAXE.id,
    'dragon_pickaxe': Tools.DRAGON_PICKAXE.id
}


# =============================================================================
# WOODCUTTING RESOURCES
# =============================================================================

WOODCUTTING_RESOURCES = {
    'normal': {
        'object_ids': Trees.TREE.ids,
        'item_id': Logs.LOGS.id,
        'display_name': 'Normal',
        'woodcutting_animation_id': 879,
        'respawn_time': (5, 10)
    },
    'oak': {
        'object_ids': Trees.OAK_TREE.ids,
        'item_id': Logs.OAK_LOGS.id,
        'display_name': 'Oak',
        'woodcutting_animation_id': 879,
        'respawn_time': (8, 15)
    },
    'willow': {
        'object_ids': Trees.WILLOW_TREE.ids,
        'item_id': Logs.WILLOW_LOGS.id,
        'display_name': 'Willow',
        'woodcutting_animation_id': 879,
        'respawn_time': (8, 15)
    },
    'maple': {
        'object_ids': Trees.MAPLE_TREE.ids,
        'item_id': Logs.MAPLE_LOGS.id,
        'display_name': 'Maple',
        'woodcutting_animation_id': 879,
        'respawn_time': (35, 55)
    },
    'yew': {
        'object_ids': Trees.YEW_TREE.ids,
        'item_id': Logs.YEW_LOGS.id,
        'display_name': 'Yew',
        'woodcutting_animation_id': 867,
        'respawn_time': (60, 90)
    },
    'magic': {
        'object_ids': Trees.MAGIC_TREE.ids,
        'item_id': Logs.MAGIC_LOGS.id,
        'display_name': 'Magic',
        'woodcutting_animation_id': 879,
        'respawn_time': (120, 240)
    }
}

WOODCUTTING_TOOLS = {
    'bronze_axe': Tools.BRONZE_AXE.id,
    'iron_axe': Tools.IRON_AXE.id,
    'steel_axe': Tools.STEEL_AXE.id,
    'mithril_axe': Tools.MITHRIL_AXE.id,
    'adamant_axe': Tools.ADAMANT_AXE.id,
    'rune_axe': Tools.RUNE_AXE.id,
    'dragon_axe': Tools.DRAGON_AXE.id
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_resource_by_object_id(skill: str, object_id: int):
    """
    Find resource info by object ID for a specific skill.
    
    Args:
        skill: Skill name ('mining', 'woodcutting', etc.)
        object_id: Game object ID to search for
    
    Returns:
        Tuple of (resource_name, resource_info) or (None, None)
    """
    skill_lower = skill.lower()
    
    if skill_lower == 'mining':
        resources = MINING_RESOURCES
    elif skill_lower == 'woodcutting':
        resources = WOODCUTTING_RESOURCES
    else:
        return None, None
    
    for resource_name, info in resources.items():
        if object_id in info['object_ids']:
            return resource_name, info
    
    return None, None


def get_all_tool_ids(skill: str) -> list[int]:
    """
    Get all tool IDs for a specific skill.
    
    Args:
        skill: Skill name ('mining', 'woodcutting', etc.)
    
    Returns:
        List of item IDs for all tools of that skill
    """
    skill_lower = skill.lower()
    
    if skill_lower == 'mining':
        return list(MINING_TOOLS.values())
    elif skill_lower == 'woodcutting':
        return list(WOODCUTTING_TOOLS.values())
    
    return []


def get_resource_names(skill: str) -> list[str]:
    """
    Get all resource names for a skill.
    
    Args:
        skill: Skill name ('mining', 'woodcutting', etc.)
    
    Returns:
        List of resource names (e.g., ['copper', 'tin', 'iron'])
    """
    skill_lower = skill.lower()
    
    if skill_lower == 'mining':
        return list(MINING_RESOURCES.keys())
    elif skill_lower == 'woodcutting':
        return list(WOODCUTTING_RESOURCES.keys())
    
    return []
