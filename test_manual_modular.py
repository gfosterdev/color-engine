"""
Manual testing file for OSRS bot features - Modular Testing System.

Test each component in isolation without initializing unnecessary dependencies.
Navigate using number keys and submenus.
"""

import keyboard
import time
import ctypes
from util import Window, Region
from typing import Optional


class ModularTester:
    """Modular testing interface - initialize only what you need."""
    
    def __init__(self):
        """Initialize basic window connection only."""
        print("Initializing window connection...")
        self.window = Window()
        self.window.find(title="RuneLite - xJawj", exact_match=True)
        
        if not self.window.window:
            raise RuntimeError("Could not find RuneLite window!")
        
        print(f"Connected to: {self.window.window['title']}")
        
        # Lazy-loaded components
        self.inventory = None
        self.interfaces = None
        self.osrs = None
        self.interaction = None
        self.anti_ban = None
        self.registry = None
        self.config = None
        
        self.current_menu = "main"
        print("Basic initialization complete!")
    
    def ensure_window(self):
        """Ensure window is captured."""
        if not self.window.window:
            print("ERROR: Window not found!")
            return False
        self.window.capture()
        return True
    
    # =================================================================
    # LAZY INITIALIZATION - LOAD MODULES ON DEMAND
    # =================================================================
    
    def init_config(self):
        """Load configuration if needed."""
        if not self.config:
            from core.config import load_profile
            print("[Loading config...]")
            self.config = load_profile("iron_miner_varrock")
            print("[Config ready]")
        return self.config
    
    def init_inventory(self):
        """Initialize inventory module."""
        if not self.inventory:
            from client.inventory import InventoryManager
            print("[Loading inventory module...]")
            self.inventory = InventoryManager(self.window)
            print("[Inventory ready]")
        return self.inventory
    
    def init_interfaces(self):
        """Initialize interfaces module."""
        if not self.interfaces:
            from client.interfaces import InterfaceDetector
            print("[Loading interfaces module...]")
            self.interfaces = InterfaceDetector(self.window)
            print("[Interfaces ready]")
        return self.interfaces
    
    def init_osrs(self):
        """Initialize OSRS client."""
        if not self.osrs:
            from client.osrs import OSRS
            print("[Loading OSRS client...]")
            self.osrs = OSRS()
            print("[OSRS client ready]")
        return self.osrs
    
    def init_interactions(self):
        """Initialize game object interactions."""
        if not self.interaction:
            from client.interactions import GameObjectInteraction
            print("[Loading interactions module...]")
            self.interaction = GameObjectInteraction(self.window)
            print("[Interactions ready]")
        return self.interaction
    
    def init_color_registry(self):
        """Initialize color registry."""
        if not self.registry:
            from client.color_registry import get_registry
            print("[Loading color registry...]")
            self.registry = get_registry()
            print("[Registry ready]")
        return self.registry
    
    def init_anti_ban(self):
        """Initialize anti-ban module."""
        if not self.anti_ban:
            from core.anti_ban import AntiBanManager
            config = self.init_config()
            print("[Loading anti-ban module...]")
            self.anti_ban = AntiBanManager(
                window=self.window,
                config=config.anti_ban,
                break_config=config.breaks
            )
            print("[Anti-ban ready]")
        return self.anti_ban
    
    # =================================================================
    # WINDOW & COLOR DETECTION TESTS
    # =================================================================
    
    def test_window_info(self):
        """Print window information."""
        if not self.ensure_window():
            return
        
        w = self.window.window
        if w:
            print(f"\nWindow Title: {w['title']}")
            print(f"Position: ({w['x']}, {w['y']})")
            print(f"Size: {w['width']}x{w['height']}")
        else:
            print("\n✗ Window not found")
    
    def test_capture_screenshot(self):
        """Capture screenshot."""
        if not self.ensure_window():
            return
        
        print("\nScreenshot captured!")
        print(f"Image shape: {self.window.screenshot.shape if self.window.screenshot is not None else 'None'}")
        print("(Image stored in memory, call debug=True in Window methods to save to disk)")
    
    def test_mouse_position(self):
        """Get mouse position and color."""
        if not self.ensure_window():
            return
        
        try:
            import win32api
            x, y = win32api.GetCursorPos()
        except ImportError:
            # Fallback to ctypes
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            point = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
            x, y = point.x, point.y
        
        w = self.window.window
        if not w:
            print("\n✗ Window not found")
            return
        
        local_x = x - w['x']
        local_y = y - w['y']
        
        print(f"\nMouse Position:")
        print(f"  Global: ({x}, {y})")
        print(f"  Local:  ({local_x}, {local_y})")
        
        if 0 <= local_x < w['width'] and 0 <= local_y < w['height']:
            if self.window.screenshot is not None:
                b, g, r = self.window.screenshot[local_y, local_x]
                print(f"  Color (RGB): ({r}, {g}, {b})")
        else:
            print("  (Mouse outside window)")
    
    def test_find_color(self):
        """Find a specific color."""
        if not self.ensure_window():
            return
        
        try:
            rgb_input = input("\nEnter RGB color (e.g., 190,25,25): ")
            r, g, b = map(int, rgb_input.split(','))
            
            print(f"Searching for ({r}, {g}, {b})...")
            found = self.window.find_color_region((r, g, b), debug=True)
            
            if found:
                print(f"✓ Found at ({found.x}, {found.y}), size {found.width}x{found.height}")
                center = found.center()
                print(f"  Center: ({center[0]}, {center[1]})")
            else:
                print("✗ Color not found")
        except Exception as e:
            print(f"Error: {e}")
    
    def test_camera_rotation(self):
        """Test camera rotation."""
        if not self.ensure_window():
            return
        
        print("\nRotating camera...")
        self.window.rotate_camera(min_drag_distance=100)
        print("✓ Done")
    
    # =================================================================
    # OCR & TEXT RECOGNITION TESTS
    # =================================================================
    
    def test_hover_text(self):
        """Read hover text region."""
        if not self.ensure_window():
            return
        
        from client.osrs import INTERACT_TEXT_REGION
        print("\nReading hover text...")
        text = self.window.read_text(INTERACT_TEXT_REGION, debug=True)
        print(f"Result: '{text}'" if text else "No text found")
    
    def test_custom_region_ocr(self):
        """Read text from custom region."""
        if not self.ensure_window():
            return
        
        try:
            coords = input("\nEnter region (x,y,width,height): ")
            x, y, w, h = map(int, coords.split(','))
            
            region = Region(x, y, w, h)
            print("Reading text...")
            text = self.window.read_text(region, debug=True)
            print(f"Result: '{text}'" if text else "No text found")
        except Exception as e:
            print(f"Error: {e}")
    
    def test_bank_title_ocr(self):
        """Read bank title region."""
        if not self.ensure_window():
            return
        
        from client.interfaces import BANK_TITLE_REGION
        print("\nReading bank title region...")
        text = self.window.read_text(BANK_TITLE_REGION, debug=True)
        
        if text and "bank" in text.lower():
            print(f"✓ Bank title found: '{text}'")
        else:
            print("✗ Bank not detected (may be closed)")
    
    def test_chatbox_ocr(self):
        """Read chatbox."""
        if not self.ensure_window():
            return
        
        from client.interfaces import CHATBOX_REGION
        print("\nReading chatbox...")
        text = self.window.read_text(CHATBOX_REGION, debug=True)
        print(f"Result: '{text}'" if text else "Chatbox empty or unreadable")
    
    def test_region_from_config(self):
        """Read text from any region in config/regions.py."""
        import config.regions as regions
        
        # Get all available region names
        available_regions = []
        for name in dir(regions):
            if not name.startswith('_'):
                obj = getattr(regions, name)
                if isinstance(obj, Region):
                    available_regions.append(name)
        
        if not available_regions:
            print("\n✗ No regions found in config.regions")
            return
        
        print(f"\n{len(available_regions)} regions available in config.regions")
        print("Enter region name to test OCR (e.g., BANK_TITLE_REGION)")
        print("Press ESC or Ctrl+C to exit this test\n")
        
        while True:
            try:
                # Prompt for region name
                region_name = input("\nRegion name: ").strip()
                
                if not region_name:
                    continue
                
                # Try to get the region
                if not hasattr(regions, region_name):
                    print(f"✗ Region '{region_name}' not found")
                    print(f"Available: {', '.join(sorted(available_regions))}")
                    continue
                
                region_obj = getattr(regions, region_name)
                
                if not isinstance(region_obj, Region):
                    print(f"✗ '{region_name}' is not a Region object")
                    continue
                
                # Capture fresh screenshot
                if not self.ensure_window():
                    print("✗ Failed to capture window")
                    continue
                
                # Read text from the region
                print(f"\nReading text from {region_name}...")
                text = self.window.read_text(region_obj, debug=True)
                
                print(f"\n✓ {region_name}")
                print(f"  Position: ({region_obj.x}, {region_obj.y})")
                print(f"  Size: {region_obj.width}x{region_obj.height}")
                print(f"  Text: '{text}'" if text else "  Text: (empty or unreadable)")
                
            except KeyboardInterrupt:
                print("\n✓ Exiting region OCR test")
                break
            except EOFError:
                print("\n✓ Exiting region OCR test")
                break
            except Exception as e:
                print(f"✗ Error: {e}")
    
    def test_visualize_all_regions(self):
        """Visualize regions one-by-one from config/regions.py."""
        import config.regions as regions
        import cv2
        
        # Get all available region names
        available_regions = []
        for name in dir(regions):
            if not name.startswith('_'):
                obj = getattr(regions, name)
                if isinstance(obj, Region):
                    available_regions.append(name)
        
        if not available_regions:
            print("\n✗ No regions found in config.regions")
            return
        
        print(f"\n{len(available_regions)} regions available in config.regions")
        print("Enter region name to visualize (e.g., BANK_TITLE_REGION)")
        print("Press ESC or Ctrl+C to exit this test\n")
        
        while True:
            try:
                # Prompt for region name
                region_name = input("\nRegion name: ").strip()
                
                if not region_name:
                    continue
                
                # Try to get the region
                if not hasattr(regions, region_name):
                    print(f"✗ Region '{region_name}' not found")
                    print(f"Available: {', '.join(sorted(available_regions))}")
                    continue
                
                region_obj = getattr(regions, region_name)
                
                if not isinstance(region_obj, Region):
                    print(f"✗ '{region_name}' is not a Region object")
                    continue
                
                # Capture fresh screenshot
                if not self.ensure_window():
                    print("✗ Failed to capture window")
                    continue
                
                if self.window.screenshot is None:
                    print("✗ No screenshot available")
                    continue
                
                # Create annotated image
                annotated = self.window.screenshot.copy()
                
                # Draw the region with bright green
                color = (0, 255, 0)  # Green in BGR
                
                # Draw rectangle
                cv2.rectangle(
                    annotated,
                    (region_obj.x, region_obj.y),
                    (region_obj.x + region_obj.width, region_obj.y + region_obj.height),
                    color,
                    2
                )
                
                # Draw crosshair at center
                center = region_obj.center()
                cv2.drawMarker(
                    annotated,
                    center,
                    color,
                    cv2.MARKER_CROSS,
                    20,
                    2
                )
                
                # Add label with background
                label = region_name
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1
                
                # Get text size for background
                (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                
                # Draw background rectangle for text
                text_x = region_obj.x + 2
                text_y = region_obj.y - 5
                cv2.rectangle(
                    annotated,
                    (text_x, text_y - text_height - 2),
                    (text_x + text_width, text_y + 2),
                    color,
                    -1  # Filled
                )
                
                # Draw text
                cv2.putText(
                    annotated,
                    label,
                    (text_x, text_y),
                    font,
                    font_scale,
                    (0, 0, 0),  # Black text
                    thickness
                )
                
                # Save the annotated image (overwrite each time)
                output_file = 'region_test.png'
                cv2.imwrite(output_file, annotated)
                
                print(f"✓ {region_name}")
                print(f"  Position: ({region_obj.x}, {region_obj.y})")
                print(f"  Size: {region_obj.width}x{region_obj.height}")
                print(f"  Center: {center}")
                print(f"  Saved to: {output_file}")
                
            except KeyboardInterrupt:
                print("\n✓ Exiting region visualization")
                break
            except EOFError:
                print("\n✓ Exiting region visualization")
                break
            except Exception as e:
                print(f"✗ Error: {e}")
    
    # =================================================================
    # INVENTORY MODULE TESTS
    # =================================================================
    
    def test_inventory_status(self):
        """Check inventory status."""
        inv = self.init_inventory()
        if not self.ensure_window():
            return
        
        count = inv.count_items()
        empty = inv.count_empty_slots()
        is_full = inv.is_full()
        is_empty = inv.is_empty()
        
        print(f"\nInventory Status:")
        print(f"  Items: {count}/28")
        print(f"  Empty: {empty}")
        print(f"  Full:  {is_full}")
        print(f"  Empty: {is_empty}")
    
    def test_inventory_open_check(self):
        """Check if inventory tab is open."""
        inv = self.init_inventory()
        if not self.ensure_window():
            return
        
        is_open = inv.is_inventory_open()
        print(f"\nInventory tab open: {is_open}")
    
    def test_open_inventory_tab(self):
        """Open inventory tab."""
        inv = self.init_inventory()
        print("\nOpening inventory tab...")
        inv.open_inventory()
        time.sleep(0.3)
        print("✓ Tab opened (press F4 in-game)")
    
    def test_click_inventory_slot_0(self):
        """Click slot 0."""
        inv = self.init_inventory()
        print("\nClicking inventory slot 0...")
        inv.click_slot(0)
        print("✓ Clicked")
    
    def test_click_inventory_slot_10(self):
        """Click slot 10."""
        inv = self.init_inventory()
        print("\nClicking inventory slot 10...")
        inv.click_slot(10)
        print("✓ Clicked")
    
    def test_find_inventory_item(self):
        """Find item by color."""
        inv = self.init_inventory()
        if not self.ensure_window():
            return
        
        try:
            rgb_input = input("\nEnter item RGB (e.g., 100,50,25): ")
            r, g, b = map(int, rgb_input.split(','))
            
            print(f"Searching for item with color ({r}, {g}, {b})...")
            slot = inv.find_item_by_color((r, g, b))
            
            if slot is not None:
                print(f"✓ Found in slot {slot}")
            else:
                print("✗ Item not found")
        except Exception as e:
            print(f"Error: {e}")
    
    # =================================================================
    # INTERFACE DETECTION TESTS
    # =================================================================
    
    def test_check_bank_open(self):
        """Check if bank is open."""
        iface = self.init_interfaces()
        if not self.ensure_window():
            return
        
        is_open = iface.is_bank_open()
        print(f"\nBank open: {is_open}")
    
    def test_check_dialogue_open(self):
        """Check if dialogue is open."""
        iface = self.init_interfaces()
        if not self.ensure_window():
            return
        
        is_open = iface.is_dialogue_open()
        print(f"\nDialogue open: {is_open}")
    
    def test_check_level_up(self):
        """Check for level up."""
        iface = self.init_interfaces()
        if not self.ensure_window():
            return
        
        level_up = iface.is_level_up_shown()
        print(f"\nLevel up shown: {level_up}")
    
    def test_complete_interface_state(self):
        """Get all interface states."""
        iface = self.init_interfaces()
        if not self.ensure_window():
            return
        
        state = iface.get_interface_state()
        print(f"\nInterface State:")
        print(f"  Bank:     {state.bank_open}")
        print(f"  Shop:     {state.shop_open}")
        print(f"  Dialogue: {state.dialogue_open}")
        print(f"  Combat:   {state.in_combat}")
        print(f"  Level Up: {state.level_up_shown}")
    
    def test_close_any_interface(self):
        """Close interfaces with ESC."""
        from client.interactions import KeyboardInput
        kbd = KeyboardInput()
        print("\nPressing ESC...")
        kbd.press_key("esc")
        time.sleep(0.3)
        print("✓ Done")
    
    # =================================================================
    # BANKING MODULE TESTS
    # =================================================================
    
    def test_banking_open(self):
        """Open bank."""
        osrs = self.init_osrs()
        print("\nOpening bank...")
        result = osrs.open_bank()
        print(f"Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
    def test_banking_deposit_all(self):
        """Deposit all items."""
        osrs = self.init_osrs()
        iface = self.init_interfaces()
        
        if not self.ensure_window():
            return
        
        if not iface.is_bank_open():
            print("\n✗ Bank is not open! Open it first.")
            return
        
        print("\nDepositing all items...")
        result = osrs.deposit_all()
        print(f"Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
    def test_banking_close(self):
        """Close bank."""
        osrs = self.init_osrs()
        print("\nClosing bank...")
        result = osrs.close_bank()
        print(f"Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
    def test_banking_search(self):
        """Search bank."""
        osrs = self.init_osrs()
        iface = self.init_interfaces()
        
        if not self.ensure_window():
            return
        
        if not iface.is_bank_open():
            print("\n✗ Bank is not open! Open it first.")
            return
        
        print("\nSearching for 'iron'...")
        result = osrs.search_bank("iron")
        print(f"Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
    def test_banking_find(self):
        """Find bank with camera rotation."""
        osrs = self.init_osrs()
        print("\nFinding bank...")
        bank_point = osrs.find_bank()
        
        if bank_point:
            print(f"✓ Bank found at ({bank_point[0]}, {bank_point[1]})")
        else:
            print("✗ Bank not found")
    
    # =================================================================
    # GAME OBJECT INTERACTION TESTS
    # =================================================================
    
    def test_gameobject_find_ore(self):
        """Find iron ore."""
        interaction = self.init_interactions()
        registry = self.init_color_registry()
        
        if not self.ensure_window():
            return
        
        from client.interactions import GameObject
        
        iron_color = registry.get_color("iron_ore")
        if not iron_color:
            print("\n✗ Iron ore not in registry!")
            return
        
        iron_ore = GameObject(
            name="iron_ore",
            color=iron_color,
            object_type="ore",
            hover_text="Iron rocks"
        )
        
        print("\nFinding iron ore...")
        found = interaction.find_object(iron_ore)
        
        if found:
            center = found.center()
            print(f"✓ Found at ({found.x}, {found.y}), size {found.width}x{found.height}")
            print(f"  Center: ({center[0]}, {center[1]})")
        else:
            print("✗ Iron ore not found")
    
    def test_gameobject_interact_ore(self):
        """Interact with iron ore."""
        interaction = self.init_interactions()
        registry = self.init_color_registry()
        
        from client.interactions import GameObject
        
        iron_color = registry.get_color("iron_ore")
        if not iron_color:
            print("\n✗ Iron ore not in registry!")
            return
        
        iron_ore = GameObject(
            name="iron_ore",
            color=iron_color,
            object_type="ore",
            hover_text="Iron rocks"
        )
        
        print("\nInteracting with iron ore...")
        result = interaction.interact_with_object(iron_ore, validate_hover=True)
        print(f"Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
    def test_gameobject_find_bank(self):
        """Find bank booth."""
        interaction = self.init_interactions()
        registry = self.init_color_registry()
        
        if not self.ensure_window():
            return
        
        from client.interactions import GameObject
        
        bank_color = registry.get_color("bank_booth")
        if not bank_color:
            print("\n✗ Bank booth not in registry!")
            return
        
        bank = GameObject(
            name="bank_booth",
            color=bank_color,
            object_type="bank",
            hover_text="Bank"
        )
        
        print("\nFinding bank booth...")
        found = interaction.find_object(bank)
        
        if found:
            center = found.center()
            print(f"✓ Found at ({found.x}, {found.y}), size {found.width}x{found.height}")
            print(f"  Center: ({center[0]}, {center[1]})")
        else:
            print("✗ Bank not found")
    
    def test_gameobject_custom_color(self):
        """Find custom color object."""
        interaction = self.init_interactions()
        
        if not self.ensure_window():
            return
        
        try:
            from client.interactions import GameObject
            
            rgb_input = input("\nEnter RGB (e.g., 190,25,25): ")
            r, g, b = map(int, rgb_input.split(','))
            
            hover = input("Expected hover text (or press Enter to skip): ").strip()
            
            obj = GameObject(
                name="custom",
                color=(r, g, b),
                object_type="custom",
                hover_text=hover if hover else None
            )
            
            print(f"\nSearching for object with color ({r}, {g}, {b})...")
            found = interaction.find_object(obj)
            
            if found:
                center = found.center()
                print(f"✓ Found at ({found.x}, {found.y}), size {found.width}x{found.height}")
                print(f"  Center: ({center[0]}, {center[1]})")
            else:
                print("✗ Object not found")
        except Exception as e:
            print(f"Error: {e}")
    
    def test_gameobject_right_click(self):
        """Test right-click menu detection."""
        print("\n[Manual Test]")
        print("This requires you to manually right-click an object.")
        print("After right-clicking, check if the menu appears.")
        print("Press any key when ready...")
        input()
        
        from client.interactions import RightClickMenu
        menu = RightClickMenu(self.window)
        
        print("Checking for right-click menu...")
        is_open = menu.is_menu_open()
        print(f"Menu open: {is_open}")
    
    # =================================================================
    # ANTI-BAN SYSTEM TESTS
    # =================================================================
    
    def test_antiban_idle_action(self):
        """Perform idle action."""
        ab = self.init_anti_ban()
        print("\nPerforming idle action...")
        ab.perform_idle_action()
        print("✓ Done")
    
    def test_antiban_camera(self):
        """Random camera movement."""
        ab = self.init_anti_ban()
        print("\nPerforming random camera movement...")
        ab._random_camera_angle()
        print("✓ Done")
    
    def test_antiban_status(self):
        """Check anti-ban status."""
        ab = self.init_anti_ban()
        status = ab.get_status()
        
        print(f"\nAnti-Ban Status:")
        print(f"  Enabled:         {status['enabled']}")
        print(f"  Actions:         {status['actions_performed']}")
        print(f"  Fatigue:         {status['fatigue_level']:.2f}")
        print(f"  Next break (m):  {status['next_break_in_minutes']:.1f}")
    
    def test_antiban_break(self):
        """Simulate 5-second break."""
        ab = self.init_anti_ban()
        print("\nSimulating 5-second break...")
        
        from core.anti_ban import BreakSchedule
        ab.next_break = BreakSchedule(
            start_time=time.time(),
            duration=5.0,
            reason="manual_test"
        )
        ab.take_break()
        print("✓ Break complete")
    
    def test_antiban_tab_switch(self):
        """Test tab switching."""
        ab = self.init_anti_ban()
        print("\nPerforming random idle action (may switch tabs)...")
        ab.perform_idle_action()
        print("✓ Done")
    
    # =================================================================
    # COLOR REGISTRY TESTS
    # =================================================================
    
    def test_registry_list_all(self):
        """List all registered colors."""
        registry = self.init_color_registry()
        
        print("\nAll Registered Colors:")
        all_objects = registry.list_all()
        for obj_name, (color, obj_type) in all_objects.items():
            print(f"  {obj_name:20} -> RGB{color} ({obj_type})")
    
    def test_registry_list_ores(self):
        """List ore colors."""
        registry = self.init_color_registry()
        
        print("\nOre Colors:")
        all_objects = registry.list_all()
        for obj_name, (color, obj_type) in all_objects.items():
            if "ore" in obj_name or "rock" in obj_name or obj_type == "ore":
                print(f"  {obj_name:20} -> RGB{color}")
    
    def test_registry_list_trees(self):
        """List tree colors."""
        registry = self.init_color_registry()
        
        print("\nTree Colors:")
        all_objects = registry.list_all()
        for obj_name, (color, obj_type) in all_objects.items():
            if "tree" in obj_name or obj_type == "tree":
                print(f"  {obj_name:20} -> RGB{color}")
    
    def test_registry_find_by_color(self):
        """Find object by color."""
        registry = self.init_color_registry()
        
        try:
            rgb_input = input("\nEnter RGB (e.g., 190,25,25): ")
            r, g, b = map(int, rgb_input.split(','))
            
            result = registry.get_object_by_color((r, g, b))
            
            if result:
                print(f"✓ Object found: {result}")
            else:
                print("✗ No object with that color")
        except Exception as e:
            print(f"Error: {e}")
    
    def test_registry_get_color(self):
        """Get color for object name."""
        registry = self.init_color_registry()
        
        name = input("\nEnter object name (e.g., 'iron_ore'): ").strip()
        color = registry.get_color(name)
        
        if color:
            print(f"✓ {name} -> RGB{color}")
        else:
            print(f"✗ '{name}' not in registry")
    
    # =================================================================
    # MENU SYSTEM
    # =================================================================
    
    def run_window_tests(self):
        """Run window testing menu."""
        self.current_menu = "window"
        
        test_map = {
            'w': ("Window Info", self.test_window_info),
            'c': ("Capture Screenshot", self.test_capture_screenshot),
            'm': ("Mouse Position & Color", self.test_mouse_position),
            'f': ("Find Color", self.test_find_color),
            'r': ("Camera Rotation", self.test_camera_rotation),
            'v': ("Visualize All Regions", self.test_visualize_all_regions),
        }
        
        print("\n" + "="*60)
        print("WINDOW & COLOR DETECTION TESTS")
        print("="*60)
        print("W - Window Info")
        print("C - Capture Screenshot")
        print("M - Mouse Position & Color")
        print("F - Find Color (input RGB)")
        print("R - Camera Rotation")
        print("V - Visualize All Regions (from config)")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def run_ocr_tests(self):
        """Run OCR testing menu."""
        self.current_menu = "ocr"
        
        test_map = {
            '1': ("Hover Text", self.test_hover_text),
            '2': ("Custom Region", self.test_custom_region_ocr),
            '3': ("Bank Title", self.test_bank_title_ocr),
            '4': ("Chatbox", self.test_chatbox_ocr),
            '5': ("Test Region from Config", self.test_region_from_config),
        }
        
        print("\n" + "="*60)
        print("OCR & TEXT RECOGNITION TESTS")
        print("="*60)
        print("1 - Read Hover Text")
        print("2 - Read Custom Region (x,y,w,h)")
        print("3 - Read Bank Title")
        print("4 - Read Chatbox")
        print("5 - Test Region from Config (by name)")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def run_inventory_tests(self):
        """Run inventory testing menu."""
        self.current_menu = "inventory"
        
        test_map = {
            's': ("Inventory Status", self.test_inventory_status),
            'o': ("Check if Open", self.test_inventory_open_check),
            't': ("Open Tab", self.test_open_inventory_tab),
            '1': ("Click Slot 0", self.test_click_inventory_slot_0),
            '2': ("Click Slot 10", self.test_click_inventory_slot_10),
            '3': ("Find Item by Color", self.test_find_inventory_item),
        }
        
        print("\n" + "="*60)
        print("INVENTORY MODULE TESTS")
        print("="*60)
        print("S - Inventory Status")
        print("O - Check if Open")
        print("T - Open Tab")
        print("1 - Click Slot 0")
        print("2 - Click Slot 10")
        print("3 - Find Item by Color")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def run_interface_tests(self):
        """Run interface testing menu."""
        self.current_menu = "interface"
        
        test_map = {
            'b': ("Check Bank Open", self.test_check_bank_open),
            'd': ("Check Dialogue Open", self.test_check_dialogue_open),
            'l': ("Check Level Up", self.test_check_level_up),
            's': ("Complete State", self.test_complete_interface_state),
            'c': ("Close Interface", self.test_close_any_interface),
        }
        
        print("\n" + "="*60)
        print("INTERFACE DETECTION TESTS")
        print("="*60)
        print("B - Check Bank Open")
        print("D - Check Dialogue Open")
        print("L - Check Level Up")
        print("S - Complete Interface State")
        print("C - Close Interface (ESC)")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def run_banking_tests(self):
        """Run banking testing menu."""
        self.current_menu = "banking"
        
        test_map = {
            'o': ("Open Bank", self.test_banking_open),
            'd': ("Deposit All", self.test_banking_deposit_all),
            'c': ("Close Bank", self.test_banking_close),
            's': ("Search Bank", self.test_banking_search),
            'f': ("Find Bank", self.test_banking_find),
        }
        
        print("\n" + "="*60)
        print("BANKING MODULE TESTS")
        print("="*60)
        print("O - Open Bank")
        print("D - Deposit All")
        print("C - Close Bank")
        print("S - Search Bank (for 'iron')")
        print("F - Find Bank (with camera)")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def run_gameobject_tests(self):
        """Run game object testing menu."""
        self.current_menu = "gameobject"
        
        test_map = {
            '1': ("Find Iron Ore", self.test_gameobject_find_ore),
            '2': ("Interact with Ore", self.test_gameobject_interact_ore),
            '3': ("Find Bank Booth", self.test_gameobject_find_bank),
            '4': ("Find Custom Color", self.test_gameobject_custom_color),
            '5': ("Right-Click Menu", self.test_gameobject_right_click),
        }
        
        print("\n" + "="*60)
        print("GAME OBJECT INTERACTION TESTS")
        print("="*60)
        print("1 - Find Iron Ore")
        print("2 - Interact with Ore")
        print("3 - Find Bank Booth")
        print("4 - Find Custom Color")
        print("5 - Right-Click Menu Test")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def run_antiban_tests(self):
        """Run anti-ban testing menu."""
        self.current_menu = "antiban"
        
        test_map = {
            'i': ("Idle Action", self.test_antiban_idle_action),
            'c': ("Camera Movement", self.test_antiban_camera),
            's': ("Status", self.test_antiban_status),
            'b': ("Simulate Break", self.test_antiban_break),
            't': ("Tab Switch", self.test_antiban_tab_switch),
        }
        
        print("\n" + "="*60)
        print("ANTI-BAN SYSTEM TESTS")
        print("="*60)
        print("I - Perform Idle Action")
        print("C - Random Camera Movement")
        print("S - Check Status")
        print("B - Simulate 5s Break")
        print("T - Test Tab Switching")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def run_registry_tests(self):
        """Run color registry testing menu."""
        self.current_menu = "registry"
        
        test_map = {
            'l': ("List All Colors", self.test_registry_list_all),
            'o': ("List Ores", self.test_registry_list_ores),
            't': ("List Trees", self.test_registry_list_trees),
            'f': ("Find by Color", self.test_registry_find_by_color),
            'g': ("Get Color", self.test_registry_get_color),
        }
        
        print("\n" + "="*60)
        print("COLOR REGISTRY TESTS")
        print("="*60)
        print("L - List All Colors")
        print("O - List Ores")
        print("T - List Trees")
        print("F - Find Object by Color")
        print("G - Get Color for Object")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def _run_submenu(self, test_map):
        """Run a submenu with tests."""
        # Wait for menu selection key to be released
        time.sleep(0.3)
        
        while True:
            if keyboard.is_pressed('esc'):
                self.current_menu = "main"
                time.sleep(0.3)  # Debounce
                return
            
            for key, (desc, func) in test_map.items():
                if keyboard.is_pressed(key):
                    try:
                        print(f"\n>>> {desc}")
                        func()
                    except Exception as e:
                        print(f"\n✗ ERROR: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    time.sleep(0.5)  # Debounce
                    break
            
            time.sleep(0.05)
    
    def run(self):
        """Main testing loop."""
        menu_map = {
            '1': ("Window & Color", self.run_window_tests),
            '2': ("OCR & Text", self.run_ocr_tests),
            '3': ("Inventory", self.run_inventory_tests),
            '4': ("Interfaces", self.run_interface_tests),
            '5': ("Banking", self.run_banking_tests),
            '6': ("Game Objects", self.run_gameobject_tests),
            '7': ("Anti-Ban", self.run_antiban_tests),
            '8': ("Color Registry", self.run_registry_tests),
        }
        
        def print_main_menu():
            print("\n" + "="*60)
            print("MODULAR TESTING - SELECT CATEGORY")
            print("="*60)
            print("1 - Window & Color Detection Tests")
            print("2 - OCR & Text Recognition Tests")
            print("3 - Inventory Module Tests")
            print("4 - Interface Detection Tests")
            print("5 - Banking Module Tests")
            print("6 - Game Object Interaction Tests")
            print("7 - Anti-Ban System Tests")
            print("8 - Color Registry Tests")
            print("\nESC - Exit")
            print("="*60)
        
        print_main_menu()
        
        while True:
            if self.current_menu == "main":
                if keyboard.is_pressed('esc'):
                    print("\n✓ Exiting...")
                    return
                
                for key, (desc, func) in menu_map.items():
                    if keyboard.is_pressed(key):
                        func()
                        # Reprint main menu when returning from submenu
                        if self.current_menu == "main":
                            print_main_menu()
                        time.sleep(0.3)  # Debounce
                        break
            
            time.sleep(0.05)


if __name__ == "__main__":
    print("="*60)
    print("OSRS BOT - MODULAR TESTING SYSTEM")
    print("="*60)
    print("\nMake sure RuneLite is running in FIXED mode!")
    print("Components are loaded only when you test them.\n")
    
    try:
        tester = ModularTester()
        tester.run()
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✓ Testing interface closed.")
