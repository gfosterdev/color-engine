# OSRS Color Engine Project - Copilot Instructions

## Project Overview

This is a Python-based automation tool for Old School RuneScape (OSRS) using the RuneLite client. The project uses computer vision and color detection to interact with the game interface.

## Technology Stack

- **Python 3.x**
- **Computer Vision**: OpenCV (cv2), NumPy
- **OCR**: PaddleOCR (PaddlePaddle)
- **Screen Capture**: PIL (ImageGrab)
- **Mouse Control**: ctypes (Windows API)
- **Keyboard Input**: keyboard library

## Project Structure

- `main.py` - Entry point with example usage and testing functions
- `test_manual_modular.py` - Interactive testing interface for all features
- `config/regions.py` - Centralized region definitions for all UI elements
- `config/profiles/` - Bot profile configurations with credentials and settings
- `client/osrs.py` - High-level OSRS game interaction logic
- `client/inventory.py` - Inventory management and item detection
- `client/interfaces.py` - Interface state detection (bank, dialogue, etc.)
- `client/interactions.py` - Game object interaction and keyboard input
- `client/color_registry.py` - Centralized color definitions for game objects
- `client/skills/` - Skill-specific automation modules
- `core/` - Core systems (anti-ban, state machine, task engine, config)
- `util/window_util.py` - Window management, screen capture, color detection, OCR
- `util/mouse_util.py` - Human-like mouse movement using Bezier curves

## Core Concepts

### Window Management

- Target window: "RuneLite - xJawj"
- Uses Windows API (user32.dll) for window detection and manipulation
- Captures screenshots for analysis

### Color Detection

- Primary method: RGB color matching with tolerance
- Identifies game elements by their characteristic colors
- Example: Bank booths use RGB(190, 25, 25)

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

### OCR (Optical Character Recognition)

- PaddleOCR for reading in-game text
- Used to validate interactions (e.g., "Bank" hover text)
- Configured to disable OneDNN for compatibility

## Coding Conventions

### Style Guidelines

- Use descriptive variable names (e.g., `INTERACT_TEXT_REGION`, `BANK`)
- Define color constants in `client/color_registry.py` for game objects
- Define region constants in `config/regions.py` for UI elements
- Use type hints for function parameters and returns
- Import regions from centralized config instead of defining inline

### Architecture Patterns

- **OSRS class**: Main interface for game-specific actions
    - Manages Window instance
    - Implements high-level actions (open_bank, login, find_bank)
    - Validates interactions with OCR
    - Can accept profile config for credentials
- **InventoryManager class**: Handles inventory detection and interaction
- **InterfaceDetector class**: Detects game interface states (bank, dialogue, etc.)
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

### Finding and Clicking Game Objects

```python
def interact_with_object(self):
    if self.window.window:
        self.window.capture()
        found = self.window.find_color_region(COLOR_VALUE, debug=True)
        if found:
            self.window.move_mouse_to(found.random_point())
            if self.validate_interact_text("ExpectedText"):
                self.window.click()
                return True
    return False
```

### Defining New Game Elements

1. Find the characteristic RGB color value
2. Add to `client/color_registry.py`: `registry.register("element_name", (r, g, b), "type")`
3. Add region to `config/regions.py` if text recognition is needed
4. Create method in appropriate class (OSRS, InventoryManager, etc.)
5. Use OCR validation when possible
6. Import regions from `config.regions`

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
2. Define color constants for new game elements
3. Create region definitions if text recognition is needed
4. Implement methods in appropriate class (OSRS, InventoryManager, InterfaceDetector, etc.)
5. **Use existing helper class methods** instead of reimplementing functionality
6. Add debug flags for testing
7. Use try-except blocks for robustness
8. **Randomize all timing and movement parameters**:
    - Use `random.uniform(min, max)` for delays instead of fixed values
    - Generate random points within regions for each interaction
    - Vary movement speeds with random multipliers
    - Add random pre/post-action delays
9. **Always create a test in `test_manual_modular.py`**:
    - Add a new test method for the feature
    - Integrate it into the appropriate test menu category
    - If no suitable category exists, create a new one
    - Test methods should be interactive and provide clear feedback
10. Test with the actual game client running

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
