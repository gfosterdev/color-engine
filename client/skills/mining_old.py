"""
Mining skill bot implementation.

Autonomous mining bot that mines ore, banks when inventory is full,
and returns to mining location using RuneLite API for object detection
and pathfinding for navigation.
"""

from typing import Optional, List, Dict, Any, Tuple
from client.osrs import OSRS
from core.state_machine import StateMachine, BotState
from core.skill_bot_base import SkillBotBase
from core.config import BotConfig, load_profile
from config.timing import TIMING
from config.skill_mappings import MINING_RESOURCES, get_all_tool_ids
from config.locations import MiningLocations, BankLocations
from util.types import Polygon
import time
import random


class MineOreTask(Task):
    """Task to mine a single ore using RuneLite API."""
    
    def __init__(self, osrs: OSRS, rock_ids: List[int], ore_name: str):
        super().__init__("Mine Ore", TaskPriority.NORMAL)
        self.osrs = osrs
        self.rock_ids = rock_ids
        self.ore_name = ore_name
        self.timeout = 10.0
    
    def validate_preconditions(self) -> TaskResult:
        """Check if we can mine (inventory not full)."""
        self.osrs.inventory.populate()
        if self.osrs.inventory.is_full():
            return TaskResult(
                success=False,
                message="Inventory is full, cannot mine",
                retry_recommended=False
            )
        return TaskResult(success=True)
    
    def execute(self) -> TaskResult:
        """Find and click on ore using API object detection."""
        # Get all objects in viewport
        objects = self.osrs.api.get_game_objects_in_viewport()
        
        if not objects:
            return TaskResult(
                success=False,
                message=f"No objects in viewport",
                retry_recommended=True
            )
        
        # Filter for our target rocks
        rocks = [obj for obj in objects if obj.get('id') in self.rock_ids]
        
        if not rocks:
            return TaskResult(
                success=False,
                message=f"Could not find {self.ore_name} rocks",
                retry_recommended=True
            )
        
        # Get player position for distance-based sorting
        coords_data = self.osrs.api.get_coords()
        if coords_data and 'world' in coords_data:
            px, py = coords_data['world'].get('x', 0), coords_data['world'].get('y', 0)
            # Sort by distance to world coordinates
            for rock in rocks:
                rx, ry = rock.get('worldX', 0), rock.get('worldY', 0)
                rock['distance_2d'] = math.sqrt((rx - px)**2 + (ry - py)**2)
            rocks.sort(key=lambda r: r.get('distance_2d', float('inf')))
        
        # Try to click the nearest rock
        target_rock = rocks[0]
        rock_id = target_rock.get('id')
        
        if self.osrs.click_game_object(rock_id, "Mine"):
            # Wait for mining animation
            time.sleep(random.uniform(*TIMING.OBJECT_INTERACT_DELAY))
            return TaskResult(success=True, message=f"Mining {self.ore_name}")
        
        return TaskResult(
            success=False,
            message="Failed to click rock",
            retry_recommended=True
        )


class BankOreTask(Task):
    """Task to bank all ore using API-based banking."""
    
    def __init__(self, osrs: OSRS):
        super().__init__("Bank Ore", TaskPriority.HIGH)
        self.osrs = osrs
        self.timeout = 30.0
    
    def validate_preconditions(self) -> TaskResult:
        """Check if inventory has items to bank."""
        self.osrs.inventory.populate()
        if self.osrs.inventory.count_empty_slots() == 28:
            return TaskResult(
                success=False,
                message="Inventory is empty, nothing to bank",
                retry_recommended=False
            )
        return TaskResult(success=True)
    
    def execute(self) -> TaskResult:
        """Open bank and deposit all items."""
        # Find and open bank
        if not self.osrs.interfaces.is_bank_open():
            if not self.osrs.open_bank():
                return TaskResult(
                    success=False,
                    message="Failed to open bank",
                    retry_recommended=True
                )
            
            # Wait for bank to open
            time.sleep(random.uniform(*TIMING.BANK_OPEN_WAIT))
        
        # Deposit all items
        if not self.osrs.deposit_all():
            return TaskResult(
                success=False,
                message="Failed to deposit items",
                retry_recommended=True
            )
        
        # Wait a moment
        time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))
        
        # Close bank
        self.osrs.interfaces.close_interface()
        time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
        
        return TaskResult(success=True, message="Successfully banked items")


class MiningBot(BotBase):
    """
    Autonomous mining bot using RuneLite API and pathfinding.
    
    Features:
    - API-based ore rock detection with world-coordinate prioritization
    - Pathfinding integration for navigation to mine/bank
    - Pickaxe verification and XP tracking
    - Ore respawn detection using animation and object polling
    - Multi-rock support with distance-based selection
    - Enhanced statistics with XP/hour tracking
    """
    
    # Ore name to rock IDs mapping
    ORE_MAPPINGS = {
        "copper": (OreRocks.COPPER, Ores.COPPER_ORE, "Copper"),
        "tin": (OreRocks.TIN, Ores.TIN_ORE, "Tin"),
        "iron": (OreRocks.IRON, Ores.IRON_ORE, "Iron"),
        "coal": (OreRocks.COAL, Ores.COAL, "Coal"),
        "silver": (OreRocks.SILVER, Ores.SILVER_ORE, "Silver"),
        "gold": (OreRocks.GOLD, Ores.GOLD_ORE, "Gold"),
        "mithril": (OreRocks.MITHRIL, Ores.MITHRIL_ORE, "Mithril"),
        "adamantite": (OreRocks.ADAMANTITE, Ores.ADAMANTITE_ORE, "Adamantite"),
        "runite": (OreRocks.RUNITE, Ores.RUNITE_ORE, "Runite"),
        "clay": (OreRocks.CLAY, Ores.CLAY, "Clay"),
        "amethyst": (OreRocks.AMETHYST, Ores.AMETHYST, "Amethyst"),
    }
    
    # Mining animation ID
    MINING_ANIMATION_ID = 628
    
    def __init__(self, profile_name: str = "iron_miner_varrock"):
        """
        Initialize mining bot.
        
        Args:
            profile_name: Configuration profile to load
        """
        super().__init__()  # Initialize BotBase
        self.config = load_profile(profile_name)
        self.osrs = OSRS()
        self.state_machine = StateMachine(BotState.IDLE)
        self.task_queue = TaskQueue("mining")
        
        # Get validation settings
        validation_config = self.config.skill_settings.get("validation", {})
        self.verify_pickaxe = validation_config.get("verify_pickaxe", True)
        self.track_xp = validation_config.get("track_xp", True)
        self.detect_respawn = validation_config.get("detect_respawn", True)
        self.use_animation_detection = validation_config.get("use_animation_detection", True)
        
        # Get ore configuration
        ore_type = self.config.skill_settings.get("ore_type", "iron")
        ore_type_clean = ore_type.lower().replace("_ore", "").replace("_", "")
        
        # Support multiple rocks from profile
        rock_types = self.config.skill_settings.get("rocks", [ore_type])
        self.rock_configs = []
        
        for rock_name in rock_types:
            rock_clean = rock_name.lower().replace("_ore", "").replace("_", "")
            if rock_clean in self.ORE_MAPPINGS:
                rock_ids, item_id, display_name = self.ORE_MAPPINGS[rock_clean]
                self.rock_configs.append({
                    "rock_ids": rock_ids,
                    "item_id": item_id,
                    "name": display_name
                })
        
        if not self.rock_configs:
            raise ValueError(f"No valid ore types found in profile. Available: {list(self.ORE_MAPPINGS.keys())}")
        
        # Primary ore config
        self.primary_ore = self.rock_configs[0]
        print(f"Configured ores: {[cfg['name'] for cfg in self.rock_configs]}")
        
        # Get all rock IDs for detection
        self.all_rock_ids = []
        for cfg in self.rock_configs:
            self.all_rock_ids.extend(cfg["rock_ids"])
        
        # Get behavior settings
        self.should_bank = self.config.skill_settings.get("banking", True)
        self.powermine = self.config.skill_settings.get("powermine", False)
        
        # Resolve locations from config
        self.mine_location = self._resolve_location(
            self.config.skill_settings.get("location", "varrock_west"),
            MiningLocations
        )
        self.bank_location = self._resolve_location(
            self.config.skill_settings.get("bank_location", "varrock_west"),
            BankLocations
        )
        
        if not self.mine_location:
            raise ValueError("Could not resolve mining location from profile")
        if self.should_bank and not self.bank_location:
            raise ValueError("Banking enabled but could not resolve bank location")
        
        print(f"Mine location: {self.mine_location}")
        print(f"Bank location: {self.bank_location}")
        
        # Initialize anti-ban system
        self.anti_ban = AntiBanManager(
            window=self.osrs.window,
            config=self.config.anti_ban,
            break_config=self.config.breaks,
            osrs_client=self.osrs
        )
        
        # Initialize anti-ban decorator
        self.anti_ban_decorator = AntiBanDecorator(self.anti_ban)
        
        # Statistics
        self.ores_mined = 0
        self.banking_trips = 0
        self.navigation_failures = 0
        self.start_time = time.time()
        self.start_xp = 0
        self.current_xp = 0
        
        # Rock memory for respawn tracking
        self.depleted_rocks: Dict[Tuple[int, int], float] = {}  # (x, y) -> timestamp
        self.rock_memory_duration = 10.0  # seconds to remember depleted rocks
    
    def _resolve_location(self, location_str: str, location_class) -> Optional[Tuple[int, int, int]]:
        """
        Resolve location string to world coordinates.
        
        Args:
            location_str: Location name from profile (e.g., "varrock_west")
            location_class: LocationCategory class to search
            
        Returns:
            (x, y, z) tuple or None
        """
        # Try exact match first
        location_upper = location_str.upper().replace(" ", "_")
        coord = location_class.find_by_name(location_upper)
        
        if coord:
            return coord
        
        # Try partial match
        all_locations = location_class.all()
        for name, coords in all_locations.items():
            if location_str.lower() in name.lower():
                return coords
        
        print(f"Warning: Could not find location '{location_str}' in {location_class.__name__}")
        return None
    
    def _verify_pickaxe_equipped(self) -> bool:
        """Check if a pickaxe is equipped in weapon slot."""
        equipment = self.osrs.api.get_equipment()
        if equipment:
            # Slot 3 is weapon slot
            weapon = next((item for item in equipment if item.get('slot') == 3), None)
            if weapon:
                pickaxe_ids = [
                    Tools.BRONZE_PICKAXE, Tools.IRON_PICKAXE, Tools.STEEL_PICKAXE,
                    Tools.MITHRIL_PICKAXE, Tools.ADAMANT_PICKAXE, Tools.RUNE_PICKAXE,
                    Tools.DRAGON_PICKAXE, Tools.CRYSTAL_PICKAXE
                ]
                return weapon.get('id') in pickaxe_ids
        return False
    
    def _get_mining_xp_stats(self) -> Optional[Dict[str, Any]]:
        """Get current mining XP and calculate gains."""
        stats = self.osrs.api.get_stats()
        if stats:
            mining = next((s for s in stats if s['stat'] == 'Mining'), None)
            if mining:
                self.current_xp = mining['xp']
                xp_gained = self.current_xp - self.start_xp if self.start_xp > 0 else 0
                return {
                    'level': mining['level'],
                    'current_xp': self.current_xp,
                    'xp_gained': xp_gained,
                    'xp_to_next': mining['xpToNextLevel']
                }
        return None
    
    def _wait_for_ore_respawn(self, timeout: float = 10.0) -> bool:
        """
        Wait for ore rock to respawn using dual detection.
        Combines animation detection and object polling.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if rock respawned, False if timeout
        """
        start_time = time.time()
        mining_stopped = False
        
        while time.time() - start_time < timeout:
            # Check if still mining (animation)
            if self.use_animation_detection:
                player_data = self.osrs.api.get_player()
                if player_data:
                    is_animating = player_data.get('isAnimating', False)
                    animation_id = player_data.get('animation', -1)
                    
                    # Detect when mining animation stops
                    if not is_animating or animation_id != self.MINING_ANIMATION_ID:
                        mining_stopped = True
            
            # Check if rocks are available in viewport
            objects = self.osrs.api.get_game_objects_in_viewport()
            if objects:
                rocks = [obj for obj in objects if obj.get('id') in self.all_rock_ids]
                if rocks and mining_stopped:
                    # Rock is available and we stopped mining
                    return True
            
            time.sleep(random.uniform(*TIMING.API_POLL_INTERVAL))
        
        return False
    
    def _find_best_rock(self) -> Optional[Dict[str, Any]]:
        """
        Find the best rock to mine based on world-coordinate distance.
        Prioritizes rocks that aren't in depleted memory.
        
        Returns:
            Rock object dict or None
        """
        # Clean up old depleted rock memories
        current_time = time.time()
        self.depleted_rocks = {
            pos: timestamp for pos, timestamp in self.depleted_rocks.items()
            if current_time - timestamp < self.rock_memory_duration
        }
        
        # Get all objects in viewport
        objects = self.osrs.api.get_game_objects_in_viewport()
        if not objects:
            return None
        
        # Filter for our target rocks
        rocks = [obj for obj in objects if obj.get('id') in self.all_rock_ids]
        
        if not rocks:
            return None
        
        # Get player position
        coords_data = self.osrs.api.get_coords()
        if not coords_data or 'world' not in coords_data:
            # Fall back to first rock if no position
            return rocks[0]
        
        px, py = coords_data['world'].get('x', 0), coords_data['world'].get('y', 0)
        
        # Calculate distance and filter out depleted rocks
        available_rocks = []
        for rock in rocks:
            rx, ry = rock.get('worldX', 0), rock.get('worldY', 0)
            rock_pos = (rx, ry)
            
            # Skip if recently depleted
            if rock_pos in self.depleted_rocks:
                continue
            
            distance = math.sqrt((rx - px)**2 + (ry - py)**2)
            rock['distance_2d'] = distance
            available_rocks.append(rock)
        
        if not available_rocks:
            # If all rocks are depleted, clear memory and try any rock
            self.depleted_rocks.clear()
            for rock in rocks:
                rx, ry = rock.get('worldX', 0), rock.get('worldY', 0)
                rock['distance_2d'] = math.sqrt((rx - px)**2 + (ry - py)**2)
            available_rocks = rocks
        
        # Sort by distance and return closest
        available_rocks.sort(key=lambda r: r.get('distance_2d', float('inf')))
        return available_rocks[0]
    
    def _mark_rock_depleted(self, rock: Dict[str, Any]):
        """Mark a rock as depleted in memory."""
        rx, ry = rock.get('worldX', 0), rock.get('worldY', 0)
        self.depleted_rocks[(rx, ry)] = time.time()
    
    def _run_loop(self):
        """Main bot loop (called by BotBase.start())."""
        print(f"Starting mining bot for {[cfg['name'] for cfg in self.rock_configs]}...")
        print(f"Configuration: Bank={self.should_bank}, Powermine={self.powermine}")
        
        self.start_time = time.time()
        self.state_machine.transition(BotState.STARTING, "Bot started")
        
        # Verify pickaxe on startup
        if self.verify_pickaxe:
            if self._verify_pickaxe_equipped():
                print("✓ Pickaxe verified equipped")
            else:
                print("⚠ Warning: No pickaxe detected in weapon slot!")
        
        # Get starting XP
        if self.track_xp:
            xp_stats = self._get_mining_xp_stats()
            if xp_stats:
                self.start_xp = xp_stats['current_xp']
                print(f"Starting Mining XP: {self.start_xp:,} (Level {xp_stats['level']})")
        
        # Verify we're at the mining location, navigate if not
        coords_data = self.osrs.api.get_coords()
        if coords_data and 'world' in coords_data and self.mine_location:
            px, py, pz = coords_data['world'].get('x', 0), coords_data['world'].get('y', 0), coords_data['world'].get('plane', 0)
            mx, my, mz = self.mine_location
            distance_to_mine = math.sqrt((px - mx)**2 + (py - my)**2)
            
            if distance_to_mine > 20:  # More than 20 tiles away
                print(f"Not at mining location (distance: {distance_to_mine:.1f} tiles), navigating...")
                self.state_machine.transition(BotState.WALKING, "Navigating to mine")
                if self.osrs.navigation.walk_to_tile(mx, my, mz):
                    print("✓ Arrived at mining location")
                else:
                    print("⚠ Failed to navigate to mining location")
                    self.navigation_failures += 1
        
        self.state_machine.transition(BotState.MINING, "Ready to mine")
        
        while self.running:
            # Check if break is needed
            if self.anti_ban.should_take_break():
                self.state_machine.transition(BotState.BREAK, "Taking scheduled break")
                self.anti_ban.take_break()
                self.state_machine.transition(BotState.MINING, "Resuming after break")
            
            # Perform random idle action occasionally
            if self.anti_ban.should_perform_idle_action():
                print("Performing idle action...")
                self.anti_ban.perform_idle_action()
            
            current_state = self.state_machine.current_state
            
            # Update inventory and XP stats
            self.osrs.inventory.populate()
            inv_count = self.osrs.inventory.count_filled()
            is_full = self.osrs.inventory.is_full()
            
            # Track XP periodically
            xp_info = ""
            if self.track_xp and random.random() < 0.1:  # 10% chance to check
                xp_stats = self._get_mining_xp_stats()
                if xp_stats:
                    runtime_hours = (time.time() - self.start_time) / 3600.0
                    xp_per_hour = xp_stats['xp_gained'] / runtime_hours if runtime_hours > 0 else 0
                    xp_info = f" | XP/hr: {xp_per_hour:.0f}"
            
            print(f"State: {current_state.value} | Inventory: {inv_count}/28 | Fatigue: {self.anti_ban.get_fatigue_level()*100:.0f}%{xp_info}")
            
            # State-based logic
            if current_state == BotState.STARTING:
                # Already handled above, transition to mining
                self.state_machine.transition(BotState.MINING, "Ready to mine")
            
            elif current_state == BotState.MINING:
                # Check if inventory is full
                if is_full:
                    if self.should_bank:
                        self.state_machine.transition(BotState.WALKING, "Traveling to bank")
                    elif self.powermine:
                        # Drop all items
                        self._drop_all_items()
                else:
                    # Mine ore
                    self._mine_ore()
            
            elif current_state == BotState.WALKING:
                # Navigate to bank
                if self.should_bank and self.bank_location:
                    bx, by, bz = self.bank_location
                    print(f"Navigating to bank at {self.bank_location}...")
                    if self.osrs.navigation.walk_to_tile(bx, by, bz):
                        print("✓ Arrived at bank")
                        self.state_machine.transition(BotState.BANKING, "At bank")
                    else:
                        print("⚠ Failed to navigate to bank")
                        self.navigation_failures += 1
                        self.state_machine.transition(BotState.ERROR, "Navigation failed")
            
            elif current_state == BotState.BANKING:
                # Bank items
                self._bank_items()
                
                # Navigate back to mine
                if self.mine_location:
                    mx, my, mz = self.mine_location
                    print(f"Navigating back to mine at {self.mine_location}...")
                    if self.osrs.navigation.walk_to_tile(mx, my, mz):
                        print("✓ Arrived at mine")
                        self.state_machine.transition(BotState.MINING, "Returned to mining")
                    else:
                        print("⚠ Failed to navigate to mine")
                        self.navigation_failures += 1
                        self.state_machine.transition(BotState.ERROR, "Navigation failed")
                else:
                    self.state_machine.transition(BotState.MINING, "Returned to mining")
            
            elif current_state == BotState.ERROR:
                # Try to recover
                print("Error state detected, attempting recovery...")
                time.sleep(random.uniform(*TIMING.LARGE_DELAY))
                self.state_machine.transition(BotState.RECOVERING, "Attempting recovery")
                
            elif current_state == BotState.RECOVERING:
                # Close any open interfaces
                self.osrs.interfaces.close_interface()
                time.sleep(random.uniform(*TIMING.MEDIUM_DELAY))
                
                # Verify location and navigate if needed
                coords_data = self.osrs.api.get_coords()
                if coords_data and 'world' in coords_data and self.mine_location:
                    px, py, pz = coords_data['world'].get('x', 0), coords_data['world'].get('y', 0), coords_data['world'].get('plane', 0)
                    mx, my, mz = self.mine_location
                    distance = math.sqrt((px - mx)**2 + (py - my)**2)
                    
                    if distance > 20:
                        print("Far from mine, navigating back...")
                        self.osrs.navigation.walk_to_tile(mx, my, mz)
                
                self.state_machine.transition(BotState.MINING, "Recovered")
            
            # Apply anti-ban action delay (includes fatigue simulation)
            self.anti_ban.apply_action_delay()
            
            # Occasional tab switching
            self.anti_ban.randomize_tab_switching()
            
            # Attention shifts
            self.anti_ban.perform_attention_shift()
    
    def _mine_ore(self):
        """Mine a single ore using API and world-coordinate prioritization."""
        # Wrap mining action with anti-ban behaviors
        def mine_action():
            # Find best rock using world coordinates
            best_rock = self._find_best_rock()
            
            if not best_rock:
                print("No rocks available in viewport")
                # Wait for respawn if detection enabled
                if self.detect_respawn:
                    print("Waiting for ore respawn...")
                    if self._wait_for_ore_respawn():
                        print("Ore respawned, continuing...")
                    else:
                        print("Respawn timeout, continuing anyway...")
                return
            
            # Determine which ore this is
            rock_id = best_rock.get('id')
            ore_name = "Ore"
            for cfg in self.rock_configs:
                if rock_id in cfg["rock_ids"]:
                    ore_name = cfg["name"]
                    break
            
            # Click the rock
            if self.osrs.click_game_object(rock_id, "Mine"):
                print(f"Mining {ore_name}...")
                
                # Mark this rock as depleted for memory
                self._mark_rock_depleted(best_rock)
                
                # Wait for mining to complete
                if self.detect_respawn and self.use_animation_detection:
                    # Wait for animation to start
                    time.sleep(random.uniform(*TIMING.OBJECT_INTERACT_DELAY))
                    
                    # Monitor animation
                    mining_time = 0
                    max_mining_time = 5.0
                    while mining_time < max_mining_time:
                        player_data = self.osrs.api.get_player()
                        if player_data:
                            is_animating = player_data.get('isAnimating', False)
                            animation_id = player_data.get('animation', -1)
                            
                            # If still mining, continue waiting
                            if is_animating and animation_id == self.MINING_ANIMATION_ID:
                                time.sleep(random.uniform(*TIMING.API_POLL_INTERVAL))
                                mining_time += 0.15
                            else:
                                # Mining stopped, ore obtained (or rock depleted)
                                break
                        else:
                            time.sleep(random.uniform(*TIMING.API_POLL_INTERVAL))
                            mining_time += 0.15
                else:
                    # Simple delay if not using animation detection
                    time.sleep(random.uniform(1.0, 3.0))
                
                self.ores_mined += 1
                print(f"✓ Mined ore (Total: {self.ores_mined})")
                
                # Track task success
                self._track_task_result("mine_ore", True)
            else:
                print(f"Failed to click {ore_name} rock")
                self._track_task_result("mine_ore", False)
        
        # Execute with anti-ban wrapper
        self.anti_ban_decorator.wrap_action(mine_action)()
    
    def _bank_items(self):
        """Bank all items using API-based banking."""
        # Wrap banking action with anti-ban behaviors
        def bank_action():
            task = BankOreTask(self.osrs)
            result = task.run()
            
            # Track task result for failure detection
            self._track_task_result("bank_items", result.success)
            
            if result.success:
                self.banking_trips += 1
                print(f"✓ Banking trip #{self.banking_trips} completed")
            else:
                print(f"⚠ Banking failed: {result.message}")
                self.state_machine.transition(BotState.ERROR, "Banking failed")
        
        # Execute with anti-ban wrapper
        self.anti_ban_decorator.wrap_action(bank_action)()
    
    def _drop_all_items(self):
        """Drop all items (for powermining) using item IDs."""
        print("Powermining: Dropping all items...")
        
        # Get all ore item IDs we're mining
        ore_item_ids = [cfg["item_id"] for cfg in self.rock_configs]
        
        # Drop each ore type
        for item_id in ore_item_ids:
            self.osrs.drop_items(item_id)
        
        time.sleep(random.uniform(*TIMING.INTERFACE_TRANSITION))
    
    def _cleanup(self):
        """Cleanup operations after bot stops (implements BotBase abstract method)."""
        self.state_machine.transition(BotState.STOPPING, "Bot stopping")
        self._print_statistics()
        self.state_machine.transition(BotState.IDLE, "Bot stopped")
    
    def _print_statistics(self):
        """Print comprehensive bot statistics."""
        runtime = time.time() - self.start_time
        runtime_minutes = runtime / 60.0
        runtime_hours = runtime / 3600.0
        
        print("\n" + "="*60)
        print("MINING BOT STATISTICS")
        print("="*60)
        print(f"Ore Types: {', '.join([cfg['name'] for cfg in self.rock_configs])}")
        print(f"Ores Mined: {self.ores_mined}")
        print(f"Banking Trips: {self.banking_trips}")
        print(f"Runtime: {runtime_minutes:.1f} minutes ({runtime_hours:.2f} hours)")
        
        if runtime_minutes > 0:
            ores_per_hour = (self.ores_mined / runtime_hours)
            print(f"Ores/Hour: {ores_per_hour:.1f}")
        
        # XP statistics
        if self.track_xp:
            xp_stats = self._get_mining_xp_stats()
            if xp_stats:
                xp_gained = xp_stats['xp_gained']
                xp_per_hour = xp_gained / runtime_hours if runtime_hours > 0 else 0
                print(f"Mining Level: {xp_stats['level']}")
                print(f"Total XP: {xp_stats['current_xp']:,}")
                print(f"XP Gained: {xp_gained:,}")
                print(f"XP/Hour: {xp_per_hour:,.0f}")
        
        print(f"Actions Performed: {self.anti_ban.action_count}")
        print(f"Navigation Failures: {self.navigation_failures}")
        print(f"Final Fatigue: {self.anti_ban.get_fatigue_level()*100:.0f}%")
        print("="*60)


# Example usage
if __name__ == "__main__":
    bot = MiningBot("iron_miner_varrock")
    bot.start()
