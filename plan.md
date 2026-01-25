# Plan: Build Complete OSRS Bot Automation Engine

Transform the current proof-of-concept into a fully functional bot engine capable of autonomous OSRS gameplay through systematic implementation of game state management, decision-making systems, and skill-specific automation modules.

## Core Assumptions

- **Fixed Client Mode** - RuneLite client must always run in 'fixed' mode to maintain consistent UI element positions for reliable region detection and interaction
- **RuneLite Color Markers** - Game objects, NPCs, and tiles will be color-marked using RuneLite's Entity Hider/Object Markers plugin with unique RGB values per object type for reliable color-based detection
- **Color Registry** - Maintain a color database mapping RGB values to game objects (e.g., `IRON_ORE = (255, 100, 50)`, `OAK_TREE = (100, 200, 75)`) in config files or [client/color_registry.py](client/color_registry.py)

## Steps

1. **Implement Core Game State Detection** - Create [client/game_state.py](client/game_state.py), [client/inventory.py](client/inventory.py), and [client/interfaces.py](client/interfaces.py) to detect inventory slots, item counts, interface states (bank open, combat status), and health/prayer/energy orbs using color detection and OCR patterns

2. **Build Task Automation Framework** - Design `Task` and `TaskQueue` classes in [core/task_engine.py](core/task_engine.py) and implement `StateMachine` in [core/state_machine.py](core/state_machine.py) to manage complex multi-step workflows with error recovery, validation, and state transitions

3. **Expand Game Interactions** - Add right-click menu detection/selection, keyboard input handling, and generic `GameObject` system in [client/interactions.py](client/interactions.py) to support diverse game objects (trees, rocks, NPCs) beyond current bank-only functionality

4. **Complete Banking System** - Extend [client/osrs.py](client/osrs.py) to handle deposit/withdraw operations, bank search, and item management using OCR for bank interface text and grid-based slot detection

5. **Develop First Skill Bot** - Implement [client/skills/mining.py](client/skills/mining.py) as a reference implementation that combines inventory management, object interaction, banking loops, and state machine to mine ore autonomously

6. **Add Anti-Ban Randomization Layer** - Create [core/anti_ban.py](core/anti_ban.py) with random idle periods, camera movements, tab switching, simulated misclicks, fatigue patterns, and break scheduling using randomized timing from `random.uniform()`

## Implementation Decisions

1. **Configuration System** - Use JSON config files for bot profiles stored in [config/](config/) directory. Structure: `config/profiles/{bot_name}.json` with settings for window title, mouse speed ranges, break schedules, and skill-specific parameters. Create [core/config.py](core/config.py) to load and validate JSON configs

2. **Navigation Approach** - Implement waypoint-based navigation system in [client/navigation.py](client/navigation.py) using predefined coordinate lists for common routes. Minimap clicking with randomized points within radius. Defer A\* pathfinding for future iteration

3. **Code Refactoring** - Split [util/window_util.py](util/window_util.py) into focused modules: [util/capture.py](util/capture.py) (screen capture), [util/color_detection.py](util/color_detection.py) (color matching), [util/ocr.py](util/ocr.py) (text recognition), and keep mouse control in [util/mouse_util.py](util/mouse_util.py). Refactor as needed during implementation to maintain clean architecture
