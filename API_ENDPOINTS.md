# RuneLite HTTP Server API - Complete Endpoint Reference

## Base URL

`http://localhost:8080`

## Endpoints Overview

### 🎮 Player Data (5 endpoints)

#### GET /player

**Player state and vitals**

```json
{
	"name": "PlayerName",
	"combatLevel": 126,
	"health": 99,
	"maxHealth": 99,
	"prayer": 99,
	"maxPrayer": 99,
	"runEnergy": 100,
	"specialAttack": 100,
	"weight": 0,
	"isAnimating": false,
	"animationId": -1,
	"interactingWith": "Rock" // if interacting
}
```

#### GET /stats

**All 23 skills with XP tracking**

```json
[
	{
		"stat": "Attack",
		"level": 99,
		"boostedLevel": 99,
		"xp": 13034431,
		"xpToNextLevel": 0,
		"nextLevelAt": 13034431
	}
]
```

#### GET /coords

**World and local coordinates**

```json
{
	"world": {
		"x": 3222,
		"y": 3218,
		"plane": 0,
		"regionID": 12850,
		"regionX": 38,
		"regionY": 50
	},
	"local": {
		"x": 4864,
		"y": 6400,
		"sceneX": 38,
		"sceneY": 50
	}
}
```

#### GET /combat

**Combat state and target info**

```json
{
	"inCombat": true,
	"autoRetaliate": true,
	"combatLevel": 126,
	"target": {
		"name": "Guard",
		"id": 1234,
		"combatLevel": 21,
		"health": 5,
		"maxHealth": 10
	}
}
```

#### GET /animation

**Current animation state**

```json
{
	"animationId": 628,
	"poseAnimation": 808,
	"isAnimating": true,
	"isMoving": false
}
```

### 🎒 Inventory & Equipment (3 endpoints)

#### GET /inv

**Inventory items (28 slots)**

```json
[
	{
		"id": 1265,
		"quantity": 1
	}
]
```

#### GET /equip

**Equipped items**

```json
[
	{
		"id": 1163,
		"quantity": 1,
		"slot": 3 // 0=Head, 3=Weapon, 4=Body, etc.
	}
]
```

#### GET /bank

**Bank items (only when bank is open)**

```json
[
	{
		"slot": 0,
		"id": 995,
		"quantity": 1000000
	}
]
```

### 🌍 World Data (4 endpoints)

#### GET /npcs

**All NPCs in scene**

```json
[
	{
		"name": "Rock",
		"id": 11364,
		"combatLevel": 0,
		"index": 123,
		"position": {
			"x": 3222,
			"y": 3218,
			"plane": 0
		},
		"distanceFromPlayer": 5,
		"healthRatio": -1,
		"healthScale": -1,
		"animation": -1,
		"isInteracting": false
	}
]
```

#### GET /players

**Other players in scene**

```json
[
	{
		"name": "OtherPlayer",
		"combatLevel": 100,
		"position": {
			"x": 3222,
			"y": 3219,
			"plane": 0
		},
		"animation": -1,
		"team": 0,
		"isFriend": false
	}
]
```

#### GET /objects

**Game objects in scene**

```json
[
	{
		"id": 11364,
		"position": {
			"x": 3222,
			"y": 3218,
			"plane": 0
		}
	}
]
```

#### GET /grounditems

**Items on the ground**

```json
[
	{
		"id": 440,
		"quantity": 1,
		"position": {
			"x": 3222,
			"y": 3218,
			"plane": 0
		}
	}
]
```

### 🎯 Game State (4 endpoints)

#### GET /camera

**Camera position and rotation**

```json
{
	"yaw": 1024,
	"pitch": 512,
	"x": 6753,
	"y": 6753,
	"z": 1500
}
```

#### GET /game

**Game state info**

```json
{
	"state": "LOGGED_IN",
	"isLoggedIn": true,
	"world": 302,
	"gameCycle": 12345,
	"tickCount": 67890,
	"fps": 50
}
```

#### GET /widgets

**Interface states**

```json
{
	"isBankOpen": false,
	"isShopOpen": false,
	"isDialogueOpen": false,
	"isInventoryVisible": true
}
```

#### GET /menu

**Right-click menu entries**

```json
[
	{
		"option": "Walk here",
		"target": "",
		"type": "WALK"
	},
	{
		"option": "Mine",
		"target": "<col=ffff>Rock",
		"type": "GAME_OBJECT_FIRST_OPTION"
	}
]
```

## Usage Examples

### Python

```python
import requests

# Get player health
response = requests.get('http://localhost:8080/player')
player = response.json()
print(f"Health: {player['health']}/{player['maxHealth']}")

# Check if mining
animation = requests.get('http://localhost:8080/animation').json()
is_mining = animation['isAnimating']

# Find nearby rocks
npcs = requests.get('http://localhost:8080/npcs').json()
rocks = [npc for npc in npcs if 'Rock' in npc['name']]
print(f"Found {len(rocks)} rocks nearby")
```

### JavaScript

```javascript
// Get coordinates
fetch("http://localhost:8080/coords")
	.then((res) => res.json())
	.then((data) => {
		console.log(`Position: (${data.world.x}, ${data.world.y})`);
	});

// Monitor inventory
setInterval(async () => {
	const inv = await fetch("http://localhost:8080/inv").then((r) => r.json());
	const itemCount = inv.filter((i) => i.id !== -1).length;
	console.log(`Inventory: ${itemCount}/28`);
}, 1000);
```

## Bot Development Tips

### Mining Bot

```python
# 1. Check if animating (mining)
animation = api.get('/animation')
if not animation['isAnimating']:
    # Find nearest rock
    npcs = api.get('/npcs')
    rocks = [n for n in npcs if 'Rock' in n['name']]
    closest = min(rocks, key=lambda r: r['distanceFromPlayer'])
    # Click rock using CV

# 2. Check inventory
inv = api.get('/inv')
if len([i for i in inv if i['id'] != -1]) >= 28:
    # Bank full inventory
```

### Combat Bot

```python
# Monitor health and prayer
player = api.get('/player')
if player['health'] < player['maxHealth'] * 0.5:
    # Eat food

if player['prayer'] < 20:
    # Drink prayer potion

# Check combat state
combat = api.get('/combat')
if combat['inCombat']:
    target = combat['target']
    print(f"Fighting {target['name']}")
```

### Pathfinding Integration

```python
# Get current position
coords = api.get('/coords')
current = (coords['world']['x'], coords['world']['y'])

# Navigate to destination
path = calculate_path(current, destination)
for tile in path:
    # Click tile using CV
    # Wait for arrival
    while True:
        coords = api.get('/coords')
        pos = (coords['world']['x'], coords['world']['y'])
        if pos == tile:
            break
```

## Performance Notes

- Average response time: 5-15ms per endpoint
- Fastest: `/animation`, `/player`, `/coords` (~5ms)
- Slowest: `/objects`, `/npcs` (~20-30ms due to scene iteration)
- Recommended polling rate: 1-2 times per second for most endpoints
- For real-time monitoring: Use `/animation` and `/player` at higher rates

## Error Handling

All endpoints return:

- **200 OK** with JSON data
- **204 No Content** when data is unavailable (e.g., not logged in, bank not open)

Always check for null/empty responses before processing data.
