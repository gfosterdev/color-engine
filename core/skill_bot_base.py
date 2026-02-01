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
from client.resource_manager import ResourceManager
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
        
        # Components - will be initialized in setup()
        self.skill_tracker: Optional[SkillTracker] = None
        self.resource_manager: Optional[ResourceManager] = None
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
        
        # Initialize resource manager
        resource_info = self._get_resource_info()
        if not resource_info:
            print("✗ Failed to get resource configuration")
            return False
        
        self.resource_manager = ResourceManager(
            self.osrs,
            resource_info['object_ids'],
            resource_info.get('respawn_time', (5, 10))
        )
        
        # Initialize respawn detector
        if self.detect_respawn:
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
        self.current_state = BotState.MINING
        
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
        if self.current_state == BotState.MINING:
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
    
    def _handle_banking(self):
        """Handle banking state logic."""
        # Check if at bank
        if not self.osrs.interfaces.is_bank_open():
            # Walk to bank
            print("Walking to bank...")
            bank_location = self.config.get('bank_location', 'varrock_west_bank')
            
            if self.osrs.open_bank(location_name=bank_location):
                print("✓ Bank opened")
            else:
                print("✗ Failed to open bank")
                time.sleep(2)
                return
        
        # Deposit items
        item_id = self._get_resource_info()['item_id']
        if self.osrs.inventory.deposit_all(item_id):
            print("✓ Items deposited")
            time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))
            
            # Close bank
            self.osrs.interfaces.close_interface()
            time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
            
            # Return to gathering
            self.current_state = BotState.MINING
        else:
            print("✗ Failed to deposit items")
            time.sleep(1)
    
    def _handle_walking(self):
        """Handle walking state logic."""
        # Wait for navigation to complete
        time.sleep(1)
        
        # Check if reached destination
        # (In real implementation, would check distance to target)
        self.current_state = BotState.MINING
    
    def _verify_tool(self) -> bool:
        """
        Verify required tool is equipped.
        
        Returns:
            True if tool equipped, False otherwise
        """
        tool_ids = self._get_tool_ids()
        return self.osrs.verify_tool_equipped(tool_ids, slot=3)
    
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
