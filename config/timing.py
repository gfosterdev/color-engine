"""
Centralized timing configuration for all bot actions.

This module defines timing constants to avoid redundant sleep calls
and provide consistent, tunable delays throughout the codebase.

All values are tuples of (min, max) for use with random.uniform(*CONSTANT).
"""

# ============================================================================
# TIMING PROFILES
# ============================================================================

class TimingProfile:
    """Base timing profile with all timing constants."""
    
    # Mouse Movement Durations (seconds)
    # Distance-based movement uses formula: min(max_duration, max(min_duration, distance/pixels_per_second))
    MOUSE_MOVE_VERY_SHORT = (0.08, 0.12)  # < 100px (inventory slots, nearby UI)
    MOUSE_MOVE_SHORT = (0.10, 0.15)       # 100-300px (same region)
    MOUSE_MOVE_MEDIUM = (0.15, 0.25)      # 300-600px (across UI panels)
    MOUSE_MOVE_LONG = (0.25, 0.40)        # > 600px (across screen)
    
    # Distance-based movement scaling
    PIXELS_PER_SECOND = 800  # Base speed for distance calculation
    MIN_MOVE_DURATION = 0.08
    MAX_MOVE_DURATION = 0.40
    
    # Game Tick Timing (seconds)
    GAME_TICK = (0.6, 0.7)                # Full OSRS game tick (600ms)
    
    # Click Delays (seconds)
    GAME_TICK_DELAY = (0.03, 0.05)        # Post-click delay for server tick
    PRE_CLICK_DELAY = (0.05, 0.15)        # Human hesitation before click (built into MouseMover)
    CLICK_HOLD_DURATION = (0.05, 0.12)    # Mouse button hold time (built into MouseMover)
    
    # Menu & Interface Delays (seconds)
    MENU_OPEN_DELAY = (0.10, 0.20)        # Wait for right-click menu to appear
    MENU_CLOSE_DELAY = (0.05, 0.10)       # Brief delay after menu closes
    INTERFACE_TRANSITION = (0.05, 0.10)   # Generic interface state change
    INTERFACE_CLOSE_DELAY = (0.15, 0.25)  # After pressing ESC to close interface
    
    # Banking Delays (seconds)
    BANK_OPEN_WAIT = (0.30, 0.50)         # Wait for bank interface to fully load
    BANK_SEARCH_TYPE = (0.10, 0.20)       # After typing in search box
    BANK_DEPOSIT_ACTION = (0.20, 0.35)    # After deposit button click
    BANK_WITHDRAW_ACTION = (0.20, 0.35)   # After withdraw click
    
    # Inventory Delays (seconds)
    INVENTORY_TAB_OPEN = (0.05, 0.10)     # After clicking inventory tab
    INVENTORY_SLOT_ACTION = (0.03, 0.05)  # After inventory slot interaction
    
    # Keyboard Input Delays (seconds)
    KEYSTROKE_DELAY = (0.05, 0.15)        # Between individual keystrokes
    KEY_HOLD_DURATION = (0.05, 0.10)      # Key press hold time
    HOTKEY_DELAY = (0.05, 0.10)           # Between hotkey press and release
    TAB_KEY_DELAY = (0.05, 0.10)          # After F-key tab switch
    
    # Combat & Interaction Delays (seconds)
    ATTACK_CLICK_DELAY = (0.05, 0.10)     # After clicking to attack
    OBJECT_INTERACT_DELAY = (0.05, 0.10)  # After interacting with game object
    NPC_INTERACT_DELAY = (0.05, 0.10)     # After interacting with NPC
    
    # Login/Logout Delays (seconds)
    LOGIN_BUTTON_DELAY = (0.30, 0.60)     # Between login screen actions
    LOGIN_VERIFY_DELAY = (1.0, 1.5)       # Between login state checks
    LOGOUT_PANEL_DELAY = (0.20, 0.40)     # After opening logout panel
    
    # API Polling Delays (seconds)
    API_POLL_INTERVAL = (0.10, 0.20)      # Between API state checks
    API_WAIT_TIMEOUT_STEP = (0.50, 1.20)  # Between timeout check iterations
    
    # Anti-pattern Randomization (seconds)
    MICRO_DELAY = (0.01, 0.03)            # Very small random delays
    TINY_DELAY = (0.03, 0.05)             # Tiny delays for realism
    SMALL_DELAY = (0.05, 0.10)            # Small delays between actions
    MEDIUM_DELAY = (0.10, 0.20)           # Medium delays
    LARGE_DELAY = (0.20, 0.40)            # Larger delays for realism

    # Camera Control
    CAMERA_ROTATION_RETRY_DELAY = (0.2, 0.5)  # Delay between rotation retry attempts


# ============================================================================
# CAMERA ROTATION RETRIES
# ============================================================================

# Maximum number of retry attempts for camera rotation before fallback to 360° sweep
CAMERA_ROTATION_MAX_RETRIES = 3


class FastProfile(TimingProfile):
    """Aggressive timing profile for speed (higher detection risk)."""
    
    MOUSE_MOVE_VERY_SHORT = (0.06, 0.08)
    MOUSE_MOVE_SHORT = (0.08, 0.10)
    MOUSE_MOVE_MEDIUM = (0.10, 0.15)
    MOUSE_MOVE_LONG = (0.15, 0.25)
    
    PIXELS_PER_SECOND = 1200
    MIN_MOVE_DURATION = 0.06
    MAX_MOVE_DURATION = 0.25
    
    GAME_TICK_DELAY = (0.02, 0.03)
    MENU_OPEN_DELAY = (0.05, 0.10)
    INTERFACE_TRANSITION = (0.03, 0.05)
    BANK_OPEN_WAIT = (0.20, 0.30)


class CautiousProfile(TimingProfile):
    """Conservative timing profile for safety (more human-like)."""
    
    MOUSE_MOVE_VERY_SHORT = (0.10, 0.15)
    MOUSE_MOVE_SHORT = (0.15, 0.25)
    MOUSE_MOVE_MEDIUM = (0.25, 0.40)
    MOUSE_MOVE_LONG = (0.40, 0.60)
    
    PIXELS_PER_SECOND = 500
    MIN_MOVE_DURATION = 0.10
    MAX_MOVE_DURATION = 0.60
    
    GAME_TICK_DELAY = (0.05, 0.10)
    MENU_OPEN_DELAY = (0.15, 0.30)
    INTERFACE_TRANSITION = (0.10, 0.20)
    BANK_OPEN_WAIT = (0.50, 0.80)


# ============================================================================
# ACTIVE PROFILE
# ============================================================================

# Change this to switch timing profiles globally
TIMING = TimingProfile()

# Uncomment one of these to use a different profile:
# TIMING = FastProfile()
# TIMING = CautiousProfile()
