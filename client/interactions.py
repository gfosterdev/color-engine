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

from .runelite_api import RuneLiteAPI

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
        """
        self.window = window
        self.api = RuneLiteAPI()

        self.is_open = None
        self.entries = None
        self.x = None
        self.y = None
        self.width = None
        self.height = None

        self.populate()

    def populate(self):
        """
        Populate the current menu state from the API.
        """
        menu = self.api.get_menu()
        if not menu:
            return
        self.is_open = menu.get('isOpen', False)
        self.entries = menu.get('entries', [])
        self.x = menu.get('x', 0)
        self.y = menu.get('y', 0)
        self.width = menu.get('width', 0)
        self.height = menu.get('height', 0)

    def open(self) -> bool:
        """
        Open the right-click menu by right-clicking at current mouse position.
        
        Returns:
            True if menu is detected as open after action
        """
        self.window.mouse.click(button='right')
        time.sleep(random.uniform(0.2, 0.4))
        self.populate()
        return self.is_open if self.is_open is not None else False

    def get_entries(self) -> List[Dict[str, str]]:
        """
        Get the current menu entries.
        
        Returns:
            List of menu entry dicts if menu is open, else None
        """
        if self.is_open and self.entries:
            return self.entries
        return []

    def get_entry(self, option: str, target: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Get a menu entry by option text match.
        
        Args:
            option: The 'action' in the menu
            target: The 'target' in the menu (optional)
            
        Returns:
            Menu entry dict if found with index, else None
        """
        if not self.entries:
            return None
        
        for rev_idx, entry in enumerate(reversed(self.entries)):
            if option.lower() in entry.get('option', '').lower():
                entry['index'] = rev_idx + 1  # 1-based index from top
                if target:
                    if target.lower() in entry.get('target', '').lower():
                        return entry
                else:
                    return entry
        
        return None
    
    def click_entry(self, idx: int) -> bool:
        """
        Clicks a specific entry index.

        Args:
            idx: Index of the menu entry (1-based)
            
        Returns:
            True if option was found and clicked else False
        """
        if not self.is_open or not self.entries:
            return False
        
        if self.x is None or self.y is None or self.width is None or self.height is None:
            return False

        item_count = len(self.entries) + 1  # +1 to account for header
        item_height = int(self.height / item_count)
        if not (idx > item_count or idx < 1):
            y = self.y + (item_height * idx)
            point = Region(self.x, y + 4, self.width, item_height - 8)
            # self.window.move_mouse_to((point.x, point.y))
            # time.sleep(random.uniform(0.1, 0.3))
            # self.window.move_mouse_to((point.x + point.width, point.y))
            # time.sleep(random.uniform(0.1, 0.3))
            # self.window.move_mouse_to((point.x, point.y + point.height))
            # time.sleep(random.uniform(0.1, 0.3))
            # self.window.move_mouse_to((point.x + point.width, point.y + point.height))
            # time.sleep(random.uniform(0.1, 0.3))
            self.window.move_mouse_to(point.random_point())
            time.sleep(random.uniform(0.1, 0.3))
            self.window.click()
            return True
        else:
            print("Invalid index")
        
        return False
    
    def can_left_click(self, option: str, target: Optional[str] = None) -> bool:
        """
        Determine if an option can be left-clicked directly.
        
        Args:
            option: The 'action' in the menu
            target: The 'target' in the menu (optional)
        """
        entry = self.get_entry(option, target)
        if entry and entry.get('index', 0) == 1:
            return True
        return False

    def close(self) -> bool:
        """
        Close the right-click menu by moving mouse elsewhere.
        
        Returns:
            True if close was attempted
        """
        if self.is_open:
            if self.x is None or self.y is None or self.width is None or self.height is None:
                return False
            rand_region = Region(self.x, self.y - self.height + 5, self.width, self.height)
            self.window.move_mouse_to(rand_region.random_point())
            time.sleep(random.uniform(0.2, 0.4))
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
