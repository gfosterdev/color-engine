"""
Interface state detection system for OSRS bot.

Detects various game interface states like bank open, combat status,
dialogue windows, and other UI elements using fixed client mode positions.
"""

from typing import Optional, Tuple
from dataclasses import dataclass
from util import Region
from config.regions import (
    BANK_TITLE_REGION,
    BANK_REARRANGE_MODE_REGION,
    SHOP_TITLE_REGION,
    DIALOGUE_BOX_REGION,
    DIALOGUE_CONTINUE_REGION,
    LEVEL_UP_REGION,
    UI_LOGOUT_BUTTON_REGION
)
from .runelite_api import RuneLiteAPI
import random


# Text detection constants
BANK_TITLE_TEXT = "Bank of"  # Common text in bank title
DEPOSIT_BOX_TITLE_TEXT = "Deposit"
SHOP_TITLE_TEXT = "Shop"

# Color constants
BANK_CLOSE_BUTTON_COLOR = (192, 30, 30)  # Red X button
LEVEL_UP_COLOR = (255, 255, 0)  # Yellow text


@dataclass
class InterfaceState:
    """Represents the current state of game interfaces."""
    bank_open: bool = False
    shop_open: bool = False
    dialogue_open: bool = False
    in_combat: bool = False
    level_up_shown: bool = False
    health_percent: Optional[int] = None
    prayer_percent: Optional[int] = None
    run_energy_percent: Optional[int] = None


class InterfaceDetector:
    """
    Detects various game interface states.
    
    Assumes RuneLite client in fixed mode for consistent UI positions.
    """
    
    def __init__(self, window):
        """
        Initialize interface detector.
        
        Args:
            window: Window instance for screen capture and OCR
        """
        self.window = window
        self.api = RuneLiteAPI()
    
    def is_bank_open(self) -> bool:
        """
        Check if the bank interface is currently open.
        
        Returns:
            True if bank is open
        """
        if not self.window.window:
            return False
        
        widgets = self.api.get_widgets()
        if widgets and widgets.get("isBankOpen", False):
            return True

        return False
    
    def is_shop_open(self) -> bool:
        """
        Check if a shop interface is open.
        
        Returns:
            True if shop is open
        """
        if not self.window.window:
            return False
        
        self.window.capture()
        text = self.window.read_text(SHOP_TITLE_REGION)
        
        return SHOP_TITLE_TEXT in text
    
    def is_dialogue_open(self) -> bool:
        """
        Check if a dialogue box is currently displayed.
        
        Returns:
            True if dialogue is active
        """
        if not self.window.window:
            return False
        
        self.window.capture()
        
        # Look for "Click here to continue" or dialogue options
        text = self.window.read_text(DIALOGUE_BOX_REGION)
        
        dialogue_keywords = ["Click here to continue", "Select an option", "Please choose"]
        
        return any(keyword in text for keyword in dialogue_keywords)
    
    def continue_dialogue(self) -> bool:
        """
        Click to continue through dialogue.
        
        Returns:
            True if click was performed
        """
        if not self.window.window:
            return False
        
        if self.is_dialogue_open():
            import time
            time.sleep(random.uniform(0.5, 1.2))
            self.window.move_mouse_to(DIALOGUE_CONTINUE_REGION.random_point())
            self.window.click()
            return True
        
        return False
    
    def is_level_up_shown(self) -> bool:
        """
        Check if a level up notification is displayed.
        
        Returns:
            True if level up notification visible
        """
        if not self.window.window:
            return False
        
        self.window.capture()
        
        # Check for bright yellow text typical of level up messages
        found = self.window.find_color_region(
            LEVEL_UP_COLOR,
            region=LEVEL_UP_REGION,
            tolerance=40
        )
        
        return found is not None
    
    def get_health_percent(self) -> Optional[int]:
        """
        Get current health percentage from health orb using RuneLite API.
        
        Returns:
            Health percentage (0-100) or None if unable to detect
        """
        player_data = self.api.get_player()
        if player_data:
            health = player_data.get('health', 0)
            max_health = player_data.get('maxHealth', 1)
            if max_health > 0:
                return int((health / max_health) * 100)
        return None
    
    def get_prayer_percent(self) -> Optional[int]:
        """
        Get current prayer percentage from prayer orb using RuneLite API.
        
        Returns:
            Prayer percentage (0-100) or None if unable to detect
        """
        player_data = self.api.get_player()
        if player_data:
            prayer = player_data.get('prayer', 0)
            max_prayer = player_data.get('maxPrayer', 1)
            if max_prayer > 0:
                return int((prayer / max_prayer) * 100)
        return None
    
    def get_run_energy(self) -> Optional[int]:
        """
        Get current run energy percentage using RuneLite API.
        
        Returns:
            Run energy percentage (0-100) or None if unable to detect
        """
        player_data = self.api.get_player()
        if player_data:
            return player_data.get('runEnergy', None)
        return None
    
    def is_in_combat(self) -> bool:
        """
        Check if player is currently in combat using RuneLite API.
        
        Returns:
            True if in combat
        """
        combat_data = self.api.get_combat()
        if combat_data:
            return combat_data.get('inCombat', False)
        return False
    
    def close_interface(self) -> bool:
        """
        Attempt to close any open interface by pressing ESC.
        
        Returns:
            True if close was attempted
        """
        if not self.window.window:
            return False
        
        # Use keyboard to press ESC
        import keyboard
        import time
        
        keyboard.press_and_release('esc')
        time.sleep(random.uniform(0.3, 0.6))
        
        return True
    
    def get_interface_state(self) -> InterfaceState:
        """
        Get comprehensive interface state snapshot.
        
        Returns:
            InterfaceState object with current state
        """
        return InterfaceState(
            bank_open=self.is_bank_open(),
            shop_open=self.is_shop_open(),
            dialogue_open=self.is_dialogue_open(),
            in_combat=self.is_in_combat(),
            level_up_shown=self.is_level_up_shown(),
            health_percent=self.get_health_percent(),
            prayer_percent=self.get_prayer_percent(),
            run_energy_percent=self.get_run_energy()
        )
    
    def wait_for_interface_close(self, interface_check_func, timeout: float = 5.0) -> bool:
        """
        Wait for a specific interface to close.
        
        Args:
            interface_check_func: Function that returns True if interface is open
            timeout: Maximum seconds to wait
            
        Returns:
            True if interface closed within timeout
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not interface_check_func():
                return True
            time.sleep(random.uniform(0.1, 0.3))
        
        return False
    
    def wait_for_bank_open(self, timeout: float = 5.0) -> bool:
        """
        Wait for bank interface to open.
        
        Args:
            timeout: Maximum seconds to wait
            
        Returns:
            True if bank opened within timeout
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_bank_open():
                return True
            time.sleep(random.uniform(0.1, 0.3))
        
        return False
