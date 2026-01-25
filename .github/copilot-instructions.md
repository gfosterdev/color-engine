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
- `client/osrs.py` - OSRS-specific game interaction logic
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
- Regions specify where to look for text or colors (x, y, width, height)
- Example: `INTERACT_TEXT_REGION = Region(12, 28, 350, 20)` for hover text

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
- Define color constants as RGB tuples at the top of files
- Use type hints for function parameters and returns
- Keep region definitions in constants for reusability

### Architecture Patterns

- **OSRS class**: Main interface for game-specific actions
    - Manages Window instance
    - Implements high-level actions (open_bank, find_bank)
    - Validates interactions with OCR
- **Window class**: Low-level screen capture and interaction utilities
- **MouseMover class**: Handles realistic mouse movement
- **Region class**: Defines areas of interest on screen

### Error Handling

- Always validate window existence before operations
- Check if colors/regions are found before clicking
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
2. Define as constant: `ELEMENT_NAME = (r, g, b)`
3. Create method in OSRS class to interact with it
4. Use OCR validation when possible

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

1. Define color constants for new game elements
2. Create region definitions if text recognition is needed
3. Implement methods in OSRS class with validation
4. Add debug flags for testing
5. Use try-except blocks for robustness
6. **Randomize all timing and movement parameters**:
    - Use `random.uniform(min, max)` for delays instead of fixed values
    - Generate random points within regions for each interaction
    - Vary movement speeds with random multipliers
    - Add random pre/post-action delays
7. Test with the actual game client running

## Dependencies to Install

```bash
pip install opencv-python numpy pillow paddlepaddle paddleocr keyboard pywin32
```

## Development Workflow

- Test color detection with `debug=True` flags
- Use `extract_region()` and `extract_text()` functions in main.py for calibration
- Validate hover text before clicking to ensure correct target
- Always capture fresh screenshots before color detection
