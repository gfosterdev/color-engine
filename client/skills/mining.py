"""
Mining skill bot implementation.

Autonomous mining bot that mines ore, banks when inventory is full,
and returns to mining location.
"""

from typing import Optional, List
from client.osrs import OSRS
from client.color_registry import get_color, ColorRegistry
from client.interactions import GameObject, GameObjectInteraction
from core.state_machine import StateMachine, BotState
from core.task_engine import Task, TaskQueue, TaskResult, TaskPriority
from core.config import BotConfig, load_profile
from core.anti_ban import AntiBanManager, AntiBanDecorator
from core.bot_base import BotBase
import time
import random


class MineOreTask(Task):
    """Task to mine a single ore."""
    
    def __init__(self, osrs: OSRS, ore_object: GameObject, interaction: GameObjectInteraction):
        super().__init__("Mine Ore", TaskPriority.NORMAL)
        self.osrs = osrs
        self.ore_object = ore_object
        self.interaction = interaction
        self.timeout = 10.0
    
    def validate_preconditions(self) -> TaskResult:
        """Check if we can mine (inventory not full)."""
        if self.osrs.inventory.is_full():
            return TaskResult(
                success=False,
                message="Inventory is full, cannot mine",
                retry_recommended=False
            )
        return TaskResult(success=True)
    
    def execute(self) -> TaskResult:
        """Find and click on ore."""
        # Wait for ore to appear
        found = self.interaction.wait_for_object(
            self.ore_object,
            timeout=5.0,
            search_rotation=True
        )
        
        if not found:
            return TaskResult(
                success=False,
                message=f"Could not find {self.ore_object.name}",
                retry_recommended=True
            )
        
        # Click the ore
        if self.interaction.interact_with_object(self.ore_object, validate_hover=True):
            # Wait for mining animation (randomized)
            time.sleep(random.uniform(1.5, 3.0))
            return TaskResult(success=True, message="Mining ore")
        
        return TaskResult(
            success=False,
            message="Failed to click ore",
            retry_recommended=True
        )


class BankOreTask(Task):
    """Task to bank all ore."""
    
    def __init__(self, osrs: OSRS):
        super().__init__("Bank Ore", TaskPriority.HIGH)
        self.osrs = osrs
        self.timeout = 30.0
    
    def validate_preconditions(self) -> TaskResult:
        """Check if inventory has items to bank."""
        if self.osrs.inventory.is_empty():
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
            bank_point = self.osrs.find_bank()
            
            if not bank_point:
                return TaskResult(
                    success=False,
                    message="Could not find bank",
                    retry_recommended=True
                )
            
            if not self.osrs.open_bank():
                return TaskResult(
                    success=False,
                    message="Failed to open bank",
                    retry_recommended=True
                )
        
        # Deposit all items
        if not self.osrs.deposit_all():
            return TaskResult(
                success=False,
                message="Failed to deposit items",
                retry_recommended=True
            )
        
        # Wait a moment
        time.sleep(random.uniform(0.5, 1.0))
        
        # Close bank
        if not self.osrs.close_bank():
            return TaskResult(
                success=False,
                message="Failed to close bank",
                retry_recommended=True
            )
        
        return TaskResult(success=True, message="Successfully banked items")


class MiningBot(BotBase):
    """
    Autonomous mining bot.
    
    Mines specified ore type, banks when inventory is full, and repeats.
    """
    
    def __init__(self, profile_name: str = "iron_miner_varrock"):
        """
        Initialize mining bot.
        
        Args:
            profile_name: Configuration profile to load
        """
        super().__init__()  # Initialize BotBase
        self.config = load_profile(profile_name)
        self.osrs = OSRS()
        self.interaction = GameObjectInteraction(self.osrs.window)
        self.state_machine = StateMachine(BotState.IDLE)
        self.task_queue = TaskQueue("mining")
        self.registry = ColorRegistry()
        
        # Get ore configuration
        self.ore_type = self.config.skill_settings.get("ore_type", "iron_ore")
        self.should_bank = self.config.skill_settings.get("banking", True)
        self.powermine = self.config.skill_settings.get("powermine", False)
        
        # Create ore object
        ore_color = self.registry.get_color(self.ore_type)
        if not ore_color:
            raise ValueError(f"Ore type '{self.ore_type}' not found in color registry")
        
        self.ore_object = GameObject(
            name=self.ore_type,
            color=ore_color,
            object_type="ore",
            hover_text=self.ore_type.replace("_", " ").title()
        )
        
        # Initialize anti-ban system
        self.anti_ban = AntiBanManager(
            window=self.osrs.window,
            config=self.config.anti_ban,
            break_config=self.config.breaks,
            osrs_client=self.osrs
        )
        
        # Initialize anti-ban decorator for wrapping actions
        self.anti_ban_decorator = AntiBanDecorator(self.anti_ban)
        
        # Statistics
        self.ores_mined = 0
        self.banking_trips = 0
        self.start_time = time.time()
    
    def _run_loop(self):
        """Main bot loop (called by BotBase.start())."""
        print(f"Starting mining bot for {self.ore_type}...")
        print(f"Configuration: Bank={self.should_bank}, Powermine={self.powermine}")
        
        self.start_time = time.time()
        self.state_machine.transition(BotState.STARTING, "Bot started")
        
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
            
            # Check inventory status
            inv_count = self.osrs.inventory.count_filled()
            is_full = self.osrs.inventory.is_full()
            
            print(f"State: {current_state.value} | Inventory: {inv_count}/28 | Fatigue: {self.anti_ban.get_fatigue_level()*100:.0f}%")
            
            # State-based logic
            if current_state == BotState.STARTING:
                # Transition to mining
                self.state_machine.transition(BotState.MINING, "Ready to mine")
            
            elif current_state == BotState.MINING:
                # Check if inventory is full
                if is_full:
                    if self.should_bank:
                        self.state_machine.transition(BotState.BANKING, "Inventory full")
                    elif self.powermine:
                        # Drop all items
                        self._drop_all_items()
                else:
                    # Mine ore
                    self._mine_ore()
            
            elif current_state == BotState.BANKING:
                # Bank items
                self._bank_items()
                self.state_machine.transition(BotState.MINING, "Returned to mining")
            
            elif current_state == BotState.ERROR:
                # Try to recover
                print("Error state detected, attempting recovery...")
                time.sleep(random.uniform(2.0, 4.0))
                self.state_machine.transition(BotState.RECOVERING, "Attempting recovery")
                
            elif current_state == BotState.RECOVERING:
                # Close any open interfaces
                self.osrs.interfaces.close_interface()
                time.sleep(random.uniform(1.0, 2.0))
                self.state_machine.transition(BotState.MINING, "Recovered")
            
            # Apply anti-ban action delay (includes fatigue simulation)
            self.anti_ban.apply_action_delay()
            
            # Occasional tab switching
            self.anti_ban.randomize_tab_switching()
            
            # Attention shifts
            self.anti_ban.perform_attention_shift()
    
    def _mine_ore(self):
        """Mine a single ore."""
        # Wrap mining action with anti-ban behaviors
        def mine_action():
            task = MineOreTask(self.osrs, self.ore_object, self.interaction)
            result = task.run()
            
            # Track task result for failure detection
            self._track_task_result("mine_ore", result.success)
            
            if result.success:
                self.ores_mined += 1
                print(f"Mined {self.ores_mined} ores")
            else:
                print(f"Mining failed: {result.message}")
                
                # If can't find ore after retries, might be stuck
                if "Could not find" in result.message:
                    self.state_machine.transition(BotState.ERROR, "Ore not found")
        
        # Execute with anti-ban wrapper
        self.anti_ban_decorator.wrap_action(mine_action)()
    
    def _bank_items(self):
        """Bank all items."""
        # Wrap banking action with anti-ban behaviors
        def bank_action():
            task = BankOreTask(self.osrs)
            result = task.run()
            
            # Track task result for failure detection
            self._track_task_result("bank_items", result.success)
            
            if result.success:
                self.banking_trips += 1
                print(f"Banking trip #{self.banking_trips} completed")
            else:
                print(f"Banking failed: {result.message}")
                self.state_machine.transition(BotState.ERROR, "Banking failed")
        
        # Execute with anti-ban wrapper
        self.anti_ban_decorator.wrap_action(bank_action)()
    
    def _drop_all_items(self):
        """Drop all items (for powermining)."""
        print("Powermining: Dropping all items...")
        
        # Open inventory if not open
        if not self.osrs.inventory.is_inventory_open():
            self.osrs.inventory.open_inventory()
            time.sleep(random.uniform(0.3, 0.5))
        
        # Drop each item
        for i in range(28):
            if not self.osrs.inventory.is_slot_empty(i):
                self.osrs.inventory.click_slot(i, right_click=True)
                time.sleep(random.uniform(0.05, 0.15))
                # TODO: Select "Drop" from menu
                # For now, just clicking
        
        time.sleep(random.uniform(0.5, 1.0))
    
    def _cleanup(self):
        """Cleanup operations after bot stops (implements BotBase abstract method)."""
        self.state_machine.transition(BotState.STOPPING, "Bot stopping")
        self._print_statistics()
        self.state_machine.transition(BotState.IDLE, "Bot stopped")
    
    def _print_statistics(self):
        """Print bot statistics."""
        runtime = time.time() - self.start_time
        runtime_minutes = runtime / 60.0
        
        print("\n" + "="*50)
        print("MINING BOT STATISTICS")
        print("="*50)
        print(f"Ore Type: {self.ore_type}")
        print(f"Ores Mined: {self.ores_mined}")
        print(f"Banking Trips: {self.banking_trips}")
        print(f"Runtime: {runtime_minutes:.1f} minutes")
        if runtime_minutes > 0:
            print(f"Ores/Hour: {(self.ores_mined / runtime_minutes * 60):.1f}")
        print(f"Actions Performed: {self.anti_ban.action_count}")
        print(f"Final Fatigue: {self.anti_ban.get_fatigue_level()*100:.0f}%")
        print("="*50)


# Example usage
if __name__ == "__main__":
    bot = MiningBot("iron_miner_varrock")
    bot.start()
