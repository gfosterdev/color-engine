# Pathfinding System Implementation

## Overview

The OSRS bot now includes a sophisticated variance-based pathfinding system that provides collision-aware navigation with built-in anti-detection mechanisms. The system uses pre-computed collision data from RuneLite and implements Dijkstra's algorithm with randomized edge weights to generate unique paths on every execution.

## Quick Start

### 1. Download Collision Data

```bash
python scripts/download_collision_data.py
```

This downloads the pre-built collision-map.zip (~50MB) from RuneLite's shortest-path plugin repository. The file is updated weekly on Wednesdays at 23:20 UTC.

### 2. Test the System

```bash
python test_manual_modular.py
```

Press `P` for Pathfinding Tests menu to verify the system is working:

- `S` - Show statistics (collision cache, path cache, hit rates)
- `C` - Test collision detection at current position
- `P` - Benchmark path calculation performance
- `V` - Verify path variance (generates 5 unique paths)
- `W` - Walk with pathfinding enabled
- `L` - Walk with linear navigation (fallback)

### 3. Configure in Profile

Edit `config/profiles/iron_miner_varrock.json`:

```json
{
	"pathfinding": {
		"enable_pathfinding": true,
		"variance_level": "moderate",
		"repathing_chance": 0.2,
		"path_cache_size": 100,
		"region_cache_size": 50
	}
}
```

**Variance Levels:**

- `conservative`: ±10-15% edge weight variance, 0-1 waypoints
- `moderate`: ±15-25% edge weight variance, 1-2 waypoints (recommended)
- `aggressive`: ±25-35% edge weight variance, 2-3 waypoints

## Architecture

### Components

1. **CollisionMap** (`util/collision_util.py`)
    - Lazy-loads collision regions from ZIP with LRU caching
    - Max 50 regions in memory (~10MB RAM)
    - Bit-packed format: 2 bits per tile (N/S and E/W flags)
    - Singleton pattern for efficient memory usage

2. **VariancePathfinder** (`client/pathfinder.py`)
    - Dijkstra's algorithm with randomized edge weights
    - Path caching (up to 100 routes) with execution randomness
    - Random waypoint injection for large-scale deviation
    - 8-directional movement (N, S, E, W, NE, NW, SE, SW)

3. **NavigationManager** (`client/navigation.py`)
    - Integrates pathfinding with existing minimap navigation
    - Dynamic re-pathing (20% chance mid-journey)
    - Enhanced stuck detection triggers re-pathing
    - Graceful fallback to linear navigation if pathfinding unavailable

### Key Features

**Path Variance Mechanisms:**

- ✅ Randomized edge weights (±10-35% per profile)
- ✅ Random waypoint injection (1-3 waypoints for paths >15 tiles)
- ✅ Random click points within tiles
- ✅ Variable movement speeds
- ✅ Dynamic re-pathing during travel

**Performance Optimizations:**

- ✅ Lazy loading (modules loaded only when needed)
- ✅ LRU caching for collision regions (configurable size)
- ✅ Path caching with execution randomness
- ✅ Efficient bit-packed collision data format

**Anti-Detection:**

- ✅ No two paths are identical (variance on every calculation)
- ✅ Execution randomness even with cached paths
- ✅ Random re-pathing triggers mid-journey
- ✅ Stuck detection causes path recalculation with new seed

## Usage Examples

### Basic Navigation

```python
from client.navigation import NavigationManager
from util import Window

window = Window()
window.find(title="RuneLite")

nav = NavigationManager(window)

# Walk to coordinates (pathfinding automatically enabled)
nav.walk_to_tile(3200, 3220, plane=0)
```

### Custom Configuration

```python
# Load profile with custom pathfinding settings
profile_config = {
    "pathfinding": {
        "variance_level": "aggressive",
        "repathing_chance": 0.3,
        "enable_pathfinding": True
    }
}

nav = NavigationManager(window, profile_config=profile_config)
nav.walk_to_tile(3200, 3220)
```

### Disable Pathfinding (Linear Navigation)

```python
# Fallback to linear interpolation
nav.walk_to_tile(3200, 3220, use_pathfinding=False)
```

### Check Statistics

```python
stats = nav.get_pathfinding_stats()
print(f"Path cache hit rate: {stats['pathfinder']['hit_rate_percent']:.1f}%")
print(f"Collision regions cached: {stats['collision_map']['cached_regions']}")
```

### Clear Cache (Force New Paths)

```python
nav.clear_path_cache()  # Useful for testing variance
```

## Testing

### Automated Tests

Run the test suite to verify functionality:

```bash
python test_manual_modular.py
```

Navigate to **Pathfinding Tests (P)** menu:

1. **Statistics Test** - Verify system is loaded and caching is working
2. **Collision Detection** - Check walkability in all 8 directions
3. **Performance Test** - Benchmark path calculation (5-50 tile distances)
4. **Variance Test** - Generate 5 paths and verify they're all unique
5. **Walk Tests** - Compare pathfinding vs. linear navigation

### Expected Performance

- **5 tile path**: < 10ms
- **10 tile path**: < 20ms
- **20 tile path**: < 50ms
- **50 tile path**: < 200ms

### Variance Validation

The variance test should show:

- ✅ All 5 generated paths are unique
- ✅ Path lengths vary within reasonable range
- ✅ Different waypoints selected each time

## Configuration Reference

### Profile Settings

```json
{
	"pathfinding": {
		// Enable collision-aware pathfinding (true/false)
		"enable_pathfinding": true,

		// Path variance level (conservative/moderate/aggressive)
		"variance_level": "moderate",

		// Chance to re-calculate path mid-journey (0.0-1.0)
		"repathing_chance": 0.2,

		// Maximum number of cached paths (default: 100)
		"path_cache_size": 100,

		// Maximum collision regions in memory (default: 50)
		"region_cache_size": 50
	}
}
```

### Variance Level Details

| Level        | Edge Weight | Waypoints | Use Case                            |
| ------------ | ----------- | --------- | ----------------------------------- |
| Conservative | ±10-15%     | 0-1       | Short distances, precise navigation |
| Moderate     | ±15-25%     | 1-2       | General use (recommended)           |
| Aggressive   | ±25-35%     | 2-3       | Long distances, maximum variance    |

## Troubleshooting

### "Collision map not found" Error

**Solution:** Run the download script:

```bash
python scripts/download_collision_data.py
```

The collision-map.zip file should be placed in `util/data/collision-map.zip`.

### Pathfinding Falls Back to Linear Navigation

**Causes:**

1. Collision data not downloaded
2. `enable_pathfinding: false` in profile
3. Region not in collision map (new game content)
4. File permissions issue

**Check:**

```python
nav = NavigationManager(window)
nav._ensure_pathfinding_loaded()  # Returns True if loaded
```

### High Memory Usage

The collision map can use significant RAM if many regions are loaded. Adjust `region_cache_size` in profile:

```json
{
	"pathfinding": {
		"region_cache_size": 25 // Reduce from default 50
	}
}
```

Each region uses ~200KB, so 50 regions = ~10MB.

### Path Cache Not Working

Check cache statistics:

```python
stats = nav.get_pathfinding_stats()
print(stats['pathfinder'])
# Look for hit_rate_percent - should increase over time
```

Clear cache if needed:

```python
nav.clear_path_cache()
```

### Paths Don't Seem Varied

1. Verify variance level is set correctly in profile
2. Check that caching isn't reusing same path:
    ```python
    nav.clear_path_cache()  # Force recalculation
    ```
3. Run variance test in test suite (should show all unique paths)

## Technical Details

### Collision Data Format

- **Source:** RuneLite shortest-path plugin
- **Format:** ZIP archive with binary region files
- **Region Size:** 64x64 tiles per region
- **Bit Packing:** 2 bits per tile (North/South flag, East/West flag)
- **Update Frequency:** Weekly (Wednesdays 23:20 UTC)

### Pathfinding Algorithm

1. **Dijkstra's Algorithm** with modifications:
    - Random edge weights (variance_config)
    - 8-directional neighbor generation
    - Collision-aware (queries CollisionMap)

2. **Waypoint Injection:**
    - Paths >15 tiles get random waypoints
    - Waypoints placed perpendicular to straight line
    - Deviation distance based on variance level

3. **Execution Randomness:**
    - Even cached paths have varied execution
    - Random click points within tiles
    - Variable movement speeds
    - Random delays

### Memory Management

- **Lazy Loading:** Modules loaded only when `walk_to_tile()` called
- **LRU Caching:** Least-recently-used regions evicted when full
- **Path Caching:** FIFO eviction when max_cache_size reached
- **Singleton Pattern:** One CollisionMap instance shared globally

## Future Enhancements

### Planned Features

- [ ] Transport system integration (doors, ladders, shortcuts)
- [ ] Agility shortcut support with skill level checking
- [ ] A\* algorithm option for faster long-distance pathing
- [ ] Dynamic obstacle detection (NPCs, players blocking path)
- [ ] Region pre-loading for common areas (banks, training spots)
- [ ] Path smoothing for more natural movement
- [ ] Teleport integration

### Configuration Ideas

- [ ] Per-skill pathfinding profiles
- [ ] Time-of-day variance adjustments
- [ ] Fatigue-scaled variance (more erratic when tired)
- [ ] Area-specific settings (cities vs. wilderness)

## Contributing

When adding new features:

1. Update `client/pathfinder.py` for algorithm changes
2. Update `client/navigation.py` for integration changes
3. Add tests to `test_manual_modular.py` pathfinding menu
4. Update profile schema in `config/profiles/*.json`
5. Document changes in this README

## Credits

- **Collision Data:** RuneLite shortest-path plugin by Skretzo
- **Algorithm:** Modified Dijkstra with variance mechanisms
- **Implementation:** OSRS Color Engine Bot Project

---

**Last Updated:** January 27, 2026
**Version:** 1.0.0
