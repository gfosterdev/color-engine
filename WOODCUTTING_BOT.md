# Woodcutting Bot - Yew Trees at Edgeville

## Overview

Autonomous woodcutting bot that cuts yew trees at Edgeville and banks at Edgeville bank. Built using the same architecture as the MiningBot, with support for XP tracking, respawn detection, and anti-ban behaviors.

## Features

- **API-First Design**: Uses RuneLite HTTP API for tree detection and game state
- **Smart Tree Selection**: Automatically finds and clicks nearest available tree
- **Respawn Detection**: Efficiently detects when trees are depleted and respawned
- **XP Tracking**: Monitors woodcutting XP gains and level progress
- **Banking System**: Automatically walks to bank and deposits logs when full
- **Birds Nest Collection**: Detects and banks valuable birds nests
- **Anti-Ban**: Random camera movements, AFK moments, and behavioral variation
- **Powerdrop Mode**: Optional drop logs on ground for powerchop training

## Configuration

Profile: `config/profiles/yew_cutter_edgeville.json`

```json
{
	"profile_name": "yew_cutter_edgeville",
	"skill_settings": {
		"tree_type": "yew",
		"trees": ["yew"],
		"location": "edgeville_yews",
		"bank_location": "edgeville",
		"banking": true,
		"powerdrop": false,
		"use_skill_tracker": true,
		"use_respawn_detector": true,
		"use_animation_detection": true
	}
}
```

### Key Settings

- **tree_type**: Primary tree type to cut (`"yew"`, `"oak"`, `"willow"`, `"maple"`, etc.)
- **trees**: Array of tree types (supports cutting multiple types)
- **location**: Woodcutting location name from `config/locations.py`
- **bank_location**: Bank location name
- **banking**: Enable/disable banking (set false for powerdrop)
- **powerdrop**: Drop logs on ground instead of banking
- **use_skill_tracker**: Track XP gains
- **use_respawn_detector**: Use smart respawn detection
- **use_animation_detection**: Use animation for depletion detection

## Location Setup

The bot uses the Edgeville yew tree location at coordinates `(3087, 3481, 0)` - south of Edgeville bank.

### Adding New Woodcutting Locations

Edit `config/locations.py`:

```python
class WoodcuttingLocations(LocationCategory):
    """World coordinates of woodcutting locations."""

    # Edgeville area
    EDGEVILLE_YEWS = (3087, 3481, 0)  # Yew trees south of bank

    # Add your custom location
    MY_CUSTOM_LOCATION = (x, y, z)  # Your coordinates
```

## Tree Types

Supported tree types from `config/skill_mappings.py`:

| Tree Type | Animation ID | Respawn Time (sec) | Level Required |
| --------- | ------------ | ------------------ | -------------- |
| normal    | 879          | 5-10               | 1              |
| oak       | 879          | 8-15               | 15             |
| willow    | 879          | 8-15               | 30             |
| maple     | 879          | 35-55              | 45             |
| yew       | 879          | 60-90              | 60             |
| magic     | 879          | 120-240            | 75             |

## How to Run

### Method 1: Direct Script

```bash
python run_yew_woodcutter.py
```

### Method 2: Import in Code

```python
from client.skills.woodcutting import WoodcuttingBot

bot = WoodcuttingBot("yew_cutter_edgeville")
bot.start()
```

### Method 3: Test Individual Features

```bash
python test_manual_modular.py
# Press W for Woodcutting Tests
# Then B for Bot Initialization
```

## Bot Workflow

1. **Initialization**
    - Load profile configuration
    - Verify axe in equipment/inventory
    - Initialize skill tracker and respawn detector
    - Resolve woodcutting and bank locations

2. **Main Loop** (GATHERING state)
    - Find nearest tree using API
    - Click tree with "Chop down" action
    - Wait for tree depletion using respawn detector
    - Perform anti-ban actions randomly
    - Check for birds nests

3. **Banking** (when inventory full)
    - Walk to Edgeville bank
    - Open bank
    - Deposit all logs and birds nests
    - Close bank
    - Return to GATHERING state

4. **Powerdrop Mode** (alternative to banking)
    - When inventory full, drop all logs
    - Continue cutting trees
    - Still bank birds nests

## Statistics Tracking

The bot tracks:

- **Logs Cut**: Total number of trees cut
- **Banking Trips**: Number of times banked
- **Birds Nests**: Number of nests collected
- **XP Gained**: Total XP gained in session
- **XP Per Hour**: Current XP rate
- **Session Time**: Total runtime

## Architecture

### Class Hierarchy

```
SkillBotBase (abstract)
    └── WoodcuttingBot (concrete)
```

### Key Methods

#### Abstract Method Implementations

```python
def _gather_resource(self):
    """Cut one tree using API and respawn detector."""

def _get_skill_name(self) -> str:
    """Return 'Woodcutting'."""

def _get_tool_ids(self) -> list[int]:
    """Return all axe item IDs."""

def _get_resource_info(self) -> Dict:
    """Return tree object IDs, log item ID, animation ID."""
```

#### Custom Methods

```python
def _handle_banking(self):
    """Bank logs and nests at Edgeville."""

def _should_bank(self) -> bool:
    """Check if inventory full or has valuable nests."""

def _handle_powerdrop(self):
    """Drop logs when inventory full (powerdrop mode)."""
```

## Refinements Over MiningBot

### 1. Birds Nest Handling

- Detects multiple nest types (normal, seed, ring nests)
- Banks nests immediately when found
- Tracks nest collection statistics

### 2. Powerdrop Mode

- Alternative to banking for training
- Drops all logs on ground
- Still banks valuable nests
- Configurable via profile setting

### 3. Longer Respawn Times

- Yew trees take 60-90 seconds to respawn
- Respawn detector uses longer max_wait (60s vs 10s)
- More intelligent tree rotation

### 4. Tree-Specific Naming

- Uses "tree" terminology instead of "rock"
- Better logging messages ("Chopping" vs "Mining")
- Woodcutting-specific variable names

### 5. Multiple Tree Type Support

- Can cut multiple tree types in one location
- Automatically selects nearest available tree
- Useful for mixed tree areas

## Testing

Run comprehensive tests:

```bash
python test_manual_modular.py
# Press W for Woodcutting Tests
```

Available tests:

- **A**: Axe Verification - Check for equipped axe
- **X**: XP Tracking - View current woodcutting stats
- **N**: Animation Detection - Monitor cutting animation
- **T**: Find Trees - List all trees in viewport
- **D**: Tree Distance Sorting - Sort by nearest
- **L**: Location Resolution - Verify locations exist
- **B**: Bot Initialization - Full bot setup test
- **R**: Respawn Detection - Monitor tree respawn timing

## Requirements

- RuneLite client running
- Fixed mode (not resizable)
- Axe equipped or in inventory
- Edgeville yew trees unlocked (60+ Woodcutting)
- Empty inventory slots for logs
- RuneLite HTTP plugin enabled

## Safety Features

- Respects configured break intervals
- Random delays between actions
- Human-like mouse movement
- Camera angle variation
- AFK simulation
- Randomized action timing

## Troubleshooting

### Bot doesn't find trees

- Verify you're at the correct location `(3087, 3481, 0)`
- Check camera angle can see trees
- Ensure trees aren't all depleted

### Banking fails

- Verify bank location is correct in profile
- Check pathfinding can reach bank
- Ensure no obstacles blocking path

### Axe not detected

- Check axe is equipped or in inventory
- Verify axe type is supported (bronze through dragon)
- Check inventory space available

### Respawn detection not working

- Enable `use_respawn_detector` in profile
- Enable `use_animation_detection` in profile
- Check RuneLite API is responding

## Future Enhancements

Potential improvements:

- Multiple location support (auto-hop between trees)
- World hopping for faster cutting
- Fletch logs while cutting (powerdrop alternative)
- Special tree support (redwood, mahogany)
- Woodcutting Guild support
- Custom log price tracking

## Credits

Based on the MiningBot architecture with woodcutting-specific refinements and improvements.
