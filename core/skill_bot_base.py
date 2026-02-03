"""
Base class for gathering skill bots (mining, woodcutting, fishing, etc.).
Provides common functionality and structure for all resource-gathering bots.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import time
import random
import sys
from core.state_machine import BotState
from core.anti_ban import AntiBanManager
from core.config import AntiBanConfig, BreakConfig, DEBUG
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
    
    def __init__(self, osrs, profile_config):
        """
        Initialize skill bot.
        
        Args:
            osrs: OSRS instance
            profile_config: Bot configuration (BotConfig object or dict)
        """
        self.osrs = osrs
        self.api = osrs.api
        
        # Convert BotConfig to dict for backwards compatibility
        from core.config import BotConfig
        if isinstance(profile_config, BotConfig):
            self.bot_config = profile_config
            self.config = profile_config.to_dict()
        else:
            self.bot_config = None
            self.config = profile_config
        
        # State management
        self.current_state = BotState.IDLE
        self.is_running = False
        
        # Navigation state
        self.walking_destination = None  # (x, y, z) world coordinates
        self.walking_next_state = None   # State to transition to after walking
        
        # Statistics
        self.resources_gathered = 0
        self.start_time = None
        
        # Components - will be initialized in setup()
        self.skill_tracker: Optional[SkillTracker] = None
        self.respawn_detector: Optional[RespawnDetector] = None
        
        # Initialize anti-ban manager
        # Use BotConfig objects if available, otherwise parse from dict
        if self.bot_config:
            anti_ban_config = self.bot_config.anti_ban
            break_config = self.bot_config.breaks
        else:
            anti_ban_config = self.config.get('anti_ban', {})
            if isinstance(anti_ban_config, dict):
                anti_ban_config = AntiBanConfig(**anti_ban_config)
            
            break_config = self.config.get('breaks', {})
            if isinstance(break_config, dict):
                break_config = BreakConfig(**break_config)
        
        # TODO: Test login_from_profile() before relying on logout breaks in production
        self.anti_ban = AntiBanManager(
            window=self.osrs.window,
            config=anti_ban_config,
            break_config=break_config,
            osrs_client=self.osrs
        )
        
        # Validation config - use BotConfig objects if available, otherwise parse from dict
        if self.bot_config:
            self.validate_tool = self.bot_config.validation.verify_pickaxe
            self.track_xp = self.bot_config.validation.track_xp
            self.detect_respawn = self.bot_config.validation.detect_respawn
            self.use_animation = self.bot_config.validation.use_animation_detection
            self.powerdrop = self.bot_config.powerdrop
            self.should_bank = self.bot_config.banking
        else:
            self.validate_tool = self.config.get('validation', {}).get('verify_pickaxe', False)
            self.track_xp = self.config.get('validation', {}).get('track_xp', False)
            self.detect_respawn = self.config.get('validation', {}).get('detect_respawn', False)
            self.use_animation = self.config.get('validation', {}).get('use_animation_detection', True)
            self.powerdrop = self.config.get('powerdrop', False)
            self.should_bank = self.config.get('banking', True)
    
    def setup(self) -> bool:
        """
        Initialize bot components and validate setup.
        
        Returns:
            True if setup successful, False otherwise
        """
        if DEBUG:
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
        
        if DEBUG:
            print(f"✓ {self._get_skill_name()} bot setup complete\n")
        return True
    
    def start(self):
        """Start the bot main loop."""
        if not self.setup():
            print("✗ Bot setup failed, cannot start")
            return
        
        self.is_running = True
        self.start_time = time.time()
        
        # Determine initial state based on player position
        self.current_state = self._get_initial_state()
        
        if DEBUG:
            print(f"Starting in {self.current_state.name} state")
        
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
        
        # Print anti-ban statistics
        if self.anti_ban and DEBUG:
            print(f"\n{'='*50}")
            print("Anti-Ban Session Summary")
            print(f"{'='*50}")
            status = self.anti_ban.get_status()
            for key, value in status.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            print(f"{'='*50}\n")
    
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
        
        # Print status line after each cycle
        self._print_status_line()
    
    def _handle_gathering(self):
        """Handle gathering state logic."""
        # Check if inventory full
        self.osrs.inventory.populate()
        if self.osrs.inventory.is_full():
            if self.powerdrop:
                # Drop items instead of banking
                self._handle_powerdrop()
            else:
                # Switch to banking
                if DEBUG:
                    print("Inventory full, switching to banking")
                self.current_state = BotState.BANKING
                return
        
        # Update XP if tracking
        if self.track_xp and self.skill_tracker:
            gains = self.skill_tracker.update()
            if gains and DEBUG:
                print(f"✓ Gained {gains['xp_gained']} XP ({gains['new_xp']:,} total)")
        
        # Check for breaks (long duration, requires state change)
        should_break, break_type = self.anti_ban.should_take_break()
        if should_break:
            previous_state = self.current_state
            self.current_state = BotState.BREAK
            if DEBUG:
                print(f"\n{'='*50}")
                print(f"Taking {break_type} break...")
                print(f"{'='*50}\n")
            self.anti_ban.take_break(break_type)
            self.current_state = previous_state
            if DEBUG:
                print("Break finished, resuming gathering\n")
        
        # Add reaction delay before action (human-like)
        self.anti_ban.add_reaction_delay()
        
        # Gather resource (implemented by subclass)
        self._gather_resource()
        
        # Apply action delay after gathering (increases with fatigue)
        self.anti_ban.apply_action_delay()
        
        # Short anti-ban actions (no state change needed)
        if self.anti_ban.should_perform_idle_action():
            self.anti_ban.perform_idle_action()
        
        # Other anti-ban behaviors
        self.anti_ban.perform_attention_shift()
        self.anti_ban.randomize_tab_switching()
    
    def _handle_powerdrop(self):
        """Drop resources when inventory is full (powerdrop mode)."""
        if DEBUG:
            print("Inventory full - dropping items...")
        
        # Get resource item ID from config
        resource_info = self._get_resource_info()
        item_id = resource_info.get('item_id')
        
        if not item_id:
            if DEBUG:
                print("✗ No item ID configured for dropping")
            return
        
        # Drop all items of this type
        dropped = self.osrs.inventory.drop_all(item_id)
        if dropped > 0:
            self.resources_gathered += dropped
            if DEBUG:
                print(f"✓ Dropped {dropped} items (Total: {self.resources_gathered})")
        
        time.sleep(random.uniform(0.5, 1.0))
    
    def _handle_banking(self):
        """Handle banking state logic."""
        # If bank is already open, proceed to deposit
        if self.osrs.interfaces.is_bank_open():
            # Deposit items
            item_id = self._get_resource_info()['item_id']
            if self.osrs.bank.deposit_item_by_id(item_id, quantity="all"):
                if DEBUG:
                    print("✓ Items deposited")
                time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))
                
                # Close bank
                self.osrs.bank.close()
                time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
                
                # Walk back to gathering location
                gathering_location = self._get_gathering_location()
                if gathering_location and not self._is_near_location(gathering_location, tolerance=10):
                    if DEBUG:
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
    
    def _handle_walking(self):
        """Handle walking state logic."""
        if not self.walking_destination:
            if DEBUG:
                print("⚠ Walking state but no destination set")
            self.current_state = self.walking_next_state or BotState.GATHERING
            return
        
        # Check if already at destination
        if self._is_near_location(self.walking_destination, tolerance=2):
            if DEBUG:
                print("✓ Reached destination")
            self.current_state = self.walking_next_state or BotState.GATHERING
            self.walking_destination = None
            self.walking_next_state = None
            return
        
        # Navigate to destination
        x, y, z = self.walking_destination
        if DEBUG:
            print(f"Walking to ({x}, {y}, {z})...")
        
        success = self.osrs.navigation.walk_to_tile(x, y, z, use_pathfinding=True)
        
        if success:
            if DEBUG:
                print("✓ Navigation complete")
            self.current_state = self.walking_next_state or BotState.GATHERING
            self.walking_destination = None
            self.walking_next_state = None
        else:
            if DEBUG:
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
    
    def _get_initial_state(self) -> BotState:
        """
        Determine the initial bot state based on player position and inventory.
        
        Returns:
            BotState to start in (GATHERING, BANKING, or WALKING)
        """
        # Check if inventory is full and banking is enabled
        self.osrs.inventory.populate()
        if self.osrs.inventory.is_full() and self.should_bank:
            if DEBUG:
                print("Inventory full - starting in BANKING state")
            return BotState.BANKING
        
        # Check if player is at gathering location
        gathering_location = self._get_gathering_location()
        if gathering_location:
            if self._is_near_location(gathering_location, tolerance=10):
                if DEBUG:
                    print("At gathering location - starting in GATHERING state")
                return BotState.GATHERING
            else:
                if DEBUG:
                    print("Not at gathering location - starting in WALKING state")
                # Set destination so WALKING state knows where to go
                self._start_walking(gathering_location, BotState.GATHERING)
                return BotState.WALKING
        else:
            # No gathering location configured, assume we're at the right place
            if DEBUG:
                print("No gathering location configured - starting in GATHERING state")
            return BotState.GATHERING
    
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
    # STATUS LINE - Base implementation, can be overridden by subclasses
    # =============================================================================
    
    def _get_status_info(self) -> Dict:
        """
        Generate status information dictionary.
        Override in subclasses to add custom status information.
        
        Returns:
            Dictionary with status information
        """
        self.osrs.inventory.populate()
        inventory_count = self.osrs.inventory.count_filled()
        inventory_capacity = f"{inventory_count}/28"
        
        # Calculate runtime
        runtime = "00:00:00"
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            runtime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return {
            'state': self.current_state.name,
            'inventory': inventory_capacity,
            'resources': self.resources_gathered,
            'runtime': runtime
        }
    
    def _format_status_line(self, status_info: Dict) -> str:
        """
        Format status information into a display string.
        Override in subclasses to customize status line format.
        
        Args:
            status_info: Status information dictionary from _get_status_info()
            
        Returns:
            Formatted status string
        """
        return (
            f"State: {status_info['state']:12} | "
            f"Inventory: {status_info['inventory']:5} | "
            f"Gathered: {status_info['resources']:4} | "
            f"Runtime: {status_info['runtime']}"
        )
    
    def _print_status_line(self):
        """
        Print status line that overwrites itself using carriage return.
        """
        status_info = self._get_status_info()
        status_line = self._format_status_line(status_info)
        
        # Use carriage return to overwrite the same line
        sys.stdout.write(f"\r{status_line}")
        sys.stdout.flush()
    
    def _wait_for_interaction_start(self, timeout: float = 8.0) -> bool:
        """
        Wait for player to walk to target and begin interaction.
        
        Should be called immediately after click_entity() for gathering actions.
        Handles cases where the player needs to walk to the resource before
        the gathering animation begins.
        
        Args:
            timeout: Maximum time to wait for walking to complete (default 8s)
            
        Returns:
            True if player stopped moving (ready for interaction), False if timeout
        """
        # Delay by a game tick to ensure movement has started
        time.sleep(random.uniform(*TIMING.GAME_TICK))

        # Check if player is moving (walking to resource)
        if self.osrs.navigation.is_moving():
            if DEBUG:
                print("  Walking to target...")
            
            # Wait until player stops moving (reached target)
            if not self.osrs.navigation.wait_until_stopped(timeout=timeout):
                if DEBUG:
                    print(f"  ⚠ Timeout while walking to target ({timeout}s)")
                return False
            
            # Brief delay for animation to start after arrival
            time.sleep(random.uniform(0.3, 0.6))
        
        return True
    
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
