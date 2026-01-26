"""
Global region definitions for OSRS bot.

All fixed-mode RuneLite client regions are defined here for centralized management.
Regions define rectangular areas of interest in the game interface.
"""

from util import Region


# ============================================================================
# General Game Regions
# ============================================================================

GAME_AREA = Region(20, 35, 500, 320)  # Main game viewing area [VERIFIED]
INTERACT_TEXT_REGION = Region(12, 28, 350, 30)  # Hover text at top left [VERIFIED]


# ============================================================================
# Bank Interface Regions
# ============================================================================

BANK_TITLE_REGION = Region(187, 40, 150, 25)  # Bank title area [VERIFIED]
BANK_REARRANGE_MODE_REGION = Region(29, 318, 102, 21)  # Rearrange mode button [VERIFIED]
BANK_SEARCH_REGION = Region(85, 45, 400, 20)  # Bank search box [UNVERIFIED]
BANK_DEPOSIT_INVENTORY_REGION = Region(441, 326, 26, 28)  # Deposit inventory button [VERIFIED]
BANK_DEPOSIT_WORN_ITEMS_REGION = Region(479, 329, 26, 24)  # Deposit worn items button [VERIFIED]
BANK_TOGGLE_ITEM_REGION = Region(138, 342, 41, 14)  # Withdraw as item toggle [VERIFIED]
BANK_TOGGLE_NOTE_REGION = Region(187, 342, 39, 13)  # Withdraw as note toggle [VERIFIED]


# ============================================================================
# Other Interface Regions
# ============================================================================

DEPOSIT_BOX_TITLE_REGION = Region(210, 8, 280, 25)  # Deposit box title [UNVERIFIED]
SHOP_TITLE_REGION = Region(210, 8, 280, 25)  # Shop interface title [UNVERIFIED]


# ============================================================================
# Dialogue Regions
# ============================================================================

DIALOGUE_BOX_REGION = Region(24, 352, 479, 130)  # Main dialogue box area [UNVERIFIED]
DIALOGUE_CONTINUE_REGION = Region(240, 445, 240, 25)  # "Click here to continue" [UNVERIFIED]
DIALOGUE_OPTIONS_REGION = Region(24, 380, 479, 100)  # Multiple choice dialogue [UNVERIFIED]


# ============================================================================
# Notification Regions
# ============================================================================

LEVEL_UP_REGION = Region(10, 10, 500, 100)  # Level up notification area [UNVERIFIED]


# ============================================================================
# Status Orb Regions
# ============================================================================

HEALTH_ORB_REGION = Region(527, 83, 28, 28)  # Health orb [UNVERIFIED]
PRAYER_ORB_REGION = Region(527, 119, 28, 28)  # Prayer orb [UNVERIFIED]
RUN_ORB_REGION = Region(555, 147, 28, 28)  # Run energy orb [UNVERIFIED]


# ============================================================================
# Combat Regions
# ============================================================================

SPECIAL_ATTACK_REGION = Region(590, 160, 100, 25)  # Special attack bar [UNVERIFIED]


# ============================================================================
# Chat Regions
# ============================================================================

CHATBOX_REGION = Region(10, 470, 500, 120)  # Main chatbox area [UNVERIFIED]


# ============================================================================
# Inventory Regions
# ============================================================================

INVENTORY_TAB_REGION = Region(648, 214, 30, 25)  # Inventory tab button [UNVERIFIED]


# ============================================================================
# Login Screen Regions
# ============================================================================

LOGIN_EXISTING_USER_BUTTON = Region(408, 305, 120, 25)  # Existing user button [VERIFIED]
LOGIN_BUTTON_REGION = Region(251, 336, 120, 25)  # Login button [VERIFIED]
LOGIN_CLICK_HERE_TO_PLAY_REGION = Region(287, 329, 210, 70)  # Click here to play area [VERIFIED]


# ============================================================================
# UI Regions
# ============================================================================

UI_LOGOUT_ICON_REGION = Region(642, 498, 22, 27)  # Logout icon in game [VERIFIED]
UI_LOGOUT_BUTTON_REGION = Region(589, 449, 133, 22)  # Logout button in menu [VERIFIED]
UI_WORLD_SWITCHER_BUTTON_REGION = Region(589, 402, 129, 19)  # World switcher button [VERIFIED]


# ============================================================================
# Overlay Regions
# ===========================================================================

COORD_WORLD_REGION = Region(82, 73, 89, 18)  # world coords
COORD_SCENE_REGION = Region(124, 89, 48, 18)  # scene coords
