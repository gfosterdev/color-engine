"""
Global region definitions for OSRS bot.

All fixed-mode RuneLite client regions are defined here for centralized management.
Regions define rectangular areas of interest in the game interface.
"""

from util import Region


# ============================================================================
# General Game Regions
# ============================================================================

GAME_AREA = Region(5, 5, 500, 320)  # Main game viewing area [VERIFIED]
INTERACT_TEXT_REGION = Region(12, 28, 350, 30)  # Hover text at top left [VERIFIED]


# ============================================================================
# Bank Interface Regions
# ============================================================================

BANK_TITLE_REGION = Region(187, 40, 150, 25)  # Bank title area [VERIFIED]
BANK_REARRANGE_MODE_REGION = Region(29, 318, 102, 21)  # Rearrange mode button [VERIFIED]
BANK_SEARCH_REGION = Region(85, 45, 400, 20)  # Bank search box [UNVERIFIED]
BANK_DEPOSIT_INVENTORY_REGION = Region(430, 299, 26, 27)  # Deposit inventory button [VERIFIED]
BANK_DEPOSIT_EQUIPMENT_REGION = Region(466, 300, 26, 26)  # Deposit worn items button [VERIFIED]
BANK_TOGGLE_ITEM_REGION = Region(138, 342, 41, 14)  # Withdraw as item toggle [VERIFIED]
BANK_TOGGLE_NOTE_REGION = Region(187, 342, 39, 13)  # Withdraw as note toggle [VERIFIED]

BANK_ITEMS_DISPLAY_REGION = Region(22, 83, 460, 210)  # Area where bank items are displayed [VERIFIED]

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

INVENTORY_TAB_REGION = Region(632, 173, 20, 27)  # Inventory tab button [UNVERIFIED]


# ============================================================================
# Login Screen Regions
# ============================================================================

LOGIN_EXISTING_USER_BUTTON = Region(400, 279, 123, 25)  # Existing user button [VERIFIED]
LOGIN_BUTTON_REGION = Region(237, 306, 130, 29)  # Login button [VERIFIED]
LOGIN_CLICK_HERE_TO_PLAY_REGION = Region(283, 301, 203, 72)  # Click here to play area [VERIFIED]


# ============================================================================
# UI Regions
# ============================================================================

UI_LOGOUT_ICON_REGION = Region(626, 466, 33, 36)  # Logout icon in game [VERIFIED]
UI_SKILLS_TAB_REGION = Region(565, 172, 22, 22)  # Skills tab region [UNVERIFIED]

UI_PRAYER_ORB_REGION = Region(547, 83, 17, 17)  # Prayer orb region
UI_RUN_ORB_REGION = Region(555, 115, 22, 18)  # Run orb region

UI_LOGOUT_BUTTON_REGION = Region(570, 414, 144, 36)  # Logout button
UI_LOGOUT_WORLD_SWITCHER_REGION = Region(570, 366, 144, 36)  # World switcher button

# ============================================================================
# Overlay Regions
# ============================================================================

COORD_WORLD_REGION = Region(99, 384, 75, 20)  # World coordinates (x, y) [VERIFIED]
COORD_SCENE_REGION = Region(125, 402, 50, 18)  # Scene coordinates (x, y) [VERIFIED]
CAMERA_YAW_REGION = Region(154, 443, 50, 20)  # Camera yaw angle (0-2048) [VERIFIED]
CAMERA_PITCH_REGION = Region(154, 425, 50, 20)  # Camera pitch [VERIFIED]
CAMERA_SCALE_REGION = Region(154, 459, 50, 20)  # Camera scale [VERIFIED]


# ============================================================================
# Minimap Regions
# ============================================================================

MINIMAP_REGION = Region(570, 14, 138, 138)  # Full minimap clickable area [VERIFIED]
MINIMAP_CENTER = Region(642, 84, 2, 2)  # Player position reference point [VERIFIED]
MINIMAP_COMPASS_REGION = Region(550, 10, 20, 21)  # Minimap compass [UNVERIFIED]
