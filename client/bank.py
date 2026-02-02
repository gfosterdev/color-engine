from typing import Optional
from util import Window
from util.types import Polygon
from config.game_objects import BankObjects
from config.regions import (
    BANK_SEARCH_REGION,
    BANK_DEPOSIT_INVENTORY_REGION,
    BANK_DEPOSIT_EQUIPMENT_REGION
)
from config.timing import TIMING
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
        if self.search(item_name):
            time.sleep(random.uniform(*TIMING.BANK_SEARCH_TYPE))
            # TODO: Click on the item in bank grid
            # This requires bank grid slot detection
            return True
        
        return False
    
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
        self.window.move_mouse_to(BANK_SEARCH_REGION.random_point())
        self.window.click()
        time.sleep(random.uniform(*TIMING.INTERFACE_TRANSITION))
        
        # Clear existing text
        self.keyboard.press_hotkey('ctrl', 'a')
        time.sleep(random.uniform(*TIMING.MICRO_DELAY))
        
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
