from typing import Optional, Union, List
from click import option
from util import Window
from util.types import Polygon
from client.inventory import InventoryManager
from client.interfaces import InterfaceDetector
from client.interactions import RightClickMenu, KeyboardInput
from client.navigation import NavigationManager
from client.runelite_api import RuneLiteAPI
from client.camera_controller import CameraController
from client.bank import BankManager
from core.config import DEBUG
from config.regions import (
    INTERACT_TEXT_REGION,
    LOGIN_EXISTING_USER_BUTTON,
    LOGIN_BUTTON_REGION,
    LOGIN_CLICK_HERE_TO_PLAY_REGION,
    UI_LOGOUT_ICON_REGION,
    UI_LOGOUT_BUTTON_REGION
)
from config.timing import TIMING, CAMERA_ROTATION_MAX_RETRIES
import time
import random
import keyboard


class OSRS:
    def __init__(self, profile_config=None):
        self.window = Window()
        self.window.find(title="RuneLite - xJawj", exact_match=False)
        self.profile_config = profile_config
        self.api = RuneLiteAPI()
        self.camera = CameraController(self)
        
        # Initialize managers that need osrs reference
        self.inventory = InventoryManager(self)
        self.interfaces = InterfaceDetector(self.window)
        self.navigation = NavigationManager(self.window)
        self.keyboard = KeyboardInput()
        self.bank = BankManager(self)
    
    def click(self, option: str, target: Optional[str] = None):
        """
        Checks if we can left click, if not attempts a right click.
        """
        menu = RightClickMenu(self.window)

        can_left_click = menu.can_left_click(option, target)
        if can_left_click:
            self.window.click()
            if DEBUG:
                print("✓ Left clicked")
        else:
            if not menu.is_open:
                menu.open()
            
            menu.populate()
            if menu.is_open:
                entry = menu.get_entry(option, target)
                if entry:
                    index = entry.get('index')
                    if not index:
                        if DEBUG:
                            print(f"✗ Could not find index for entry {entry}")
                        return
                    index = int(index)
                    menu.click_entry(index)
                    if DEBUG:
                        print("✓ Clicked")
            
            menu.populate()
            if menu.is_open:
                menu.close()

    def login_from_profile(self) -> bool:
        """.
        Log in using password from profile configuration.
        
        Returns:
            True if login successful
        """
        if not self.profile_config:
            print("No profile configuration provided")
            return False
        
        if "credentials" not in self.profile_config or "password" not in self.profile_config["credentials"]:
            print("No password found in profile configuration")
            return False
        
        username = self.profile_config["credentials"]["username"]
        password = self.profile_config["credentials"]["password"]
        
        if not username:
            print("Username is empty in profile configuration")
            return False
        if not password:
            print("Password is empty in profile configuration")
            return False
        
        return self.login(username, password)

    def validate_interact_text(self, expected_text):
        """
        Validate right click menu has expected text.
        """
        menu = self.api.get_menu()
        menu_entries = menu.get("entries", []) if menu else []
        if menu_entries:
            for entry in menu_entries:
                option = entry.get("option", "")
                if expected_text.lower() in option.lower():
                    if DEBUG:
                        print(f"Found expected interact text: {option}")
                    return True
            if DEBUG:
                print(f"Expected interact text '{expected_text}' not found in menu entries.")
        return False
    
    def click_entity(self, entity_id_or_dict: Union[int, dict], entity_type: str, action: str) -> bool:
        """
        Click on a game entity (NPC or object) by its ID or using an already-retrieved entity.
        
        Args:
            entity_id_or_dict: Either an entity ID (int) or an entity dict from get_entity_in_viewport
            entity_type: Type of entity - either "npc" or "object"
            action: Action to perform (e.g., "Attack", "Mine", "Chop", "Bank")
            
        Returns:
            True if successfully clicked, False otherwise
        """
        if entity_type not in ["npc", "object"]:
            raise ValueError(f"entity_type must be 'npc' or 'object', got '{entity_type}'")
        
        # If it's an int, fetch the entity; if it's a dict, use it directly
        if isinstance(entity_id_or_dict, int):
            entity = self.api.get_entity_in_viewport(entity_id_or_dict, entity_type)
            if not entity:
                if DEBUG:
                    print(f"{entity_type.capitalize()} with ID {entity_id_or_dict} not found in viewport.")
                return False
        else:
            entity = entity_id_or_dict
        
        target = entity.get('name', None)

        hull = entity.get('hull', None)
        if hull:
            points = hull.get('points', None)
            if points:
                polygon = Polygon(points)
                try:
                    click_point = polygon.random_point_inside(self.window.GAME_AREA)
                except Exception as e:
                    if DEBUG:
                        print(f"Failed to get random point inside polygon: {e}")
                    return False
                self.window.move_mouse_to(click_point, in_canvas=True)
                self.click(action, target)
                
                # Use appropriate delay based on entity type
                delay = TIMING.NPC_INTERACT_DELAY if entity_type == "npc" else TIMING.OBJECT_INTERACT_DELAY
                time.sleep(random.uniform(*delay))
                return True
            
        return False
    
    def find_entity(self, entity_ids: Union[int, List[int]], entity_type: str) -> Optional[dict]:
        """
        Find an entity (game object or NPC) by ID(s), using camera adjustment if needed.
        
        First checks if any matching entity exists in the viewport. If not found, searches for
        the nearest entity matching any of the IDs and adjusts the camera to point at it, then
        verifies it's in the viewport.
        
        Args:
            entity_ids: Game object ID(s) or NPC ID(s) to search for (single int or list)
            entity_type: Type of entity - either "npc" or "object"
            
        Returns:
            Entity dictionary with hull data if found in viewport, None otherwise
        """
        if entity_type not in ["npc", "object"]:
            raise ValueError(f"entity_type must be 'npc' or 'object', got '{entity_type}'")
        
        # Normalize to list
        if isinstance(entity_ids, int):
            entity_ids = [entity_ids]
        
        # First check if entity already in viewport
        if DEBUG:
            print(f"[find_entity] Checking if {entity_type} {entity_ids} exists in viewport...")
        entity = self.api.get_entity_in_viewport(entity_ids=entity_ids, entity_type=entity_type, selection="nearest")
        
        if entity:
            if DEBUG:
                print(f"[find_entity] ✓ {entity_type.capitalize()} found in viewport")
            return entity
        
        # Not in viewport, find nearest entity in current world, not viewport
        if DEBUG:
            print(f"[find_entity] {entity_type.capitalize()} not in viewport, searching for nearest...")
        nearest = self.api.get_nearest_by_id(entity_ids, entity_type)
        
        if not nearest or not nearest.get('found', False):
            if DEBUG:
                print(f"[find_entity] ✗ No {entity_type} with IDs {entity_ids} found nearby")
            return None
        
        # Extract coordinates
        world_x = nearest.get('worldX')
        world_y = nearest.get('worldY')
        plane = nearest.get('plane', 0)
        distance = nearest.get('distance', 0)
        
        if world_x is None or world_y is None:
            if DEBUG:
                print(f"[find_entity] ✗ Nearest entity missing coordinate data")
            return None
        
        if DEBUG:
            print(f"[find_entity] Found nearest {entity_type} at ({world_x}, {world_y}, plane {plane}), distance: {distance} tiles")
        
        # Point camera at the entity
        if DEBUG:
            print(f"[find_entity] Adjusting camera to point at entity...")
        camera_success = self.camera.set_camera_to_tile(world_x, world_y, plane)
        
        if not camera_success:
            if DEBUG:
                print(f"[find_entity] ✗ Failed to adjust camera to entity location")
            return None
        
        if DEBUG:
            print(f"[find_entity] ✓ Camera adjusted, verifying entity in viewport...")
        
        # Verify entity is now in viewport - pass world coords to get the specific entity
        time.sleep(random.uniform(0.3, 0.5))  # Brief delay for render
        entity = self.api.get_entity_in_viewport(entity_ids, entity_type, world_x, world_y)
        
        if entity:
            if DEBUG:
                print(f"[find_entity] ✓ {entity_type.capitalize()} now visible in viewport")
            return entity
        else:
            if DEBUG:
                print(f"[find_entity] ✗ {entity_type.capitalize()} still not visible after camera adjustment")
            return None
        
    def open_right_click_menu(self):
        """
        Attemps to open right click menu.

        Returns:
            True if menu opened else False.
        """
        menu_state = self.api.get_menu()
        if menu_state and menu_state.get('isOpen'):
            if DEBUG:
                print("Right click menu is already open.")
            return menu_state
        if DEBUG:
            print("Opening right click menu...")
        self.window.click(button='right')

        # Validate menu is open
        menu_state = self.api.get_menu()
        if not (menu_state and menu_state.get('isOpen')):
            if DEBUG:
                print("Failed to open right click menu.")
            return None
        return menu_state

    def is_at_login_screen(self) -> bool:
        """
        Check if we are at the login screen.
        
        Returns:
            True if at login screen
        """
        if not self.window.window:
            return False
        
        game_state = self.api.get_game_state()
        return bool(game_state and game_state.get("state", "") == "LOGIN_SCREEN")
    
    def is_logged_in(self) -> bool:
        """
        Check if we are logged into the game.
        
        Returns:
            True if logged in
        """
        if not self.window.window:
            return False
        
        game_state = self.api.get_game_state()
        return bool(game_state and game_state.get("isLoggedIn", False))

    def login(self, username: str, password: str) -> bool:
        """.
        Log into OSRS using existing user credentials.
        
        Args:
            username: Account username to enter
            password: Account password to enter
            
        Returns:
            True if successfully logged in
        """
        if DEBUG:
            print("Starting login process...")
        
        if not self.window.window:
            if DEBUG:
                print("Window not found")
            return False
        
        # Verify we're at the login screen
        if not self.is_at_login_screen():
            if DEBUG:
                print("Not at login screen - cannot proceed with login")
            return False
        
        # Click "Existing User" button
        if DEBUG:
            print("Clicking 'Existing User' button...")
        self.window.move_mouse_to(LOGIN_EXISTING_USER_BUTTON.random_point())
        self.window.click()
        time.sleep(random.uniform(*TIMING.LOGIN_BUTTON_DELAY))
        
        # Type username
        if DEBUG:
            print("Entering username...")
        self.keyboard.type_text(username)
        time.sleep(random.uniform(*TIMING.INTERFACE_TRANSITION))

        # Press tab to move to password field
        if DEBUG:
            print("Pressing Tab to move to password field...")
        keyboard.press_and_release('tab')
        time.sleep(random.uniform(*TIMING.INTERFACE_TRANSITION))

        # Type password
        if DEBUG:
            print("Entering password...")
        self.keyboard.type_text(password)
        time.sleep(random.uniform(*TIMING.INTERFACE_TRANSITION))
        
        # Click login button
        if DEBUG:
            print("Clicking login button...")
        self.window.move_mouse_to(LOGIN_BUTTON_REGION.random_point())
        self.window.click()
        
        # Wait and check for "Click here to play" screen
        if DEBUG:
            print("Waiting for character selection screen...")
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(random.uniform(*TIMING.LOGIN_VERIFY_DELAY))

            # Check if state is not LOGGING_IN
            game_state = self.api.get_game_state()
            if game_state and game_state.get("state", "") != "LOGGING_IN":
                # Either logged in or incorrect details
                if self.is_logged_in():
                    time.sleep(random.uniform(*TIMING.LOGIN_VERIFY_DELAY))
                    # Click to enter game
                    if DEBUG:
                        print("Clicking to enter game...")
                    self.window.move_mouse_to(LOGIN_CLICK_HERE_TO_PLAY_REGION.random_point())
                    self.window.click()
                    # Extra delay for world load
                    min_delay, max_delay = TIMING.LOGIN_BUTTON_DELAY
                    time.sleep(random.uniform(min_delay + 1.0, max_delay + 2.0))
                    
                    if DEBUG:
                        print("Login successful!")
                    return True
                else:
                    if DEBUG:
                        print("Login failed - incorrect credentials or other issue")
                    return False
        
        if DEBUG:
            print("Login verification timed out")
        return False
    
    def logout(self) -> bool:
        """
        Log out of the account.
        
        Returns:
            True if logout was successful
        """
        if DEBUG:
            print("Starting logout process...")
        
        if not self.window.window:
            if DEBUG:
                print("Window not found")
            return False
        
        # Close any open interfaces first (bank, shop, etc.)
        if DEBUG:
            print("Closing any open interfaces...")
        self.interfaces.close_interface()
        
        # Click logout icon to open the menu
        if DEBUG:
            print("Clicking logout icon...")
        self.window.move_mouse_to(UI_LOGOUT_ICON_REGION.random_point())
        self.window.click()
        time.sleep(random.uniform(*TIMING.LOGOUT_PANEL_DELAY))
        
        # Verify logout panel opened by checking for "Logout" text
        if DEBUG:
            print("Verifying logout panel opened...")
        sidebar = self.api.get_sidebar_tab("logout")
        if not sidebar:
            print("✗ Failed to retrieve logout sidebar data")
            return False
        
        if not sidebar.get('isOpen', False):
            if DEBUG:
                print("Logout panel did not open. Another interface may have priority.")
            return False
        
        if DEBUG:
            print("Logout panel confirmed open")
        
        # Click the logout button in the menu
        if DEBUG:
            print("Clicking logout button...")
        self.window.move_mouse_to(UI_LOGOUT_BUTTON_REGION.random_point())
        self.window.click()
        # Extra time for logout
        min_delay, max_delay = TIMING.LOGIN_BUTTON_DELAY
        time.sleep(random.uniform(min_delay + 0.5, max_delay + 1.0))
        
        # Verify we're back at login screen
        if DEBUG:
            print("Verifying logout successful...")
        if self.is_at_login_screen():
            if DEBUG:
                print("Logout complete!")
            return True
        else:
            if DEBUG:
                print("Logout verification failed. Not at login screen.")
            return False

    def get_equipped_tool_id(self, slot: int = 3) -> Optional[int]:
        """
        Get the item ID of the equipped tool in a specific slot.
        
        Args:
            slot: Equipment slot (default 3 for weapon/tool)
                  Common slots: 3=weapon, 0=head, 4=body, etc.
        
        Returns:
            Item ID if something is equipped, None otherwise
        """
        equipment = self.api.get_equipment()
        if not equipment:
            return None
        
        # Equipment API returns list of equipped items
        for item in equipment:
            if item.get('slot') == slot:
                return item.get('id')
        
        return None

    def verify_tool_equipped(self, required_tool_ids: list[int], slot: int = 3) -> bool:
        """
        Verify that one of the required tools is equipped in the specified slot.
        
        Args:
            required_tool_ids: List of acceptable tool item IDs
            slot: Equipment slot to check (default 3 for weapon/tool)
        
        Returns:
            True if a required tool is equipped, False otherwise
        """
        equipped_id = self.get_equipped_tool_id(slot)
        if equipped_id in required_tool_ids:
            if DEBUG:
                print(f"✓ Required tool equipped (ID: {equipped_id})")
            return True
        else:
            if DEBUG:
                print(f"✗ No required tool equipped in slot {slot}")
            return False