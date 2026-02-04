from typing import Optional
from util import Window
from util.window_util import Region
from util.types import Polygon
from config.game_objects import BankObjects
from config import items
from config.regions import (
    BANK_SEARCH_REGION,
    BANK_DEPOSIT_INVENTORY_REGION,
    BANK_DEPOSIT_EQUIPMENT_REGION
)
from config.timing import TIMING
from core.config import DEBUG
import time
import random


class BankManager:
    """Manages all bank-related operations."""
    
    def __init__(self, osrs_instance):
        """
        Initialize BankManager with reference to OSRS instance.
        
        Args:
            osrs_instance: Reference to OSRS class instance for API and helper access
        """
        self.osrs = osrs_instance
        self.window = osrs_instance.window
        self.api = osrs_instance.api
        self.interfaces = osrs_instance.interfaces
        self.inventory = osrs_instance.inventory
        self.keyboard = osrs_instance.keyboard
    
    def open(self) -> bool:
        """
        Open bank by clicking on bank booth/chest using RuneLite API.

        Returns:
            True if bank opened successfully
        """
        print("Attempting to open bank...")
        
        # Find any bank object (handles camera adjustment if needed)
        all_bank_ids = BankObjects.all_interactive()
        bank_entity = self.osrs.find_entity(all_bank_ids, "object")
        
        if not bank_entity:
            print("No bank objects found")
            return False
        
        # Click the bank
        if self.osrs.click_entity(bank_entity, "object", "Bank"):
            time.sleep(random.uniform(*TIMING.BANK_OPEN_WAIT))
            
            # Wait for bank to open
            if self.interfaces.wait_for_bank_open(timeout=5.0):
                print("Bank opened successfully")
                return True
            else:
                print("Bank did not open in time")
                return False
        
        print("Failed to click bank")
        return False
    
    def close(self) -> bool:
        """Close the bank interface."""
        if not self.interfaces.is_bank_open():
            return True
        
        print("Closing bank...")
        self.keyboard.press_key('esc')
        time.sleep(random.uniform(*TIMING.INTERFACE_CLOSE_DELAY))
        
        return not self.interfaces.is_bank_open()
    
    def deposit_all(self) -> bool:
        """Deposit entire inventory using the deposit inventory button."""
        if not self.interfaces.is_bank_open():
            print("Bank not open, cannot deposit")
            return False
        
        print("Depositing all items...")
        self.window.move_mouse_to(BANK_DEPOSIT_INVENTORY_REGION.random_point())
        self.window.click()
        time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))
        
        return True
    
    def deposit_item_by_id(self, item_id: int, quantity: str = "all") -> bool:
        """
        Deposit a specific item from inventory by its item ID.
        
        Args:
            item_id: Item ID to deposit
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
            time.sleep(random.uniform(*TIMING.INVENTORY_TAB_OPEN))
        
        # Populate inventory data from API
        self.inventory.populate()
        
        # Find the item in inventory by ID
        slot_index = None
        for slot in self.inventory.slots:
            if slot.item_id == item_id:
                slot_index = slot.index
                break
        
        if slot_index is None:
            print(f"Item with ID {item_id} not found in inventory")
            return False
        
        # Move to slot and perform action
        slot = self.inventory.slots[slot_index - 1]
        self.window.move_mouse_to(slot.region.random_point())
        
        if quantity == "all":
            # Right-click and select "Deposit-All"
            self.osrs.click("Deposit-All", None)
        else:
            # Left-click deposits 1
            self.window.click()
        
        time.sleep(random.uniform(*TIMING.BANK_DEPOSIT_ACTION))
        return True
    
    def withdraw_item(self, item_id: int, quantity: int | str = 1, search: bool = False) -> bool:
        """
        Withdraw an item from the bank.
        
        Args:
            item_id: ID of the item to withdraw
            quantity: Number to withdraw [1, 5, 10, "All"]
            search: Whether to search for the item if not immediately accessible
        Returns:
            True if withdrawal was attempted
        """
        if not self.interfaces.is_bank_open():
            print("Bank not open, cannot withdraw")
            return False
        
        # Validate quantity
        if isinstance(quantity, int):
            if quantity not in [1, 5, 10]:
                print("Quantity must be 1, 5, 10, or 'All'")
                return False
        elif quantity != "All":
            print("Quantity must be 1, 5, 10, or 'All'")
            return False
        
        # Item constant
        item_constant = items.find_item(item_id)
        if not item_constant:
            print("ITEM IS NOT CONFIGURED IN ITEMS.PY, CANNOT WITHDRAW")
            raise ValueError("Item ID not configured in items.py")
            return False

        if DEBUG:
            print(f"Withdrawing {quantity} {item_constant.name}...")
        
        # Should search
        if search:
            # Type into search box
            if not self.search(item_constant.name):
                print("Failed to perform bank search")
                return False
            time.sleep(random.uniform(*TIMING.BANK_SEARCH_TYPE))

        # Grab bank item info via api
        item = self.api.get_bank_item(item_id)
        if not item:
            print(f"Item ID {item_id} not found in bank")
            return False
        
        widget = item.get('widget', None)
        if not widget:
            print(f"Item ID {item_id} has no widget data")
            return False

        if not widget.get('accessible', False) and not widget.get('hidden', False):
            if search:
                print(f"Item ID {item_id} is still not accessible after search")
                return False
            if DEBUG:
                print(f"Item ID {item_id} is not accessible in bank (may need to search)")
            return self.withdraw_item(item_id, quantity, search=True)
        
        if DEBUG:
            print("Item found without search, moving to item...")
        # Move mouse to item
        item_region = Region(widget['x'], widget['y'], widget['width'], widget['height'])
        self.window.move_mouse_to(item_region.random_point())
        time.sleep(random.uniform(*TIMING.MOUSE_MOVE_MEDIUM))
        # Click to withdraw
        self.osrs.click(f"Withdraw-{quantity}", None)
        time.sleep(random.uniform(*TIMING.BANK_WITHDRAW_ACTION))

        if search:
            # Close search box
            self._click_search_box()

        return True
    
    def search(self, search_text: str) -> bool:
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
        self._click_search_box()
        
        # Type search text
        self.keyboard.type_text(search_text)
        time.sleep(random.uniform(*TIMING.BANK_SEARCH_TYPE))
        
        return True

    def find(self) -> Optional[Polygon]:
        """
        Find nearest bank object using RuneLite API (handles camera adjustment if needed).
        
        Returns:
            Polygon of bank object convex hull, or None if not found
        """
        all_bank_ids = BankObjects.all_interactive()
        bank_entity = self.osrs.find_entity(all_bank_ids, "object")
        
        if bank_entity:
            hull = bank_entity.get('hull', None)
            if hull and hull.get('points'):
                print(f"Found bank: {bank_entity.get('name', 'Unknown')}")
                return Polygon(hull['points'])
        
        print("No bank objects found")
        return None

    def _click_search_box(self):
        """
        Clicks search box UI element
        """
        self.window.move_mouse_to(BANK_SEARCH_REGION.random_point())
        self.window.click()
        time.sleep(random.uniform(*TIMING.INTERFACE_TRANSITION))