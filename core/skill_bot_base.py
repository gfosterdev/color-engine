"""
Base class for gathering skill bots (mining, woodcutting, fishing, etc.).
Provides common functionality and structure for all resource-gathering bots.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import time
import random
from core.state_machine import BotState
from core.anti_ban import AntiBanManager
from client.skill_tracker import SkillTracker
from client.respawn_detector import RespawnDetector
from config.timing import TIMING


class SkillBotBase(ABC):
    """
    Abstract base class for gathering skill bots.
    
    Provides:
    - State management
    - XP tracking
    - Resource management
    - Tool verification
    - Banking logic
    - Anti-ban integration
    
    Subclasses must implement:
    - _gather_resource()
    - _get_skill_name()
    - _get_tool_ids()
    """
    
    def __init__(self, osrs, profile_config: dict):
        """
        Initialize skill bot.
        
        Args:
            osrs: OSRS instance
            profile_config: Bot configuration dictionary
        """
        self.osrs = osrs
        self.api = osrs.api
        self.config = profile_config
        
        # State management
        self.current_state = BotState.IDLE
        self.is_running = False
        
        # Navigation state
        self.walking_destination = None  # (x, y, z) world coordinates
        self.walking_next_state = None   # State to transition to after walking
        
        # Components - will be initialized in setup()
        self.skill_tracker: Optional[SkillTracker] = None
        self.respawn_detector: Optional[RespawnDetector] = None
        
        # Anti-ban (optional if config not provided)
        try:
            if hasattr(osrs, 'anti_ban'):
                self.anti_ban = osrs.anti_ban
            else:
                self.anti_ban = None
        except:
            self.anti_ban = None
        
        # Validation config
        self.validate_tool = self.config.get('validation', {}).get('verify_pickaxe', False)
        self.track_xp = self.config.get('validation', {}).get('track_xp', False)
        self.detect_respawn = self.config.get('validation', {}).get('detect_respawn', False)
        self.use_animation = self.config.get('validation', {}).get('use_animation_detection', True)
        
        # Behavior config
        self.powerdrop = self.config.get('powerdrop', False)
        self.should_bank = self.config.get('banking', True)
    
    def setup(self) -> bool:
        """
        Initialize bot components and validate setup.
        
        Returns:
            True if setup successful, False otherwise
        """
        print(f"\n{'='*50}")
        print(f"Setting up {self._get_skill_name()} bot...")
        print(f"{'='*50}\n")
        
        # Verify tool equipped
        if self.validate_tool:
            if not self._verify_tool():
                return False
        
        # Initialize XP tracker
        if self.track_xp:
            self.skill_tracker = SkillTracker(self._get_skill_name(), self.api)
            if not self.skill_tracker.start_tracking():
                print("✗ Failed to initialize XP tracking")
                return False
        
        # Initialize respawn detector
        if self.detect_respawn:
            resource_info = self._get_resource_info()
            if not resource_info:
                print("✗ Failed to get resource configuration")
                return False
            
            animation_id = resource_info.get('animation_id', -1)
            self.respawn_detector = RespawnDetector(
                self.api,
                animation_id,
                enabled=True
            )
        
        print(f"✓ {self._get_skill_name()} bot setup complete\n")
        return True
    
    def start(self):
        """Start the bot main loop."""
        if not self.setup():
            print("✗ Bot setup failed, cannot start")
            return
        
        self.is_running = True
        self.current_state = BotState.GATHERING
        
        try:
            while self.is_running:
                self._run_cycle()
        
        except KeyboardInterrupt:
            print("\n\nBot stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bot and print session summary."""
        self.is_running = False
        
        if self.track_xp and self.skill_tracker:
            self.skill_tracker.print_session_summary()
    
    def _run_cycle(self):
        """Execute one bot cycle based on current state."""
        if self.current_state == BotState.GATHERING:
            self._handle_gathering()
        
        elif self.current_state == BotState.BANKING:
            self._handle_banking()
        
        elif self.current_state == BotState.WALKING:
            self._handle_walking()
        
        else:
            print(f"Unknown state: {self.current_state}")
            time.sleep(1)
    
    def _handle_gathering(self):
        """Handle gathering state logic."""
        # Check if inventory full
        if self.osrs.inventory.is_full():
            if self.powerdrop:
                # Drop items instead of banking
                self._handle_powerdrop()
            else:
                # Switch to banking
                print("Inventory full, switching to banking")
                self.current_state = BotState.BANKING
                return
        
        # Update XP if tracking
        if self.track_xp and self.skill_tracker:
            gains = self.skill_tracker.update()
            if gains:
                print(f"✓ Gained {gains['xp_gained']} XP ({gains['new_xp']:,} total)")
        
        # Gather resource (implemented by subclass)
        self._gather_resource()
        
        # Anti-ban actions
        if self.anti_ban:
            self.anti_ban.perform_random_action()
    
    def _handle_powerdrop(self):
        """Drop resources when inventory is full (powerdrop mode)."""
        print("Inventory full - dropping items...")
        
        # Get resource item ID from config
        resource_info = self._get_resource_info()
        item_id = resource_info.get('item_id')
        
        if not item_id:
            print("✗ No item ID configured for dropping")
            return
        
        # Drop all items of this type
        dropped = self.osrs.inventory.drop_all(item_id)
        if dropped > 0:
            print(f"✓ Dropped {dropped} items")
        
        time.sleep(random.uniform(0.5, 1.0))
    
    def _handle_banking(self):
        """Handle banking state logic."""
        # If bank is already open, proceed to deposit
        if self.osrs.interfaces.is_bank_open():
            # Deposit items
            item_id = self._get_resource_info()['item_id']
            if self.osrs.bank.deposit_item_by_id(item_id, quantity="all"):
                print("✓ Items deposited")
                time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))
                
                # Close bank
                self.osrs.bank.close()
                time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
                
                # Walk back to gathering location
                gathering_location = self._get_gathering_location()
                if gathering_location and not self._is_near_location(gathering_location, tolerance=10):
                    print("Walking back to gathering location...")
                    self._start_walking(gathering_location, BotState.GATHERING)
                else:
                    # Already at gathering location
                    self.current_state = BotState.GATHERING
            else:
                print("✗ Failed to deposit items")
                time.sleep(1)
            return
        
        # Bank not open - check if we need to walk to bank first
        bank_location = self._get_bank_location()
        
        if bank_location and not self._is_near_location(bank_location, tolerance=10):
            # Need to walk to bank
            print("Walking to bank...")
            self._start_walking(bank_location, BotState.BANKING)
        else:
            # Already near bank, try to open it
            print("Opening bank...")
            if self.osrs.bank.open():
                print("✓ Bank opened")
            else:
                print("✗ Failed to open bank")
                time.sleep(2)
    
    def _handle_walking(self):
        """Handle walking state logic."""
        if not self.walking_destination:
            print("⚠ Walking state but no destination set")
            self.current_state = self.walking_next_state or BotState.GATHERING
            return
        
        # Check if already at destination
        if self._is_near_location(self.walking_destination, tolerance=2):
            print("✓ Reached destination")
            self.current_state = self.walking_next_state or BotState.GATHERING
            self.walking_destination = None
            self.walking_next_state = None
            return
        
        # Navigate to destination
        x, y, z = self.walking_destination
        print(f"Walking to ({x}, {y}, {z})...")
        
        success = self.osrs.navigation.walk_to_tile(x, y, z, use_pathfinding=True)
        
        if success:
            print("✓ Navigation complete")
            self.current_state = self.walking_next_state or BotState.GATHERING
            self.walking_destination = None
            self.walking_next_state = None
        else:
            print("✗ Navigation failed, retrying...")
            time.sleep(random.uniform(1.0, 2.0))
    
    def _verify_tool(self) -> bool:
        """
        Verify required tool is equipped.
        
        Returns:
            True if tool equipped, False otherwise
        """
        tool_ids = self._get_tool_ids()
        return self.osrs.verify_tool_equipped(tool_ids, slot=3)
    
    def _start_walking(self, destination: tuple, next_state: BotState):
        """
        Initiate walking to a destination.
        
        Args:
            destination: (x, y, z) world coordinates
            next_state: State to transition to after reaching destination
        """
        self.walking_destination = destination
        self.walking_next_state = next_state
        self.current_state = BotState.WALKING
    
    def _is_near_location(self, location: tuple, tolerance: int = 5) -> bool:
        """
        Check if player is near a location.
        
        Args:
            location: (x, y, z) world coordinates
            tolerance: Distance in tiles to consider "near"
            
        Returns:
            True if within tolerance distance, False otherwise
        """
        current_pos = self.osrs.navigation.read_world_coordinates()
        if not current_pos:
            return False
        
        current_x, current_y = current_pos
        target_x, target_y, target_z = location
        
        # Calculate 2D distance (ignore Z for now)
        distance = ((current_x - target_x) ** 2 + (current_y - target_y) ** 2) ** 0.5
        
        return distance <= tolerance
    
    def _get_bank_location(self) -> Optional[tuple]:
        """
        Get bank location from config.
        
        Returns:
            (x, y, z) coordinates or None if not configured
        """
        # Subclasses may override this if they store bank location differently
        # Default: try to get from standard config key
        if hasattr(self, 'bank_location'):
            return getattr(self, 'bank_location')
        return None
    
    def _get_gathering_location(self) -> Optional[tuple]:
        """
        Get gathering location from config.
        
        Returns:
            (x, y, z) coordinates or None if not configured
        """
        # Subclasses should override this to provide their gathering location
        # Default implementation for backwards compatibility
        if hasattr(self, 'wc_location'):
            return getattr(self, 'wc_location')
        if hasattr(self, 'mining_location'):
            return getattr(self, 'mining_location')
        return None
    
    # =============================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # =============================================================================
    
    @abstractmethod
    def _gather_resource(self):
        """
        Perform one gathering action.
        Must be implemented by subclass.
        """
        pass
    
    @abstractmethod
    def _get_skill_name(self) -> str:
        """
        Get the skill name (e.g., "Mining", "Woodcutting").
        Must be implemented by subclass.
        """
        pass
    
    @abstractmethod
    def _get_tool_ids(self) -> list[int]:
        """
        Get list of acceptable tool item IDs.
        Must be implemented by subclass.
        """
        pass
    
    @abstractmethod
    def _get_resource_info(self) -> Dict:
        """
        Get resource configuration dictionary.
        Must include: object_ids, item_id, animation_id (optional), respawn_time (optional)
        Must be implemented by subclass.
        """
        pass
