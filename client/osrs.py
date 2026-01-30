from typing import Optional
from click import option
from util import Window
from util.types import Polygon
from client.inventory import InventoryManager
from client.interfaces import InterfaceDetector
from client.interactions import RightClickMenu, KeyboardInput
from client.navigation import NavigationManager
from client.runelite_api import RuneLiteAPI
from config.regions import (
    INTERACT_TEXT_REGION,
    BANK_SEARCH_REGION,
    BANK_DEPOSIT_INVENTORY_REGION,
    BANK_DEPOSIT_WORN_ITEMS_REGION,
    LOGIN_EXISTING_USER_BUTTON,
    LOGIN_BUTTON_REGION,
    LOGIN_CLICK_HERE_TO_PLAY_REGION,
    UI_LOGOUT_ICON_REGION,
    UI_LOGOUT_BUTTON_REGION
)
import time
import random

# Color References
BANK = (190, 25, 25)


class OSRS:
    def __init__(self, profile_config=None):
        self.window = Window()
        self.window.find(title="RuneLite - xJawj", exact_match=False)
        self.inventory = InventoryManager(self.window)
        self.interfaces = InterfaceDetector(self.window)
        self.navigation = NavigationManager(self.window)
        self.keyboard = KeyboardInput()
        self.profile_config = profile_config
        self.api = RuneLiteAPI()
    
    def click(self, option: str, target: Optional[str] = None):
        """
        Checks if we can left click, if not attempts a right click.
        """
        menu = RightClickMenu(self.window)
        print(f"Menu is open: {menu.is_open}")

        can_left_click = menu.can_left_click(option, target)
        print(f"Can left click: {can_left_click}")
        if can_left_click:
            print("Performing left click...")
            self.window.click()
            time.sleep(random.uniform(0.1, 0.3))
            print("✓ Left clicked")
        else:
            if not menu.is_open:
                print("Opening menu...")
                menu.open()
                time.sleep(random.uniform(0.1, 0.3))
                print(f"Menu is open: {menu.is_open}")
            
            menu.populate()
            if menu.is_open:
                print(f"\nSelecting menu entry with option {option}")
                entry = menu.get_entry(option, target)
                if entry:
                    index = entry.get('index')
                    if not index:
                        print(f"✗ Could not find index for entry {entry}")
                        return
                    index = int(index)
                    print(f"Clicking entry: {entry}")
                    menu.click_entry(index)
                    time.sleep(random.uniform(0.1, 0.3))
                    print("✓ Clicked")
            
            menu.populate()
            if menu.is_open:
                print("Closing menu...")
                menu.close()
                time.sleep(random.uniform(0.1, 0.3))
                print(f"Menu is open: {menu.is_open}")

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
        
        password = self.profile_config["credentials"]["password"]
        
        if not password:
            print("Password is empty in profile configuration")
            return False
        
        return self.login(password)
    
    def open_bank(self) -> bool:
        """
        Open bank by clicking on bank booth/chest.

        Returns:
            True if bank opened successfully
        """

        print("Attempting to open bank...")
        if self.window.window:
            self.window.capture()
            found = self.window.find_color_region(BANK, debug=True)
            if found:
                print("Bank color found, moving mouse to it...")
                self.window.move_mouse_to(found.random_point())
                if self.validate_interact_text("Bank"):
                    self.window.click()
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    # Wait for bank to open
                    if self.interfaces.wait_for_bank_open(timeout=5.0):
                        print("Bank opened successfully")
                        return True
                    else:
                        print("Bank did not open in time")
            else:
                print("Bank color not found on screen.")
        return False
    
    def close_bank(self) -> bool:
        """Close the bank interface."""
        if not self.interfaces.is_bank_open():
            return True
        
        print("Closing bank...")
        self.keyboard.press_key('esc')
        time.sleep(random.uniform(0.3, 0.6))
        
        return not self.interfaces.is_bank_open()
    
    def deposit_all(self) -> bool:
        """Deposit entire inventory using the deposit inventory button."""
        if not self.interfaces.is_bank_open():
            print("Bank not open, cannot deposit")
            return False
        
        print("Depositing all items...")
        self.window.move_mouse_to(BANK_DEPOSIT_INVENTORY_REGION.random_point())
        time.sleep(random.uniform(0.2, 0.4))
        self.window.click()
        time.sleep(random.uniform(0.5, 0.8))
        
        return True
    
    def deposit_item_by_color(self, item_color: tuple, quantity: str = "all") -> bool:
        """
        Deposit a specific item from inventory by its color.
        
        Args:
            item_color: RGB tuple of the item
            quantity: "all", "1", "5", "10", or "X"
            
        Returns:
            True if item was found and deposited
        """
        if not self.interfaces.is_bank_open():
            print("Bank not open, cannot deposit item")
            return False
        
        # Ensure inventory tab is open
        if not self.inventory.is_inventory_open():
            self.inventory.open_inventory()
            time.sleep(random.uniform(0.3, 0.5))
        
        # Find the item in inventory
        slots = self.inventory.find_item_by_color(item_color)
        
        if not slots:
            print(f"Item with color {item_color} not found in inventory")
            return False
        
        # Click the first item found
        slot_index = slots[0]
        
        if quantity == "all":
            # Right-click and select "Deposit-All"
            self.inventory.click_slot(slot_index, right_click=True)
            time.sleep(random.uniform(0.2, 0.4))
            # TODO: Implement menu option selection
            # For now, just left-click (deposits 1)
            self.inventory.click_slot(slot_index, right_click=False)
        else:
            # Left-click deposits 1
            self.inventory.click_slot(slot_index, right_click=False)
        
        time.sleep(random.uniform(0.3, 0.6))
        return True
    
    def withdraw_item(self, item_name: str, quantity: int = 1) -> bool:
        """
        Withdraw an item from the bank.
        
        Args:
            item_name: Name of the item to withdraw
            quantity: Number to withdraw
            
        Returns:
            True if withdrawal was attempted
        """
        if not self.interfaces.is_bank_open():
            print("Bank not open, cannot withdraw")
            return False
        
        print(f"Withdrawing {quantity}x {item_name}...")
        
        # Use bank search
        if self.search_bank(item_name):
            time.sleep(random.uniform(0.5, 0.8))
            # TODO: Click on the item in bank grid
            # This requires bank grid slot detection
            return True
        
        return False
    
    def search_bank(self, search_text: str) -> bool:
        """
        Type text into the bank search box.
        
        Args:
            search_text: Text to search for
            
        Returns:
            True if search was performed
        """
        if not self.interfaces.is_bank_open():
            return False
        
        print(f"Searching bank for: {search_text}")
        
        # Click on search box
        self.window.move_mouse_to(BANK_SEARCH_REGION.random_point())
        time.sleep(random.uniform(0.1, 0.3))
        self.window.click()
        time.sleep(random.uniform(0.2, 0.4))
        
        # Clear existing text
        self.keyboard.press_hotkey('ctrl', 'a')
        time.sleep(random.uniform(0.05, 0.1))
        
        # Type search text
        self.keyboard.type_text(search_text)
        time.sleep(random.uniform(0.2, 0.4))
        
        return True

    def find_bank(self):
        """Find bank using camera rotation search."""
        if self.window.window:
            self.window.capture()
            found = self.window.search(rgb=BANK, debug=True, rotation_amount=300)
            if found:
                return found.random_point()
        return None

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
                    print(f"Found expected interact text: {option}")
                    return True
            print(f"Expected interact text '{expected_text}' not found in menu entries.")
        return False

    def validate_interact_text_ocr(self, expected_text):
        """Validate hover text matches expected text."""
        if self.window.window:
            self.window.capture()
            text = self.window.read_text(INTERACT_TEXT_REGION, debug=True)
            if expected_text in text:
                print(f"Found expected text: {expected_text}")
                return True
            else:
                print(f"Expected text '{expected_text}' not found. Extracted text: {text}")
                return False
        return False
    
    def click_npc(self, npc_id, action: str):
        """
        Click on an NPC by it's ID.
        """
        npc = self.api.get_npc_in_viewport(npc_id)
        if not npc:
            print(f"NPC with ID {npc_id} not found in viewport.")
            return False
        
        target = npc.get('name', None)

        hull = npc.get('hull', None)
        if hull:
            points = hull.get('points', None)
            if points:
                polygon = Polygon(points)
                click_point = polygon.random_point_inside(self.window.GAME_AREA)
                self.window.move_mouse_to(click_point, in_canvas =True, duration=random.uniform(0.1, 0.3))
                time.sleep(random.uniform(0.05, 0.1))
                self.click(action, target)
                time.sleep(random.uniform(0.5, 0.8))
                return True
            
        return False

    def click_game_object(self, obj_id, action: str):
        """
        Click on a game object by it's ID.
        """
        game_object = self.api.get_game_object_in_viewport(obj_id)
        if not game_object:
            print(f"Game object with ID {obj_id} not found in viewport.")
            return False
        
        target = game_object.get('name', None)

        hull = game_object.get('hull', None)
        if hull:
            points = hull.get('points', None)
            if points:
                polygon = Polygon(points)
                click_point = polygon.random_point_inside(self.window.GAME_AREA)
                self.window.move_mouse_to(click_point, in_canvas=True)
                time.sleep(random.uniform(0.2, 0.4))
                self.click(action, target)
                time.sleep(random.uniform(0.5, 0.8))
                return True

        return False
        
    def open_right_click_menu(self):
        """
        Attemps to open right click menu.

        Returns:
            True if menu opened else False.
        """
        menu_state = self.api.get_menu()
        if menu_state and menu_state.get('isOpen'):
            print("Right click menu is already open.")
            return menu_state
        print("Opening right click menu...")
        self.window.click(button='right')
        time.sleep(random.uniform(0.2, 0.4))

        # Validate menu is open
        menu_state = self.api.get_menu()
        if not (menu_state and menu_state.get('isOpen')):
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

    def login(self, password: str) -> bool:
        """.
        Log into OSRS using existing user credentials.
        
        Assumes username is remembered and cursor starts on password field.
        
        Args:
            password: Account password to enter
            
        Returns:
            True if successfully logged in
        """
        print("Starting login process...")
        
        if not self.window.window:
            print("Window not found")
            return False
        
        # Verify we're at the login screen
        if not self.is_at_login_screen():
            print("Not at login screen - cannot proceed with login")
            return False
        
        # Click "Existing User" button
        print("Clicking 'Existing User' button...")
        self.window.capture()
        self.window.move_mouse_to(LOGIN_EXISTING_USER_BUTTON.random_point())
        time.sleep(random.uniform(0.3, 0.6))
        self.window.click()
        time.sleep(random.uniform(0.8, 1.5))
        
        # Type password
        print("Entering password...")
        self.keyboard.type_text(password)
        time.sleep(random.uniform(0.3, 0.6))
        
        # Click login button
        print("Clicking login button...")
        self.window.capture()
        self.window.move_mouse_to(LOGIN_BUTTON_REGION.random_point())
        time.sleep(random.uniform(0.3, 0.6))
        self.window.click()
        
        # Wait and check for "Click here to play" screen
        print("Waiting for character selection screen...")
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(random.uniform(1.0, 1.5))

            # Check if state is not LOGGING_IN
            game_state = self.api.get_game_state()
            if game_state and game_state.get("state", "") != "LOGGING_IN":
                # Either logged in or incorrect details
                if self.is_logged_in():
                    time.sleep(random.uniform(1.5, 2.5))
                    # Click to enter game
                    print("Clicking to enter game...")
                    self.window.move_mouse_to(LOGIN_CLICK_HERE_TO_PLAY_REGION.random_point())
                    time.sleep(random.uniform(0.3, 0.6))
                    self.window.click()
                    time.sleep(random.uniform(2.0, 3.0))
                    
                    print("Login successful!")
                    return True
                else:
                    print("Login failed - incorrect credentials or other issue")
                    return False
        
        print("Login verification timed out")
        return False
    
    def logout(self) -> bool:
        """
        Log out of the account.
        
        Returns:
            True if logout was successful
        """
        print("Starting logout process...")
        
        if not self.window.window:
            print("Window not found")
            return False
        
        # Close any open interfaces first (bank, shop, etc.)
        print("Closing any open interfaces...")
        self.interfaces.close_interface()
        
        # Click logout icon to open the menu
        print("Clicking logout icon...")
        self.window.capture()
        self.window.move_mouse_to(UI_LOGOUT_ICON_REGION.random_point())
        time.sleep(random.uniform(0.2, 0.4))
        self.window.click()
        time.sleep(random.uniform(0.5, 0.8))
        
        # Verify logout panel opened by checking for "Logout" text
        print("Verifying logout panel opened...")
        self.window.capture()
        logout_text = self.window.read_text(UI_LOGOUT_BUTTON_REGION, debug=True)
        
        if not logout_text or "logout" not in logout_text.lower():
            print(f"Logout panel did not open. Another interface may have priority. Extracted text: {logout_text}")
            return False
        
        print("Logout panel confirmed open")
        
        # Click the logout button in the menu
        print("Clicking logout button...")
        self.window.move_mouse_to(UI_LOGOUT_BUTTON_REGION.random_point())
        time.sleep(random.uniform(0.2, 0.4))
        self.window.click()
        time.sleep(random.uniform(1.5, 2.5))
        
        # Verify we're back at login screen
        print("Verifying logout successful...")
        if self.is_at_login_screen():
            print("Logout complete!")
            return True
        else:
            print("Logout verification failed. Not at login screen.")
            return False