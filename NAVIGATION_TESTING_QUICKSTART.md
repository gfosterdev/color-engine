# Navigation Test File - Quick Reference

## File Created

`test_navigation.py` - Standalone navigation testing tool for OSRS bot

## Purpose

Interactive testing interface for bot navigation systems, allowing you to test pathfinding, coordinate reading, minimap clicking, and full navigation cycles for any bot profile.

## Quick Start

```bash
# Interactive mode (select profile from menu)
python test_navigation.py

# Direct mode (specify profile)
python test_navigation.py gargoyle_killer_canifis
```

## What Can Be Tested

### 1. Coordinate Reading (Real-time)

- World coordinates (x, y, z)
- Scene coordinates
- API connectivity

### 2. Camera Tracking (Real-time)

- Yaw angle (0-2048)
- Pitch angle
- Rotation tracking

### 3. Pathfinding (Calculation Only)

- Path generation with variance
- Waypoint visualization
- Distance calculation
- Destinations: Bank, Combat Area, or Custom

### 4. Minimap Clicking (Movement)

- Yaw-adjusted clicking
- Random movement patterns
- Click accuracy testing

### 5. Walk to Location (Full Walk)

- Complete pathfinding walk
- Minimap navigation
- Arrival validation
- Destinations: Bank, Combat Area, or Custom

### 6. Full Navigation Cycle (Complete Bot Cycle)

Three-phase test:

1. Current → Bank
2. Bank → Combat/Training Area
3. Combat Area → Bank

Duration: 5-15 minutes

### 7. Stuck Detection (Monitoring)

- Position change monitoring
- Stuck counter
- Re-pathing triggers

## Supported Bots

Automatically configured for:

- `gargoyle_killer_canifis` (Slayer Tower ↔ Canifis Bank)
- `cow_killer_lumbridge` (Lumbridge Cows ↔ Lumbridge Bank)
- `yew_cutter_edgeville` (Edgeville Yews ↔ Edgeville Bank)
- `iron_miner_varrock` (Varrock Mine ↔ Varrock West Bank)

## Test Order (Recommended)

1. Coordinate Reading → Verify API connectivity
2. Camera Reading → Verify camera tracking
3. Pathfinding → Calculate path (no movement)
4. Walk to Location → Test single walk
5. Full Cycle → Test complete bot cycle

## Safety Notes

⚠️ Always test in safe areas (no aggressive NPCs)  
⚠️ Character will move automatically during tests  
⚠️ Full cycle takes 10-20 minutes of unattended movement  
⚠️ Press ESC to stop most tests

## Documentation

Full guide: `NAVIGATION_TESTING.md`

## Integration

Also available in `test_manual_modular.py` → Menu 8: "Pathfinding Tests"
