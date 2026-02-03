"""
Woodcutting skill bot implementation using reusable utility components.

Autonomous woodcutting bot that cuts trees, banks when inventory is full,
and returns to cutting location using RuneLite API for object detection
and pathfinding for navigation.
"""

from typing import Optional, Dict
from client.osrs import OSRS
from core.skill_bot_base import SkillBotBase
from core.state_machine import BotState
from core.config import load_profile, DEBUG
from config.timing import TIMING
from config.skill_mappings import WOODCUTTING_RESOURCES, get_all_tool_ids
from config.locations import WoodcuttingLocations, BankLocations
from config.items import BirdsNests
import time
import random


class WoodcuttingBot(SkillBotBase):
    """
    Autonomous woodcutting bot using RuneLite API and reusable skill bot components.
    
    Features:
    - Extends SkillBotBase for common gathering bot functionality
    - Uses API-based object detection for tree finding
    - Uses SkillTracker for XP monitoring
    - Uses RespawnDetector for efficient tree respawn detection
    - Supports multiple tree types with automatic distance-based selection
    - Intelligent respawn tracking with tree depletion detection
    """
    
    def __init__(self, profile_name: str = "yew_cutter_edgeville"):
        """
        Initialize woodcutting bot.
        
        Args:
            profile_name: Configuration profile to load
        """
        config = load_profile(profile_name)
        osrs = OSRS(config)
        
        # Initialize base class with full config
        super().__init__(osrs, config)
        
        self.bot_config = config
        
        # Get tree configuration
        tree_type = self.bot_config.skill_settings.get("tree_type", "yew")
        
        # Support multiple tree types from profile
        tree_types = self.bot_config.skill_settings.get("trees", [tree_type])
        self.tree_configs = []
        
        for tree_name in tree_types:
            tree_clean = tree_name.lower().replace("_logs", "").replace("_", "")
            if tree_clean in WOODCUTTING_RESOURCES:
                resource = WOODCUTTING_RESOURCES[tree_clean]
                self.tree_configs.append({
                    "tree_ids": resource['object_ids'],
                    "item_id": resource['item_id'],
                    "name": resource['display_name'],
                    "animation_id": resource['woodcutting_animation_id'],
                    "respawn_time": resource['respawn_time']
                })
        
        if not self.tree_configs:
            raise ValueError(f"No valid tree types found in profile. Available: {list(WOODCUTTING_RESOURCES.keys())}")
        
        # Primary tree config
        self.primary_tree = self.tree_configs[0]
        if DEBUG:
            print(f"Configured trees: {[cfg['name'] for cfg in self.tree_configs]}")
        
        # Get behavior settings
        self.should_bank = self.bot_config.skill_settings.get("banking", True)
        self.powerdrop = self.bot_config.skill_settings.get("powerdrop", False)
        
        # Resolve locations from config
        wc_location_str = self.bot_config.skill_settings.get("location", "edgeville_yews")
        bank_location_str = self.bot_config.skill_settings.get("bank_location", "edgeville")
        
        self.wc_location = WoodcuttingLocations.find_by_name(wc_location_str.upper().replace(" ", "_"))
        self.bank_location = BankLocations.find_by_name(bank_location_str.upper().replace(" ", "_"))
        
        if not self.wc_location:
            raise ValueError(f"Could not resolve woodcutting location: {wc_location_str}")
        if self.should_bank and not self.bank_location:
            raise ValueError(f"Banking enabled but could not resolve bank location: {bank_location_str}")
        
        if DEBUG:
            print(f"Woodcutting location: {self.wc_location}")
            print(f"Bank location: {self.bank_location}")
        
        # Statistics
        self.logs_cut = 0
        self.banking_trips = 0
        
        # Nest tracking (birds nests can drop while woodcutting)
        self.nests_collected = 0
    
    # =============================================================================
    # ABSTRACT METHOD IMPLEMENTATIONS (required by SkillBotBase)
    # =============================================================================
    
    def _gather_resource(self):
        """
        Cut one tree using API and respawn detector.
        Implements SkillBotBase abstract method.
        """
        # Get all tree IDs we're looking for
        tree_ids = []
        for cfg in self.tree_configs:
            tree_ids.extend(cfg["tree_ids"])
        
        # Find nearest tree in viewport
        nearest_tree = self.osrs.find_entity(tree_ids, "object")
        
        if not nearest_tree:
            if DEBUG:
                print("No trees available")
            time.sleep(1)
            return
        
        # Determine tree name for logging
        tree_id = nearest_tree.get('id')
        tree_name = "Tree"
        for cfg in self.tree_configs:
            if tree_id in cfg["tree_ids"]:
                tree_name = cfg["name"]
                break
        
        if DEBUG:
            print(f"Chopping {tree_name}...")
        
        # Get current log count before cutting
        log_item_id = None
        for cfg in self.tree_configs:
            if tree_id in cfg["tree_ids"]:
                log_item_id = cfg["item_id"]
                break
        
        # Populate inventory and count logs before cutting
        self.osrs.inventory.populate()
        logs_before = self.osrs.inventory.count_item(log_item_id) if log_item_id else 0
        
        # Click the tree (handles all interaction logic)
        if not self.osrs.click_entity(nearest_tree, "object", "Chop down"):
            if DEBUG:
                print("Failed to click tree")
            return

        

        # Wait for tree depletion using respawn detector
        if self.detect_respawn and self.respawn_detector and tree_id:
            self.respawn_detector.wait_for_respawn(
                tree_id,
                nearest_tree['worldX'],
                nearest_tree['worldY'],
                max_wait=60.0,  # Trees take longer than rocks
                use_animation=self.use_animation
            )
        else:
            # Simple delay if not using detection
            time.sleep(random.uniform(2.0, 4.0))
        
        # Count logs obtained from this tree
        self.osrs.inventory.populate()
        logs_after = self.osrs.inventory.count_item(log_item_id) if log_item_id else 0
        logs_obtained = logs_after - logs_before
        
        if logs_obtained > 0:
            self.logs_cut += logs_obtained
            if DEBUG:
                print(f"✓ Obtained {logs_obtained} {tree_name} logs (Total: {self.logs_cut})")
        else:
            if DEBUG:
                print(f"⚠ No logs obtained from {tree_name}")
    
    def _get_skill_name(self) -> str:
        """Get skill name. Implements SkillBotBase abstract method."""
        return "Woodcutting"
    
    def _get_tool_ids(self) -> list[int]:
        """Get axe item IDs. Implements SkillBotBase abstract method."""
        return get_all_tool_ids('woodcutting')
    
    def _get_resource_info(self) -> Dict:
        """Get primary tree resource info. Implements SkillBotBase abstract method."""
        return {
            'object_ids': self.primary_tree['tree_ids'],
            'item_id': self.primary_tree['item_id'],
            'animation_id': self.primary_tree.get('animation_id', 867),
            'respawn_time': self.primary_tree.get('respawn_time', (60, 90))
        }
    
    # =============================================================================
    # STATUS LINE OVERRIDES
    # =============================================================================
    
    def _get_status_info(self) -> Dict:
        """Override to add woodcutting-specific status information."""
        # Get base status info
        base_info = super()._get_status_info()
        
        # Update resources with logs count
        base_info['resources'] = self.logs_cut
        
        # Add woodcutting-specific info
        base_info['logs_cut'] = self.logs_cut
        base_info['banking_trips'] = self.banking_trips
        base_info['nests'] = self.nests_collected
        
        return base_info
    
    def _format_status_line(self, status_info: Dict) -> str:
        """Override to format woodcutting-specific status line."""
        return (
            f"State: {status_info['state']:12} | "
            f"Inv: {status_info['inventory']:5} | "
            f"Logs: {status_info['logs_cut']:4} | "
            f"Banks: {status_info['banking_trips']:3} | "
            f"Nests: {status_info['nests']:2} | "
            f"Time: {status_info['runtime']}"
        )
    
    # =============================================================================
    # CUSTOM METHODS
    # =============================================================================
    
    def _get_bank_location(self) -> Optional[tuple]:
        """Return configured bank location."""
        return self.bank_location
    
    def _get_gathering_location(self) -> Optional[tuple]:
        """Return configured woodcutting location."""
        return self.wc_location
    
    def _handle_banking(self):
        """Override banking to use log-specific item ID and handle birds nests."""
        # If bank is already open, proceed to deposit
        if self.osrs.interfaces.is_bank_open():
            # Check for birds nests before depositing (for tracking)
            nest_ids = BirdsNests.all()
            for nest_id in nest_ids:
                nest_count = self.osrs.inventory.count_item(nest_id)
                if nest_count > 0:
                    self.nests_collected += nest_count
                    if DEBUG:
                        print(f"✓ Found {nest_count} birds nest(s) in inventory")
            
            # Deposit everything
            self.osrs.bank.deposit_all()
            if DEBUG:
                print("✓ Deposited all items")
            
            time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))
            
            # Close bank
            self.osrs.bank.close()
            time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
            
            self.banking_trips += 1
            
            # Walk back to gathering location (base class handles this)
            gathering_location = self._get_gathering_location()
            if gathering_location and not self._is_near_location(gathering_location, tolerance=10):
                if DEBUG:
                    print("Walking back to woodcutting location...")
                self._start_walking(gathering_location, BotState.GATHERING)
            else:
                # Already at location
                self.current_state = BotState.GATHERING
            return
        
        # Bank not open - check if we need to walk to bank first
        bank_location = self._get_bank_location()
        
        if bank_location and not self._is_near_location(bank_location, tolerance=10):
            # Need to walk to bank
            if DEBUG:
                print("Walking to bank...")
            self._start_walking(bank_location, BotState.BANKING)
        else:
            # Already near bank, try to open it
            if DEBUG:
                print("Opening bank...")
            if self.osrs.bank.open():
                if DEBUG:
                    print("✓ Bank opened")
            else:
                if DEBUG:
                    print("✗ Failed to open bank")
                time.sleep(2)
    
    def _handle_powerdrop(self):
        """Override to drop multiple log types from tree configs."""
        if DEBUG:
            print("Inventory full - dropping logs...")
        
        # Drop all log types
        for cfg in self.tree_configs:
            item_id = cfg['item_id']
            dropped = self.osrs.inventory.drop_all(item_id)
            if dropped > 0 and DEBUG:
                print(f"✓ Dropped {dropped} {cfg['name']} logs")
        
        time.sleep(random.uniform(0.5, 1.0))
    
    def stop(self):
        """Override stop to print woodcutting-specific statistics."""
        super().stop()
        
        # Print additional woodcutting stats
        print(f"\nLogs Cut: {self.logs_cut}")
        print(f"Banking Trips: {self.banking_trips}")
        print(f"Birds Nests Collected: {self.nests_collected}")


# Example usage
if __name__ == "__main__":
    bot = WoodcuttingBot("yew_cutter_edgeville")
    bot.start()
