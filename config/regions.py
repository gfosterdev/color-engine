"""
Global region definitions for OSRS bot.

All fixed-mode RuneLite client regions are defined here for centralized management.
Regions define rectangular areas of interest in the game interface.
"""

from util import Region


# ============================================================================
# General Game Regions
# ============================================================================

GAME_AREA = Region(20, 35, 500, 320)  # Main game viewing area
INTERACT_TEXT_REGION = Region(12, 28, 350, 30)  # Hover text at top left


# ============================================================================
# Bank Interface Regions
# ============================================================================

BANK_TITLE_REGION = Region(187, 40, 150, 25)  # Bank title area
BANK_REARRANGE_MODE_REGION = Region(29, 318, 102, 21)  # Rearrange mode button
BANK_CLOSE_BUTTON_REGION = Region(494, 11, 16, 16)  # Red X close button
BANK_SEARCH_REGION = Region(85, 45, 400, 20)  # Bank search box
BANK_DEPOSIT_INVENTORY_BUTTON = Region(437, 288, 36, 32)  # Deposit inventory button
BANK_DEPOSIT_EQUIPMENT_BUTTON = Region(477, 288, 36, 32)  # Deposit equipment button


# ============================================================================
# Other Interface Regions
# ============================================================================

DEPOSIT_BOX_TITLE_REGION = Region(210, 8, 280, 25)  # Deposit box title
SHOP_TITLE_REGION = Region(210, 8, 280, 25)  # Shop interface title


# ============================================================================
# Dialogue Regions
# ============================================================================

DIALOGUE_BOX_REGION = Region(24, 352, 479, 130)  # Main dialogue box area
DIALOGUE_CONTINUE_REGION = Region(240, 445, 240, 25)  # "Click here to continue"
DIALOGUE_OPTIONS_REGION = Region(24, 380, 479, 100)  # Multiple choice dialogue


# ============================================================================
# Notification Regions
# ============================================================================

LEVEL_UP_REGION = Region(10, 10, 500, 100)  # Level up notification area


# ============================================================================
# Status Orb Regions
# ============================================================================

HEALTH_ORB_REGION = Region(527, 83, 28, 28)  # Health orb
PRAYER_ORB_REGION = Region(527, 119, 28, 28)  # Prayer orb
RUN_ORB_REGION = Region(555, 147, 28, 28)  # Run energy orb


# ============================================================================
# Combat Regions
# ============================================================================

SPECIAL_ATTACK_REGION = Region(590, 160, 100, 25)  # Special attack bar


# ============================================================================
# Chat Regions
# ============================================================================

CHATBOX_REGION = Region(10, 470, 500, 120)  # Main chatbox area


# ============================================================================
# Inventory Regions
# ============================================================================

INVENTORY_TAB_REGION = Region(648, 214, 30, 25)  # Inventory tab button


# ============================================================================
# Login Screen Regions
# ============================================================================

LOGIN_EXISTING_USER_BUTTON = Region(408, 305, 120, 25)  # Existing user button
LOGIN_BUTTON_REGION = Region(251, 336, 120, 25)  # Login button
LOGIN_CLICK_HERE_TO_PLAY_REGION = Region(287, 329, 210, 70)  # Click here to play area


# ============================================================================
# Miscellaneous Regions
# ============================================================================

LOGOUT_BUTTON_REGION = Region(652, 10, 100, 25)  # Logout button area