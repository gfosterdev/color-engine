# Combat Handler - Phase 2 Design

This document outlines the Phase 2 features for the Combat Handler class. Phase 1 (completed) includes core combat state tracking, NPC engagement with filtering, and basic consumable usage (requiring explicit item IDs). Phase 2 extends the combat handler with advanced safety checks, auto-consumable selection, prayer management, and special attack handling.

## Phase 1 Recap (Completed)

✅ **Core Combat State Methods:**

- `get_health()`, `get_max_health()`, `get_health_percent()`
- `get_prayer()`, `get_max_prayer()`, `get_prayer_percent()`
- `get_special_attack()`
- `is_player_in_combat()`
- `get_current_target()`, `get_target_health_percent()`, `is_target_alive()`
- `is_npc_in_combat(npc_id)` - Checks if NPC is engaged with another entity (not player)

✅ **Combat Actions:**

- `engage_npc(npc_id, attack_option)` - Engages NPC, filtering out those in combat with others
- `eat_food(item_id)` - Eats specific food item by ID
- `drink_potion(item_id)` - Drinks specific potion by ID

✅ **Threshold Helpers:**

- `should_eat(threshold_percent)` - Returns True if health below threshold
- `should_drink_prayer(threshold_percent)` - Returns True if prayer below threshold

✅ **Wait Methods:**

- `wait_until_not_in_combat(timeout)` - Waits for combat to end
- `wait_until_target_dead(timeout)` - Waits for target to die (uses isDying flag)

✅ **API Extensions:**

- Enhanced `/combat` endpoint with auto-retaliate, poison/venom status
- Enhanced `/npcs_in_viewport` with Actor data: interactingWith, isDying, animation, graphicId, overheadText, overheadIcon

---

## Phase 2 Features

### 1. Safety Checks

#### `is_safe_to_engage(health_threshold, prayer_threshold, required_food_count)`

**Purpose:** Comprehensive safety check before engaging in combat.

**Parameters:**

- `health_threshold` (int, default: 70) - Minimum health % required
- `prayer_threshold` (int, default: 30) - Minimum prayer % required (if using prayer)
- `required_food_count` (int, default: 5) - Minimum food items required in inventory

**Returns:** `bool` - True if safe to engage, False otherwise

**Logic:**

```python
def is_safe_to_engage(self, health_threshold: int = 70,
                      prayer_threshold: int = 30,
                      required_food_count: int = 5) -> bool:
    # Check health
    health_percent = self.get_health_percent()
    if health_percent is None or health_percent < health_threshold:
        return False

    # Check prayer (if using prayer)
    if prayer_threshold > 0:
        prayer_percent = self.get_prayer_percent()
        if prayer_percent is None or prayer_percent < prayer_threshold:
            return False

    # Check food count
    food_count = self._count_food_in_inventory()
    if food_count < required_food_count:
        return False

    # Check for poison/venom
    poison_status = self.api.get_poison_status()
    if poison_status and (poison_status.get('isPoisoned') or poison_status.get('isVenomed')):
        # Consider unsafe if poisoned without antidote
        if not self._has_antipoison_in_inventory():
            return False

    return True
```

**Usage:**

```python
if osrs.combat.is_safe_to_engage(health_threshold=80, required_food_count=10):
    osrs.combat.engage_npc(chicken_id)
else:
    print("Not safe to engage - banking or restocking needed")
```

---

#### `emergency_teleport()`

**Purpose:** Execute emergency teleport when in danger (low health, out of food, etc.)

**Parameters:** None (uses inventory to find teleport items)

**Returns:** `bool` - True if teleport successful, False otherwise

**Logic:**

```python
def emergency_teleport(self) -> bool:
    # Priority order for teleport items
    teleport_items = [
        # Jewelry (instant)
        (2552, "Ring of dueling"),      # Ring of dueling (8)
        (3853, "Games necklace"),       # Games necklace (8)
        (1712, "Glory amulet"),         # Amulet of glory (6)

        # Tablets (instant)
        (8007, "House tablet"),         # Teleport to house
        (8013, "Varrock tablet"),       # Varrock teleport
        (8008, "Lumbridge tablet"),     # Lumbridge teleport
        (8009, "Falador tablet"),       # Falador teleport
        (8010, "Camelot tablet"),       # Camelot teleport
        (8011, "Ardougne tablet"),      # Ardougne teleport
    ]

    # Try each teleport item
    for item_id, name in teleport_items:
        if self.inventory.has_item(item_id):
            print(f"Emergency teleport using {name}...")
            success = self.inventory.click_item(item_id)
            if success:
                time.sleep(random.uniform(3.0, 4.0))  # Wait for teleport
                return True

    # No teleport found
    print("ERROR: No teleport items found!")
    return False
```

**Usage:**

```python
# In combat loop
if osrs.combat.get_health_percent() < 20 and not osrs.combat._has_food():
    print("EMERGENCY: Low health, no food!")
    osrs.combat.emergency_teleport()
```

---

### 2. Auto-Consumable Selection

#### `get_best_available_food()`

**Purpose:** Automatically select best food from inventory based on healing value.

**Parameters:** None

**Returns:** `Optional[int]` - Item ID of best food, or None if no food

**Logic:**

```python
def get_best_available_food(self) -> Optional[int]:
    from config.items import Food

    # Get inventory items
    inventory_items = self.api.get_inventory()
    if not inventory_items:
        return None

    # Get all food IDs in inventory
    inventory_ids = [item['id'] for item in inventory_items if item]

    # Food healing values (sorted high to low)
    food_priority = [
        # High tier (19-22 hp)
        (Food.ANGLERFISH.item_ids, 22),
        (Food.MANTA_RAY.item_ids, 22),
        (Food.DARK_CRAB.item_ids, 22),
        (Food.SHARK.item_ids, 20),

        # Mid tier (14-18 hp)
        (Food.SEA_TURTLE.item_ids, 21),
        (Food.TUNA_POTATO.item_ids, 22),
        (Food.MONKFISH.item_ids, 16),
        (Food.SWORDFISH.item_ids, 14),
        (Food.LOBSTER.item_ids, 12),

        # Low tier (6-12 hp)
        (Food.SALMON.item_ids, 9),
        (Food.TROUT.item_ids, 7),
        (Food.COOKED_MEAT.item_ids, 3),
        (Food.BREAD.item_ids, 5),
    ]

    # Find best food in inventory
    for food_ids, healing in food_priority:
        for food_id in food_ids:
            if food_id in inventory_ids:
                return food_id

    return None
```

**Usage:**

```python
if osrs.combat.should_eat(50):
    food_id = osrs.combat.get_best_available_food()
    if food_id:
        osrs.combat.eat_food(food_id)
    else:
        print("No food in inventory!")
```

---

#### `eat_best_food()`

**Purpose:** Wrapper that combines `get_best_available_food()` and `eat_food()`.

**Parameters:** None

**Returns:** `bool` - True if ate food successfully, False otherwise

**Logic:**

```python
def eat_best_food(self) -> bool:
    food_id = self.get_best_available_food()
    if food_id:
        return self.eat_food(food_id)
    return False
```

**Usage:**

```python
# Simple auto-eating
if osrs.combat.should_eat(60):
    osrs.combat.eat_best_food()
```

---

### 3. Prayer Management

Requires new API endpoint to expose active prayers.

#### **New API Endpoint:** `/combat` enhancement

Add to `HttpServerPlugin.java` handleCombat():

```java
// Active prayers
JsonArray activePrayers = new JsonArray();
for (Prayer prayer : Prayer.values()) {
    if (client.isPrayerActive(prayer)) {
        activePrayers.add(prayer.name());
    }
}
data.add("activePrayers", activePrayers);
```

#### **New API Wrapper:** `get_active_prayers()`

Add to `runelite_api.py`:

```python
def get_active_prayers(self) -> Optional[List[str]]:
    """
    Get list of currently active prayers.

    Returns:
        List of prayer names (e.g., ["PROTECT_FROM_MELEE", "PIETY"]) or None
    """
    combat_data = self.get_combat()
    if combat_data:
        return combat_data.get('activePrayers', [])
    return None
```

---

#### `get_combat_style()`

**Purpose:** Get current combat style (accurate/aggressive/defensive/controlled).

Requires new API endpoint.

#### **New API Endpoint:** `/combat` enhancement

Add to `HttpServerPlugin.java` handleCombat():

```java
// Combat style (VarPlayer 43: attack style index 0-3)
int attackStyle = client.getVarpValue(VarPlayer.ATTACK_STYLE);
String[] styleNames = {"ACCURATE", "AGGRESSIVE", "DEFENSIVE", "CONTROLLED"};
if (attackStyle >= 0 && attackStyle < styleNames.length) {
    data.addProperty("combatStyle", styleNames[attackStyle]);
}
```

#### **New API Wrapper:** `get_combat_style()`

Add to `runelite_api.py`:

```python
def get_combat_style(self) -> Optional[str]:
    """
    Get current combat style.

    Returns:
        Combat style string ("ACCURATE", "AGGRESSIVE", "DEFENSIVE", "CONTROLLED") or None
    """
    combat_data = self.get_combat()
    if combat_data:
        return combat_data.get('combatStyle')
    return None
```

---

#### `get_active_prayers()`

**Purpose:** Get list of currently active prayers.

**Parameters:** None

**Returns:** `Optional[List[str]]` - List of prayer names or None

**Logic:**

```python
def get_active_prayers(self) -> Optional[List[str]]:
    return self.api.get_active_prayers()
```

**Usage:**

```python
prayers = osrs.combat.get_active_prayers()
if prayers:
    print(f"Active prayers: {', '.join(prayers)}")
    if "PROTECT_FROM_MELEE" in prayers:
        print("Melee protection active")
```

---

### 4. Special Attack Handling

#### `use_special_attack()`

**Purpose:** Activate weapon special attack.

**Parameters:** None

**Returns:** `bool` - True if special attack activated, False otherwise

**Requirements:**

- Special attack energy >= weapon requirement (usually 25%, 50%, or 100%)
- Special attack bar must be accessible

**Logic:**

```python
def use_special_attack(self) -> bool:
    # Check if we have enough special attack energy
    special = self.get_special_attack()
    if special is None or special < 25:  # Most weapons require 25-50%
        return False

    # Click special attack orb
    # Need to define SPECIAL_ATTACK_ORB_REGION in config/regions.py
    from config.regions import SPECIAL_ATTACK_ORB_REGION

    self.window.move_mouse_to(SPECIAL_ATTACK_ORB_REGION.random_point())
    time.sleep(random.uniform(0.05, 0.10))
    self.window.click()

    time.sleep(random.uniform(0.10, 0.20))
    return True
```

**Usage:**

```python
# Dragon dagger special attack (50% energy, 2 hits)
if osrs.combat.get_special_attack() >= 50:
    osrs.combat.use_special_attack()
    print("Special attack activated!")
```

---

### 5. Combat Loop Helpers

#### `auto_heal_during_combat(health_threshold, prayer_threshold)`

**Purpose:** Automatically eat/drink during combat when thresholds are met.

**Parameters:**

- `health_threshold` (int, default: 50) - Health % to trigger eating
- `prayer_threshold` (int, default: 25) - Prayer % to trigger drinking

**Returns:** None (performs actions as needed)

**Logic:**

```python
def auto_heal_during_combat(self, health_threshold: int = 50,
                           prayer_threshold: int = 25) -> None:
    # Check health
    if self.should_eat(health_threshold):
        food_id = self.get_best_available_food()
        if food_id:
            self.eat_food(food_id)

    # Check prayer
    if self.should_drink_prayer(prayer_threshold):
        # Find prayer potion in inventory
        from config.items import Potions
        prayer_potions = [
            Potions.PRAYER_POTION_4.item_ids[0],
            Potions.PRAYER_POTION_3.item_ids[0],
            Potions.PRAYER_POTION_2.item_ids[0],
            Potions.PRAYER_POTION_1.item_ids[0],
            Potions.SUPER_RESTORE_4.item_ids[0],
            Potions.SUPER_RESTORE_3.item_ids[0],
            Potions.SUPER_RESTORE_2.item_ids[0],
            Potions.SUPER_RESTORE_1.item_ids[0],
        ]

        inventory_items = self.api.get_inventory()
        if inventory_items:
            inventory_ids = [item['id'] for item in inventory_items if item]
            for potion_id in prayer_potions:
                if potion_id in inventory_ids:
                    self.drink_potion(potion_id)
                    break
```

**Usage:**

```python
# In combat loop
while osrs.combat.is_player_in_combat():
    osrs.combat.auto_heal_during_combat(health_threshold=60, prayer_threshold=30)
    time.sleep(0.5)
```

---

## Implementation Priority

### High Priority (Essential for safe combat)

1. ✅ `is_safe_to_engage()` - Prevents engaging without resources
2. ✅ `emergency_teleport()` - Critical safety mechanism
3. ✅ `get_best_available_food()` / `eat_best_food()` - Auto-healing

### Medium Priority (Quality of life)

4. ⏳ `get_active_prayers()` - Prayer management (requires API)
5. ⏳ `get_combat_style()` - Combat style detection (requires API)
6. ⏳ `auto_heal_during_combat()` - Automated healing loop

### Low Priority (Advanced features)

7. ⏳ `use_special_attack()` - Special attack handling
8. ⏳ Advanced prayer flicking
9. ⏳ Combat style switching
10. ⏳ Loot detection and pickup

---

## Testing Strategy

Phase 2 tests should be added to `test_manual_modular.py`:

### Safety Check Tests

- `test_is_safe_to_engage()` - Test safety checks with various thresholds
- `test_emergency_teleport()` - Verify teleport item detection and usage

### Auto-Consumable Tests

- `test_get_best_available_food()` - Display food priority selection
- `test_eat_best_food()` - Auto-eating with food detection

### Prayer Tests (requires API)

- `test_get_active_prayers()` - Display active prayers
- `test_prayer_monitoring()` - Monitor prayer drain during combat

### Combat Loop Tests

- `test_auto_heal_during_combat()` - Full auto-healing loop
- `test_safe_combat_cycle()` - Complete combat with safety checks

---

## Configuration Requirements

### New Region Definitions (config/regions.py)

```python
# Special attack orb (combat tab)
SPECIAL_ATTACK_ORB_REGION = Region(563, 577, 50, 22)  # Adjust as needed
```

### Food Healing Values (config/items.py)

Already defined in Food category - no changes needed.

### Prayer Potion IDs (config/items.py)

Already defined in Potions category - no changes needed.

---

## API Extensions Summary

### Phase 2 API Changes

#### 1. Enhanced `/combat` endpoint:

```java
// Add to existing /combat endpoint:
- activePrayers: JsonArray of active prayer names
- combatStyle: String ("ACCURATE", "AGGRESSIVE", "DEFENSIVE", "CONTROLLED")
```

#### 2. New RuneLiteAPI methods:

```python
def get_active_prayers(self) -> Optional[List[str]]
def get_combat_style(self) -> Optional[str]
```

---

## Example: Complete Combat Bot Loop

```python
from client.osrs import OSRS
from config.npcs import LowLevelMonsters
from config.items import Food, Potions
import time

osrs = OSRS()

# Combat configuration
target_npc = LowLevelMonsters.CHICKEN.npc_ids
health_threshold = 60
prayer_threshold = 30
required_food = 8

# Main combat loop
while True:
    # Safety check before engaging
    if not osrs.combat.is_safe_to_engage(
        health_threshold=70,
        required_food_count=required_food
    ):
        print("Not safe to engage - restocking needed")
        break

    # Engage NPC
    if not osrs.combat.is_player_in_combat():
        print("Finding target...")
        if osrs.combat.engage_npc(target_npc):
            print("Engaged!")

    # Monitor combat
    while osrs.combat.is_player_in_combat():
        # Auto-heal
        osrs.combat.auto_heal_during_combat(
            health_threshold=health_threshold,
            prayer_threshold=prayer_threshold
        )

        # Emergency teleport if critical
        if osrs.combat.get_health_percent() < 20:
            print("EMERGENCY: Critical health!")
            osrs.combat.emergency_teleport()
            break

        time.sleep(0.5)

    # Wait for loot (optional)
    time.sleep(2.0)
```

---

## Migration from Phase 1 to Phase 2

Existing Phase 1 code remains **fully compatible**. Phase 2 adds **optional** enhancements:

### Before (Phase 1):

```python
# Manual food selection
if osrs.combat.should_eat(50):
    osrs.combat.eat_food(385)  # Shark ID
```

### After (Phase 2):

```python
# Auto food selection
if osrs.combat.should_eat(50):
    osrs.combat.eat_best_food()  # Automatically picks best food
```

All Phase 1 methods remain available and unchanged.
