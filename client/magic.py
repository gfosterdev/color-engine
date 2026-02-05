"""
Magic handler for OSRS spellcasting and spellbook management.

This module provides a MagicHandler class for managing all magic-related operations
including opening the magic tab, casting spells, checking spell requirements, and
detecting active spell states.

Usage:
    from client.magic import MagicHandler
    from config.spells import StandardSpells
    
    # Initialize handler (typically done in OSRS class)
    magic = MagicHandler(osrs_instance)
    
    # Open magic tab
    magic.open_magic_tab()
    
    # Cast a spell
    success = magic.cast_spell(StandardSpells.HIGH_LEVEL_ALCHEMY)
    
    # Check if player can cast a spell
    if magic.can_cast_spell(StandardSpells.VARROCK_TELEPORT):
        magic.cast_spell(StandardSpells.VARROCK_TELEPORT)
    
    # Check if spell is active (awaiting target)
    if magic.is_spell_active("High Level Alchemy"):
        print("Spell selected, waiting for target")
"""

import time
import random
from typing import Optional
from config.spells import Spell, StandardSpells
from config.regions import (
    MAGIC_TAB_REGION,
    MAGIC_HIGH_ALCHEMY,
    MAGIC_VARROCK_TELEPORT,
    MAGIC_LUMBRIDGE_TELEPORT,
    MAGIC_FALADOR_TELEPORT,
    MAGIC_CAMELOT_TELEPORT,
    MAGIC_ARDOUGNE_TELEPORT,
    MAGIC_LOW_ALCHEMY,
    MAGIC_TELEKINETIC_GRAB,
    MAGIC_SUPERHEAT_ITEM
)
from config.timing import TIMING
from client.interactions import KeyboardInput


class MagicHandler:
    """Manages all magic-related operations."""
    
    def __init__(self, osrs_instance):
        """
        Initialize MagicHandler with reference to OSRS instance.
        
        Args:
            osrs_instance: Reference to OSRS class instance for API and helper access
        """
        self.osrs = osrs_instance
        self.window = osrs_instance.window
        self.api = osrs_instance.api
        self.interfaces = osrs_instance.interfaces
        self.inventory = osrs_instance.inventory
        self.keyboard = osrs_instance.keyboard
        
        # Map spells to their screen regions for direct clicking
        self._spell_regions = {
            StandardSpells.HIGH_LEVEL_ALCHEMY: MAGIC_HIGH_ALCHEMY,
            StandardSpells.LOW_LEVEL_ALCHEMY: MAGIC_LOW_ALCHEMY,
            StandardSpells.VARROCK_TELEPORT: MAGIC_VARROCK_TELEPORT,
            StandardSpells.LUMBRIDGE_TELEPORT: MAGIC_LUMBRIDGE_TELEPORT,
            StandardSpells.FALADOR_TELEPORT: MAGIC_FALADOR_TELEPORT,
            StandardSpells.CAMELOT_TELEPORT: MAGIC_CAMELOT_TELEPORT,
            StandardSpells.ARDOUGNE_TELEPORT: MAGIC_ARDOUGNE_TELEPORT,
            StandardSpells.TELEKINETIC_GRAB: MAGIC_TELEKINETIC_GRAB,
            StandardSpells.SUPERHEAT_ITEM: MAGIC_SUPERHEAT_ITEM,
        }
    
    def open_magic_tab(self) -> bool:
        """
        Open the magic spellbook tab.
        
        Uses F6 hotkey to open the magic tab efficiently.
        
        Returns:
            True if magic tab is open after execution
        """
        # Check if already open
        if self.is_magic_tab_open():
            return True
        
        print("Opening magic tab...")
        
        # Press F6 to open magic tab
        KeyboardInput.open_tab('f6')
        time.sleep(random.uniform(*TIMING.TAB_KEY_DELAY))
        
        # Verify it opened
        success = self.is_magic_tab_open()
        if success:
            print("Magic tab opened successfully")
        else:
            print("Failed to open magic tab")
        
        return success
    
    def is_magic_tab_open(self) -> bool:
        """
        Check if the magic tab is currently open.
        
        Uses RuneLite API to detect sidebar state.
        
        Returns:
            True if magic tab is open
        """
        magic_tab = self.api.get_sidebar_tab("magic")
        if magic_tab:
            return magic_tab.get('isOpen', False)
        return False
    
    def cast_spell(self, spell: Spell) -> bool:
        """
        Cast a spell by clicking on it in the spellbook.
        
        This method clicks the spell region directly without hover text validation
        for speed. It automatically opens the magic tab if needed.
        
        Args:
            spell: The Spell object to cast
            
        Returns:
            True if spell was clicked successfully
        """
        # Open magic tab if not already open
        if not self.open_magic_tab():
            print(f"Failed to open magic tab to cast {spell.name}")
            return False
        
        # Get the region for this spell
        region = self._spell_regions.get(spell)
        if not region:
            print(f"No region defined for spell: {spell.name}")
            return False
        
        print(f"Casting spell: {spell.name}")
        
        # Click a random point within the spell region
        self.window.move_mouse_to(region.random_point())
        time.sleep(random.uniform(0.05, 0.15))
        self.window.click()
        
        # Small delay after casting
        time.sleep(random.uniform(0.1, 0.3))
        
        return True
    
    def can_cast_spell(self, spell: Spell) -> bool:
        """
        Check if the player can cast a spell.
        
        Verifies both the required magic level and that the player has
        all required runes in sufficient quantities.
        
        Args:
            spell: The Spell object to check
            
        Returns:
            True if player has the level and runes to cast the spell
        """
        # Check magic level
        magic_level = self.api.get_magic_level()
        if magic_level is None:
            print("Unable to get magic level from API")
            return False
        
        if magic_level < spell.level_required:
            print(f"Magic level {magic_level} too low for {spell.name} (requires {spell.level_required})")
            return False
        
        # Check runes
        if not self.has_runes(spell):
            print(f"Missing required runes for {spell.name}")
            return False
        
        return True
    
    def has_runes(self, spell: Spell) -> bool:
        """
        Check if the player has all required runes for a spell.
        
        This is a wrapper around inventory methods that checks each rune
        requirement for the spell.
        
        Args:
            spell: The Spell object to check runes for
            
        Returns:
            True if player has all required runes in sufficient quantities
        """
        # Populate inventory data from API
        self.inventory.populate()
        
        # Check each rune requirement
        for rune_id, required_amount in spell.runes_required.items():
            current_amount = self.inventory.count_item(rune_id)
            if current_amount < required_amount:
                return False
        
        return True
    
    def is_spell_active(self, spell_name: str) -> bool:
        """
        Check if a spell is currently selected and awaiting a target.
        
        This is used for spells like High Alchemy, Telekinetic Grab, etc.
        that require clicking a target after selecting the spell.
        
        Uses the RuneLite API's selected widget endpoint to detect if
        a spell has been selected.

        Args:
            spell_name: The name of the spell to check (e.g., "High Level Alchemy")
        
        Returns:
            True if a spell is selected and awaiting target
        """
        selected_widget = self.api.get_selected_widget()
        if not selected_widget:
            return False
        
        if not spell_name:
            raise ValueError("Spell name is required to check active spell state")

        # Check spell name matches
        target_spell = selected_widget.get('selectedWidgetName', '')
        if spell_name.lower() in target_spell.lower():
            return True
        
        return False
    
    def wait_for_spell_cast(self, timeout: float = 3.0) -> bool:
        """
        Wait for a spell cast animation to complete.
        
        This monitors the player's animation state to detect when
        a spell has been cast.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if spell cast was detected
        """
        start_time = time.time()
        casting_detected = False
        
        while time.time() - start_time < timeout:
            player = self.api.get_player()
            if player:
                is_animating = player.get('isAnimating', False)
                animation_id = player.get('animationId', -1)
                
                # Detect casting animation (animation IDs vary by spell)
                # Common magic casting animations: 1162, 1167, 1168, etc.
                if is_animating and animation_id > 0:
                    casting_detected = True
                    # Wait for animation to finish
                    time.sleep(0.5)
                    
                # If we detected casting and animation stopped, we're done
                if casting_detected and not is_animating:
                    return True
            
            time.sleep(0.1)
        
        return casting_detected

    def cast_spell_on_item(self, spell: Spell, item_id: int) -> bool:
        """
        Cast a spell on a specific item in the inventory.
        
        This is used for spells like Alchemy and Superheat Item that require
        clicking an inventory item after selecting the spell.
        
        Args:
            spell: The Spell object to cast
            item_id: The ID of the inventory item to cast the spell on
        """
        # First, cast the spell to select it
        if not self.cast_spell(spell):
            print(f"Failed to cast {spell.name} to target item")
            return False
        
        # Wait for spell to be active
        if not self.is_spell_active(spell.name):
            print(f"Spell {spell.name} was not detected as active after casting")
            return False
        
        # Click the target item in inventory
        self.inventory.click_item(item_id, "Cast")
        
        return True