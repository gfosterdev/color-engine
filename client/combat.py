"""
Combat management system for OSRS bot.

Handles all combat-related operations including engaging NPCs,
monitoring health/prayer, consuming food/potions, and tracking combat state.
"""

from typing import Dict, List, Optional, Union, Any
import time
import random
from config.timing import TIMING
from core.config import DEBUG


class CombatHandler:
    """
    Manages all combat-related operations.
    
    Uses RuneLite API for real-time combat state and NPC data.
    Integrates with OSRS class for entity interaction and inventory management.
    """
    
    def __init__(self, osrs_instance):
        """
        Initialize combat handler with reference to OSRS instance.
        
        Args:
            osrs_instance: Reference to OSRS class instance for API and helper access
        """
        self.osrs = osrs_instance
        self.window = osrs_instance.window
        self.api = osrs_instance.api
        self.interfaces = osrs_instance.interfaces
        self.inventory = osrs_instance.inventory
        self.keyboard = osrs_instance.keyboard
    
    # ========== Player State Methods ==========
    
    def get_health(self) -> Optional[int]:
        """
        Get player's current health points.
        
        Returns:
            Current HP or None on error
        """
        player_data = self.api.get_player()
        if player_data:
            return player_data.get('health')
        return None
    
    def get_max_health(self) -> Optional[int]:
        """
        Get player's maximum health points.
        
        Returns:
            Max HP or None on error
        """
        player_data = self.api.get_player()
        if player_data:
            return player_data.get('maxHealth')
        return None
    
    def get_health_percent(self) -> Optional[int]:
        """
        Get player's health as a percentage.
        
        Returns:
            Health percentage (0-100) or None on error
        """
        health = self.get_health()
        max_health = self.get_max_health()
        if health is not None and max_health is not None and max_health > 0:
            return int((health / max_health) * 100)
        return None
    
    def get_prayer(self) -> Optional[int]:
        """
        Get player's current prayer points.
        
        Returns:
            Current prayer points or None on error
        """
        player_data = self.api.get_player()
        if player_data:
            return player_data.get('prayer')
        return None
    
    def get_max_prayer(self) -> Optional[int]:
        """
        Get player's maximum prayer points.
        
        Returns:
            Max prayer points or None on error
        """
        player_data = self.api.get_player()
        if player_data:
            return player_data.get('maxPrayer')
        return None
    
    def get_prayer_percent(self) -> Optional[int]:
        """
        Get player's prayer as a percentage.
        
        Returns:
            Prayer percentage (0-100) or None on error
        """
        prayer = self.get_prayer()
        max_prayer = self.get_max_prayer()
        if prayer is not None and max_prayer is not None and max_prayer > 0:
            return int((prayer / max_prayer) * 100)
        return None
    
    def get_special_attack(self) -> Optional[int]:
        """
        Get player's special attack energy.
        
        Returns:
            Special attack energy (0-100) or None on error
        """
        player_data = self.api.get_player()
        if player_data:
            return player_data.get('specialAttack')
        return None
    
    # ========== Combat State Methods ==========
    
    def is_player_in_combat(self) -> bool:
        """
        Check if player is currently in combat.
        
        Returns:
            True if player is in combat, False otherwise
        """
        combat_data = self.api.get_combat()
        if combat_data:
            return combat_data.get('inCombat', False)
        return False
    
    def get_current_target(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current target.
        
        Returns:
            Dictionary with target info (name, id, combatLevel, health, maxHealth, isDying)
            or None if no target
        """
        combat_data = self.api.get_combat()
        if combat_data:
            return combat_data.get('target')
        return None
    
    def get_target_health_percent(self) -> Optional[int]:
        """
        Get current target's health as a percentage.
        
        Returns:
            Target health percentage (0-100) or None if no target or health unavailable
        """
        target = self.get_current_target()
        if target:
            health = target.get('health')
            max_health = target.get('maxHealth')
            if health is not None and max_health is not None and max_health > 0:
                return int((health / max_health) * 100)
        return None
    
    def is_target_alive(self) -> bool:
        """
        Check if current target is still alive.
        
        Returns:
            True if target exists and is not dying, False otherwise
        """
        target = self.get_current_target()
        if target:
            return not target.get('isDying', False)
        return False
    
    def is_npc_in_combat(self, npc_id: Union[int, List[int]]) -> Optional[Dict[str, Any]]:
        """
        Check if an NPC is in combat with another entity (not the player).
        This is useful to determine if an NPC is available to attack.
        
        Args:
            npc_id: Single NPC ID or list of NPC IDs to check
            
        Returns:
            Dictionary with NPC data if found and not in combat with player,
            None if NPC not found or already engaged with player
        """
        if not self.window.window:
            return None
        
        # Normalize to list
        if isinstance(npc_id, int):
            npc_ids = [npc_id]
        else:
            npc_ids = npc_id
        
        # Get player name for comparison
        player_data = self.api.get_player()
        if not player_data:
            return None
        player_name = player_data.get('name')
        
        # Get NPCs in viewport with Actor data
        npcs = self.api.get_npcs_in_viewport()
        if not npcs:
            return None
        
        for npc in npcs:
            # Check if NPC matches target ID(s)
            if npc.get('id') not in npc_ids:
                continue
            
            # Check if NPC is interacting with anything
            interacting_with = npc.get('interactingWith')
            
            # If NPC is not interacting with anyone, it's available
            if interacting_with is None:
                return npc
            
            # If NPC is interacting with the player, skip it
            if interacting_with == player_name:
                continue
            
            # If NPC is interacting with something else (another player/NPC), skip it
            # We only want NPCs that are free or already fighting us
            
        return None
    
    # ========== Threshold Helpers ==========
    
    def should_eat(self, threshold_percent: int = 50) -> bool:
        """
        Check if player health is below threshold.
        
        Args:
            threshold_percent: Health percentage threshold (default: 50)
            
        Returns:
            True if health is below threshold, False otherwise
        """
        health_percent = self.get_health_percent()
        if health_percent is not None:
            return health_percent < threshold_percent
        return False
    
    def should_drink_prayer(self, threshold_percent: int = 25) -> bool:
        """
        Check if player prayer is below threshold.
        
        Args:
            threshold_percent: Prayer percentage threshold (default: 25)
            
        Returns:
            True if prayer is below threshold, False otherwise
        """
        prayer_percent = self.get_prayer_percent()
        if prayer_percent is not None:
            return prayer_percent < threshold_percent
        return False
    
    # ========== Combat Actions ==========
    
    def engage_npc(self, npc_id: Union[int, List[int]], attack_option: str = "Attack") -> bool:
        """
        Engage an NPC in combat.
        
        Filters out NPCs already in combat with other players before attempting to attack.
        Uses osrs.find_entity() to locate NPC with camera adjustment if needed.
        Uses osrs.click() for menu validation and interaction.
        
        Args:
            npc_id: Single NPC ID or list of NPC IDs to attack
            attack_option: Attack option text (default: "Attack")
            
        Returns:
            True if successfully clicked NPC, False otherwise
        """
        if not self.window.window:
            return False
        
        # Normalize to list
        if isinstance(npc_id, int):
            npc_ids = [npc_id]
        else:
            npc_ids = npc_id
        
        # Use osrs.find_entity to locate and make NPC visible (with camera adjustment)
        found_entity = self.osrs.find_entity(npc_ids, "npc")
        if not found_entity:
            return False
    
        # Click on NPC to attack
        if not self.osrs.click_entity(found_entity, "npc", attack_option):
            if DEBUG:
                print(f"Failed to click on NPC ID(s) {npc_ids} to engage in combat")
            return False
        
        # Wait for initial movement/action to start
        time.sleep(random.uniform(*TIMING.COMBAT_ENGAGE_WAIT))
        
        # Wait for player to stop moving (if they started moving toward the NPC)
        if not self._wait_for_player_to_stop_moving(timeout=5.0):
            if DEBUG:
                print(f"Player did not stop moving after clicking NPC ID(s) {npc_ids}")
            # Continue anyway as this might be due to already being in range

        # Check if player is now in combat
        if not self.is_player_in_combat():
            if DEBUG:
                print(f"Failed to engaged NPC ID(s) {npc_ids} in combat")
            return False
        
        return True
    
    def eat_food(self, item_id: int) -> bool:
        """
        Eat food from inventory.
        
        Args:
            item_id: Item ID of the food to eat
            
        Returns:
            True if successfully ate food, False otherwise
        """
        if not self.window.window:
            return False
        
        # Use inventory manager to click the food item
        success = self.inventory.click_item(item_id, "Eat")
        
        if success:
            # Wait for eating animation/game tick
            time.sleep(random.uniform(*TIMING.COMBAT_FOOD_DELAY))
        
        return success
    
    def drink_potion(self, item_id: int) -> bool:
        """
        Drink a potion from inventory.
        
        Args:
            item_id: Item ID of the potion to drink
            
        Returns:
            True if successfully drank potion, False otherwise
        """
        if not self.window.window:
            return False
        
        # Use inventory manager to click the potion
        success = self.inventory.click_item(item_id, "Drink")
        
        if success:
            # Wait for drinking animation
            time.sleep(random.uniform(*TIMING.COMBAT_POTION_DELAY))
        
        return success
    
    # ========== Wait Methods ==========
    
    def _wait_for_player_to_stop_moving(self, timeout: float = 5.0) -> bool:
        """
        Wait for the player to stop moving.
        
        Args:
            timeout: Maximum time to wait in seconds (default: 5)
            
        Returns:
            True if player stopped moving within timeout, False if timed out
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            animation_data = self.api.get_animation()
            if animation_data:
                # If not moving, we're done
                if not animation_data.get('isMoving', False):
                    return True
            else:
                # If we can't get animation data, assume player stopped
                return True
            
            # Small delay before checking again
            time.sleep(random.uniform(0.05, 0.1))
        
        return False
    
    def wait_until_not_in_combat(self, timeout: float = 60.0) -> bool:
        """
        Wait until player is no longer in combat.
        
        Args:
            timeout: Maximum time to wait in seconds (default: 60)
            
        Returns:
            True if combat ended within timeout, False if timed out
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.is_player_in_combat():
                return True
            time.sleep(random.uniform(*TIMING.API_POLL_INTERVAL))
        
        return False
    
    def wait_until_target_dead(self, timeout: float = 60.0) -> bool:
        """
        Wait until current target dies.
        
        Uses isDying flag from API for accurate detection.
        
        Args:
            timeout: Maximum time to wait in seconds (default: 60)
            
        Returns:
            True if target died within timeout, False if timed out or no target
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            target = self.get_current_target()
            
            # No target means it's dead or we lost aggro
            if not target:
                time.sleep(random.uniform(*TIMING.COMBAT_DEATH_DETECT))
                # Double-check it's really gone
                if not self.get_current_target():
                    return True
            
            # Check isDying flag
            if target and target.get('isDying', False):
                time.sleep(random.uniform(*TIMING.COMBAT_DEATH_DETECT))
                return True
            
            time.sleep(random.uniform(*TIMING.API_POLL_INTERVAL))
        
        return False
    
    def wait_for_loot(self, target_x: int, target_y: int, timeout: float = 10.0, radius: int = 3) -> Optional[List[Dict[str, Any]]]:
        """
        Wait for loot to appear at target's death location.
        
        Polls ground items at specified coordinates until items appear or timeout.
        Useful for detecting NPC death drops before attempting to pick them up.
        
        Args:
            target_x: World X coordinate of target's death location
            target_y: World Y coordinate of target's death location
            timeout: Maximum time to wait in seconds (default: 10)
            radius: Search radius in tiles around target location (default: 3)
            
        Returns:
            List of ground item dictionaries if loot appears, None if timed out
            
        Example:
            # Get target position before it dies
            target = combat.get_current_target()
            if target and 'position' in target:
                pos = target['position']
                # Wait for target to die
                if combat.wait_until_target_dead():
                    # Wait for loot to appear
                    loot = combat.wait_for_loot(pos['x'], pos['y'], timeout=10, radius=3)
                    if loot:
                        print(f"Found {len(loot)} items!")
        """
        start_time = time.time()
        
        if DEBUG:
            print(f"[Combat] Waiting for loot at ({target_x}, {target_y}) with radius {radius}...")
        
        while time.time() - start_time < timeout:
            # Check for ground items at target location
            loot = self.api.get_ground_items(x=target_x, y=target_y, radius=radius)
            
            if loot and len(loot) > 0:
                if DEBUG:
                    print(f"[Combat] Found {len(loot)} items at loot location!")
                return loot
            
            time.sleep(random.uniform(*TIMING.API_POLL_INTERVAL))
        
        if DEBUG:
            print(f"[Combat] No loot appeared within {timeout}s timeout")
        
        return None
