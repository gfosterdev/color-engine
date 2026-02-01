"""
Mining skill bot implementation using reusable utility components.

Autonomous mining bot that mines ore, banks when inventory is full,
and returns to mining location using RuneLite API for object detection
and pathfinding for navigation.
"""

from typing import Optional, Dict
from client.osrs import OSRS
from core.skill_bot_base import SkillBotBase
from core.state_machine import BotState
from core.config import load_profile
from config.timing import TIMING
from config.skill_mappings import MINING_RESOURCES, get_all_tool_ids
from config.locations import MiningLocations, BankLocations
from util.types import Polygon
import time
import random


class MiningBot(SkillBotBase):
    """
    Autonomous mining bot using RuneLite API and reusable skill bot components.
    
    Features:
    - Extends SkillBotBase for common gathering bot functionality
    - Uses ResourceManager for rock prioritization and depletion tracking
    - Uses SkillTracker for XP monitoring
    - Uses RespawnDetector for efficient ore respawn detection
    - Supports multiple ore types with automatic distance-based selection
    """
    
    def __init__(self, profile_name: str = "iron_miner_varrock"):
        """
        Initialize mining bot.
        
        Args:
            profile_name: Configuration profile to load
        """
        config = load_profile(profile_name)
        osrs = OSRS(config)
        
        # Initialize base class
        super().__init__(osrs, config.skill_settings)
        
        self.config = config
        
        # Get ore configuration
        ore_type = self.config.skill_settings.get("ore_type", "iron")
        
        # Support multiple rocks from profile
        rock_types = self.config.skill_settings.get("rocks", [ore_type])
        self.rock_configs = []
        
        for rock_name in rock_types:
            rock_clean = rock_name.lower().replace("_ore", "").replace("_", "")
            if rock_clean in MINING_RESOURCES:
                resource = MINING_RESOURCES[rock_clean]
                self.rock_configs.append({
                    "rock_ids": resource['object_ids'],
                    "item_id": resource['item_id'],
                    "name": resource['display_name'],
                    "animation_id": resource['mining_animation_id'],
                    "respawn_time": resource['respawn_time']
                })
        
        if not self.rock_configs:
            raise ValueError(f"No valid ore types found in profile. Available: {list(MINING_RESOURCES.keys())}")
        
        # Primary ore config
        self.primary_ore = self.rock_configs[0]
        print(f"Configured ores: {[cfg['name'] for cfg in self.rock_configs]}")
        
        # Get behavior settings
        self.should_bank = self.config.skill_settings.get("banking", True)
        self.powermine = self.config.skill_settings.get("powermine", False)
        
        # Resolve locations from config
        mine_location_str = self.config.skill_settings.get("location", "varrock_west_mine")
        bank_location_str = self.config.skill_settings.get("bank_location", "varrock_west_bank")
        
        self.mine_location = MiningLocations.find_by_name(mine_location_str.upper().replace(" ", "_"))
        self.bank_location = BankLocations.find_by_name(bank_location_str.upper().replace(" ", "_"))
        
        if not self.mine_location:
            raise ValueError(f"Could not resolve mining location: {mine_location_str}")
        if self.should_bank and not self.bank_location:
            raise ValueError(f"Banking enabled but could not resolve bank location: {bank_location_str}")
        
        print(f"Mine location: {self.mine_location}")
        print(f"Bank location: {self.bank_location}")
        
        # Statistics
        self.ores_mined = 0
        self.banking_trips = 0
    
    # =============================================================================
    # ABSTRACT METHOD IMPLEMENTATIONS (required by SkillBotBase)
    # =============================================================================
    
    def _gather_resource(self):
        """
        Mine one ore using resource manager and respawn detector.
        Implements SkillBotBase abstract method.
        """
        if not self.resource_manager:
            print("Resource manager not initialized")
            return
        
        # Find nearest rock using resource manager
        nearest_rock = self.resource_manager.find_nearest_node(exclude_depleted=True)
        
        if not nearest_rock:
            print("No rocks available")
            time.sleep(1)
            return
        
        # Determine ore name
        rock_id = nearest_rock.get('id')
        ore_name = "Ore"
        for cfg in self.rock_configs:
            if rock_id in cfg["rock_ids"]:
                ore_name = cfg["name"]
                break
        
        # Get convex hull polygon for clicking
        if 'convexHull' not in nearest_rock:
            print("Rock missing convex hull data")
            return
        
        polygon = self.osrs.window.convex_hull_to_polygon(nearest_rock['convexHull'])
        
        # Move mouse to random point on rock
        self.osrs.window.move_mouse_to(polygon.random_point())
        time.sleep(random.uniform(0.1, 0.3))
        
        # Validate "Mine" option
        if not self.osrs.validate_interact_text("Mine"):
            print("Mine option not found")
            return
        
        # Click rock
        self.osrs.window.click()
        print(f"Mining {ore_name}...")
        
        # Mark rock as depleted
        self.resource_manager.mark_node_depleted(nearest_rock['x'], nearest_rock['y'])
        
        # Wait for ore depletion using respawn detector
        if self.detect_respawn and self.respawn_detector and rock_id:
            self.respawn_detector.wait_for_respawn(
                rock_id,
                nearest_rock['x'],
                nearest_rock['y'],
                max_wait=10.0,
                use_animation=self.use_animation
            )
        else:
            # Simple delay if not using detection
            time.sleep(random.uniform(1.5, 3.0))
        
        self.ores_mined += 1
        print(f"✓ Mined ore (Total: {self.ores_mined})")
    
    def _get_skill_name(self) -> str:
        """Get skill name. Implements SkillBotBase abstract method."""
        return "Mining"
    
    def _get_tool_ids(self) -> list[int]:
        """Get pickaxe item IDs. Implements SkillBotBase abstract method."""
        return get_all_tool_ids('mining')
    
    def _get_resource_info(self) -> Dict:
        """Get primary ore resource info. Implements SkillBotBase abstract method."""
        return {
            'object_ids': self.primary_ore['rock_ids'],
            'item_id': self.primary_ore['item_id'],
            'animation_id': self.primary_ore.get('animation_id', 628),
            'respawn_time': self.primary_ore.get('respawn_time', (5, 10))
        }
    
    # =============================================================================
    # CUSTOM METHODS
    # =============================================================================
    
    def _handle_banking(self):
        """Override banking to use ore-specific item ID."""
        # Check if at bank
        if not self.osrs.interfaces.is_bank_open():
            # Walk to bank
            print("Walking to bank...")
            bank_location = self.config.skill_settings.get('bank_location', 'varrock_west_bank')
            
            if self.osrs.open_bank(location_name=bank_location):
                print("✓ Bank opened")
            else:
                print("✗ Failed to open bank")
                time.sleep(2)
                return
        
        # Deposit all ores
        for cfg in self.rock_configs:
            item_id = cfg['item_id']
            if self.osrs.inventory.deposit_all(item_id):
                print(f"✓ Deposited {cfg['name']}")
        
        time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))
        
        # Close bank
        self.osrs.interfaces.close_interface()
        time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
        
        self.banking_trips += 1
        
        # Return to gathering
        self.current_state = BotState.MINING
    
    def stop(self):
        """Override stop to print mining-specific statistics."""
        super().stop()
        
        # Print additional mining stats
        print(f"\nOres Mined: {self.ores_mined}")
        print(f"Banking Trips: {self.banking_trips}")
        if self.resource_manager:
            print(f"Depleted Rocks Tracked: {self.resource_manager.get_depleted_count()}")


# Example usage
if __name__ == "__main__":
    bot = MiningBot("iron_miner_varrock")
    bot.start()
