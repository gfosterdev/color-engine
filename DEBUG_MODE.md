# DEBUG Mode

## Overview

All info-level print statements throughout the codebase are now controlled by a global `DEBUG` flag in `core/config.py`.

## How to Enable DEBUG Mode

### Option 1: Edit the config file directly

Open `core/config.py` and change:

```python
# Global debug flag - set to True to enable info-level print statements
DEBUG = False
```

to:

```python
# Global debug flag - set to True to enable info-level print statements
DEBUG = True
```

### Option 2: Set it programmatically at runtime

At the top of your script (before importing other modules):

```python
from core import config
config.DEBUG = True

# Now import and use other modules
from client.osrs import OSRS
from client.skills.woodcutting import WoodcuttingBot
# ...
```

## What's Controlled by DEBUG Flag

When `DEBUG = True`, you'll see detailed info prints including:

### Bot Operations

- Setup and initialization messages
- State transitions (gathering, banking, walking)
- Resource collection confirmations
- Break notifications
- XP gains
- Anti-ban action summaries

### Game Interactions

- Entity finding operations (finding trees, rocks, NPCs)
- Camera adjustments
- Click confirmations
- Menu interactions
- Login/logout operations
- Tool verification

### Technical Details

- Color region detection details
- Mouse position information
- Camera rotation attempts
- Collision map loading
- Region cache operations

## Files Modified

The following files were refactored to support the DEBUG flag:

1. `core/config.py` - Added the global `DEBUG = False` flag
2. `core/skill_bot_base.py` - Wrapped all info-level prints
3. `client/skills/woodcutting.py` - Wrapped all info-level prints
4. `client/osrs.py` - Wrapped all info-level prints
5. `util/window_util.py` - Wrapped debug prints
6. `util/collision_util.py` - Wrapped initialization prints

## Important Notes

- **Error messages** and **critical warnings** are NOT behind the DEBUG flag - they will always be shown
- The DEBUG flag only controls **informational** print statements
- Changes to the DEBUG flag require restarting your bot script to take effect
- When DEBUG is False, the bot runs silently, only showing critical errors and warnings
- Test scripts (like `test_runelite_api.py`) intentionally keep their print statements visible regardless of DEBUG flag

## Example: Silent vs Verbose Mode

### Silent Mode (DEBUG = False)

```
[Only critical errors and warnings shown]
```

### Verbose Mode (DEBUG = True)

```
==================================================
Setting up Woodcutting bot...
==================================================

✓ Woodcutting bot setup complete

Configured trees: ['Yew tree']
Woodcutting location: (3087, 3468, 0)
Bank location: (3094, 3491, 0)

[find_entity] Checking if object [10822] exists in viewport...
[find_entity] ✓ Object found in viewport
Chopping Yew tree...
✓ Obtained 1 Yew logs (Total: 1)
...
```
