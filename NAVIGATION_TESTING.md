# Navigation Testing Guide

## Overview

The `test_navigation.py` file provides a comprehensive, interactive testing tool for the bot's navigation system. It allows you to test pathfinding, coordinate reading, minimap interaction, and full navigation cycles for any bot profile.

## Features

### Core Navigation Tests

- **Coordinate Reading**: Monitor real-time world and scene coordinates from RuneLite API
- **Camera Yaw Reading**: Track camera rotation (0-2048 units)
- **Pathfinding**: Calculate paths between locations with variance
- **Minimap Clicking**: Test clicking at different angles with yaw rotation
- **Walk to Location**: Execute full pathfinding walks to specific locations
- **Full Navigation Cycle**: Test complete bot cycles (bank → combat area → bank)
- **Stuck Detection**: Monitor position changes and detect when player is stuck

### Bot-Specific Testing

- Automatically detects bot type from profile name
- Loads bank and combat/training area locations
- Tests navigation paths specific to each bot's requirements

## Usage

### Basic Usage

```bash
python test_navigation.py
```

This will prompt you to select a bot profile, then present an interactive menu.

### Profile-Specific Testing

```bash
python test_navigation.py gargoyle_killer_canifis
```

Pass a profile name as an argument to skip the selection menu.

## Test Menu Options

### 1. Test Coordinate Reading

Continuously displays world and scene coordinates from the RuneLite API.

**Use Case**: Verify coordinate tracking is working correctly.

**Controls**:

- ESC to stop

### 2. Test Camera Yaw Reading

Displays camera yaw and pitch values in real-time.

**Use Case**: Verify camera rotation tracking for minimap clicking.

**Controls**:

- ESC to stop

### 3. Test Pathfinding

Calculates a path between your current position and a destination without walking.

**Options**:

- Bank location (from profile)
- Combat/training area (from profile)
- Custom coordinates

**Output**:

- Number of waypoints
- Path distance
- Variance percentage
- First/last waypoints
- Optional visualization

**Use Case**: Test pathfinding algorithm without moving the character.

### 4. Test Minimap Clicking

Randomly clicks points on the minimap to test yaw-adjusted clicking.

**Use Case**: Verify minimap clicking accuracy at different camera angles.

**Warning**: Make sure you're in a safe area! Character will move around randomly.

**Controls**:

- ESC to stop

### 5. Test Walk to Location

Walks to a specific location using pathfinding and minimap navigation.

**Options**:

- Bank location
- Combat/training area
- Custom coordinates

**Use Case**: Test full navigation to a single destination.

**Controls**:

- ESC during walk to cancel

### 6. Test Full Navigation Cycle

Tests the complete bot navigation cycle in three phases:

1. Current location → Bank
2. Bank → Combat/Training area
3. Combat area → Bank

**Duration**: 5-15 minutes depending on distance

**Use Case**: Verify bot can complete full operational cycle.

**Warning**: This test takes significant time. Make sure you're ready before starting.

**Controls**:

- ESC during any phase to cancel

### 7. Test Stuck Detection

Monitors position changes and counts stuck detections.

**Use Case**: Test stuck detection by walking into walls or obstacles.

**Output**:

- Position changes
- Stuck detection count
- Warnings when stuck

**Controls**:

- ESC to stop

## Supported Bot Profiles

The tester automatically detects bot type and loads appropriate locations:

### Combat Bots

- **gargoyle_killer_canifis**: Slayer Tower → Canifis Bank
- **cow_killer_lumbridge**: Lumbridge Cows → Lumbridge Bank

### Skill Bots

- **yew_cutter_edgeville**: Edgeville Yews → Edgeville Bank
- **iron_miner_varrock**: Varrock West Mine → Varrock West Bank

## Configuration

### Bot Profile Requirements

For navigation testing to work properly, your bot profile should include:

```json
{
	"combat_settings": {
		"bank_location": "canifis",
		"combat_area": "slayer_tower_gargoyles"
	},
	"navigation": {
		"path_variance": 0.25
	}
}
```

Or for skill bots:

```json
{
	"skill_settings": {
		"bank_location": "varrock_west",
		"mining_location": "varrock_west_mine"
	},
	"navigation": {
		"path_variance": 0.25
	}
}
```

### Variance Settings

Path variance controls how much randomness is added to paths:

- `0.0` = No variance (straight Dijkstra path)
- `0.25` = 25% edge weight variance (recommended)
- `0.35` = 35% variance (high randomness)

## Troubleshooting

### "Cannot read current coordinates"

- Make sure RuneLite client is running
- Verify RuneLite HTTP plugin is enabled
- Check that window title matches "RuneLite - xJawj"

### "No path found"

- Destination may be unreachable
- Collision data might be missing for that region
- Try using `scripts/download_collision_data.py` to update collision maps

### "Failed to reach destination"

- Check for obstacles blocking the path
- Verify stuck detection isn't triggering false positives
- Try increasing path variance in profile

### Path takes unusual route

- This is expected behavior with variance enabled
- Paths are randomized to avoid bot detection
- Different paths will be generated each time

## Integration with test_manual_modular.py

Navigation tests are also available in `test_manual_modular.py`:

- Menu option 8: "Pathfinding Tests"
- Provides similar functionality in the main test suite

## Best Practices

1. **Start Simple**: Begin with coordinate reading and pathfinding tests before attempting walks
2. **Safe Testing**: Always test in safe areas (no aggressive NPCs)
3. **Profile Setup**: Ensure your bot profile has correct bank and area locations
4. **Collision Data**: Download collision maps for your testing region first
5. **Variance Testing**: Try different variance values to find optimal randomness
6. **Full Cycle Last**: Only run full navigation cycle after individual tests pass

## Example Testing Session

```
1. Select profile: gargoyle_killer_canifis
2. Test coordinate reading (verify coordinates display)
3. Test camera reading (verify yaw tracking)
4. Test pathfinding (calculate path from current location to bank)
5. Test walk to bank (execute the walk)
6. Test walk to combat area (walk from bank to Slayer Tower)
7. Test full cycle (complete bank → tower → bank cycle)
```

## Development Notes

### Adding New Bot Support

To add navigation testing for a new bot:

1. Create bot profile in `config/profiles/`
2. Add location coordinates to `config/locations.py`
3. Update `_detect_bot_type()` in test_navigation.py
4. Add location mappings in `_get_bank_location()` and `_get_combat_area()`

### Extending Tests

To add new navigation tests:

1. Add test method to `NavigationTester` class
2. Follow naming convention: `test_<feature_name>()`
3. Add menu option in `show_menu()`
4. Add handler in `run()` method
5. Document the test in this guide

## Related Files

- `client/navigation.py` - Navigation system implementation
- `client/pathfinder.py` - Pathfinding algorithm
- `config/locations.py` - Location coordinate definitions
- `util/collision_util.py` - Collision detection
- `test_manual_modular.py` - Main test suite (includes navigation tests)

## API Reference

### NavigationManager

- `get_current_coordinates()` - Get player position
- `walk_to_coord(x, y, z)` - Walk to specific coordinates
- `click_minimap_coord(x, y, z)` - Click minimap at coordinates
- `get_pathfinding_stats()` - Get pathfinding statistics

### Pathfinder

- `find_path(start_x, start_y, start_z, end_x, end_y, end_z, variance)` - Calculate path

## Performance Notes

- Coordinate reading: ~2 API calls/second
- Pathfinding: 1-5 seconds for typical paths
- Full navigation cycle: 5-15 minutes
- Stuck detection: Checks every 1 second

## Safety Warnings

⚠️ **Do not run navigation tests in dangerous areas**

- Player will move automatically
- Cannot control where player walks during tests
- May encounter aggressive NPCs
- Use safe areas like banks, training areas with low-level NPCs

⚠️ **Full navigation cycle takes significant time**

- Plan 10-20 minutes for complete cycle
- Player will be moving unattended
- Monitor the test to ensure safety

## Conclusion

The navigation testing tool provides comprehensive testing for all navigation features. Use it to verify pathfinding, validate bot navigation cycles, and debug movement issues before running production bots.
