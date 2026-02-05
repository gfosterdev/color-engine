"""
Gargoyle Killer Bot for Slayer Tower.

Kills gargoyles on the second floor of the Slayer Tower in Canifis.
This is a mid-high level slayer bot requiring 75 Slayer and a rock hammer.
"""

from typing import Callable, List, Dict, Tuple, Optional, Any
import time
import random

from core.combat_bot_base import CombatBotBase, NavigationPath, NavigationStep
from core.config import DEBUG, load_profile
from client.osrs import OSRS
from config.npcs import SlayerMonsters
from config.items import Item, CookedFish, Armor, Weapons, Tools, SlayerDrops, SlayerItems
from config.locations import BankLocations, TrainingLocations
from config.game_objects import StairsAndLadders, DoorsAndGates
from config.spells import StandardSpells


class GargoyleKillerBot(CombatBotBase):
    """
    Combat bot for killing gargoyles at Slayer Tower.
    
    Features:
    - Kills gargoyles on floor 2 of Slayer Tower
    - Requires rock hammer to finish off gargoyles (below 10 HP)
    - Loots valuable drops (granite maul, mystic robes, rune items)
    - Uses sharks or better for food
    - Banks at Canifis
    - Navigates through stairs
    - Emergency teleport on low health (house teleport or ectophial)
    """
    
    def __init__(self, profile_name: str = "gargoyle_killer_canifis"):
        """
        Initialize gargoyle killer bot.
        
        Args:
            profile_name: Configuration profile to load
        """
        config = load_profile(profile_name)
        osrs = OSRS(config)
        
        # Initialize base class
        super().__init__(osrs, config)
        
        self.bot_config = config
    
    def get_target_npc_ids(self) -> List[int]:
        """
        Get list of gargoyle NPC IDs to attack.
        
        Returns:
            List of gargoyle IDs (excludes marble gargoyle superior).
        """
        return SlayerMonsters.GARGOYLE.ids
    
    def get_combat_area(self) -> Tuple[int, int, int]:
        """
        Get combat area center coordinates (Slayer Tower floor 2, gargoyles).
        
        Returns:
            Tuple of (x, y, plane) world coordinates
        """
        return TrainingLocations.SLAYER_TOWER_GARGOYLES
    
    def get_loot_items(self) -> List[Item]:
        """
        Get list of items to loot from gargoyles.
        
        Valuable drops:
        - Granite maul (4153)
        - Mystic robe top (dark) (4101)
        - Mystic robe bottom (dark) (4103)
        - Rune full helm (1163)
        - Rune platelegs (1079)
        - Rune boots (4131)
        - Rune plateskirt (1093)
        - Seeds (ranarr, snapdragon)
        
        Returns:
            List of valuable items to loot
        """
        return [
            Weapons.GRANITE_MAUL,
            SlayerDrops.MYSTIC_ROBE_TOP_DARK,
            SlayerDrops.MYSTIC_ROBE_BOTTOM_DARK,
            SlayerDrops.RUNE_FULL_HELM,
            SlayerDrops.RUNE_PLATELEGS,
            SlayerDrops.RUNE_BOOTS,
            SlayerDrops.RUNE_PLATESKIRT,
            SlayerDrops.RANARR_SEED,
            SlayerDrops.SNAPDRAGON_SEED,
        ]
    
    def get_food_items(self) -> List[Item]:
        """
        Get list of food items (shark or better recommended).
        
        Returns:
            List containing shark item
        """
        return [CookedFish.SWORDFISH]
    
    def get_required_equipment(self) -> Dict[int, int]:
        """
        Get required equipment for fighting gargoyles.
        
        Equipment requirements:
        - Melee combat gear (rune or better)
        - Rock hammer in inventory (required to finish gargoyles)
        
        Equipment setup:
        - Rune full helm
        - Rune platebody
        - Rune platelegs
        - Rune kiteshield
        - Rune scimitar (or better)
        - Amulet of strength (or better)
        
        Returns:
            Dictionary mapping equipment slot to item ID
        """
        return {
            0: SlayerItems.NOSE_PEG.id,      # Head
            # Slot 2: Neck (optional - amulet of strength)
            # 3: Weapons.RUNE_SCIMITAR.id,      # Weapon
            # 4: Armor.RUNE_PLATEBODY.id,       # Body
            # 5: Armor.RUNE_KITESHIELD.id,      # Shield
            # 6: Armor.RUNE_PLATELEGS.id,       # Legs
            # Slot 10: Feet (optional - rune boots)
        }
    
    def get_path_to_combat_area(self) -> NavigationPath:
        """
        Get navigation path from Canifis bank to Slayer Tower gargoyles.
        
        Path:
        1. Exit Canifis bank
        2. Walk to Slayer Tower entrance
        3. Climb stairs to floor 1
        4. Climb stairs to floor 2 (gargoyles)
        
        Returns:
            NavigationPath with steps from bank to combat area
        """
        bank_x, bank_y, bank_plane = BankLocations.CANIFIS
        combat_x, combat_y, combat_plane = TrainingLocations.SLAYER_TOWER_GARGOYLES
        
        steps = [
            # Start at Canifis bank
            NavigationStep(
                x=bank_x,
                y=bank_y,
                plane=bank_plane
            ),
            # Walk to Slayer Tower entrance
            NavigationStep(
                x=3428,
                y=3537,
                plane=0,
                object_ids=DoorsAndGates.SLAYER_TOWER_DOOR.ids,
                action_text="Open"
            ),
            # Walk to ground floor stairs
            NavigationStep(
                x=3439,
                y=3538,
                plane=0
            ),
            # Climb stairs to floor 1
            NavigationStep(
                x=3438,
                y=3538,
                plane=0,
                object_ids=StairsAndLadders.SLAYER_TOWER_STAIRS.ids,
                action_text="Climb-up"
            ),
            # Walk to bloodveld door
            NavigationStep(
                x=3426,
                y=3556,
                plane=1,
                object_ids=DoorsAndGates.SLAYER_TOWER_BLOODVELD_DOOR.ids,
                action_text="Open"
            ),
            # Walk to second stairs & climb to floor 2 (gargoyle area)
            NavigationStep(
                x=3412,
                y=3540,
                plane=1,
                object_ids=StairsAndLadders.SLAYER_TOWER_STAIRS.ids,
                action_text="Climb-up"
            ),
            # Walk to gargoyle area
            NavigationStep(
                x=combat_x,
                y=combat_y,
                plane=combat_plane
            ),
        ]
        
        return NavigationPath(steps=steps)
    
    def get_path_to_bank(self) -> NavigationPath:
        """
        Get navigation path from gargoyle area to Canifis bank.
        
        Path:
        1. Walk to stairs
        2. Climb down to floor 1
        3. Climb down to floor 0
        4. Walk to Canifis bank
        
        Returns:
            NavigationPath with steps from combat area to bank
        """
        combat_x, combat_y, combat_plane = TrainingLocations.SLAYER_TOWER_GARGOYLES
        bank_x, bank_y, bank_plane = BankLocations.CANIFIS
        
        steps = [
            # Start at gargoyle area
            NavigationStep(
                x=combat_x,
                y=combat_y,
                plane=combat_plane
            ),
            # Walk to stairs
            NavigationStep(
                x=3418,
                y=3540,
                plane=2
            ),
            # Climb down to floor 1
            NavigationStep(
                x=3418,
                y=3540,
                plane=2,
                object_ids=StairsAndLadders.SLAYER_TOWER_STAIRS.ids,
                action_text="Climb-down"
            ),
            # Walk to next stairs
            NavigationStep(
                x=3422,
                y=3540,
                plane=1
            ),
            # Climb down to ground floor
            NavigationStep(
                x=3422,
                y=3540,
                plane=1,
                object_ids=StairsAndLadders.SLAYER_TOWER_STAIRS.ids,
                action_text="Climb-down"
            ),
            # Walk to Canifis bank
            NavigationStep(
                x=bank_x,
                y=bank_y,
                plane=bank_plane
            ),
        ]
        
        return NavigationPath(steps=steps)
    
    def get_escape_threshold(self) -> int:
        """
        Get health percentage threshold for emergency escape.
        
        Returns:
            20 - Emergency escape when health drops below 20% (gargoyles hit hard)
        """
        return 20
    
    def get_escape_teleport_item_id(self) -> Optional[int]:
        """
        Get item ID of emergency teleport item.
        
        Returns:
            None - Configure teleport in profile (house tab, ectophial, etc.)
        """
        # User should configure teleport item in their profile
        # Common options:
        # - House teleport tab: 8013
        # - Ectophial: 4251
        return None
    
    def get_food_threshold(self) -> int:
        """
        Get health percentage threshold for eating during combat.
        
        Returns:
            60 - Eat when health drops below 60% (gargoyles deal good damage)
        """
        return 60
    
    def get_min_food_count(self) -> int:
        """
        Get minimum food count before returning to bank.
        
        Returns:
            3 - Bank when only 3 sharks remaining
        """
        return 3
    
    def get_required_inventory(self) -> Dict[int, Optional[int]]:
        """
        Get required inventory layout for all 28 slots.
        
        Inventory setup:
        - Slot 1: Rock hammer (REQUIRED - to finish gargoyles)
        - Slots 2-8: Sharks (7 food items)
        - Slots 9-28: Flexible (for looting)
        
        Returns:
            Dictionary mapping slot number to item ID or None
        """
        inventory = {}
        
        # Slot 1: Rock hammer (REQUIRED)
        inventory[1] = Tools.ROCK_HAMMER.id
        
        # Slots 2-16: Karambwans for food (15 total)
        for slot in range(2, 17):
            inventory[slot] = CookedFish.SWORDFISH.id
        
        # Slots 17-28: Flexible for loot
        for slot in range(17, 29):
            inventory[slot] = None
        
        return inventory

    def get_special_loot_actions(self) -> Dict[int, Callable[[Dict[str, Any]], bool]]:
        """
        Get special actions to perform on specific loot items.
        
        Returns:
            Empty dictionary (no special actions)
        """
        return {
            SlayerDrops.RUNE_FULL_HELM.id: self.alch_item,
        }

    # ========== Special Loot Handlers ==========

    def alch_item(self, item: Dict[str, Any]) -> bool:
        """
        Alch a specific item immediately after looting.
        
        Args:
            item: Dictionary containing item information (id, name, quantity)
        """
        spell = StandardSpells.HIGH_LEVEL_ALCHEMY

        # Check if can cast
        if not self.osrs.magic.can_cast_spell(spell):
            if DEBUG:
                print(f"Cannot alch {item['name']} - insufficient magic level or runes")
            return False

        # Cast alchemy on the item
        if not self.osrs.magic.cast_spell_on_item(spell, item.get('id')):
            if DEBUG:
                print(f"Failed to cast alchemy on {item['name']}")
            return False
        return True
