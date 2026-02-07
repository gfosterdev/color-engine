"""
Comprehensive Test Suite for RuneLite HTTP Server Plugin API
Tests all available endpoints with detailed output and performance metrics.

Usage:
    python test_comprehensive_api.py

Features:
    - Tests all 17 endpoints
    - Performance benchmarking
    - Data validation
    - Real-time monitoring modes
    - Export capabilities
"""

import time
import keyboard
from typing import Any, Dict, List
from client.runelite_api import RuneLiteAPI


def print_header(title: str, char="="):
    """Print formatted header."""
    width = 80
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}\n")


def test_player_data(api: RuneLiteAPI):
    """Test all player-related endpoints."""
    print_header("🎮 PLAYER DATA TESTS")
    
    # Player State
    print("📊 Player State:")
    player = api.get_player()
    if player:
        print(f"  Name:           {player.get('name', 'N/A')}")
        print(f"  Combat Level:   {player.get('combatLevel', 'N/A')}")
        print(f"  Auto Retaliate:   {player.get('autoretaliate', 'N/A')}")
        print(f"  Health:         {player.get('health', 0)}/{player.get('maxHealth', 0)}")
        print(f"  Prayer:         {player.get('prayer', 0)}/{player.get('maxPrayer', 0)}")
        print(f"  Run Energy:     {player.get('runEnergy', 0)}%")
        print(f"  Special Attack: {player.get('specialAttack', 0)}%")
        print(f"  Weight:         {player.get('weight', 0)} kg")
        print(f"  Is Animating:   {player.get('isAnimating', False)}")
        if player.get('interactingWith'):
            print(f"  Interacting:    {player['interactingWith']}")
    else:
        print("  ❌ No player data available")
    
    # Combat State
    print("\n⚔️  Combat State:")
    combat = api.get_combat()
    if combat:
        print(f"  In Combat:      {combat.get('inCombat', False)}")
        print(f"  Auto Retaliate: {combat.get('autoRetaliate', False)}")
        if combat.get('target'):
            target = combat['target']
            print(f"  Target:         {target.get('name', 'Unknown')}")
            if 'id' in target:
                print(f"  Target ID:      {target['id']}")
                print(f"  Target Level:   {target.get('combatLevel', 'N/A')}")
    else:
        print("  ❌ No combat data available")
    
    # Animation
    print("\n🏃 Animation State:")
    anim = api.get_animation()
    if anim:
        print(f"  Animation ID:   {anim.get('animationId', -1)}")
        print(f"  Pose Animation: {anim.get('poseAnimation', -1)}")
        print(f"  Is Animating:   {anim.get('isAnimating', False)}")
        print(f"  Is Moving:      {anim.get('isMoving', False)}")
    else:
        print("  ❌ No animation data available")
    
    # Coordinates
    print("\n📍 Location:")
    coords = api.get_coords()
    if coords and 'world' in coords:
        world = coords['world']
        local = coords.get('local', {})
        print(f"  World: ({world.get('x')}, {world.get('y')}, Plane {world.get('plane')})")
        print(f"  Region: {world.get('regionID')} [{world.get('regionX')}, {world.get('regionY')}]")
        print(f"  Scene: ({local.get('sceneX')}, {local.get('sceneY')})")
    else:
        print("  ❌ No coordinate data available")


def test_skills(api: RuneLiteAPI):
    """Test skills endpoint with detailed breakdown."""
    print_header("📈 SKILLS TEST")
    
    stats = api.get_stats()
    if not stats:
        print("❌ No stats available")
        return
    
    print(f"✅ Retrieved {len(stats)} skills\n")
    
    # Group skills by category
    combat = ["Attack", "Strength", "Defence", "Hitpoints", "Ranged", "Prayer", "Magic"]
    gathering = ["Mining", "Fishing", "Woodcutting", "Farming", "Hunter"]
    production = ["Smithing", "Crafting", "Fletching", "Herblore", "Cooking", "Firemaking", "Runecraft", "Construction"]
    support = ["Agility", "Thieving", "Slayer"]
    
    def print_skill_group(name: str, skill_names: List[str]):
        print(f"{name}:")
        for stat in stats:
            if stat['stat'] in skill_names:
                level = stat['level']
                boosted = stat['boostedLevel']
                xp = stat['xp']
                to_next = stat.get('xpToNextLevel', 0)
                
                boost_str = f" ({boosted-level:+d})" if boosted != level else ""
                next_str = f" ({to_next:,} to {level+1})" if to_next > 0 and level < 99 else ""
                
                print(f"  {stat['stat']:14} Lvl {boosted}{boost_str:7} | {xp:>10,} XP{next_str}")
        print()
    
    print_skill_group("⚔️  Combat Skills", combat)
    print_skill_group("⛏️  Gathering Skills", gathering)
    print_skill_group("🔨 Production Skills", production)
    print_skill_group("🏃 Support Skills", support)
    
    # Calculate totals
    total_level = sum(s['level'] for s in stats)
    total_xp = sum(s['xp'] for s in stats)
    print(f"📊 Total Level: {total_level}")
    print(f"📊 Total XP: {total_xp:,}")


def test_inventory_equipment(api: RuneLiteAPI):
    """Test inventory and equipment endpoints."""
    print_header("🎒 INVENTORY & EQUIPMENT TEST")
    
    # Inventory
    print("📦 Inventory:")
    inv = api.get_inventory()
    if inv:
        for i, item in enumerate(inv, 1):
            qty = item.get('quantity', 1)
            qty_str = f" x{qty}" if qty > 1 else ""
            print(f"  {i}. ID {item.get('id')}{qty_str}")
    else:
        print("  ❌ Could not retrieve inventory")
    
    # Equipment
    print("\n🛡️  Equipment:")
    equip = api.get_equipment()
    if equip:
        items = [item for item in equip if item.get('id', -1) != -1]
        if items:
            slots = {0: "Head", 1: "Cape", 2: "Neck", 3: "Weapon", 4: "Body",
                    5: "Shield", 6: "Legs", 7: "Hands", 8: "Feet", 9: "Ring", 10: "Ammo"}
            for item in items:
                slot_name = slots.get(item.get('slot', -1), 'Unknown')
                print(f"  {slot_name:8} - ID {item.get('id')}")
        else:
            print("  No items equipped")
    else:
        print("  ❌ Could not retrieve equipment")
    
    # Bank (only if open)
    print("\n🏦 Bank:")
    bank = api.get_bank()
    if bank:
        print(f"  {len(bank)} items in bank")
        total_value = len(bank)  # Could calculate actual value if we had prices
        print(f"  Total slots used: {total_value}")
    else:
        print("  Bank not open or empty")

def test_inventory(api: RuneLiteAPI):
    """Test inventory endpoint."""
    print_header("🎒 INVENTORY TEST")
    
    # Inventory
    print("📦 Inventory:")
    index = int(input("Slot index: "))
    slot = api.get_inventory_slot(index)
    if slot:
        print(f"  Requested Slot: {slot.get('requestedSlot', 'N/A')}")
        print(f"  Empty:          {slot.get('empty', True)}")
        print(f"  Item ID:       {slot.get('itemId', -1)}")
        print(f"  Quantity:      {slot.get('quantity', 0)}")
    else:
        print("  ❌ Could not retrieve slot")

def test_world_data(api: RuneLiteAPI):
    """Test NPCs, players, objects, and ground items."""
    print_header("🌍 WORLD DATA TEST")
    
    # NPCs
    print("👹 NPCs in Scene:")
    npcs = api.get_npcs()
    if npcs:
        print(f"  Total NPCs: {len(npcs)}\n")
        
        # Group by name
        npc_counts = {}
        for npc in npcs:
            name = npc.get('name', 'Unknown')
            npc_counts[name] = npc_counts.get(name, 0) + 1
        
        # Show top 10
        sorted_npcs = sorted(npc_counts.items(), key=lambda x: x[1], reverse=True)
        for name, count in sorted_npcs[:10]:
            print(f"  {name:30} x{count}")
        
        if len(sorted_npcs) > 10:
            print(f"  ... and {len(sorted_npcs)-10} more types")
        
        # Show closest NPC
        npcs_with_dist = [n for n in npcs if n.get('distanceFromPlayer', -1) >= 0]
        if npcs_with_dist:
            closest = min(npcs_with_dist, key=lambda n: n['distanceFromPlayer'])
            print(f"\n  Closest: {closest.get('name')} (ID: {closest.get('id')}) - {closest['distanceFromPlayer']} tiles away")
    else:
        print("  No NPCs found")
    
    # Players
    print("\n👥 Other Players:")
    players = api.get_players()
    if players:
        print(f"  {len(players)} players nearby\n")
        for player in players[:10]:
            name = player.get('name', 'Unknown')
            level = player.get('combatLevel', '?')
            print(f"  {name} (Level {level})")
        if len(players) > 10:
            print(f"  ... and {len(players)-10} more players")
    else:
        print("  No other players nearby")
    
    # Ground Items
    print("\n💎 Ground Items:")
    items = api.get_ground_items()
    if items:
        print(f"  {len(items)} items on ground")
        item_counts = {}
        for item in items:
            item_id = item.get('id', -1)
            item_counts[item_id] = item_counts.get(item_id, 0) + item.get('quantity', 1)
        
        print(f"  {len(item_counts)} unique item types")
        
        # Test coordinate filtering if items exist
        if items:
            test_item = items[0]
            pos = test_item.get('position', {})
            test_x, test_y, test_plane = pos.get('x'), pos.get('y'), pos.get('plane')
            
            if test_x and test_y:
                # Test exact coordinate match
                filtered = api.get_ground_items(x=test_x, y=test_y, plane=test_plane)
                if filtered:
                    print(f"  ✓ Coordinate filter (exact): {len(filtered)} items at ({test_x}, {test_y})")
                
                # Test radius filter
                radius_filtered = api.get_ground_items(x=test_x, y=test_y, radius=5)
                if radius_filtered:
                    print(f"  ✓ Coordinate filter (radius=5): {len(radius_filtered)} items near ({test_x}, {test_y})")
    else:
        print("  No ground items visible")
    
    # Objects
    print("\n🏛️  Game Objects:")
    objects = api.get_objects()
    if objects:
        print(f"  {len(objects)} objects in scene")
        
        # Count unique objects
        obj_counts = {}
        iron_ore_count = 0
        for obj in objects:
            obj_id = obj.get('id', -1)
            obj_counts[obj_id] = obj_counts.get(obj_id, 0) + 1
            if obj_id == 11365 or obj_id == 11364:  # Iron ore rock IDs
                iron_ore_count += 1

        print(f"  {len(obj_counts)} unique object types")
        print(f"  Iron ore rocks (ID 11365): {iron_ore_count}")
    else:
        print("  No objects found")


def test_loot_detection(api: RuneLiteAPI):
    """Test ground item coordinate filtering for loot detection."""
    print_header("💰 LOOT DETECTION TEST (Coordinate Filtering)")
    
    # Get optional x/y coordinates from user
    print("Enter coordinates to filter by (or press Enter to skip):")
    x_input = input("  X coordinate: ").strip()
    y_input = input("  Y coordinate: ").strip()
    radius_input = input("  Radius (default 3): ").strip()
    
    # Parse coordinates
    filter_x = int(x_input) if x_input else None
    filter_y = int(y_input) if y_input else None
    filter_radius = int(radius_input) if radius_input else 3
    
    # Test 1: Get all ground items (unfiltered)
    print("\nTest 1: Get all ground items (unfiltered)")
    all_items = api.get_ground_items()
    if all_items:
        print(f"  ✅ Found {len(all_items)} total items in scene")
        for item in all_items[:5]:
            pos = item['position']
            print(f"     - Item ID {item['id']}, Qty: {item['quantity']} at ({pos['x']}, {pos['y']})")
        if len(all_items) > 5:
            print(f"     ... and {len(all_items) - 5} more items")
    else:
        print("  ❌ No ground items found")
    
    # Test 2: Get items with coordinate filter (if coordinates provided)
    if filter_x is not None and filter_y is not None:
        print(f"\nTest 2: Get items near ({filter_x}, {filter_y}) with radius {filter_radius}")
        filtered_items = api.get_ground_items(x=filter_x, y=filter_y, radius=filter_radius)
        if filtered_items:
            print(f"  ✅ Found {len(filtered_items)} items within {filter_radius} tiles:")
            for item in filtered_items:
                pos = item['position']
                dist = ((pos['x'] - filter_x)**2 + (pos['y'] - filter_y)**2)**0.5
                print(f"     - Item ID {item['id']}, Qty: {item['quantity']} at ({pos['x']}, {pos['y']}) - {dist:.1f} tiles away")
        else:
            print(f"  ℹ️  No items found within {filter_radius} tiles of ({filter_x}, {filter_y})")
    else:
        print("\nTest 2: Skipped (no coordinates provided)")


def test_menu(api: RuneLiteAPI):
    """
    Test Menu state.
    """
    print_header("📋 API Menu State")
    
    menu = api.get_menu()
    if not menu:
        print("❌ No menu data available")
        return
    
    print("❌ Menu is not open" if not menu.get("isOpen", False) else "✅ Menu is open")
    print(f"X Position: {menu.get('x', 'N/A')}")
    print(f"Y Position: {menu.get('y', 'N/A')}")
    print(f"Width:      {menu.get('width', 'N/A')}")
    print(f"Height:     {menu.get('height', 'N/A')}")

    # Entries
    menu_entries = menu.get("entries", []) if menu else []
    if menu_entries:
        print(f"✅ Retrieved {len(menu_entries)} menu entries:\n")
        for i, entry in enumerate(menu_entries, 1):
            option = entry.get('option', '')
            target = entry.get('target', '')
            print(f"  {i:2}. {option} {target}")
    else:
        print("❌ No menu entries available")

def test_widgets(api: RuneLiteAPI):
    print_header("📱 WIDGETS TEST")

    widgets = api.get_widgets()
    if widgets:
        print("✅ Retrieved widget states:\n")
        for key, value in widgets.items():
            print(f"  {key:25}: {value}")
    else:
        print("❌ No widget data available")

def test_sidebars(api: RuneLiteAPI):
    """
    Test sidebar tabs
    """
    print_header("📚 SIDEBAR TAB TEST")
    
    sidebar = api.get_sidebar_tabs()
    if not sidebar:
        print("❌ No sidebar tab data available")
        return
    
    for tab, is_open in sidebar.items():
        status = "Open" if is_open else "Closed"
        print(f"  {tab}: {status}")

def test_sidebar(api: RuneLiteAPI):
    """
    Test sidebar tabs
    """
    print_header("📚 SIDEBAR TAB TEST")
    
    tab = input("Enter tab name to check (e.g., inventory, skills): ")
    sidebar = api.get_sidebar_tab(tab)
    if not sidebar:
        print("❌ No sidebar tab data available")
        return
    
    for k, v in sidebar.items():
        print(f"  {k}: {v}")

def test_game_state(api: RuneLiteAPI):
    """Test camera, game state, menu, and widgets."""
    print_header("🎯 GAME STATE TEST")
    
    # Camera
    print("📷 Camera:")
    camera = api.get_camera()
    if camera:
        print(f"  Yaw:   {camera.get('yaw', 0)}")
        print(f"  Pitch: {camera.get('pitch', 0)}")
        print(f"  Scale: {camera.get('scale', 0)}")
        print(f"  Position: ({camera.get('x')}, {camera.get('y')}, {camera.get('z')})")
    else:
        print("  ❌ No camera data")
    
    # Game State
    print("\n🎮 Game State:")
    game = api.get_game_state()
    if game:
        print(f"  State:       {game.get('state', 'Unknown')}")
        print(f"  Logged In:   {game.get('isLoggedIn', False)}")
        print(f"  World:       {game.get('world', 'N/A')}")
        print(f"  Game Cycle:  {game.get('gameCycle', 0)}")
        print(f"  Tick Count:  {game.get('tickCount', 0)}")
        print(f"  FPS:         {game.get('fps', 0)}")
    else:
        print("  ❌ No game state data")
    
    # Widgets
    print("\n📱 Interface States:")
    widgets = api.get_widgets()
    if widgets:
        print(f"  Logout Panel Open:       {widgets.get('isLogoutPanelOpen', False)}")
        print(f"  Bank Open:       {widgets.get('isBankOpen', False)}")
        print(f"  Shop Open:       {widgets.get('isShopOpen', False)}")
        print(f"  Dialogue Open:   {widgets.get('isDialogueOpen', False)}")
        print(f"  Inventory Open: {widgets.get('isInventoryOpen', False)}")
    else:
        print("  ❌ No widget data")
    
    # # Menu
    # print("\n📋 Right-Click Menu:")
    # menu = api.get_menu()
    # if menu:
    #     print(f"  {len(menu)} menu entries")
    #     for i, entry in enumerate(menu[:5], 1):
    #         option = entry.get('option', '')
    #         target = entry.get('target', '')
    #         print(f"  {i}. {option} {target}")
    #     if len(menu) > 5:
    #         print(f"  ... and {len(menu)-5} more entries")
    # else:
    #     print("  Menu empty or not open")

def test_right_click_menu(api: RuneLiteAPI):
    """Test right-click menu entries."""
    print_header("📋 RIGHT-CLICK MENU TEST")
    
    menu = api.get_menu()
    menu_entries = menu.get("entries", []) if menu else []
    if menu_entries:
        print(f"✅ Retrieved {len(menu_entries)} menu entries:\n")
        for i, entry in enumerate(menu_entries, 1):
            option = entry.get('option', '')
            target = entry.get('target', '')
            print(f"  {i:2}. {option} {target}")
    else:
        print("❌ No menu entries available")

def test_performance(api: RuneLiteAPI):
    """Test API performance and response times."""
    print_header("⚡ PERFORMANCE TEST")
    
    endpoints = [
        ('stats', api.get_stats),
        ('player', api.get_player),
        ('coords', api.get_coords),
        ('combat', api.get_combat),
        ('animation', api.get_animation),
        ('inv', api.get_inventory),
        ('equip', api.get_equipment),
        ('npcs', api.get_npcs),
        ('players', api.get_players),
        ('objects', api.get_objects),
        ('grounditems', api.get_ground_items),
        ('camera', api.get_camera),
        ('game', api.get_game_state),
        ('menu', api.get_menu),
        ('widgets', api.get_widgets),
    ]
    
    print("Running performance tests (3 iterations each)...\n")
    
    results = {}
    for name, func in endpoints:
        times = []
        for _ in range(3):
            start = time.time()
            func()
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            time.sleep(0.1)  # Small delay between tests
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        results[name] = (avg_time, min_time, max_time)
    
    # Sort by average time
    sorted_results = sorted(results.items(), key=lambda x: x[1][0])
    
    print("Endpoint Performance (avg / min / max ms):")
    print("-" * 60)
    for name, (avg, minimum, maximum) in sorted_results:
        bar_len = int(avg / 5)
        bar = "█" * min(bar_len, 40)
        print(f"  /{name:12} {avg:6.1f} / {minimum:6.1f} / {maximum:6.1f} ms {bar}")
    
    total_avg = sum(r[0] for r in results.values()) / len(results)
    print(f"\n📊 Average response time: {total_avg:.1f}ms")

def test_bank(api: RuneLiteAPI):
    """
    Bank API output
    """
    print_header("🏦 BANK TEST")
    
    item_id = input("Enter item ID to check in bank (or press Enter to skip): ")
    if item_id.strip().isdigit():
        item_id = int(item_id.strip())
        item = api.get_bank_item(item_id)
        if item:
            print(f"✅ Item ID {item_id} found in bank:")
            print(f"  Slot:     {item.get('slot', 'N/A')}")
            print(f"  Quantity: {item.get('quantity', 0)}")
            widget = item.get('widget', None)
            if widget:
                print(f"  x: {widget.get('x', 'N/A')}, y: {widget.get('y', 'N/A')}, width: {widget.get('width', 'N/A')}, height: {widget.get('height', 'N/A')}")
                print(f"  Is Accessible: {widget.get('accessible', False)}")
                print(f"  Is Hidden: {widget.get('hidden', False)}")
                print(f"  Name: {widget.get('name', 'N/A')}")
        else:
            print(f"❌ Item ID {item_id} not found in bank")
    else:
        bank = api.get_bank()
        if bank:
            print(f"✅ Retrieved {len(bank)} bank items:\n")
            for i, item in enumerate(bank, 1):
                qty = item.get('quantity', 1)
                qty_str = f" x{qty}" if qty > 1 else ""
                slot = item.get('slot', -1)
                print(f"  {i}. ID {item.get('id')}{qty_str} (Slot {slot})")
        else:
            print("❌ Could not retrieve bank items or bank is closed")

def monitor_mining(api: RuneLiteAPI):
    """Real-time mining monitor - perfect for bots!"""
    print_header("⛏️  MINING MONITOR", "=")
    print("Monitoring mining activity in real-time...")
    print("Shows: Animation state, inventory changes, nearby rocks")
    print("Press Ctrl+C to stop\n")
    
    last_inv_count = 0
    mining_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Get player state
            player = api.get_player()
            anim = api.get_animation()
            inv = api.get_inventory()
            
            # Count inventory items
            if inv:
                ore_count = len([i for i in inv if i.get('id', -1) != -1])
            else:
                ore_count = 0
            
            # Detect mining
            is_mining = anim and anim.get('isAnimating', False)
            
            # Detect inventory change
            if ore_count > last_inv_count:
                mining_count += 1
                print(f"  ⛏️  Mined ore #{mining_count}! Inventory: {ore_count}/28")
            
            last_inv_count = ore_count
            
            # Display status
            timestamp = time.strftime("%H:%M:%S")
            status = "⛏️  MINING" if is_mining else "⏸️  IDLE"
            health = player.get('health', 0) if player else 0
            
            print(f"\r[{timestamp}] {status} | HP: {health} | Inv: {ore_count}/28 | Mined: {mining_count}", end="")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\n⏹️  Stopped after {elapsed:.0f} seconds")
        print(f"   Total ore mined: {mining_count}")
        if elapsed > 0:
            print(f"   Average rate: {mining_count/(elapsed/60):.1f} ore/minute")


def run_all_tests(api: RuneLiteAPI):
    """Run complete test suite."""
    print_header("🚀 COMPREHENSIVE API TEST SUITE", "=")
    
    test_player_data(api)
    input("\nPress Enter to continue to Skills test...")
    
    test_skills(api)
    input("\nPress Enter to continue to Inventory test...")
    
    test_inventory_equipment(api)
    input("\nPress Enter to continue to World Data test...")
    
    test_world_data(api)
    input("\nPress Enter to continue to Game State test...")
    
    test_game_state(api)
    input("\nPress Enter to continue to Performance test...")
    
    test_performance(api)
    
    print_header("✅ ALL TESTS COMPLETED", "=")

def test_npcs_in_viewport(api: RuneLiteAPI):
    """Test NPCs in viewport endpoint."""
    print_header("👀 NPCs IN VIEWPORT TEST")
    
    npcs = api.get_npcs_in_viewport()
    if npcs:
        print(f"✅ Retrieved {len(npcs)} NPCs in viewport:\n")
        for i, npc in enumerate(npcs, 1):
            name = npc.get('name', 'Unknown')
            npc_id = npc.get('id', -1)
            x = npc.get('x', -1)
            y = npc.get('y', -1)
            print(f"  {i:2}. {name} (ID: {npc_id}) - ({x}, {y})")
    else:
        print("❌ No NPCs in viewport or endpoint not available")

def test_viewport_data(api: RuneLiteAPI):
    """Test viewport data endpoint."""
    print_header("🖼️ VIEWPORT DATA TEST")
    
    viewport = api.get_viewport_data()
    if viewport:
        print("✅ Viewport Data:\n")
        print(f"  Width:        {viewport.get('width', 'N/A')}")
        print(f"  Height:       {viewport.get('height', 'N/A')}")
        print(f"  X Offset:     {viewport.get('xOffset', 'N/A')}")
        print(f"  Y Offset:     {viewport.get('yOffset', 'N/A')}")
    else:
        print("❌ No viewport data available")

def print_menu():
    """Display test menu."""
    print("\n" + "=" * 80)
    print("  ⚡ COMPREHENSIVE RUNELITE API TEST SUITE")
    print("=" * 80)
    print("\n📡 Individual Tests:")
    print("  1 - Player Data (health, prayer, energy, combat, animation)")
    print("  2 - Skills (all 23 skills with XP tracking)")
    print("  3 - Inventory & Equipment")
    print("  4 - World Data (NPCs, players, objects, ground items)")
    print("  5 - Game State (camera, widgets, menu)")
    print("  6 - Performance Benchmark")
    print("\n🔥 Special Features:")
    print("  7 - Mining Monitor (real-time bot-ready tracking)")
    print("  8 - Run All Tests")
    print("  9 - Menu State Test (displays current menu state)")
    print("  a - NPCs in Viewport Test")
    print("  L - Loot Detection Test (coordinate filtering)")
    print("  v - Viewport Data Test")
    print("  i - Inventory Slot Test")
    print("  w - Test widgets")
    print("  s - Test sidebar tabs")
    print("  d - Test specific sidebar tab")
    print("  b - Test bank")
    print("\n❌ Exit:")
    print("  0 - Quit")
    print("\n" + "=" * 80)


def main():
    """Main interactive menu."""
    print("\n" + "⚡" * 40)
    print("  COMPREHENSIVE RUNELITE HTTP API TEST SUITE")
    print("⚡" * 40)
    
    api = RuneLiteAPI()
    
    # Connection check
    print("\n🔌 Testing connection...")
    test_data = api.get_game_state()
    if test_data:
        print(f"✅ Connected successfully!")
        print(f"   World: {test_data.get('world', 'N/A')}")
        print(f"   FPS: {test_data.get('fps', 0)}")
    else:
        print("⚠️  Could not connect to API")
        print("   Make sure RuneLite is running with the HTTP Server plugin enabled")
    
    while True:
        print_menu()
        print("\nPress a key to run the corresponding test (Esc or 0 to quit)")

        # Dispatch map: key -> callable that runs the test and optionally pauses
        actions = {
            '1': lambda: (test_player_data(api), input("\nPress Enter to continue...")),
            '2': lambda: (test_skills(api), input("\nPress Enter to continue...")),
            '3': lambda: (test_inventory_equipment(api), input("\nPress Enter to continue...")),
            '4': lambda: (test_world_data(api), input("\nPress Enter to continue...")),
            '5': lambda: (test_game_state(api), input("\nPress Enter to continue...")),
            '6': lambda: (test_performance(api), input("\nPress Enter to continue...")),
            '7': lambda: (monitor_mining(api), input("\nPress Enter to continue...")),
            '8': lambda: (run_all_tests(api), input("\nPress Enter to continue...")),
            '9': lambda: (test_menu(api), input("\n⚡ Press Enter to continue...")),
            'a': lambda: (test_npcs_in_viewport(api), input("\n⚡ Press Enter to continue...")),
            'L': lambda: (test_loot_detection(api), input("\n⚡ Press Enter to continue...")),
            'v': lambda: (test_viewport_data(api), input("\n⚡ Press Enter to continue...")),
            'i': lambda: (test_inventory(api), input("\n⚡ Press Enter to continue...")),
            'w': lambda: (test_widgets(api), input("\n⚡ Press Enter to continue...")),
            's': lambda: (test_sidebars(api), input("\n⚡ Press Enter to continue...")),
            'd': lambda: (test_sidebar(api), input("\n⚡ Press Enter to continue...")),
            'b': lambda: (test_bank(api), input("\n⚡ Press Enter to continue...")),
        }

        # Wait for key presses and dispatch immediately
        while True:
            # Exit
            if keyboard.is_pressed('0') or keyboard.is_pressed('esc'):
                print("\n👋 Goodbye!")
                return

            for key, func in actions.items():
                if keyboard.is_pressed(key):
                    try:
                        func()
                    except Exception as e:
                        print(f"\n✗ ERROR: {e}")
                        import traceback
                        traceback.print_exc()
                    time.sleep(0.3)  # debounce after handling
                    break

            time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test suite interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
