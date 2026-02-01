# OSRS Color Engine Project - Copilot Instructions

## Project Overview

This is a Python-based automation tool for Old School RuneScape (OSRS) using the RuneLite client. The project **primarily uses the RuneLite HTTP API** for game data and interaction, with color detection and OCR as fallback methods for UI elements not exposed via API.

## Technology Stack

- **Python 3.x**
- **RuneLite HTTP API**: Primary method for game data (player stats, inventory, NPCs, objects, etc.)
- **Computer Vision**: OpenCV (cv2), NumPy (fallback for UI elements)
- **OCR**: PaddleOCR (PaddlePaddle) (fallback for text recognition)
- **Screen Capture**: PIL (ImageGrab)
- **Mouse Control**: ctypes (Windows API)
- **Keyboard Input**: keyboard library

## Project Structure

- `main.py` - Entry point with example usage and testing functions
- `test_manual_modular.py` - Interactive testing interface for all features
- `config/regions.py` - Centralized region definitions for all UI elements
- `config/game_objects.py` - **Game object IDs (banks, ores, trees, etc.)**
- `config/npcs.py` - **NPC IDs (bankers, monsters, bosses, etc.)**
- `config/items.py` - **Item IDs (ores, food, potions, tools, etc.)**
- `config/profiles/` - Bot profile configurations with credentials and settings
- `client/osrs.py` - High-level OSRS game interaction logic
- `client/runelite_api.py` - **RuneLite HTTP API wrapper**
- `client/inventory.py` - Inventory management using API data
- `client/interfaces.py` - Interface state detection using API
- `client/interactions.py` - Game object interaction and keyboard input
- `client/color_registry.py` - Color definitions (for user-configured markers only)
- `client/skills/` - Skill-specific automation modules
- `core/` - Core systems (anti-ban, state machine, task engine, config)
- `external/HttpServerPlugin.java` - **RuneLite plugin that exposes HTTP API**
- `util/window_util.py` - Window management, screen capture, mouse control
- `util/mouse_util.py` - Human-like mouse movement using Bezier curves

## Core Concepts

### RuneLite HTTP API

- **Primary data source**: Always check API first before using vision/OCR
- **Available endpoints**: `/player`, `/combat`, `/inventory`, `/coords`, `/camera`, `/menu`, `/objects_in_viewport`, `/npcs_in_viewport`, `/interfaces`
- **Game Object IDs**: Use centralized IDs from `config/game_objects.py` (BankObjects, OreRocks, Trees, etc.)
- **NPC IDs**: Use centralized IDs from `config/npcs.py` (Bankers, Guards, Monsters, Bosses, etc.)
- **Item IDs**: Use centralized IDs from `config/items.py` (Ores, Food, Potions, Tools, etc.)
- **Convex hull data**: API provides polygon coordinates for accurate clicking
- **Extending the API**: If needed data isn't exposed, add new endpoints to `external/HttpServerPlugin.java`

### Window Management

- Target window: "RuneLite - xJawj"
- Uses Windows API (user32.dll) for window detection and manipulation
- Captures screenshots for analysis

### Color Detection (Fallback)

- **Use only when API doesn't provide data** (e.g., user-configured tile markers)
- Identifies game elements by their characteristic colors
- Example: Custom ground markers use RGB values

### Region System

- `Region` class defines rectangular areas with optional masks
- **All regions centralized in `config/regions.py`** for easy management
- Regions specify where to look for text or colors (x, y, width, height)
- Regions can also define clickable areas for static UI elements (buttons, tabs, etc.)
- Import regions from `config.regions` instead of defining inline
- Example: `from config.regions import INTERACT_TEXT_REGION, BANK_TITLE_REGION`
- Categorized by purpose: Game Area, Bank Interface, Dialogue, Status Orbs, etc.

### Mouse Movement

- Implements human-like movement using cubic Bezier curves
- **CRITICAL**: Never use constant values - always randomize:
    - Movement speed (vary duration/steps)
    - Bezier control points (randomize curve shape)
    - Movement direction/path
    - Delays between actions
    - Target click points within regions
- Uses Windows user32 API for precise control

### OCR (Optical Character Recognition - Fallback)

- **Use only when API doesn't provide data** (e.g., custom chat parsing)
- PaddleOCR for reading in-game text
- Configured to disable OneDNN for compatibility

## Coding Conventions

### Style Guidelines

- **API-first approach**: Always check RuneLite API for data before using vision/OCR
- **Use centralized IDs**: Import from `config.game_objects`, `config.npcs`, `config.items`
- **Extend API when needed**: Add new endpoints to `external/HttpServerPlugin.java` if data isn't exposed
- Use descriptive variable names (e.g., `INTERACT_TEXT_REGION`, `BankObjects.VARROCK_WEST`)
- Define color constants in `client/color_registry.py` only for user markers
- Define region constants in `config/regions.py` for UI elements
- Use type hints for function parameters and returns
- Import regions from centralized config instead of defining inline

### Architecture Patterns

- **OSRS class**: Main interface for game-specific actions
    - Manages Window instance
    - Uses RuneLiteAPI for game data via `self.api`
    - Implements high-level actions (open_bank, login, find_bank)
    - Uses OCR for validation only when API doesn't provide data
    - Can accept profile config for credentials
- **RuneLiteAPI class**: Wrapper for all HTTP API calls
- **InventoryManager class**: Handles inventory using API data
- **InterfaceDetector class**: Detects game interface states using API
- **Window class**: Low-level screen capture and interaction utilities
- **MouseMover class**: Handles realistic mouse movement
- **Region class**: Defines areas of interest on screen (centralized in config)

### Code Reuse and Architecture Guidelines

**CRITICAL**: Always check for existing functionality before implementing new features:

1. **Search before implementing**: Use grep or semantic search to check if similar functionality exists
2. **Respect the class hierarchy**:
    - Use `self.interfaces.*` methods for interface detection/interaction (e.g., `close_interface()`, `is_bank_open()`)
    - Use `self.inventory.*` methods for inventory operations
    - Use `self.keyboard.*` methods for keyboard input
    - Use `self.window.*` methods for low-level window operations
3. **Don't duplicate functionality**: If a method exists in a helper class, use it instead of reimplementing
4. **Follow established patterns**: Look at existing methods to understand how similar features are implemented
5. **Layer appropriately**: High-level methods in OSRS class should orchestrate calls to lower-level helper classes

**Examples of proper architecture usage**:

- ✅ Use `self.interfaces.close_interface()` instead of `keyboard.press_and_release('esc')`
- ✅ Use `self.interfaces.is_bank_open()` instead of custom OCR checks for bank
- ✅ Use `self.inventory.click_slot()` instead of calculating slot positions manually
- ✅ Use `self.keyboard.type_text()` instead of importing keyboard library directly in OSRS class

### Error Handling

- Always validate window existence before operations
- Check if colors/regions are found before clicking (unless static UI element)
- Use debug flags to visualize color detection and OCR results
- Return boolean success indicators for validation methods

## Common Patterns

### Finding and Clicking Game Objects (API-First)

```python
from config.game_objects import BankObjects

def find_and_click_bank(self):
    """Find nearest bank using RuneLite API."""
    # Get all objects in viewport
    objects = self.api.get_objects_in_viewport()

    # Filter for bank objects using centralized IDs
    bank_ids = BankObjects.all_interactive()
    banks = [obj for obj in objects if obj['id'] in bank_ids]

    if banks:
        # Get closest bank by distance
        closest = min(banks, key=lambda x: x['distance'])
        polygon = self.window.convex_hull_to_polygon(closest['convexHull'])
        self.window.move_mouse_to(polygon.random_point())
        self.window.click()
        return True
    return False
```

### Defining New Game Elements

1. **Check API first**: Verify if data is available via existing endpoints
2. **If API has data**: Add IDs to appropriate config file:
    - `config/game_objects.py` for game objects (banks, ores, trees)
    - `config/npcs.py` for NPCs (monsters, merchants, bankers)
    - `config/items.py` for items (food, tools, weapons)
3. **If API missing data**: Extend `external/HttpServerPlugin.java` with new endpoint
4. **Fallback only**: Use color detection if API extension is not feasible:
    - Add to `client/color_registry.py`: `registry.register("element_name", (r, g, b), "type")`
    - Add region to `config/regions.py` if text recognition needed
5. Create method in appropriate class (OSRS, InventoryManager, etc.)
6. Import IDs/regions from centralized config files

## Important Notes

- **Windows Only**: Uses Windows-specific APIs (user32.dll, ctypes)
- **RuneLite Client**: Designed specifically for RuneLite interface
- **PaddlePaddle Config**: `PADDLE_DISABLE_ONEDNN=1` must be set before imports
- **Keyboard Controls**:
    - Space bar triggers actions in debug/testing modes
    - ESC exits debug loops
- **Human-like Behavior**:
    - Always use random points within regions (never click same pixel)
    - Randomize all timing delays (sleep durations)
    - Vary mouse movement speeds and trajectories
    - Never use constant values for any timing or movement parameters
    - Add random micro-adjustments to avoid predictable patterns

## When Implementing New Features

1. **Check for existing functionality first**: Search the codebase to see if similar features already exist
2. **Check RuneLite API first**: Verify if required data is available via API endpoints
3. **If API missing data**: Consider adding new endpoint to `external/HttpServerPlugin.java`
4. **Use centralized IDs**: Import from `config/game_objects.py`, `config/npcs.py`, or `config/items.py`
5. Define region definitions if UI interaction needed (add to `config/regions.py`)
6. Implement methods in appropriate class (OSRS, InventoryManager, InterfaceDetector, etc.)
7. **Use existing helper class methods** instead of reimplementing functionality
8. Add debug flags for testing
9. Use try-except blocks for robustness
10. **Randomize all timing and movement parameters**:
    - Use `random.uniform(min, max)` for delays instead of fixed values
    - Generate random points within regions for each interaction
    - Vary movement speeds with random multipliers
    - Add random pre/post-action delays
11. **Always create a test in `test_manual_modular.py`**:
    - Add a new test method for the feature
    - Integrate it into the appropriate test menu category
    - If no suitable category exists, create a new one
    - Test methods should be interactive and provide clear feedback
12. Test with the actual game client running

## Dependencies to Install

```bash
pip install opencv-python numpy pillow paddlepaddle paddleocr keyboard pywin32
```

## Development Workflow

- Test color detection with `debug=True` flags
- Use `test_manual_modular.py` for interactive testing of all features
- Use region visualization test to verify region positions
- Use OCR region test to validate text extraction
- Validate hover text before clicking to ensure correct target
- Always capture fresh screenshots before color detection
