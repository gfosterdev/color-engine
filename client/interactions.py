"""
Game interactions system for OSRS bot.

Handles right-click menus, keyboard input, and generic game object interactions.
"""

from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
from util import Region, Window
import keyboard
import time
import random


# Right-click menu detection regions
MENU_REGION = Region(0, 0, 765, 503)  # Full game window for menu detection
MENU_OPTION_HEIGHT = 15  # Approximate height of each menu option

# Menu colors
MENU_BACKGROUND_COLOR = (94, 86, 83)  # Dark brown menu background
MENU_TEXT_COLOR = (255, 255, 255)  # White text


@dataclass
class GameObject:
    """
    Represents an interactable game object.
    
    Objects can be NPCs, rocks, trees, items, or any clickable entity.
    """
    name: str
    color: Tuple[int, int, int]
    object_type: str  # 'npc', 'object', 'item', etc.
    actions: Optional[List[str]] = None  # Available right-click actions
    hover_text: Optional[str] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []


class RightClickMenu:
    """
    Handles detection and interaction with right-click context menus.
    """
    
    def __init__(self, window: Window):
        """
        Initialize right-click menu handler.
        
        Args:
            window: Window instance for screen interaction
        """
        self.window = window
        self.last_menu_position: Optional[Tuple[int, int]] = None
    
    def is_menu_open(self) -> bool:
        """
        Check if a right-click menu is currently displayed.
        
        Returns:
            True if menu is visible
        """
        if not self.window.window:
            return False
        
        self.window.capture()
        
        # Look for menu background color
        found = self.window.find_color_region(
            MENU_BACKGROUND_COLOR,
            tolerance=20
        )
        
        return found is not None
    
    def wait_for_menu(self, timeout: float = 2.0) -> bool:
        """
        Wait for right-click menu to appear.
        
        Args:
            timeout: Maximum seconds to wait
            
        Returns:
            True if menu appeared
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_menu_open():
                return True
            time.sleep(random.uniform(0.05, 0.15))
        
        return False
    
    def read_menu_options(self) -> List[str]:
        """
        Read all options from the open menu using OCR.
        
        Returns:
            List of menu option texts
        """
        if not self.window.window or not self.is_menu_open():
            return []
        
        self.window.capture()
        
        # Read text from menu region
        # Note: This is a simplified implementation
        # In practice, you'd need to detect menu bounds first
        text = self.window.read_text(MENU_REGION)
        
        # Split by newlines to get individual options
        options = [line.strip() for line in text.split('\n') if line.strip()]
        
        return options
    
    def select_option(self, option_text: str, partial_match: bool = True) -> bool:
        """
        Select a specific option from the right-click menu.
        
        Args:
            option_text: Text of the option to select
            partial_match: Whether to match partial text
            
        Returns:
            True if option was found and clicked
        """
        if not self.is_menu_open():
            return False
        
        options = self.read_menu_options()
        
        for i, option in enumerate(options):
            if partial_match:
                if option_text.lower() in option.lower():
                    # Click on this option
                    # Estimate position based on index
                    return self._click_menu_option(i)
            else:
                if option_text.lower() == option.lower():
                    return self._click_menu_option(i)
        
        return False
    
    def _click_menu_option(self, index: int) -> bool:
        """
        Click a menu option by index.
        
        Args:
            index: Option index (0-based)
            
        Returns:
            True if click was performed
        """
        # This is a simplified implementation
        # In practice, you'd need to detect the actual menu position
        # and calculate the correct Y offset for each option
        
        # For now, just click and close menu
        time.sleep(random.uniform(0.1, 0.3))
        self.window.click()
        
        return True
    
    def close_menu(self) -> bool:
        """
        Close the right-click menu (usually by left-clicking elsewhere).
        
        Returns:
            True if close was attempted
        """
        if self.is_menu_open():
            # Click somewhere safe to close menu
            self.window.click()
            time.sleep(random.uniform(0.1, 0.2))
            return True
        return False


class KeyboardInput:
    """
    Handles keyboard input for typing and hotkeys.
    """
    
    @staticmethod
    def type_text(text: str, delay_min: float = 0.05, delay_max: float = 0.15) -> None:
        """
        Type text with human-like delays between keystrokes.
        
        Args:
            text: Text to type
            delay_min: Minimum delay between keys
            delay_max: Maximum delay between keys
        """
        for char in text:
            keyboard.write(char)
            time.sleep(random.uniform(delay_min, delay_max))
    
    @staticmethod
    def press_key(key: str, hold_time: Optional[float] = None) -> None:
        """
        Press and release a key.
        
        Args:
            key: Key to press (e.g., 'f1', 'esc', 'enter')
            hold_time: How long to hold the key (random if None)
        """
        if hold_time is None:
            hold_time = random.uniform(0.05, 0.12)
        
        keyboard.press(key)
        time.sleep(hold_time)
        keyboard.release(key)
    
    @staticmethod
    def press_hotkey(*keys: str) -> None:
        """
        Press a combination of keys simultaneously.
        
        Args:
            keys: Keys to press together (e.g., 'ctrl', 'c')
        """
        keyboard.press(*keys)
        time.sleep(random.uniform(0.05, 0.1))
        keyboard.release(*keys)
    
    @staticmethod
    def open_tab(tab_key: str) -> None:
        """
        Open a game tab using F-keys.
        
        Args:
            tab_key: Tab to open ('f1' through 'f7')
        """
        KeyboardInput.press_key(tab_key)
        time.sleep(random.uniform(0.2, 0.4))


class GameObjectInteraction:
    """
    Manages interaction with game objects using color detection and menus.
    """
    
    def __init__(self, window: Window):
        """
        Initialize game object interaction handler.
        
        Args:
            window: Window instance
        """
        self.window = window
        self.menu = RightClickMenu(window)
        self.keyboard = KeyboardInput()
    
    def find_object(self, game_object: GameObject, 
                    region: Optional[Region] = None) -> Optional[Region]:
        """
        Find a game object by its color marker.
        
        Args:
            game_object: GameObject to find
            region: Optional region to search within
            
        Returns:
            Region where object was found, or None
        """
        if not self.window.window:
            return None
        
        self.window.capture()
        
        # Note: region parameter not supported by find_color_region
        # If region filtering is needed, crop the screenshot first
        found = self.window.find_color_region(
            game_object.color,
            tolerance=20
        )
        
        return found
    
    def interact_with_object(self, game_object: GameObject, 
                            action: Optional[str] = None,
                            validate_hover: bool = True) -> bool:
        """
        Interact with a game object (left-click or right-click with action).
        
        Args:
            game_object: GameObject to interact with
            action: Specific action to select (right-click if provided)
            validate_hover: Whether to validate hover text before clicking
            
        Returns:
            True if interaction was successful
        """
        # Find the object
        found = self.find_object(game_object)
        
        if not found:
            return False
        
        # Move mouse to object
        self.window.move_mouse_to(found.random_point())
        time.sleep(random.uniform(0.1, 0.3))
        
        # Validate hover text if required
        if validate_hover and game_object.hover_text:
            from client.osrs import INTERACT_TEXT_REGION
            self.window.capture()
            text = self.window.read_text(INTERACT_TEXT_REGION)
            
            if game_object.hover_text.lower() not in text.lower():
                return False
        
        # Perform interaction
        if action:
            # Right-click and select action
            self.window.mouse.click(button='right')
            time.sleep(random.uniform(0.2, 0.4))
            
            if self.menu.wait_for_menu():
                return self.menu.select_option(action)
        else:
            # Left-click
            self.window.click()
            time.sleep(random.uniform(0.1, 0.2))
            return True
        
        return False
    
    def wait_for_object(self, game_object: GameObject, 
                       timeout: float = 10.0,
                       search_rotation: bool = True) -> Optional[Region]:
        """
        Wait for an object to appear, optionally rotating camera to search.
        
        Args:
            game_object: GameObject to wait for
            timeout: Maximum seconds to wait
            search_rotation: Whether to rotate camera if object not found
            
        Returns:
            Region where object was found, or None
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            found = self.find_object(game_object)
            
            if found:
                return found
            
            # If search rotation enabled and half timeout passed, try rotating
            if search_rotation and (time.time() - start_time) > (timeout / 2):
                # Rotate camera (min_drag_distance is required parameter)
                min_drag = random.randint(100, 200)
                self.window.rotate_camera(min_drag_distance=min_drag)
                time.sleep(random.uniform(0.5, 1.0))
            
            time.sleep(random.uniform(0.3, 0.6))
        
        return None
    
    def spam_click_object(self, game_object: GameObject, 
                         clicks: int = 3,
                         delay_min: float = 0.1,
                         delay_max: float = 0.3) -> bool:
        """
        Spam click an object multiple times (useful for depleting resources).
        
        Args:
            game_object: GameObject to click
            clicks: Number of clicks to perform
            delay_min: Minimum delay between clicks
            delay_max: Maximum delay between clicks
            
        Returns:
            True if at least one click was successful
        """
        success = False
        
        for _ in range(clicks):
            if self.interact_with_object(game_object, validate_hover=False):
                success = True
            
            time.sleep(random.uniform(delay_min, delay_max))
        
        return success
