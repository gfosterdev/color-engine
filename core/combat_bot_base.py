"""
Base class for combat bots.
Provides common functionality and structure for all combat-based bots.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Tuple, Callable, Any
from dataclasses import dataclass
import time
import random
import sys
from core.state_machine import BotState
from core.anti_ban import AntiBanManager
from core.config import AntiBanConfig, BreakConfig, DEBUG
from config.items import Item
from config.timing import TIMING


@dataclass
class NavigationStep:
    """
    Represents a single step in a navigation path.
    
    A step consists of coordinates to walk to, and optionally an interaction
    with a game object (door, ladder, gate, etc.).
    """
    x: int
    y: int
    plane: int = 0
    custom: Optional[Callable] = None  # custom function to execute for this step (if action is "custom")
    object_ids: Optional[List[int]] = None  # Object IDs to interact with at this location
    action_text: Optional[str] = None  # Action text (e.g., "Open", "Climb-up", "Enter")
    should_retry_action: bool = False  # Whether to retry this step if interaction fails (e.g., object not found or action not available)
    
    def has_interaction(self) -> bool:
        """Check if this step requires an interaction."""
        return self.object_ids is not None and self.action_text is not None

    def has_custom_action(self) -> bool:
        """Check if this step has a custom action function."""
        return self.custom is not None


@dataclass
class NavigationPath:
    """
    Represents a complete navigation path consisting of multiple steps.
    
    Each step can optionally include an interaction with a game object
    before proceeding to the next step.
    """
    steps: List[NavigationStep]
    
    def is_valid(self) -> bool:
        """Check if path has at least one step."""
        return len(self.steps) > 0


class CombatBotBase(ABC):
    """
    Abstract base class for combat bots.
    
    Provides:
    - Multi-step navigation with intermediate interactions (doors, ladders, etc.)
    - Combat loop with NPC engagement, health monitoring, looting
    - Banking with equipment verification and food restocking
    - Emergency escape on critical health
    - Death detection and logout
    - Anti-ban integration
    
    Subclasses must implement:
    - get_target_npc_ids()
    - get_combat_area()
    - get_loot_items()
    - get_food_items()
    - get_required_equipment()
    - get_path_to_combat_area()
    - get_path_to_bank()
    - get_escape_threshold()
    - get_escape_teleport_item_id()
    - get_food_threshold()
    - get_min_food_count()
    """
    
    def __init__(self, osrs, profile_config):
        """
        Initialize combat bot.
        
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
        self.current_path: Optional[NavigationPath] = None
        self.current_step_index: int = 0
        self.walking_next_state: Optional[BotState] = None
        self.navigation_retry: int = 0
        
        # Statistics
        self.kills = 0
        self.deaths = 0
        self.loot_collected = 0
        self.escapes = 0
        self.start_time = None
        
        # Combat state tracking
        self.last_target_position: Optional[Tuple[int, int, int]] = None
        self.food_eaten_this_session = 0
        
        # Initialize anti-ban manager
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
        
        self.anti_ban = AntiBanManager(
            window=self.osrs.window,
            config=anti_ban_config,
            break_config=break_config,
            osrs_client=self.osrs
        )
    
    # ========== Abstract Methods (must be implemented by subclasses) ==========
    
    @abstractmethod
    def get_target_npc_ids(self) -> List[int]:
        """
        Get list of NPC IDs to attack.
        
        Returns:
            List of NPC IDs from config.npcs
        """
        pass
    
    @abstractmethod
    def get_combat_area(self) -> Tuple[int, int, int]:
        """
        Get combat area center coordinates.
        
        Returns:
            Tuple of (x, y, plane) world coordinates
        """
        pass
    
    @abstractmethod
    def get_loot_items(self) -> List[Item]:
        """
        Get list of items to loot from kills.
        
        Returns:
            List of Item objects from config.items
        """
        pass
    
    @abstractmethod
    def get_special_loot_actions(self) -> Dict[int, Callable[[Dict[str, Any]], bool]]:
        """
        Get mapping of item ID to special loot handling function.
        
        This can be used to define custom processing for specific items when they are looted,
        such as automatically alching valuable drops, burying bones, or using items immediately.
        
        Returns:
            Dictionary mapping item ID to a function that takes the item dict as argument
            Example: {Items.DRAGON_BONES.id: self._bury_bones}
        """
        return {}

    @abstractmethod
    def get_food_items(self) -> List[Item]:
        """
        Get list of food items to use for healing.
        
        Returns:
            List of Item objects from config.items (e.g., [Food.LOBSTER])
        """
        pass
    
    @abstractmethod
    def get_required_equipment(self) -> Dict[int, int]:
        """
        Get required equipment for combat.
        
        Returns:
            Dictionary mapping slot number to item ID
            Example: {0: Items.HELM_ID, 3: Items.WEAPON_ID, 4: Items.BODY_ID}
        """
        pass
    
    @abstractmethod
    def get_path_to_combat_area(self) -> NavigationPath:
        """
        Get navigation path from bank to combat area.
        
        Returns:
            NavigationPath with steps including any required interactions
        """
        pass
    
    @abstractmethod
    def get_path_to_bank(self) -> NavigationPath:
        """
        Get navigation path from combat area to bank.
        
        Returns:
            NavigationPath with steps including any required interactions
        """
        pass
    
    @abstractmethod
    def get_escape_threshold(self) -> int:
        """
        Get health percentage threshold for emergency escape.
        
        Returns:
            Health percentage (1-99) that triggers emergency escape
            Example: 15 means escape when health drops below 15%
        """
        pass
    
    @abstractmethod
    def get_escape_teleport_item_id(self) -> Tuple[Optional[int], Optional[str]]:
        """
        Get item ID of emergency teleport item.
        
        Returns:
            Item ID of teleport tab/item, or None if no teleport available, action to execute item
        """
        pass
    
    @abstractmethod
    def get_food_threshold(self) -> int:
        """
        Get health percentage threshold for eating during combat.
        
        Returns:
            Health percentage (1-99) that triggers eating
            Example: 60 means eat when health drops below 60%
        """
        pass
    
    @abstractmethod
    def get_min_food_count(self) -> int:
        """
        Get minimum food count before returning to bank.
        
        Returns:
            Minimum number of food items to continue combat
            Example: 3 means go to bank when food count drops to 3 or less
        """
        pass
    
    @abstractmethod
    def get_required_inventory(self) -> Dict[int, Dict[str, Optional[int | str]]]:
        """
        Get required inventory layout for all 28 slots.
        
        Returns:
            Dictionary mapping slot number (1-28) to item ID or None for empty slots
            Example: {1: {id: Food.LOBSTER.id, quantity: 1}, 2: {id: Food.LOBSTER.id, quantity: 1}, 3: {id: Runes.NATURE_RUNE.id, quantity: "all"}, ..., 28: None}
            
        Note:
            - Slots with specific item IDs will be validated and required
            - Slots with None are enforced as empty (must not contain any item)
            - All 28 slots must be defined
        """
        pass
    
    # ========== Setup and Lifecycle Methods ==========
    
    def setup(self) -> bool:
        """
        Initialize bot components and validate setup.
        
        Returns:
            True if setup successful, False otherwise
        """
        if DEBUG:
            print(f"\n{'='*50}")
            print(f"Setting up Combat bot...")
            print(f"{'='*50}")
        
        # Validate escape threshold
        escape_threshold = self.get_escape_threshold()
        if not (1 <= escape_threshold <= 99):
            print(f"✗ Invalid escape threshold: {escape_threshold} (must be 1-99)")
            return False
        
        # Validate food threshold
        food_threshold = self.get_food_threshold()
        if not (1 <= food_threshold <= 99):
            print(f"✗ Invalid food threshold: {food_threshold} (must be 1-99)")
            return False
        
        # Validate paths
        path_to_combat = self.get_path_to_combat_area()
        path_to_bank = self.get_path_to_bank()
        
        if not path_to_combat.is_valid():
            print("✗ Path to combat area is empty")
            return False
        
        if not path_to_bank.is_valid():
            print("✗ Path to bank is empty")
            return False
        
        if DEBUG:
            print(f"  Path to combat: {len(path_to_combat.steps)} steps")
            print(f"  Path to bank: {len(path_to_bank.steps)} steps")
        
        # Verify and setup equipment
        if DEBUG:
            print("\nVerifying equipment...")
        
        if not self._verify_equipment():
            if DEBUG:
                print("  Equipment validation failed, attempting setup...")
            if not self._setup_equipment():
                print("✗ Failed to setup equipment")
                return False
        
        if DEBUG:
            required_equipment = self.get_required_equipment()
            print(f"✓ All equipment verified ({len(required_equipment)} slots)")
        
        # Verify and setup inventory layout
        if DEBUG:
            print("\nVerifying inventory...")
        
        required_inventory = self.get_required_inventory()
        
        # Ensure all 28 slots are defined
        if len(required_inventory) != 28:
            print(f"✗ Required inventory must define all 28 slots (found {len(required_inventory)})")
            return False
        
        if not self._verify_inventory():
            if DEBUG:
                print("  Inventory validation failed, attempting setup...")
            if not self._setup_inventory():
                print("✗ Failed to setup inventory")
                return False
        
        # Count food for informational purposes
        food_items = self.get_food_items()
        total_food = self._count_total_food()
        
        if DEBUG:
            print(f"✓ Inventory validated (Food: {total_food})")
            print(f"\n{'='*50}")
            print(f"✓ Combat bot setup complete\n")
        
        return True
    
    def start(self):
        """Start the bot main loop."""
        if not self.setup():
            print("✗ Bot setup failed, cannot start")
            return
        
        self.is_running = True
        self.start_time = time.time()
        
        # Determine initial state
        self.current_state = self._get_initial_state()
        
        if DEBUG:
            print(f"Starting in {self.current_state.name} state")
        
        # If starting in WALKING state, initialize the appropriate path
        if self.current_state == BotState.WALKING:
            if self._verify_combat_ready():
                # Walking to combat area
                if DEBUG:
                    print("Navigating to combat area...")
                self._start_path_navigation(self.get_path_to_combat_area(), BotState.COMBAT)
            else:
                # Walking to bank
                if DEBUG:
                    print("Navigating to bank...")
                self._start_path_navigation(self.get_path_to_bank(), BotState.BANKING)
        
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
        
        # Print combat session summary
        if self.start_time:
            duration = time.time() - self.start_time
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            
            print(f"\n{'='*50}")
            print("Combat Session Summary")
            print(f"{'='*50}")
            print(f"  Duration: {hours}h {minutes}m")
            print(f"  Kills: {self.kills}")
            print(f"  Deaths: {self.deaths}")
            print(f"  Loot collected: {self.loot_collected} items")
            print(f"  Food eaten: {self.food_eaten_this_session}")
            print(f"  Emergency escapes: {self.escapes}")
            if self.kills > 0:
                print(f"  Avg loot/kill: {self.loot_collected / self.kills:.1f}")
            print(f"{'='*50}\n")
        
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
        if self.current_state == BotState.COMBAT:
            self._handle_combat_state()
        
        elif self.current_state == BotState.BANKING:
            self._handle_banking_state()
        
        elif self.current_state == BotState.WALKING:
            self._handle_walking_state()
        
        else:
            print(f"Unknown state: {self.current_state}")
            time.sleep(1)
        
        # Print status line after each cycle
        self._print_status_line()
    
    # ========== Combat State Handler ==========
    
    def _handle_combat_state(self):
        """Handle combat state logic."""
        # Check for death first
        if self._check_for_death():
            print("✗ Player death detected, logging out...")
            self.deaths += 1
            self.osrs.logout()
            self.is_running = False
            return
        
        # Check escape threshold (critical health)
        if self._check_escape_threshold():
            return  # Escape handler stops execution
        
        # Check if already in combat (aggressive NPCs or leftover state)
        if self.osrs.combat.is_player_in_combat():
            if DEBUG:
                print("Already in combat, monitoring existing fight...")
            
            # Get target position for loot detection
            target = self.osrs.combat.get_current_target()
            if target and 'position' in target:
                pos = target['position']
                self.last_target_position = (pos['x'], pos['y'], pos.get('plane', 0))
                if DEBUG:
                    print(f"  Target position: {self.last_target_position}")
            
            # Handle the kill and loot collection
            self._handle_kill_and_loot()
            
            return  # Exit after handling existing combat
        
        # Check for breaks (long duration)
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
                print("Break finished, resuming combat\n")
        
        # Check if need to eat (normal threshold)
        food_threshold = self.get_food_threshold()
        if self.osrs.combat.should_eat(threshold_percent=food_threshold):
            if not self._eat_food():
                print("✗ Out of food, returning to bank")
                self.current_state = BotState.BANKING
                return
        
        # Check if need to bank (low food or full inventory)
        if self._should_return_to_bank():
            if DEBUG:
                print("Need to bank (low food or inventory full)")
            self.current_state = BotState.BANKING
            return
        
        # Add reaction delay before engaging (human-like)
        self.anti_ban.add_reaction_delay()
        
        # Engage NPC
        npc_ids = self.get_target_npc_ids()
        if DEBUG:
            print(f"Engaging NPC (IDs: {npc_ids})...")
        
        success = self.osrs.combat.engage_npc(npc_ids, "Attack")
        
        if not success:
            if DEBUG:
                print("✗ Failed to engage NPC (may not be available)")
            time.sleep(random.uniform(1.0, 2.0))
            return
        
        # Get target position for loot detection
        target = self.osrs.combat.get_current_target()
        if target and 'position' in target:
            pos = target['position']
            self.last_target_position = (pos['x'], pos['y'], pos.get('plane', 0))
            if DEBUG:
                print(f"  Target position: {self.last_target_position}")
        else:
            self.last_target_position = None
        
        # Wait for target to die and collect loot
        if DEBUG:
            print("  Waiting for target to die...")
        
        self._handle_kill_and_loot()
    
    # ========== Banking State Handler ==========
    
    def _handle_banking_state(self):
        """Handle banking state logic."""
        # Check if bank is already open
        if self.osrs.interfaces.is_bank_open():
            if DEBUG:
                print("Bank is open, processing...")
            
            # Deposit all loot
            if DEBUG:
                print("  Depositing items...")
            self.osrs.bank.deposit_all()
            time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))
            
            # Setup equipment
            if not self._setup_equipment():
                print("✗ Failed to setup equipment at bank")
                self.is_running = False
                return
            
            # Setup inventory
            if not self._setup_inventory():
                print("✗ Failed to setup inventory at bank")
                self.is_running = False
                return
            
            # Eat to full HP
            if not self._recover_hp_at_bank():
                print("✗ Failed to recover HP at bank")
                self.is_running = False
                return

            # Close bank
            self.osrs.bank.close()
            time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
            
            # Navigate to combat area
            if DEBUG:
                print("Navigating to combat area...")
            self._start_path_navigation(self.get_path_to_combat_area(), BotState.COMBAT)
            return
        
        # Bank not open - check if we need to walk to bank first
        # Get bank location from the last step of path to bank
        path_to_bank = self.get_path_to_bank()
        if path_to_bank.steps:
            bank_location = (path_to_bank.steps[-1].x, path_to_bank.steps[-1].y, path_to_bank.steps[-1].plane)
            
            if self._is_near_location(bank_location, tolerance=10):
                # Near bank, try to open it
                if DEBUG:
                    print("Opening bank...")
                if self.osrs.bank.open():
                    if DEBUG:
                        print("✓ Bank opened")
                else:
                    if DEBUG:
                        print("✗ Failed to open bank")
                    time.sleep(2)
            else:
                # Far from bank, navigate to it
                if DEBUG:
                    print("Navigating to bank...")
                self._start_path_navigation(path_to_bank, BotState.BANKING)
        else:
            # No path defined, try to open bank anyway
            if DEBUG:
                print("Opening bank...")
            self.osrs.bank.open()
            time.sleep(2)
    
    # ========== Walking State Handler ==========
    
    def _handle_walking_state(self):
        """Handle walking/navigation state logic."""
        if not self.current_path:
            if DEBUG:
                print("⚠ Walking state but no path set")
            self.current_state = self.walking_next_state or BotState.COMBAT
            return
        
        # Check if we've completed all steps
        if self.current_step_index >= len(self.current_path.steps):
            if DEBUG:
                print("✓ Navigation path completed")
            self.current_state = self.walking_next_state or BotState.COMBAT
            self.current_path = None
            self.current_step_index = 0
            self.walking_next_state = None
            return
        
        # Check if we've exceeded retry limit
        if self.navigation_retry > 3:
            if DEBUG:
                print("✗ Navigation failed after multiple attempts, triggering emergency escape")
            self.current_state = self.walking_next_state or BotState.COMBAT
            self.current_path = None
            self.current_step_index = 0
            self.walking_next_state = None
            self.navigation_retry = 0
            self._execute_emergency_escape()
            return

        # Execute current step
        step = self.current_path.steps[self.current_step_index]
        
        if DEBUG:
            print(f"Executing step {self.current_step_index + 1}/{len(self.current_path.steps)}: ({step.x}, {step.y}, plane {step.plane})")
        
        # Walk to step coordinates
        success = self.osrs.navigation.walk_to_tile(step.x, step.y, step.plane, use_pathfinding=True)
        time.sleep(random.uniform(.6, 1.2))

        if not success:
            if DEBUG:
                print("✗ Navigation failed, retrying...")
            time.sleep(random.uniform(1.0, 2.0))
            self.navigation_retry += 1
            return
        
        # If step has interaction, execute it
        if step.has_interaction():
            if DEBUG:
                print(f"  Interaction required: {step.action_text}")
            
            interaction_success = self._execute_step_interaction(step)
            time.sleep(random.uniform(2.0, 3.0))
            
            if not interaction_success:
                # Interaction failed - escape and reset from bank
                if DEBUG:
                    print("  ✗ Interaction failed, escaping and resetting from bank...")
                self.current_state = self.walking_next_state or BotState.COMBAT
                self.current_path = None
                self.current_step_index = 0
                self.walking_next_state = None
                self.navigation_retry = 0
                self._execute_emergency_escape()
                return
        
        if step.has_custom_action():
            if DEBUG:
                print(f"  Executing custom action for step...")
            
            custom_success = self._execute_step_custom_action(step)

            if not custom_success:
                if DEBUG:
                    print("  ✗ Custom action failed, restarting path...")
                self.current_step_index = 0
                time.sleep(random.uniform(2.0, 3.0))
                self.navigation_retry += 1
                return

        # Move to next step
        self.navigation_retry = 0
        self.current_step_index += 1
        time.sleep(random.uniform(*TIMING.TINY_DELAY))
    
    # ========== Navigation Helper Methods ==========
    
    def _execute_step_interaction(self, step: NavigationStep, retry: int = 0) -> bool:
        """
        Execute interaction for a navigation step.
        
        Args:
            step: NavigationStep with interaction details
            
        Returns:
            True if interaction succeeded or object already interacted with, False if failed
        """
        if not step.has_interaction():
            return True
        
        # Find the object
        found_entity = self.osrs.find_entity(step.object_ids, "object", globalAfterSearch=True)
        
        if not found_entity:
            if DEBUG:
                print(f"  ⚠ Object not found (IDs: {step.object_ids})")
            return False
        
        # Try to interact with it
        try:
            if self.osrs.click_entity(found_entity, "object", step.action_text):
                if DEBUG:
                    print(f"  ✓ Interaction completed: {step.action_text}")
                time.sleep(random.uniform(*TIMING.GAME_TICK))
                return True
            else:
                if step.should_retry_action:
                    if retry < 2:
                        if DEBUG:
                            print(f"  ⚠ Action '{step.action_text}' not available, retrying interaction (attempt {retry + 1})...")
                        time.sleep(random.uniform(1.0, 2.0))
                        self.osrs.window.rotate_camera(min_drag_distance=random.uniform(220, 300))
                        return self._execute_step_interaction(step, retry=retry + 1)
                    
                    if DEBUG:
                        print(f"  ⚠ Action '{step.action_text}' not available and max retries reached. Navigation cannot continue.")
                    return False
                else:
                    # Click failed - might mean action not in menu (already open/climbed)
                    if DEBUG:
                        print(f"  ⚠ Action '{step.action_text}' not available, assuming already complete")
                    time.sleep(random.uniform(*TIMING.TINY_DELAY))
                    return True  # Assume door already open, ladder already climbed, etc.
        except Exception as e:
            if DEBUG:
                print(f"  ✗ Interaction error: {e}")
            return False
    
    def _execute_step_custom_action(self, step: NavigationStep) -> bool:
        """
        Execute custom action for a navigation step.
        
        Args:
            step: NavigationStep with custom action
        """
        if not step.has_custom_action() or not isinstance(step.custom, Callable):
            return True
        
        try:
            result = step.custom()
            if result:
                if DEBUG:
                    print(f"  ✓ Custom action succeeded")
                time.sleep(random.uniform(*TIMING.GAME_TICK))
                return True
            else:
                if DEBUG:
                    print(f"  ✗ Custom action returned False")
                return False
        except Exception as e:
            if DEBUG:
                print(f"  ✗ Custom action error: {e}")
            return False

    def _start_path_navigation(self, path: NavigationPath, next_state: BotState):
        """
        Start navigating along a path.
        
        Args:
            path: NavigationPath to execute
            next_state: State to transition to after completing path
        """
        self.current_path = path
        self.current_step_index = 0
        self.walking_next_state = next_state
        self.current_state = BotState.WALKING
    
    def _is_near_location(self, location: Tuple[int, int, int], tolerance: int = 5) -> bool:
        """
        Check if player is near a location.
        
        Args:
            location: (x, y, plane) world coordinates
            tolerance: Distance in tiles to consider "near"
            
        Returns:
            True if within tolerance distance
        """
        current_pos = self.osrs.navigation.read_world_coordinates()
        if not current_pos:
            return False
        
        current_x, current_y = current_pos
        target_x, target_y, target_plane = location
        
        # Calculate distance (ignoring plane for now)
        distance = ((current_x - target_x) ** 2 + (current_y - target_y) ** 2) ** 0.5
        
        return distance <= tolerance
    
    def _handle_kill_and_loot(self) -> bool:
        """
        Handle waiting for kill completion and collecting loot.
        
        Assumes target position has been stored in self.last_target_position.
        Increments kill counter and loot counter.
        
        Returns:
            True if kill was completed successfully, False otherwise
        """
        # Wait for this kill to finish
        if not self._wait_for_kill():
            if DEBUG:
                print("  ⚠ Failed to complete kill")
            return False
        
        if DEBUG:
            print("  ✓ Target died!")
        
        self.kills += 1
        
        # Wait for loot to appear
        if self.last_target_position:
            x, y, plane = self.last_target_position
            loot = self.osrs.combat.wait_for_loot(x, y, timeout=2.5, radius=3)
            
            if loot:
                print(f"  Looting...")
                # Take loot
                loot_items = self.get_loot_items()
                taken, failed = self.osrs.combat.take_loot(loot, loot_items)
                
                self.loot_collected += len(taken)
                
                # Pass taken to special loot handling
                self._handle_special_loot(taken)

                if DEBUG and taken:
                    print(f"  ✓ Collected {len(taken)} item(s)")
                if DEBUG and failed:
                    print(f"  ⚠ Failed to take {len(failed)} item(s)")
        
        # Small delay between kills (anti-ban)
        time.sleep(random.uniform(0.5, 1.5))
        
        return True
    
    def _wait_for_kill(self, timeout: float = 120.0) -> bool:
        """
        Wait for current target to die while monitoring health and eating if needed.
        
        This method actively monitors player health during combat and eats food
        if health drops below the food threshold, ensuring survival during extended fights.
        
        Args:
            timeout: Maximum time to wait in seconds (default: 120)
            
        Returns:
            True if target died within timeout, False if timed out or escaped
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check for death
            if self._check_for_death():
                print("✗ Player death detected during combat")
                self.deaths += 1
                self.osrs.logout()
                self.is_running = False
                return False
            
            # Check escape threshold (critical health)
            if self._check_escape_threshold():
                return False  # Escape triggered, abort kill
            
            # Check if need to eat during combat
            food_threshold = self.get_food_threshold()
            if self.osrs.combat.should_eat(threshold_percent=food_threshold):
                if not self._eat_food():
                    # Out of food during combat - emergency escape
                    print("✗ Out of food during combat!")
                    if self._check_escape_threshold():  # This will trigger escape
                        return False
                    # If we're above escape threshold but out of food, try to finish kill
                    if DEBUG:
                        print("  ⚠ No food but above escape threshold, continuing...")
            
            # Get current target
            target = self.osrs.combat.get_current_target()

            # Check if current target is different from previous target position
            if target and 'position' in target:
                pos = target['position']
                current_target_position = (pos['x'], pos['y'], pos.get('plane', 0))
                
                if self.last_target_position and current_target_position != self.last_target_position:
                    if DEBUG:
                        print("  ⚠ Target position changed during combat, possible escape or new target")
                    return True  # Assume kill completed if target changed (could be new aggressive NPC)
            
            # No target means it's dead or we lost aggro
            if not target:
                time.sleep(random.uniform(*TIMING.COMBAT_DEATH_DETECT))
                # Double-check it's really gone
                if not self.osrs.combat.get_current_target():
                    return True
            
            # Check isDying flag
            if target and target.get('isDying', False):
                time.sleep(random.uniform(*TIMING.COMBAT_DEATH_DETECT))
                return True
            
            
            # Small delay before next check
            time.sleep(random.uniform(*TIMING.API_POLL_INTERVAL))
        
        # Timeout
        return False
    
    # ========== Emergency Escape System ==========
    
    def _check_escape_threshold(self) -> bool:
        """
        Check if health is below escape threshold and trigger escape.
        
        Returns:
            True if escape was triggered, False otherwise
        """
        health_percent = self.osrs.combat.get_health_percent()
        if health_percent is None:
            return False
        
        escape_threshold = self.get_escape_threshold()
        
        if health_percent < escape_threshold:
            print(f"\n{'='*50}")
            print(f"⚠ EMERGENCY ESCAPE TRIGGERED")
            print(f"  Health: {health_percent}% (threshold: {escape_threshold}%)")
            print(f"{'='*50}\n")
            
            self._execute_emergency_escape()
            return True
        
        return False
    
    def _execute_emergency_escape(self):
        """Execute emergency escape procedure."""
        self.escapes += 1
        
        # Try teleport first if available
        teleport_item_id, action = self.get_escape_teleport_item_id()
        
        if teleport_item_id and action:
            if DEBUG:
                print("Attempting emergency teleport...")
            
            self.osrs.inventory.populate()
            if self.osrs.inventory.click_item(teleport_item_id, action):
                if DEBUG:
                    print("✓ Teleport activated")
                time.sleep(random.uniform(3.0, 4.0))  # Wait for teleport

                # After teleport, navigate directly to bank tile
                self.current_state = BotState.RECOVERING
                path = self.get_path_to_bank()
                path.steps = [path.steps[len(path.steps) - 1]]  # Only navigate to final bank tile
                self._start_path_navigation(path, BotState.BANKING)
                return
            else:
                if DEBUG:
                    print("✗ Teleport failed")
        
        # No teleport or teleport failed - logout immediately
        if DEBUG:
            print("Logging out immediately...")
        
        self.osrs.logout()
        self.is_running = False
    
    # ========== Death Detection ==========
    
    def _check_for_death(self) -> bool:
        """
        Check if player has died.
        
        Returns:
            True if death/respawn interface detected, False otherwise
        """
        # Check for death/respawn screen
        # TODO: Add proper interface detection once death interfaces are mapped
        # For now, check if health is 0
        health = self.osrs.combat.get_health()
        if health is not None and health == 0:
            return True
        
        return False
    
    # ========== Helper Methods ==========
    
    def _verify_equipment(self) -> bool:
        """Verify all required equipment is equipped.
        
        Returns:
            True if all equipment is equipped, False otherwise
        """
        required_equipment = self.get_required_equipment()
        equipped_ids = self.osrs.get_equipped_item_ids()
        
        for slot, item_id in required_equipment.items():
            if item_id not in equipped_ids:
                if DEBUG:
                    print(f"  Equipment missing: item ID {item_id} (slot {slot})")
                return False
        return True
    
    def _verify_inventory(self) -> bool:
        """Verify inventory contains required items in correct quantities.
        
        Does not check exact slot positions, only that items exist with correct counts.
        
        Returns:
            True if all required items are present with correct quantities, False otherwise
        """
        required_inventory = self.get_required_inventory()
        self.osrs.inventory.populate()
        
        if DEBUG:
            print("  Checking inventory requirements...")
        
        # Count how many of each item we need and how many empty slots required
        item_requirements = {}
        empty_slots_required = 0
        for slot_num in range(1, 29):
            required_item_slot = required_inventory.get(slot_num)
            required_item_id = required_item_slot.get('id') if required_item_slot else None
            if required_item_slot and required_item_id is not None:
                quant = required_item_slot.get('quantity', 1)
                item_requirements[required_item_id] = item_requirements.get(required_item_id, 0) + quant if quant != "all" else "all"
            else:
                empty_slots_required += 1
        
        if DEBUG:
            print(f"  Required items: {len(item_requirements)} unique item(s)")
            for item_id, qty in item_requirements.items():
                print(f"    Item ID {item_id}: {qty}x required")
            print(f"  Empty slots required: {empty_slots_required}")
        
        # Get loot and food item IDs for flexible verification
        loot_items = self.get_loot_items()
        loot_item_ids = set(item.id for item in loot_items)
        
        food_items = self.get_food_items()
        food_item_ids = set(item.id for item in food_items)
        
        # Verify each required item has correct quantity in inventory
        # For food items, allow shortage if loot items are present (mid-trip restart)
        # For non-food items, require exact quantities
        for item_id, required_quantity in item_requirements.items():
            actual_quantity = self.osrs.inventory.count_item(item_id)
            if DEBUG:
                print(f"  Checking item ID {item_id}: have {actual_quantity}, need {required_quantity}")
            
            # If this is NOT a food item, it must match exactly
            if item_id not in food_item_ids:
                if required_quantity == "all":
                    if actual_quantity == 0:
                        if DEBUG:
                            print(f"  ✗ Required item ID {item_id} is missing (required all)")
                        return False
                else :
                    if actual_quantity != required_quantity:
                        if DEBUG:
                            print(f"  ✗ Incorrect quantity for non-food item ID {item_id}")
                        return False
            else:
                # Food items can be less than required (eaten and replaced by loot)
                # But must have at least minimum food count
                pass  # Will check minimum food separately
        
        # Check minimum food count (sum of all food types)
        total_food = sum(self.osrs.inventory.count_item(food.id) for food in food_items)
        min_food = self.get_min_food_count()
        if total_food < min_food:
            if DEBUG:
                print(f"  ✗ Insufficient food: have {total_food}, need at least {min_food}")
            return False
        
        # Verify that any extra items in inventory are loot items only
        for slot in self.osrs.inventory.slots:
            if not slot.is_empty:
                # Skip items that are in our requirements
                if slot.item_id in item_requirements:
                    continue
                # Any other items must be loot items
                if slot.item_id not in loot_item_ids:
                    if DEBUG:
                        print(f"  ✗ Unexpected item ID {slot.item_id} in inventory (not required or loot)")
                    return False
        
        if DEBUG:
            loot_count = sum(1 for slot in self.osrs.inventory.slots if not slot.is_empty and slot.item_id in loot_item_ids)
            if loot_count > 0:
                print(f"  ✓ Found {loot_count} loot item(s) (allowed for mid-trip restart)")
            print("  ✓ All inventory requirements met")
        
        return True
    
    def _setup_equipment(self) -> bool:
        """Withdraw and equip required equipment from bank.
        
        Assumes bank is open or will open bank if needed.
        
        Returns:
            True if equipment setup successful, False otherwise
        """
        required_equipment = self.get_required_equipment()
        
        # Open bank if not already open
        bank_was_closed = False
        if not self.osrs.interfaces.is_bank_open():
            if DEBUG:
                print("  Opening bank for equipment setup...")
            if not self.osrs.bank.open():
                print("  ✗ Failed to open bank")
                return False
            bank_was_closed = True
            time.sleep(random.uniform(*TIMING.INTERFACE_TRANSITION))
        

        # Check each equipment slot
        equipped_ids = self.osrs.get_equipped_item_ids()
        for slot, item_id in required_equipment.items():
            if item_id not in equipped_ids:
                if DEBUG:
                    print(f"  Withdrawing and equipping item for slot {slot} (ID: {item_id})...")
                
                # Withdraw the item
                if not self.osrs.bank.withdraw_item(item_id, quantity=1):
                    print(f"  ✗ Failed to withdraw item ID {item_id}")
                    return False
                
                time.sleep(random.uniform(*TIMING.BANK_WITHDRAW_ACTION))
                
                # Equip the item
                self.osrs.inventory.populate()
                if not (self.osrs.inventory.click_item(item_id, "Wear") or 
                        self.osrs.inventory.click_item(item_id, "Wield")):
                    print(f"  ✗ Failed to equip item ID {item_id}")
                    return False
                
                time.sleep(random.uniform(*TIMING.TINY_DELAY))
                
                if DEBUG:
                    print(f"  ✓ Equipped item in slot {slot}")
        
        # Close bank if we opened it
        if bank_was_closed:
            self.osrs.bank.close()
            time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
        
        if DEBUG:
            print(f"  ✓ Equipment setup complete")
        
        return True
    
    def _calculate_withdrawal_batches(self, quantity: int) -> List[int]:
        """Calculate withdrawal batches for a given quantity.
        
        OSRS only allows withdrawing 1, 5, 10, or All items at a time.
        This breaks down an arbitrary quantity into valid batches.
        
        Args:
            quantity: Total quantity to withdraw
            
        Returns:
            List of batch sizes (each will be 1, 5, or 10)
            Example: 17 -> [10, 5, 1, 1]
        """
        batches = []
        remaining = quantity
        
        # Withdraw as many 10s as possible
        tens = remaining // 10
        for _ in range(tens):
            batches.append(10)
        remaining = remaining % 10
        
        # Withdraw a 5 if needed
        if remaining >= 5:
            batches.append(5)
            remaining -= 5
        
        # Withdraw remaining 1s
        for _ in range(remaining):
            batches.append(1)
        
        return batches
    
    def _setup_inventory(self) -> bool:
        """Withdraw required inventory items from bank.
        
        Assumes bank is open or will open bank if needed.
        
        Returns:
            True if inventory setup successful, False otherwise
        """
        required_inventory = self.get_required_inventory()
        
        # Open bank if not already open
        bank_was_closed = False
        if not self.osrs.interfaces.is_bank_open():
            if DEBUG:
                print("  Opening bank for inventory setup...")
            if not self.osrs.bank.open():
                print("  ✗ Failed to open bank")
                return False
            bank_was_closed = True
            time.sleep(random.uniform(*TIMING.INTERFACE_TRANSITION))
        
        # Deposit everything before withdrawing
        self.osrs.bank.deposit_all()
        time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))

        item_requirements = {}
        for slot_num in range(1, 29):
            required_item_slot = required_inventory.get(slot_num)
            required_item_id = required_item_slot.get('id') if required_item_slot else None
            if required_item_slot and required_item_id is not None:
                quant = required_item_slot.get('quantity', 1)
                item_requirements[required_item_id] = item_requirements.get(required_item_id, 0) + quant if quant != "all" else "all"
        
        # Withdraw each required item in valid batches
        for item_id, quantity in item_requirements.items():
            if DEBUG:
                print(f"  Withdrawing {quantity}x item ID {item_id}...")
            
            # Calculate withdrawal batches (1, 5, 10)
            if isinstance(quantity, str) and quantity.lower() == "all":
                batches = ["All"]
            elif isinstance(quantity, int) and quantity > 0:
                batches = self._calculate_withdrawal_batches(quantity)
            else:
                batches = [1]  # Default to withdrawing 1 if quantity is invalid
            
            # Execute each batch withdrawal
            for batch_size in batches:
                if not self.osrs.bank.withdraw_item(item_id, quantity=batch_size):
                    print(f"  ✗ Failed to withdraw {batch_size}x item ID {item_id}")
                    return False
                
                time.sleep(random.uniform(*TIMING.BANK_WITHDRAW_ACTION))
        
        # Close bank if we opened it
        if bank_was_closed:
            self.osrs.bank.close()
            time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
        
        if DEBUG:
            total_food = self._count_total_food()
            print(f"  ✓ Inventory setup complete (Food: {total_food})")
        
        return True
    
    def _handle_special_loot(self, taken: List[Dict[str, Any]]) -> None:
        """
        Handle any special loot processing after taking items.
        
        This method is called after loot is taken and can be used to process
        specific items, such as alching, burying bones, or using items immediately.

        Args:
            taken: List of items that were successfully taken from loot, each item is a dict with keys like 'id', 'name', 'quantity'
        """
        special_loot_actions = self.get_special_loot_actions()
        
        for item in taken:
            item_id = item['id']
            if item_id in special_loot_actions:
                action_func = special_loot_actions[item_id]
                if callable(action_func):
                    if DEBUG:
                        print(f"  Processing special loot: {item['name']} (ID: {item_id})")
                    try:
                        success = action_func(item)
                        if DEBUG:
                            print(f"  ✓ Special loot action completed for {item['name']}") if success else print(f"  ✗ Special loot action failed for {item['name']}")
                    except Exception as e:
                        if DEBUG:
                            print(f"  ✗ Error processing special loot: {e}")

    def _count_total_food(self) -> int:
        """
        Count total food items in inventory.
        
        Returns:
            Total count of all food items
        """
        self.osrs.inventory.populate()
        food_items = self.get_food_items()
        
        total = 0
        for food_item in food_items:
            total += self.osrs.inventory.count_item(food_item.id)
        
        return total
    
    def _eat_food(self) -> bool:
        """
        Eat one food item from inventory.
        
        Returns:
            True if food was eaten, False if no food available
        """
        food_items = self.get_food_items()
        self.osrs.inventory.populate()
        
        # Try each food type in order
        for food_item in food_items:
            if self.osrs.inventory.count_item(food_item.id) > 0:
                if self.osrs.combat.eat_food(food_item.id):
                    self.food_eaten_this_session += 1
                    if DEBUG:
                        print(f"  ✓ Ate {food_item.name}")
                    return True
        
        if DEBUG:
            print("  ✗ No food available")
        return False
    
    def _toggle_auto_retaliate_on(self) -> bool:
        """
        Toggles auto retaliate on 
        """
        return self.osrs.combat.toggle_auto_retaliate(True)

    def _toggle_auto_retaliate_off(self) -> bool:
        """
        Toggles auto retaliate off
        """
        return self.osrs.combat.toggle_auto_retaliate(False)

    def _should_return_to_bank(self) -> bool:
        """
        Check if should return to bank (low food or full inventory).
        
        Returns:
            True if should bank, False otherwise
        """
        # Check food count
        total_food = self._count_total_food()
        min_food = self.get_min_food_count()
        
        if total_food < min_food:
            return True
        
        # Check if inventory is full (no space for loot)
        self.osrs.inventory.populate()
        if self.osrs.inventory.is_full():
            return True
        
        return False
    
    def _recover_hp_at_bank(self) -> bool:
        """
        Eats to full HP at the bank before next trip
        """
        current_hp = self.osrs.combat.get_health_percent()
        if current_hp is None:
            return False
        
        if not self.osrs.interfaces.is_bank_open():
            self.osrs.bank.open()
            time.sleep(random.uniform(2, 3))

        while current_hp < 90:
            # Withdraw 1 food
            food_items = self.get_food_items()
            success = self.osrs.bank.withdraw_item(food_items[0].id, quantity=1)

            # Eat 1 food
            if success:
                self._eat_food()

            time.sleep(random.uniform(1.2, 1.8))
            
            current_hp = self.osrs.combat.get_health_percent()
            if current_hp is None:
                return False

        return True
        

    def _verify_combat_ready(self) -> bool:
        """
        Verify player is ready for combat.
        
        Returns:
            True if ready (health good, has food, equipment equipped), False otherwise
        """
        # Check health
        health_percent = self.osrs.combat.get_health_percent()
        if health_percent is None or health_percent < self.get_food_threshold():
            return False
        
        # Check food
        total_food = self._count_total_food()
        if total_food < self.get_min_food_count():
            return False
        
        # Check equipment
        required_equipment = self.get_required_equipment()
        equipped_ids = self.osrs.get_equipped_item_ids()
        for slot, item_id in required_equipment.items():
            if item_id not in equipped_ids:
                return False
        
        return True
    
    def _get_initial_state(self) -> BotState:
        """
        Determine initial state based on player position and inventory.
        
        Returns:
            Initial BotState to start in
        """
        # Check if we're near combat area
        combat_area = self.get_combat_area()
        if self._is_near_location(combat_area, tolerance=50):
            # At combat area - check if ready
            if self._verify_combat_ready():
                return BotState.COMBAT
            else:
                return BotState.BANKING
        else:
            # Not at combat area - check if we have food
            if self._verify_combat_ready():
                # Ready to fight, walk to combat area
                return BotState.WALKING
            else:
                # Need to bank first
                return BotState.BANKING
    
    def _print_status_line(self):
        """Print current status line (overwrites previous line)."""
        if not DEBUG:
            return
        
        health_percent = self.osrs.combat.get_health_percent() or 0
        food_count = self._count_total_food()
        
        status = (
            f"\r[{self.current_state.name}] "
            f"Kills: {self.kills} | "
            f"Loot: {self.loot_collected} | "
            f"HP: {health_percent}% | "
            f"Food: {food_count} | "
            f"Deaths: {self.deaths}"
        )
        
        print(status, end='', flush=True)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current bot status as dictionary.
        
        Returns:
            Dictionary with current bot state and statistics
        """
        return {
            'state': self.current_state.name,
            'kills': self.kills,
            'deaths': self.deaths,
            'loot_collected': self.loot_collected,
            'food_eaten': self.food_eaten_this_session,
            'escapes': self.escapes,
            'health_percent': self.osrs.combat.get_health_percent(),
            'food_count': self._count_total_food(),
            'is_running': self.is_running
        }
