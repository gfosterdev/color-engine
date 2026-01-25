from util import Window, Region
from client.inventory import InventoryManager
from client.interfaces import InterfaceDetector
from client.interactions import KeyboardInput
import time
import random

# Regions
INTERACT_TEXT_REGION = Region(12, 28, 350, 20)  # x,y,w,h
BANK_SEARCH_REGION = Region(85, 45, 400, 20)  # Bank search box
BANK_DEPOSIT_INVENTORY_BUTTON = Region(437, 288, 36, 32)  # Deposit inventory button
BANK_DEPOSIT_EQUIPMENT_BUTTON = Region(477, 288, 36, 32)  # Deposit equipment button

# Color References
BANK = (190, 25, 25)


class OSRS:
    def __init__(self):
        self.window = Window()
        self.window.find(title="RuneLite - xJawj", exact_match=True)
        self.inventory = InventoryManager(self.window)
        self.interfaces = InterfaceDetector(self.window)
        self.keyboard = KeyboardInput()
    
    def open_bank(self):
        """Open bank by clicking on bank booth/chest."""
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
        self.window.move_mouse_to(BANK_DEPOSIT_INVENTORY_BUTTON.random_point())
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