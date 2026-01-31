"""
Inventory management system for OSRS bot.

Detects inventory slots, items, and counts using fixed client mode positions.
"""

from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import cv2
import numpy as np
from util import Region
from config.regions import INVENTORY_TAB_REGION
from .runelite_api import RuneLiteAPI


# Fixed mode inventory constants (positions for 28 slots in fixed client mode)
INVENTORY_START_X = 563
INVENTORY_START_Y = 213
INVENTORY_Y_OFFSET = 4
INVENTORY_X_OFFSET = 6
SLOT_WIDTH = 36
SLOT_HEIGHT = 32
SLOTS_PER_ROW = 4
TOTAL_SLOTS = 28

# Inventory tab color constant
INVENTORY_TAB_COLOR = (127, 84, 60)  # Brown color when selected


@dataclass
class InventorySlot:
    """Represents a single inventory slot."""
    index: int  # 1-28
    region: Region
    is_empty: bool = True
    item_id: Optional[int] = None
    quantity: Optional[int] = None
    item_name: Optional[str] = None
    
    def center(self) -> Tuple[int, int]:
        """Get the center point of the slot."""
        return self.region.center()
    
    def random_point(self) -> Tuple[int, int]:
        """Get a random point within the slot."""
        return self.region.random_point()


class InventoryManager:
    """
    Manages inventory detection and interaction.
    
    Assumes RuneLite client in fixed mode for consistent slot positions.
    """
    
    def __init__(self, window):
        """
        Initialize inventory manager.
        
        Args:
            window: Window instance for screen capture and interaction
        """
        self.window = window
        self.slots: List[InventorySlot] = []
        self._initialize_slots()
        self.api = RuneLiteAPI()
    
    def _initialize_slots(self):
        """Initialize all 28 inventory slot regions."""
        self.slots = []
        
        for i in range(1, TOTAL_SLOTS + 1):
            idx = i
            row = (i - 1) // SLOTS_PER_ROW
            col = (i - 1) % SLOTS_PER_ROW
            
            xp = int(SLOT_WIDTH * 0.2)
            xy = int(SLOT_HEIGHT * 0.2)
            x = INVENTORY_START_X + (col * SLOT_WIDTH) + (col * INVENTORY_X_OFFSET) + xp
            y = INVENTORY_START_Y + (row * SLOT_HEIGHT) + (row * INVENTORY_Y_OFFSET) + xy
            width = SLOT_WIDTH - (2 * xp)
            height = SLOT_HEIGHT - (2 * xy)
            
            region = Region(x, y, width, height)
            slot = InventorySlot(index=idx, region=region)
            self.slots.append(slot)
    
    def populate(self):
        """
        Fills slot data from the RuneLite API.
        """
        slots = self.api.get_inventory()
        if slots:
            for i in range(1, TOTAL_SLOTS + 1):
                item = slots[i - 1]
                qty = item.get('quantity', 1)
                id = item.get('id', -1)
                self.slots[i - 1].index = i
                self.slots[i - 1].is_empty = (id == -1)
                self.slots[i - 1].item_id = id if id != -1 else None
                self.slots[i - 1].quantity = qty if id != -1 else None

    def is_inventory_open(self) -> bool:
        """
        Check if the inventory tab is currently open.
        
        Returns:
            True if inventory tab is selected
        """
        inventory = self.api.get_sidebar_tab("inventory")
        if inventory:
            return inventory.get('isOpen', False)
        return False
    
    def open_inventory(self) -> bool:
        """
        Open the inventory tab if not already open.
        
        Returns:
            True if inventory is now open
        """
        if self.is_inventory_open():
            return True
        
        # Click the inventory tab
        if self.window.window:
            self.window.move_mouse_to(INVENTORY_TAB_REGION.random_point())
            self.window.click()
            
            # Wait briefly and check again
            import time
            time.sleep(random.uniform(0.2, 0.4))
            return self.is_inventory_open()
        
        return False
    
    def is_slot_empty(self, slot_index: int, empty_color: Tuple[int, int, int] = (62, 53, 41)) -> bool:
        """
        Check if a specific inventory slot is empty.
        
        Args:
            slot_index: Slot index (1-28)
            empty_color: RGB color of empty slot background
            
        Returns:
            True if slot appears empty
        """
        if slot_index < 1 or slot_index > TOTAL_SLOTS:
            return False

        if not self.window.window:
            return False

        self.window.capture()
        slot = self.slots[slot_index - 1]
        
        # Extract the slot region
        img = self.window.screenshot
        x, y, w, h = slot.region.x, slot.region.y, slot.region.width, slot.region.height
        slot_img = img[y:y+h, x:x+w]
        
        # Check if dominant color is the empty slot color
        avg_color = slot_img.mean(axis=(0, 1))
        
        # Calculate color difference
        diff = np.abs(avg_color - np.array(empty_color)).sum()
        
        return diff < 30  # Threshold for "close enough" to empty color
    
    def count_empty_slots(self) -> int:
        """
        Count the number of empty inventory slots.
        
        Returns:
            Number of empty slots (0-28)
        """
        x = [slot for slot in self.slots if slot.is_empty]
        return len(x)
    
    def count_filled(self) -> int:
        """
        Count the number of filled inventory slots.
        
        Returns:
            Number of items in inventory (0-28)
        """
        return TOTAL_SLOTS - self.count_empty_slots()
    
    def is_full(self) -> bool:
        """
        Check if inventory is full.
        
        Returns:
            True if all 28 slots are occupied
        """
        return self.count_empty_slots() == 0
    
    def is_empty(self) -> bool:
        """
        Check if inventory is completely empty.
        
        Returns:
            True if all 28 slots are empty
        """
        return self.count_empty_slots() == TOTAL_SLOTS
    
    # Deprecated -- use osrs.inventory functions instead
    def click_slot(self, slot_index: int, right_click: bool = False) -> bool:
        """
        Click on a specific inventory slot.
        
        Args:
            slot_index: Slot index to click (1-28)
            right_click: Whether to right-click instead of left-click
            
        Returns:
            True if click was performed
        """
        if slot_index < 1 or slot_index > TOTAL_SLOTS:
            print("Invalid slot index")
            return False

        slot = self.slots[slot_index - 1]
        self.window.move_mouse_to(slot.random_point())
        
        if right_click:
            self.window.right_click()
        else:
            self.window.click()
        
        return True
    
import random
