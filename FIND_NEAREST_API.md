# Find Nearest API Endpoint - Implementation Summary

## Overview

Added a new API endpoint `/find_nearest` that searches for the closest game object or NPC by ID and returns its world coordinates.

## Files Modified

### 1. `external/HttpServerPlugin.java`

**Changes:**

- Added route registration: `server.createContext("/find_nearest", this::handleFindNearest);`
- Implemented `handleFindNearest()` method that:
    - Accepts query parameter: `?id=<entity_id>`
    - Searches NPCs first (prioritized for performance)
    - Falls back to game objects if no NPC match found
    - Returns world coordinates (x, y, plane) and distance from player

**Response Format:**

```json
{
	"searchId": 10583,
	"found": true,
	"type": "object",
	"worldX": 3185,
	"worldY": 3436,
	"plane": 0,
	"distance": 15
}
```

For NPCs, includes additional `name` field:

```json
{
	"searchId": 1,
	"found": true,
	"type": "npc",
	"name": "Man",
	"worldX": 3200,
	"worldY": 3400,
	"plane": 0,
	"distance": 8
}
```

### 2. `client/runelite_api.py`

**Changes:**

- Added method: `get_nearest_by_id(entity_id: int) -> Optional[Dict[str, Any]]`
- Full documentation with parameter and return type descriptions
- Follows existing API wrapper patterns

**Usage Example:**

```python
from client.runelite_api import RuneLiteAPI

api = RuneLiteAPI()
result = api.get_nearest_by_id(10583)  # Bank booth

if result and result.get('found'):
    print(f"Found {result['type']} at ({result['worldX']}, {result['worldY']})")
    print(f"Distance: {result['distance']} tiles")
```

### 3. `test_manual_modular.py`

**Changes:**

- Added `test_find_nearest_by_id()` method for interactive testing
- Updated gameobject test menu to include new test (key 'N')
- Test prompts for entity ID and displays full result details

**Test Location:**

- Main Menu → Option 6 (Game Objects) → Press 'N'

### 4. `test_find_nearest.py` (New File)

**Purpose:**

- Quick automated test script for the new endpoint
- Tests bank objects, NPCs, and invalid IDs
- Can be run standalone: `python test_find_nearest.py`

## How It Works

1. **Client sends request:** `GET http://localhost:8080/find_nearest?id=10583`
2. **Server searches:**
    - First checks all NPCs in the scene for matching ID
    - If no NPC found, searches all game objects on current plane
    - Calculates distance from player to each match
    - Returns closest match with world coordinates
3. **Client receives response** with world position and metadata

## Use Cases

- **Pathfinding:** Get target coordinates for navigation
- **Object interaction:** Determine if target is reachable
- **Smart clicking:** Choose optimal targets based on distance
- **Bot logic:** Make decisions based on entity proximity

## Testing

1. **Manual testing via test menu:**

    ```bash
    python test_manual_modular.py
    # Press 6 → Press N → Enter entity ID
    ```

2. **Quick automated test:**

    ```bash
    python test_find_nearest.py
    ```

3. **In your code:**

    ```python
    api = RuneLiteAPI()

    # Find nearest bank
    bank = api.get_nearest_by_id(10583)
    if bank and bank['found']:
        walk_to(bank['worldX'], bank['worldY'])
    ```

## Performance Notes

- Searches NPCs first (typically faster, fewer entities)
- Only searches current plane for game objects
- Returns immediately when first match type is found
- Runs in game thread via `invokeAndWait()` for thread safety

## Error Handling

- Returns 400 if ID parameter missing or invalid
- Returns `{"found": false}` if entity not in area
- Returns `None` in Python wrapper if request fails
- All errors logged to console

## Future Enhancements (Potential)

- Add optional `type` parameter to search only NPCs or only objects
- Add `max_distance` parameter to limit search radius
- Return multiple matches within range
- Include convex hull data for immediate clicking
- Cache recent searches for performance
