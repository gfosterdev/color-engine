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


# Fixed mode inventory constants (positions for 28 slots in fixed client mode)
INVENTORY_START_X = 579
INVENTORY_START_Y = 253
SLOT_WIDTH = 42
SLOT_HEIGHT = 36
SLOTS_PER_ROW = 4
TOTAL_SLOTS = 28

# Inventory tab color constant
INVENTORY_TAB_COLOR = (127, 84, 60)  # Brown color when selected


@dataclass
class InventorySlot:
    """Represents a single inventory slot."""
    index: int  # 0-27
    region: Region
    is_empty: bool = True
    item_color: Optional[Tuple[int, int, int]] = None
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
    
    def _initialize_slots(self):
        """Initialize all 28 inventory slot regions."""
        self.slots = []
        
        for i in range(TOTAL_SLOTS):
            row = i // SLOTS_PER_ROW
            col = i % SLOTS_PER_ROW
            
            x = INVENTORY_START_X + (col * SLOT_WIDTH)
            y = INVENTORY_START_Y + (row * SLOT_HEIGHT)
            
            region = Region(x, y, SLOT_WIDTH, SLOT_HEIGHT)
            slot = InventorySlot(index=i, region=region)
            self.slots.append(slot)
    
    def is_inventory_open(self) -> bool:
        """
        Check if the inventory tab is currently open.
        
        Returns:
            True if inventory tab is selected
        """
        if not self.window.window:
            return False
        
        self.window.capture()
        found = self.window.find_color_region(
            INVENTORY_TAB_COLOR,
            region=INVENTORY_TAB_REGION,
            tolerance=20
        )
        
        return found is not None
    
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
            slot_index: Slot index (0-27)
            empty_color: RGB color of empty slot background
            
        Returns:
            True if slot appears empty
        """
        if slot_index < 0 or slot_index >= TOTAL_SLOTS:
            return False
        
        if not self.window.window:
            return False
        
        self.window.capture()
        slot = self.slots[slot_index]
        
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
        count = 0
        for i in range(TOTAL_SLOTS):
            if self.is_slot_empty(i):
                count += 1
        return count
    
    def count_items(self) -> int:
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
    
    def find_item_by_color(self, item_color: Tuple[int, int, int], tolerance: int = 30) -> List[int]:
        """
        Find all slots containing an item with the specified color.
        
        Args:
            item_color: RGB color to search for
            tolerance: Color matching tolerance
            
        Returns:
            List of slot indices containing the color
        """
        if not self.window.window:
            return []
        
        self.window.capture()
        matching_slots = []
        
        for slot in self.slots:
            # Skip if slot is empty
            if self.is_slot_empty(slot.index):
                continue
            
            # Check if color exists in this slot
            found = self.window.find_color_region(
                item_color,
                region=slot.region,
                tolerance=tolerance
            )
            
            if found:
                matching_slots.append(slot.index)
        
        return matching_slots
    
    def click_slot(self, slot_index: int, right_click: bool = False) -> bool:
        """
        Click on a specific inventory slot.
        
        Args:
            slot_index: Slot index to click (0-27)
            right_click: Whether to right-click instead of left-click
            
        Returns:
            True if click was performed
        """
        if slot_index < 0 or slot_index >= TOTAL_SLOTS:
            return False
        
        if not self.window.window:
            return False
        
        slot = self.slots[slot_index]
        self.window.move_mouse_to(slot.random_point())
        
        if right_click:
            self.window.right_click()
        else:
            self.window.click()
        
        return True
    
    def click_first_item_with_color(self, item_color: Tuple[int, int, int], 
                                     right_click: bool = False) -> bool:
        """
        Find and click the first item matching the given color.
        
        Args:
            item_color: RGB color to search for
            right_click: Whether to right-click
            
        Returns:
            True if item was found and clicked
        """
        slots = self.find_item_by_color(item_color)
        
        if not slots:
            return False
        
        return self.click_slot(slots[0], right_click=right_click)
    
    def get_slot_region(self, slot_index: int) -> Optional[Region]:
        """
        Get the region for a specific slot.
        
        Args:
            slot_index: Slot index (0-27)
            
        Returns:
            Region object or None if invalid index
        """
        if 0 <= slot_index < TOTAL_SLOTS:
            return self.slots[slot_index].region
        return None


import random
