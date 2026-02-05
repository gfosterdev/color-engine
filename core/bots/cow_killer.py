"""
Cow Killer Bot for Lumbridge.

Kills cows in the Lumbridge east cow pens and banks cowhides at Lumbridge castle top floor.
This is a low-level combat bot suitable for new accounts.
"""

from typing import Any, Callable, List, Dict, Tuple, Optional
from core.combat_bot_base import CombatBotBase, NavigationPath, NavigationStep
from core.config import DEBUG, load_profile
from client.osrs import OSRS
from config.npcs import LowLevelMonsters
from config.items import Item, CookedFish, Armor, Weapons, Jewelry
from config.locations import BankLocations, TrainingLocations
from config.game_objects import StairsAndLadders, DoorsAndGates

# Import Hides directly from items module to avoid circular import
import config.items as items_module


class CowKillerBot(CombatBotBase):
    """
    Combat bot for killing cows in Lumbridge east cow pens.
    
    Features:
    - Kills cows (excluding calves) in east cow pens
    - Loots only cowhides
    - Uses single swordfish for food
    - Banks at Lumbridge castle top floor
    - Navigates through gates and stairs
    - No emergency escape (low-level area)
    """
    
    def __init__(self, profile_name: str = "cow_killer_lumbridge"):
        """
        Initialize cow killer bot.
        
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
        Get list of cow NPC IDs to attack.
        
        Returns:
            List of cow IDs.
        """
        # Get all cow IDs and exclude calf IDs
        all_cow_ids = LowLevelMonsters.COW.ids
        # calf_ids = LowLevelMonsters.COW_CALF.ids
        # adult_cow_ids = [cow_id for cow_id in all_cow_ids if cow_id not in calf_ids]
        return all_cow_ids
    
    def get_combat_area(self) -> Tuple[int, int, int]:
        """
        Get combat area center coordinates (Lumbridge east cow pens).
        
        Returns:
            Tuple of (x, y, plane) world coordinates
        """
        return TrainingLocations.LUMBRIDGE_COWS
    
    def get_loot_items(self) -> List[Item]:
        """
        Get list of items to loot (only cowhides).
        
        Returns:
            List containing only cowhide item
        """
        return [items_module.Hides.COWHIDE, items_module.Bones.BONES]
    
    def get_food_items(self) -> List[Item]:
        """
        Get list of food items (single swordfish).
        
        Returns:
            List containing swordfish item
        """
        return [CookedFish.SWORDFISH]
    
    def get_required_equipment(self) -> Dict[int, int]:
        """
        Get required equipment for fighting cows.
        
        Equipment:
        - Rune full helm
        - Rune platebody
        - Rune platelegs
        - Rune kiteshield
        - Rune scimitar
        - Amulet of strength
        
        Returns:
            Dictionary mapping equipment slot to item ID
        """
        return {
            0: Armor.RUNE_FULL_HELM.id,      # Head
            2: Jewelry.AMULET_OF_STRENGTH.id, # Neck
            3: Weapons.RUNE_SCIMITAR.id,      # Weapon
            4: Armor.RUNE_PLATEBODY.id,       # Body
            5: Armor.RUNE_KITESHIELD.id,      # Shield
            6: Armor.RUNE_PLATELEGS.id,       # Legs
        }
    
    def get_path_to_combat_area(self) -> NavigationPath:
        """
        Get navigation path from Lumbridge castle bank to cow pens.
        
        Path:
        1. Climb down stairs from floor 2 to floor 1
        2. Climb down stairs from floor 1 to floor 0
        3. Walk to cow pen
        4. Open gate to enter cow pen
        
        Returns:
            NavigationPath with steps from bank to combat area
        """
        bank_x, bank_y, bank_plane = BankLocations.LUMBRIDGE_CASTLE
        combat_x, combat_y, combat_plane = TrainingLocations.LUMBRIDGE_COWS
        
        steps = [
            # Start at bank on floor 2
            NavigationStep(
                x=bank_x,
                y=bank_y,
                plane=2
            ),
            # Climb down stairs to floor 1
            NavigationStep(
                x=3205,
                y=3209,
                plane=2,
                object_ids=StairsAndLadders.LUMBRIDGE_CASTLE_STAIRS.ids,
                action_text="Climb-down"
            ),
            # Climb down stairs to ground floor
            NavigationStep(
                x=3205,
                y=3209,
                plane=1,
                object_ids=StairsAndLadders.LUMBRIDGE_CASTLE_STAIRS.ids,
                action_text="Climb-down"
            ),
            # Walk to cow pen gate
            NavigationStep(
                x=3253,
                y=3266,
                plane=0
            ),
            # Open gate to enter cow pen
            NavigationStep(
                x=3251,
                y=3266,
                plane=0,
                object_ids=DoorsAndGates.LUMBRIDGE_COW_PEN_GATE.ids,
                action_text="Open"
            ),
            # Walk to combat area center
            NavigationStep(
                x=combat_x,
                y=combat_y,
                plane=combat_plane
            ),
        ]
        
        return NavigationPath(steps=steps)
    
    def get_path_to_bank(self) -> NavigationPath:
        """
        Get navigation path from cow pens to Lumbridge castle bank.
        
        Path:
        1. Open gate to exit cow pen
        2. Walk to castle
        3. Climb up stairs from floor 0 to floor 1
        4. Climb up stairs from floor 1 to floor 2
        
        Returns:
            NavigationPath with steps from combat area to bank
        """
        combat_x, combat_y, combat_plane = TrainingLocations.LUMBRIDGE_COWS
        bank_x, bank_y, bank_plane = BankLocations.LUMBRIDGE_CASTLE
        
        steps = [
            # Start at combat area
            NavigationStep(
                x=combat_x,
                y=combat_y,
                plane=combat_plane
            ),
            # Walk to gate
            NavigationStep(
                x=3253,
                y=3266,
                plane=0
            ),
            # Open gate to exit
            NavigationStep(
                x=3254,
                y=3266,
                plane=0,
                object_ids=DoorsAndGates.LUMBRIDGE_COW_PEN_GATE.ids,
                action_text="Open"
            ),
            # Walk to castle stairs
            NavigationStep(
                x=3205,
                y=3209,
                plane=0
            ),
            # Climb up stairs to floor 1
            NavigationStep(
                x=3205,
                y=3209,
                plane=0,
                object_ids=StairsAndLadders.LUMBRIDGE_CASTLE_STAIRS.ids,
                action_text="Climb-up"
            ),
            # Climb up stairs to floor 2
            NavigationStep(
                x=3205,
                y=3209,
                plane=1,
                object_ids=StairsAndLadders.LUMBRIDGE_CASTLE_STAIRS.ids,
                action_text="Climb-up"
            ),
            # Walk to bank location
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
            5 - Emergency escape when health drops below 5%
        """
        return 5
    
    def get_escape_teleport_item_id(self) -> Optional[int]:
        """
        Get item ID of emergency teleport item.
        
        Returns:
            None - No emergency teleport needed for cows
        """
        return None
    
    def get_food_threshold(self) -> int:
        """
        Get health percentage threshold for eating during combat.
        
        Returns:
            50 - Eat when health drops below 50%
        """
        return 50
    
    def get_min_food_count(self) -> int:
        """
        Get minimum food count before returning to bank.
        
        Returns:
            1 - Bank when swordfish is eaten
        """
        return 1
    
    def get_required_inventory(self) -> Dict[int, Optional[int]]:
        """
        Get required inventory layout for all 28 slots.
        
        Inventory setup:
        - Slot 1: Swordfish (food)
        - Slots 2-28: Flexible (for looting cowhides)
        
        Returns:
            Dictionary mapping slot number to item ID or None
        """
        inventory = {}
        
        # Slot 1: Swordfish for food
        inventory[1] = CookedFish.SWORDFISH.id
        
        # Slots 2-28: Flexible for cowhide looting
        for slot in range(2, 29):
            inventory[slot] = None
        
        return inventory

    def get_special_loot_actions(self) -> Dict[int, Callable[[Dict[str, Any]], bool]]:
        """
        Get special actions to perform on specific loot items.
        
        For cow killer bot, no special loot actions are needed since we only loot cowhides.
        
        Returns:
            Empty dictionary (no special actions)
        """
        return {
            items_module.Bones.BONES.id: self.bury_bones
        }

    # ========== Special Loot Handlers ==========

    def bury_bones(self, item: Dict[str, Any]) -> bool:
        """
        Bury bones after looting them.
        
        Args:
            item: Dictionary containing item information (id, name, quantity)
        """
        if DEBUG:
            print(f"  → Burying bones: {item['name']}")
        if self.osrs.inventory.count_item(item['id']):
            self.osrs.inventory.click_item(item['id'], "Bury")
            return True
        return False