"""
Manual testing file for OSRS bot features - Modular Testing System.

Test each component in isolation without initializing unnecessary dependencies.
Navigate using number keys and submenus.
"""

import keyboard
import time
import random
import ctypes
from util import Window, Region
from util.types import Polygon
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
        self.navigation = None
        self.api = None
        
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
            # Need to initialize a minimal OSRS instance for inventory
            osrs = self.init_osrs()
            self.inventory = osrs.inventory
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
    
    def init_api(self):
        """Initialize API"""
        if not self.api:
            from client.runelite_api import RuneLiteAPI
            print("[Loading RuneLite API...]")
            self.api = RuneLiteAPI()
            print("[RuneLite API ready]")
        return self.api

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
            osrs = self.init_osrs()  # Need OSRS client for logout breaks
            print("[Loading anti-ban module...]")
            self.anti_ban = AntiBanManager(
                window=self.window,
                config=config.anti_ban,
                break_config=config.breaks,
                osrs_client=osrs
            )
            print("[Anti-ban ready]")
        return self.anti_ban
    
    def init_navigation(self):
        """Initialize navigation module."""
        if not self.navigation:
            from client.navigation import NavigationManager
            print("[Loading navigation module...]")
            self.navigation = NavigationManager(self.window)
            print("[Navigation ready]")
        return self.navigation
    
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
            import win32api  # type: ignore[import-not-found]
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
    
    def test_move_mouse_to(self):
        """Move mouse to specified position."""
        if not self.ensure_window():
            return
        
        try:
            coords = input("\nEnter target position (x,y): ")
            x, y = map(int, coords.split(','))
            
            print(f"Moving mouse to ({x}, {y})...")
            self.window.move_mouse_to((x, y))
            print("✓ Mouse moved")
        except Exception as e:
            print(f"Error: {e}")

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
    
    def test_click_at_position(self):
        """Test clicking at current mouse position."""
        if not self.ensure_window():
            return
        
        print("\nTest: Click at current mouse position")
        print("Move your mouse to where you want to click")
        print("Press SPACE to execute the click, ESC to cancel\n")
        
        import keyboard
        
        while True:
            if keyboard.is_pressed('space'):
                w = self.window.window
                if w:
                    print(f"Clicking at current mouse position...")
                    
                    if self.window.click():
                        print("✓ Click executed successfully")
                    else:
                        print("✗ Click failed")
                else:
                    print("✗ Window not found")
                
                time.sleep(0.3)  # Debounce
                break
            
            if keyboard.is_pressed('esc'):
                print("Cancelled")
                time.sleep(0.3)  # Debounce
                break
            
            time.sleep(0.05)
    
    def test_mouse_against_api(self):
        """
        Tests what the Window class has for mouse pos against
        API actual canvas pos
        """
        api = self.init_api()
        osrs = self.init_osrs()

        # print(f"\nMoving mouse to window: 512, 334")
        # osrs.window.move_mouse_to((512, 334))
        # import time
        # time.sleep(1.5)

        print(f"\nGetting canvas mouse position from API")
        viewport = api.get_viewport_data()
        if viewport:
            x = viewport.get('canvasMouseX', -1)
            y = viewport.get('canvasMouseY', -1)
            print(f"✓ Canvas mouse position from API: {(x, y)}")

    def test_viewport_bounds(self):
        """Tests if viewport bounds are correct"""
        osrs = self.init_osrs()
        game_area = osrs.window.GAME_AREA
        import time

        print(f"\nMoving mouse to viewport top left: {(game_area.x, game_area.y)}")
        osrs.window.move_mouse_to((game_area.x, game_area.y), in_canvas=True)
        time.sleep(1.5)
        print(f"\nMoving mouse to viewport top right: {(game_area.x + game_area.width, game_area.y)}")
        osrs.window.move_mouse_to((game_area.x + game_area.width, game_area.y), in_canvas=True)
        time.sleep(1.5)
        print(f"\nMoving mouse to viewport bottom left: {(game_area.x, game_area.y + game_area.height)}")
        osrs.window.move_mouse_to((game_area.x, game_area.y + game_area.height), in_canvas=True)
        time.sleep(1.5)
        print(f"\nMoving mouse to viewport bottom right: {(game_area.x + game_area.width, game_area.y + game_area.height)}")
        osrs.window.move_mouse_to((game_area.x + game_area.width, game_area.y + game_area.height), in_canvas=True)
        print(f"\nCanvas test complete")
        
    def test_gameobject_right_click(self):
        """
        Finds and tests right click menu functionality.
        """
        osrs = self.init_osrs()
        print("\nTesting right click menu...")
        option = "Drop"
        target = "Iron ore"

        osrs.click(option, target)
    
        print("\nFinished right click menu test")


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
        
        # from client.interfaces import CHATBOX_REGION
        # print("\nReading chatbox...")
        # text = self.window.read_text(CHAT
        text = None
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
        
        inv.populate()
        count = inv.count_filled()
        empty = inv.count_empty_slots()
        is_full = inv.is_full()
        is_empty = inv.is_empty()
        
        print(f"\nInventory Status:")
        print(f"  Items: {count}/28")
        print(f"  Empty: {empty}")
        print(f"  Full:  {is_full}")
        print(f"  Empty: {is_empty}")
    
    def test_inventory_regions(self):
        inv = self.init_inventory()
        for i, slot in enumerate(inv.slots):
            print(f"Slot {i}")
            self.window.move_mouse_to((slot.region.x, slot.region.y))
            time.sleep(.1)
            self.window.move_mouse_to((slot.region.x + slot.region.width, slot.region.y))
            time.sleep(.1)
            self.window.move_mouse_to((slot.region.x, slot.region.y + slot.region.height))
            time.sleep(.1)
            self.window.move_mouse_to((slot.region.x + slot.region.width, slot.region.y + slot.region.height))
            time.sleep(.1)

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
    
    def test_click_inventory_slot(self):
        """Click slot 0."""
        inv = self.init_inventory()

        slot = int(input("Inventory slot: "))
        print(f"\nClicking inventory slot {slot}...")
        inv.click_slot(slot)
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
            # Note: This test requires implementing find_item_by_color in InventoryManager
            print("✗ Method find_item_by_color not yet implemented")
        except Exception as e:
            print(f"Error: {e}")
    
    def test_click_inventory_item(self):
        print("TEST CLICKING ITEM")
        osrs = self.init_osrs()

        item_id = int(input("itemID: ").strip())
        action = input("action: ").strip()

        self.osrs.inventory.click_item(item_id, action)

    def test_drop_slot(self):
        """
        Drops item at slot.
        """
        osrs = self.init_osrs()

        slot = int(input("Inventory slot to drop: "))
        print(f"\nDropping inventory slot {slot}...")
        success = osrs.inventory.drop_item(slot)
        print("✓ Dropped" if success else "✗ Drop failed")

    def test_drop_item(self):
        """
        Drops all items with ID.
        """
        osrs = self.init_osrs()

        item_id = int(input("Item ID to drop: "))
        print(f"\nDropping all items with ID {item_id}...")
        drop_count = osrs.inventory.drop_all(item_id)
        print(f"✓ Dropped {drop_count} items" if drop_count > 0 else "✗ No items dropped")

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
        result = osrs.bank.open()
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
        result = osrs.bank.deposit_all()
        print(f"Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
    def test_banking_close(self):
        """Close bank."""
        osrs = self.init_osrs()
        print("\nClosing bank...")
        result = osrs.bank.close()
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
        result = osrs.bank.search("iron")
        print(f"Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
    def test_banking_find(self):
        """Find bank with camera rotation."""
        osrs = self.init_osrs()
        print("\nFinding bank...")
        bank_polygon = osrs.bank.find()
        
        if bank_polygon:
            # Get a random point from the polygon to display
            point = bank_polygon.random_point_inside(osrs.window.GAME_AREA)
            print(f"✓ Bank found (Polygon with {len(bank_polygon.points)} points)")
            print(f"  Sample point: ({point[0]}, {point[1]})")
        else:
            print("✗ Bank not found")
    
    def test_banking_withdraw_item(self):
        """Withdraw item from bank."""
        osrs = self.init_osrs()
        iface = self.init_interfaces()
        
        if not self.ensure_window():
            return
        
        if not iface.is_bank_open():
            print("\n✗ Bank is not open! Open it first.")
            return
        
        # Test with iron ore (item ID 440)
        item_id_input = input("Enter item ID to withdraw (e.g., 440 for Iron ore): ").strip()
        quantity_input = input("Enter quantity to withdraw (e.g., 1, 5, 10, All): ").strip()

        # Validate item_id and quantity
        try:
            item_id = int(item_id_input)
        except ValueError:
            print("✗ Invalid item ID (must be a number)")
            return
        
        # Validate quantity
        if quantity_input.lower() == 'all':
            quantity = 'All'
        else:
            try:
                quantity = int(quantity_input)
                if quantity <= 0:
                    print("✗ Invalid quantity (must be positive)")
                    return
            except ValueError:
                print("✗ Invalid quantity (must be a number or 'All')")
                return
        
        result = osrs.bank.withdraw_item(item_id, quantity)
        print(f"Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
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
    
    def test_gameobject_find_bank_api(self):
        """Find bank booth via api"""
        api = self.init_api()
        osrs = self.init_osrs()

        bank_booth = api.get_entity_in_viewport(10583, "object")
        print(f"\n Bank booth data: {bank_booth}")
        if bank_booth:
            x = bank_booth.get('x', -1)
            y = bank_booth.get('y', -1)
            print(f"\n✓ Found bank booth at ({x}, {y})")
            osrs.window.move_mouse_to((x, y))
            
    def test_gameobject_find_api(self):
        """Find bank booth via api"""
        api = self.init_api()
        osrs = self.init_osrs()

        try:
            id_input = input("\nEnter object id (e.g., 10583): ").strip()
            if not id_input:
                print("✗ No id entered, cancelling")
                return
            obj_id = int(id_input, 0)
        except ValueError:
            print("✗ Invalid object id")
            return
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        

        game_object = api.get_entity_in_viewport(obj_id, "object")
        print(f"\n Game Object data: {game_object}")
        if game_object:
            x = game_object.get('x', -1)
            y = game_object.get('y', -1)
            print(f"\n✓ Found {obj_id} at ({x}, {y})")
            osrs.window.move_mouse_to((x, y))
            import time
            time.sleep(1)
            print("Moving mouse around hull")
            hull = game_object.get('hull')
            if hull and hull.get('exists', False) == True:
                points = hull.get('points', [])
                polygon = Polygon(points)
                for point in points:
                    osrs.window.move_mouse_to((point.get('x'), point.get('y')))
                    time.sleep(0.2)
                # for _ in range(5):
                #     rand = polygon.random_point_inside(osrs.window.GAME_AREA)
                #     osrs.window.move_mouse_to(rand)
                #     time.sleep(0.5)

    def test_npc_find_api(self):
        """Find NPC api"""
        api = self.init_api()
        osrs = self.init_osrs()

        try:
            id_input = input("\nEnter NPC id (e.g., 10583): ").strip()
            if not id_input:
                print("✗ No id entered, cancelling")
                return
            npc_id = int(id_input, 0)
        except ValueError:
            print("✗ Invalid NPC id")
            return
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        

        npc_object = api.get_entity_in_viewport(npc_id, "npc")
        print(f"\n NPC data: {npc_object}")
        if npc_object:
            x = npc_object.get('x', -1)
            y = npc_object.get('y', -1)
            print(f"\n✓ Found {npc_id} at ({x}, {y})")
            osrs.window.move_mouse_to((x, y))
            import time
            time.sleep(.1)
            print("Moving mouse around hull")
            hull = npc_object.get('hull')
            if hull and hull.get('exists', False) == True:
                points = hull.get('points', [])
                polygon = Polygon(points)
                for point in points:
                    osrs.window.move_mouse_to((point.get('x'), point.get('y')))
                    time.sleep(0.1)
                # for _ in range(5):
                #     rand = polygon.random_point_inside(osrs.window.GAME_AREA)
                #     osrs.window.move_mouse_to(rand)
                #     time.sleep(0.5)

    def test_click_on_npc(self):
        """Clicks on a given NPC"""
        osrs = self.init_osrs()

        try:
            id_input = input("\nEnter NPC id (e.g., 10583): ").strip()
            if not id_input:
                print("✗ No id entered, cancelling")
                return
            npc_id = int(id_input, 0)
            action = input("Enter action (default 'Talk-to'): ").strip()
            if not action:
                print("No action entered, cancelling'")
                return
        except ValueError:
            print("✗ Invalid NPC id")
            return
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        print(f"\nClicking on NPC id {npc_id}...")
        success = osrs.click_entity(npc_id, "npc", action)
        print("✓ Click successful" if success else "✗ Click failed")

    def test_click_on_gameobject(self):
        """Clicks on a given game object"""
        osrs = self.init_osrs()

        try:
            id_input = input("\nEnter object id (e.g., 10583): ").strip()
            if not id_input:
                print("✗ No id entered, cancelling")
                return
            obj_id = int(id_input, 0)
            action = input("Enter action (default 'Talk-to'): ").strip()
            if not action:
                print("No action entered, cancelling'")
                return
        except ValueError:
            print("✗ Invalid object id")
            return
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        print(f"\nClicking on game object id {obj_id}...")
        success = osrs.click_entity(obj_id, "object", action)
        print("✓ Click successful" if success else "✗ Click failed")

    def test_find_nearest_by_id(self):
        """Find nearest game object or NPC by ID and display world coordinates."""
        api = self.init_api()

        try:
            id_input = input("\nEnter object/NPC ID (e.g., 10583 for bank or 1 for man): ").strip()
            if not id_input:
                print("✗ No ID entered, cancelling")
                return
            entity_id = int(id_input, 0)
            
            type_input = input("Enter entity type (npc/object): ").strip().lower()
            if type_input not in ["npc", "object"]:
                print("✗ Invalid type, must be 'npc' or 'object'")
                return
        except ValueError:
            print("✗ Invalid ID format")
            return
        except Exception as e:
            print(f"✗ Error: {e}")
            return

        print(f"\nSearching for nearest {type_input} with ID {entity_id}...")
        result = api.get_nearest_by_id(entity_id, type_input)
        
        if not result:
            print("✗ API request failed")
            return
        
        if result.get('found'):
            entity_type = result.get('type', 'unknown')
            world_x = result.get('worldX')
            world_y = result.get('worldY')
            plane = result.get('plane')
            distance = result.get('distance')
            
            print(f"\n✓ Found {entity_type.upper()} with ID {entity_id}")
            if entity_type == 'npc':
                name = result.get('name')
                print(f"  Name: {name}")
            print(f"  World Coordinates: ({world_x}, {world_y}, {plane})")
            print(f"  Distance: {distance} tiles")
        else:
            print(f"\n✗ No entity with ID {entity_id} found in area")

    def test_find_entity(self):
        """Test find_entity method that checks viewport and adjusts camera if needed."""
        osrs = self.init_osrs()

        try:
            id_input = input("\nEnter object/NPC ID (e.g., 10583 for bank or 1 for man): ").strip()
            if not id_input:
                print("✗ No ID entered, cancelling")
                return
            entity_id = int(id_input, 0)
            
            type_input = input("Enter entity type (npc/object): ").strip().lower()
            if type_input not in ["npc", "object"]:
                print("✗ Invalid type, must be 'npc' or 'object'")
                return
        except ValueError:
            print("✗ Invalid ID format")
            return
        except Exception as e:
            print(f"✗ Error: {e}")
            return

        print(f"\n{'='*60}")
        print(f"Finding {type_input} with ID {entity_id}...")
        print(f"{'='*60}\n")
        
        entity = osrs.find_entity(entity_id, type_input)
        
        if entity:
            print(f"\n{'='*60}")
            print(f"✓ SUCCESS - {type_input.upper()} FOUND IN VIEWPORT")
            print(f"{'='*60}")
            print(f"Entity data: {entity}")
            
            # Prompt for click action
            try:
                action = input("\nEnter action (e.g., 'Mine', 'Bank', 'Talk-to', or press Enter to skip): ").strip()
                if not action:
                    print("✗ No action entered, skipping click")
                    return
                
                print(f"\n{'='*60}")
                print(f"Attempting to click: {action} on {type_input} {entity_id}")
                print(f"{'='*60}\n")
                
                # Click the entity
                success = osrs.click_entity(entity, type_input, action)
                
                if success:
                    print(f"\n✓ Click successful")
                else:
                    print(f"\n✗ Click failed")
                    
            except KeyboardInterrupt:
                print("\n✗ Click cancelled")
            except Exception as e:
                print(f"✗ Click error: {e}")
        else:
            print(f"\n{'='*60}")
            print(f"✗ FAILED - Could not find {type_input} with ID {entity_id}")
            print(f"{'='*60}")

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
        print(f"  Enabled:              {status['enabled']}")
        print(f"  Actions:              {status['actions_performed']}")
        print(f"  Fatigue:              {status['fatigue_level']}")
        print(f"  Next idle break (m):  {status['next_idle_break_in_minutes']}")
        print(f"  Next logout break (m):{status['next_logout_break_in_minutes']}")
    
    def test_antiban_break(self):
        """Simulate 5-second idle break."""
        ab = self.init_anti_ban()
        print("\nSimulating 5-second idle break...")
        
        from core.anti_ban import BreakSchedule
        ab.next_break = BreakSchedule(
            start_time=time.time(),
            duration=5.0,
            break_type="idle",
            reason="manual_test"
        )
        ab.take_break("idle")
        print("✓ Idle break complete")
    
    def test_antiban_tab_switch(self):
        """Test tab switching."""
        ab = self.init_anti_ban()
        print("\nPerforming random idle action (may switch tabs)...")
        ab.perform_idle_action()
        print("✓ Done")
    
    def test_antiban_logout_break(self):
        """Test logout break functionality."""
        ab = self.init_anti_ban()
        print("\n[Logout Break Test]")
        print("WARNING: This will log you out for 10 seconds, then log back in.")
        print("Make sure you are logged in and have credentials in profile!\n")
        
        response = input("Continue? (y/n): ").strip().lower()
        if response != 'y':
            print("Test cancelled.")
            return
        
        print("\nSimulating 10-second logout break...")
        
        from core.anti_ban import BreakSchedule
        ab.next_logout_break = BreakSchedule(
            start_time=time.time(),
            duration=10.0,
            break_type="logout",
            reason="test_logout_break"
        )
        ab._take_logout_break()
        print("✓ Logout break test complete")
    
    # =================================================================
    # LOGIN/AUTHENTICATION TESTS
    # =================================================================
    
    def test_login(self):
        """Test login functionality."""
        print("\n[Login Test]")
        print("WARNING: This will attempt to log into the game.")
        print("Make sure you are at the login screen!")
        
        # Get password from user input
        try:
            username = input("\nEnter username: ").strip()
            password = input("\nEnter password (or press Ctrl+C to cancel): ").strip()
            
            if not username:
                print("✗ No username entered")
                return
            if not password:
                print("✗ No password entered")
                return
            
            osrs = self.init_osrs()
            print("\nAttempting login...")
            result = osrs.login(username, password)
            
            if result:
                print("✓ Login successful!")
            else:
                print("✗ Login failed")
                
        except KeyboardInterrupt:
            print("\n✗ Login test cancelled")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def test_login_from_profile(self):
        """Test login using password from profile."""
        print("\n[Login from Profile Test]")
        print("WARNING: This will attempt to log into the game.")
        print("Make sure you are at the login screen!")
        print("Password will be loaded from profile configuration.")
        
        try:
            confirm = input("\nContinue? (y/n): ").strip().lower()
            if confirm != 'y':
                print("✗ Login test cancelled")
                return
            
            config = self.init_config()
            
            # Create OSRS instance with profile
            from client.osrs import OSRS
            osrs = OSRS(profile_config=config)
            
            print("\nAttempting login from profile...")
            result = osrs.login_from_profile()
            
            if result:
                print("✓ Login successful!")
            else:
                print("✗ Login failed - check password in profile")
                
        except KeyboardInterrupt:
            print("\n✗ Login test cancelled")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def test_logout(self):
        """Test logout functionality."""
        print("\n[Logout Test]")
        print("WARNING: This will log you out of the game.")
        print("Make sure you are logged in!")
        
        try:
            confirm = input("\nContinue? (y/n): ").strip().lower()
            if confirm != 'y':
                print("✗ Logout test cancelled")
                return
            
            osrs = self.init_osrs()
            print("\nAttempting logout...")
            result = osrs.logout()
            
            if result:
                print("✓ Logout successful!")
            else:
                print("✗ Logout failed - check if logout panel opened")
                
        except KeyboardInterrupt:
            print("\n✗ Logout test cancelled")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def test_is_at_login_screen(self):
        """Test if currently at login screen."""
        print("\n[Check Login Screen Test]")
        
        try:
            osrs = self.init_osrs()
            print("\nChecking if at login screen...")
            result = osrs.is_at_login_screen()
            
            if result:
                print("✓ At login screen!")
            else:
                print("✗ Not at login screen")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
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
            'm': ("Move mouse to position", self.test_move_mouse_to),
            'f': ("Find Color", self.test_find_color),
            'r': ("Camera Rotation", self.test_camera_rotation),
            'k': ("Click at Position", self.test_click_at_position),
            'v': ("Test viewport bounds", self.test_viewport_bounds),
            't': ("Test mouse against API Canvas", self.test_mouse_against_api),
            's': ("Find right click menu", self.test_gameobject_right_click),
        }
        
        print("\n" + "="*60)
        print("WINDOW & COLOR DETECTION TESTS")
        print("="*60)
        print("W - Window Info")
        print("C - Capture Screenshot")
        print("M - Move Mouse To Position")
        print("F - Find Color (input RGB)")
        print("R - Camera Rotation")
        print("K - Click at Position")
        print("V - Test viewport bounds")
        print("T - Test mouse against API Canvas")
        print("S - Find right click menu")
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
            'c': ("Click inventory item", self.test_click_inventory_item),
            'i': ("Inventory Status", self.test_inventory_status),
            'o': ("Check if Open", self.test_inventory_open_check),
            't': ("Test slot regions", self.test_inventory_regions),
            '1': ("Click Slot 0", self.test_click_inventory_slot),
            '3': ("Find Item by Color", self.test_find_inventory_item),
            's': ("Drop Slot", self.test_drop_slot),
            'd': ("Drop all items", self.test_drop_item)
        }
        
        print("\n" + "="*60)
        print("INVENTORY MODULE TESTS")
        print("="*60)
        print("C - Click inventory item")
        print("I - Inventory Status")
        print("O - Check if Open")
        print("T - Test slot regions")
        print("1 - Click Slot")
        print("3 - Find Item by Color")
        print("S - Drop Slot")
        print("D - Drop all items by ID")
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
            'w': ("Withdraw Item", self.test_banking_withdraw_item),
        }
        
        print("\n" + "="*60)
        print("BANKING MODULE TESTS")
        print("="*60)
        print("O - Open Bank")
        print("D - Deposit All")
        print("C - Close Bank")
        print("S - Search Bank (for 'iron')")
        print("F - Find Bank (with camera)")
        print("W - Withdraw Item (Iron ore)")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def run_gameobject_tests(self):
        """Run game object testing menu."""
        self.current_menu = "gameobject"
        
        test_map = {
            's': ("Find Game Object via ID", self.test_gameobject_find_api),
            'c': ("Click on Game Object via ID", self.test_click_on_gameobject),
            'l': ("Find NPC via ID", self.test_npc_find_api),
            'k': ("Click on NPC via ID", self.test_click_on_npc),
            'n': ("Find Nearest by ID (World Coords)", self.test_find_nearest_by_id),
            'f': ("Find Entity (Viewport + Camera Adjust)", self.test_find_entity),
            '1': ("Find Iron Ore", self.test_gameobject_find_ore),
            '2': ("Interact with Ore", self.test_gameobject_interact_ore),
            '3': ("Find Bank Booth", self.test_gameobject_find_bank),
            'e': ("Find Bank Booth (api)", self.test_gameobject_find_bank_api),
            '4': ("Find Custom Color", self.test_gameobject_custom_color),
            '5': ("Right-Click Menu", self.test_gameobject_right_click),
            '6': ("Find NPCS in Viewport", self.test_npc_in_viewport),
            '7': ("Find Game Objects in Viewport", self.test_game_object_in_viewport),
            '8': ("Find in Viewport (with rotation)", self.test_find_in_viewport_with_rotation)
        }
        
        print("\n" + "="*60)
        print("GAME OBJECT INTERACTION TESTS")
        print("="*60)
        print("S - Find Game Object by ID")
        print("C - Click on Game Object by ID")
        print("L - Find NPC by ID")
        print("K - Click on NPC by ID")
        print("N - Find Nearest by ID (World Coords)")
        print("F - Find Entity (Viewport + Camera Adjust) [NEW]")
        print("1 - Find Iron Ore")
        print("2 - Interact with Ore")
        print("3 - Find Bank Booth")
        print("e - Find Bank Booth (API)")
        print("4 - Find Custom Color")
        print("5 - Right-Click Menu Test")
        print("6 - Find NPCS in Viewport")
        print("7 - Find Game Objects in Viewport")
        print("8 - Find in Viewport (with rotation)")
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
            'l': ("Logout Break", self.test_antiban_logout_break),
        }
        
        print("\n" + "="*60)
        print("ANTI-BAN SYSTEM TESTS")
        print("="*60)
        print("I - Perform Idle Action")
        print("C - Random Camera Movement")
        print("S - Check Status")
        print("B - Simulate 5s Idle Break")
        print("T - Test Tab Switching")
        print("L - Test Logout Break (10s)")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    def run_login_tests(self):
        """Run login testing menu."""
        self.current_menu = "login"
        
        test_map = {
            '1': ("Login with Password", self.test_login),
            '2': ("Login from Profile", self.test_login_from_profile),
            '3': ("Logout", self.test_logout),
            '4': ("Check Login Screen", self.test_is_at_login_screen),
        }
        
        print("\n" + "="*60)
        print("LOGIN/AUTHENTICATION TESTS")
        print("="*60)
        print("1 - Login with Password (manual input)")
        print("2 - Login from Profile (uses config)")
        print("3 - Logout (logs out of game)")
        print("4 - Check if at Login Screen")
        print("\nWARNING: Make sure you are at the appropriate screen!")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    # =================================================================
    # PATHFINDING TESTS
    # =================================================================
    
    def test_pathfinding_stats(self):
        """Display pathfinding system statistics."""
        nav = self.init_navigation()
        
        print("\nPathfinding System Statistics:")
        print("-" * 60)
        
        stats = nav.get_pathfinding_stats()
        
        print(f"Pathfinding Enabled: {stats.get('pathfinding_enabled', False)}")
        print(f"Variance Level: {stats.get('variance_level', 'N/A')}")
        
        if 'collision_map' in stats:
            cm_stats = stats['collision_map']
            print(f"\nCollision Map:")
            print(f"  Cached Regions: {cm_stats.get('cached_regions', 0)} / {cm_stats.get('max_cache_size', 0)}")
            print(f"  Cache Utilization: {cm_stats.get('cache_utilization', 0):.1f}%")
        
        if 'pathfinder' in stats:
            pf_stats = stats['pathfinder']
            print(f"\nPathfinder:")
            print(f"  Cached Paths: {pf_stats.get('cached_paths', 0)} / {pf_stats.get('max_cache_size', 0)}")
            print(f"  Cache Hits: {pf_stats.get('cache_hits', 0)}")
            print(f"  Cache Misses: {pf_stats.get('cache_misses', 0)}")
            print(f"  Hit Rate: {pf_stats.get('hit_rate_percent', 0):.1f}%")
    
    def test_collision_detection(self):
        """Test collision detection at current location."""
        nav = self.init_navigation()
        
        print("\nTesting collision detection...")
        
        # Ensure pathfinding is loaded
        if not nav._ensure_pathfinding_loaded():
            print("✗ Pathfinding not available")
            return
        
        # Get current position
        pos = nav.read_world_coordinates()
        if not pos:
            print("✗ Could not read coordinates")
            return
        
        x, y = pos
        z = 0  # Assume ground level
        
        print(f"Position: ({x}, {y}, {z})")
        print("-" * 60)
        
        from util.collision_util import CollisionMap
        collision_map = CollisionMap()
        
        # Check all 8 directions
        directions = {
            "North": collision_map.can_move_north,
            "South": collision_map.can_move_south,
            "East": collision_map.can_move_east,
            "West": collision_map.can_move_west,
            "NE": collision_map.can_move_northeast,
            "NW": collision_map.can_move_northwest,
            "SE": collision_map.can_move_southeast,
            "SW": collision_map.can_move_southwest
        }
        
        for direction, check_func in directions.items():
            can_move = check_func(x, y, z)
            status = "✓ Walkable" if can_move else "✗ Blocked"
            print(f"{direction:6} {status}")
        
        # Check if tile itself is blocked
        if collision_map.is_tile_blocked(x, y, z):
            print("\n⚠ Current tile is completely blocked!")
        
        # Show walkable neighbors
        neighbors = collision_map.get_walkable_neighbors(x, y, z)
        print(f"\nWalkable neighbors: {len(neighbors)}")
    
    def test_pathfinding_calculation(self):
        """Test pathfinding calculation performance."""
        nav = self.init_navigation()
        
        print("\nTesting pathfinding calculation...")
        
        # Ensure pathfinding is loaded
        if not nav._ensure_pathfinding_loaded():
            print("✗ Pathfinding not available")
            return
        
        # Get current position
        pos = nav.read_world_coordinates()
        if not pos:
            print("✗ Could not read coordinates")
            return
        
        x, y = pos
        z = 0
        
        # Test distances: 5, 10, 20, 50 tiles
        test_distances = [5, 10, 20, 50]
        
        from client.pathfinder import VariancePathfinder
        from util.collision_util import CollisionMap
        
        pathfinder = VariancePathfinder(CollisionMap())
        
        print(f"Starting position: ({x}, {y}, {z})")
        print("-" * 60)
        
        for distance in test_distances:
            # Test north
            goal = (x, y + distance, z)
            
            import time
            start_time = time.time()
            path = pathfinder.find_path((x, y, z), goal, variance_level="moderate")
            elapsed = time.time() - start_time
            
            if path:
                print(f"{distance:2} tiles: {len(path):3} waypoints in {elapsed*1000:.1f}ms")
            else:
                print(f"{distance:2} tiles: No path found")
    
    def test_path_variance(self):
        """Visualize path variance by generating multiple paths."""
        nav = self.init_navigation()
        
        print("\nTesting path variance (generating 5 paths)...")
        
        # Ensure pathfinding is loaded
        if not nav._ensure_pathfinding_loaded():
            print("✗ Pathfinding not available")
            return
        
        # Get current position
        pos = nav.read_world_coordinates()
        if not pos:
            print("✗ Could not read coordinates")
            return
        
        x, y = pos
        z = 0
        
        # Target: 20 tiles northeast
        goal = (x + 20, y + 20, z)
        
        from client.pathfinder import VariancePathfinder
        from util.collision_util import CollisionMap
        
        pathfinder = VariancePathfinder(CollisionMap())
        
        print(f"Start: ({x}, {y})")
        print(f"Goal: {goal}")
        print("-" * 60)
        
        # Clear cache to force new calculations
        pathfinder.clear_cache()
        
        paths = []
        for i in range(5):
            path = pathfinder.find_path((x, y, z), goal, variance_level="moderate", use_cache=False)
            if path:
                paths.append(path)
                print(f"Path {i+1}: {len(path)} waypoints")
            else:
                print(f"Path {i+1}: No path found")
        
        # Analyze variance
        if len(paths) > 1:
            print("\nVariance Analysis:")
            lengths = [len(p) for p in paths]
            print(f"  Length range: {min(lengths)}-{max(lengths)} waypoints")
            
            # Check if paths are actually different
            unique_paths = len(set(tuple(p) for p in paths))
            print(f"  Unique paths: {unique_paths} / {len(paths)}")
            
            if unique_paths == len(paths):
                print("  ✓ All paths are unique (good variance)")
            else:
                print("  ⚠ Some paths are identical (increase variance)")
    
    def test_walk_with_pathfinding(self):
        """Walk a short distance using pathfinding."""
        nav = self.init_navigation()
        
        print("\nWalking with pathfinding (+10 tiles north)...")
        
        # Get current position
        pos = nav.read_world_coordinates()
        if not pos:
            print("✗ Could not read coordinates")
            return
        
        x, y = pos
        target_x = x
        target_y = y + 10
        
        print(f"From: ({x}, {y})")
        print(f"To: ({target_x}, {target_y})")
        print("\nStarting walk (using pathfinding)...")
        
        success = nav.walk_to_tile(target_x, target_y, plane=0, use_pathfinding=True)
        
        if success:
            print("✓ Walk completed successfully")
        else:
            print("✗ Walk failed")
    
    def test_walk_without_pathfinding(self):
        """Walk a short distance using linear navigation."""
        nav = self.init_navigation()
        
        print("\nWalking without pathfinding (+10 tiles north)...")
        
        # Get current position
        pos = nav.read_world_coordinates()
        if not pos:
            print("✗ Could not read coordinates")
            return
        
        x, y = pos
        target_x = x
        target_y = y + 10
        
        print(f"From: ({x}, {y})")
        print(f"To: ({target_x}, {target_y})")
        print("\nStarting walk (linear path)...")
        
        success = nav.walk_to_tile(target_x, target_y, plane=0, use_pathfinding=False)
        
        if success:
            print("✓ Walk completed successfully")
        else:
            print("✗ Walk failed")
    
    def test_clear_path_cache(self):
        """Clear the pathfinding cache."""
        nav = self.init_navigation()
        
        print("\nClearing path cache...")
        nav.clear_path_cache()
        print("✓ Cache cleared")
        
        # Show stats
        stats = nav.get_pathfinding_stats()
        if 'pathfinder' in stats:
            pf_stats = stats['pathfinder']
            print(f"Cached paths: {pf_stats.get('cached_paths', 0)}")
    
    def test_custom_coordinates_pathfinding(self):
        """Test pathfinding from current position to custom world coordinates."""
        nav = self.init_navigation()
        
        print("\nCustom Coordinate Pathfinding Test")
        print("="*60)
        
        # Ensure pathfinding is loaded
        if not nav._ensure_pathfinding_loaded():
            print("✗ Pathfinding not available")
            return
        
        # Get current position as start
        current_pos = nav.read_world_coordinates()
        if not current_pos:
            print("✗ Could not read current position")
            return
        
        start_x, start_y = current_pos
        print(f"Start position: ({start_x}, {start_y})")
        print("-"*60)
        
        # Get goal coordinates
        try:
            goal_input = input(f"Enter goal coordinates (x,y): ").strip()
            if not goal_input:
                print("✗ Goal coordinates required")
                return
            
            goal_parts = goal_input.split(',')
            goal_x = int(goal_parts[0].strip())
            goal_y = int(goal_parts[1].strip())
            
            start_z = int(input(f"Enter plane (0-3) [default 0]: ").strip() or "0")
            goal_z = start_z  # Same plane unless otherwise needed
            
            # Get variance level
            print("\nVariance levels: conservative, moderate, aggressive")
            variance = input("Enter variance level [default moderate]: ").strip() or "moderate"
            
        except (ValueError, IndexError) as e:
            print(f"✗ Invalid input: {e}")
            return
        
        print("\n" + "="*60)
        print(f"Start: ({start_x}, {start_y}, {start_z})")
        print(f"Goal:  ({goal_x}, {goal_y}, {goal_z})")
        print(f"Variance: {variance}")
        print("="*60)
        
        # Calculate path
        from client.pathfinder import VariancePathfinder
        from util.collision_util import CollisionMap
        
        pathfinder = VariancePathfinder(CollisionMap())
        
        import time
        start_time = time.time()
        path = pathfinder.find_path(
            (start_x, start_y, start_z),
            (goal_x, goal_y, goal_z),
            variance_level=variance,
            use_cache=False
        )
        elapsed = time.time() - start_time
        
        if path:
            print(f"✓ Path found: {len(path)} waypoints in {elapsed*1000:.1f}ms")
            
            # Calculate distance
            dx = goal_x - start_x
            dy = goal_y - start_y
            straight_line = (dx**2 + dy**2)**0.5
            
            print(f"Straight-line distance: {straight_line:.1f} tiles")
            print(f"Path efficiency: {straight_line/len(path)*100:.1f}%")
            
            # Show first/last few waypoints
            print("\nFirst 5 waypoints:")
            for i, (x, y, z) in enumerate(path[:5]):
                print(f"  {i+1}. ({x}, {y}, {z})")
            
            if len(path) > 10:
                print("  ...")
                print(f"Last 5 waypoints:")
                for i, (x, y, z) in enumerate(path[-5:], len(path)-4):
                    print(f"  {i}. ({x}, {y}, {z})")
            elif len(path) > 5:
                print(f"Remaining waypoints:")
                for i, (x, y, z) in enumerate(path[5:], 6):
                    print(f"  {i}. ({x}, {y}, {z})")
            
            # Ask if user wants to walk the path
            walk_input = input("\nExecute this path? (y/n): ").strip().lower()
            if walk_input == 'y':
                print("\nExecuting path...")
                success = nav.walk_to_tile(goal_x, goal_y, plane=goal_z, use_pathfinding=True)
                if success:
                    print("✓ Walk completed successfully")
                else:
                    print("✗ Walk failed or interrupted")
        else:
            print(f"✗ No path found (searched for {elapsed*1000:.1f}ms)")
            print("Possible reasons:")
            print("  - Goal is unreachable (blocked by obstacles)")
            print("  - Goal is too far (>100 tiles)")
            print("  - Different planes with no connection")
    
    def run_pathfinding_tests(self):
        """Run pathfinding testing menu."""
        self.current_menu = "pathfinding"
        
        test_map = {
            's': ("Pathfinding Statistics", self.test_pathfinding_stats),
            'c': ("Collision Detection", self.test_collision_detection),
            'p': ("Path Calculation Performance", self.test_pathfinding_calculation),
            'v': ("Path Variance Test", self.test_path_variance),
            'w': ("Walk with Pathfinding", self.test_walk_with_pathfinding),
            'l': ("Walk without Pathfinding", self.test_walk_without_pathfinding),
            'i': ("Custom Coordinates Input", self.test_custom_coordinates_pathfinding),
            'x': ("Clear Path Cache", self.test_clear_path_cache),
        }
        
        print("\n" + "="*60)
        print("PATHFINDING TESTS")
        print("="*60)
        print("S - Show Pathfinding Statistics")
        print("C - Test Collision Detection (current position)")
        print("P - Path Calculation Performance (various distances)")
        print("V - Path Variance Test (generate 5 paths)")
        print("W - Walk with Pathfinding (+10 north)")
        print("L - Walk without Pathfinding (+10 north)")
        print("I - Custom Coordinates Input (test any path)")
        print("X - Clear Path Cache")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    # =================================================================
    # NAVIGATION TESTS
    # =================================================================
    
    def test_read_coordinates(self):
        """Read and display current world coordinates."""
        nav = self.init_navigation()
        
        print("\nReading coordinates...")
        world_coords = nav.read_world_coordinates()
        scene_coords = nav.read_scene_coordinates()
        
        if world_coords:
            print(f"✓ World coordinates: {world_coords}")
        else:
            print("✗ Could not read world coordinates")
        
        if scene_coords:
            print(f"✓ Scene coordinates: {scene_coords}")
        else:
            print("✗ Could not read scene coordinates")
    
    def test_read_camera_yaw(self):
        """Read and display current camera yaw angle."""
        nav = self.init_navigation()
        
        print("\nReading camera yaw...")
        yaw = nav.read_camera_yaw()
        
        if yaw is not None:
            print(f"✓ Camera yaw: {yaw} / 2048")
            # Convert to degrees for reference (counter-clockwise from north)
            degrees = (yaw / 2048) * 360
            print(f"  ({degrees:.1f}° counter-clockwise from north)")
            # 8-direction cardinal direction
            direction = nav.get_cardinal_direction(yaw)
            print(f"  Facing: {direction}")
        else:
            print("✗ Could not read camera yaw")
    
    def test_click_compass_to_north(self):
        """Test clicking compass to reset camera to north."""
        nav = self.init_navigation()
        
        print("\nTesting compass click to reset to north...")
        
        # Show current direction
        yaw_before = nav.read_camera_yaw()
        if yaw_before is not None:
            direction_before = nav.get_cardinal_direction(yaw_before)
            print(f"Before: Yaw = {yaw_before}, Facing {direction_before}")
        else:
            print("Before: Could not read yaw")
        
        # Click compass
        if nav.click_compass_to_north():
            print("✓ Compass clicked successfully")
            
            # Show new direction
            yaw_after = nav.read_camera_yaw()
            if yaw_after is not None:
                direction_after = nav.get_cardinal_direction(yaw_after)
                print(f"After: Yaw = {yaw_after}, Facing {direction_after}")
            else:
                print("After: Could not read yaw")
        else:
            print("✗ Compass click failed")
    
    def test_player_moving(self):
        """Check if player is currently moving."""
        nav = self.init_navigation()
        
        print("\nChecking player movement...")
        print("(This takes ~0.6 seconds)")
        
        is_moving = nav.is_player_moving()
        
        if is_moving:
            print("✓ Player is MOVING")
        else:
            print("✓ Player is STATIONARY")
    
    def test_minimap_offset_click(self):
        """Test clicking minimap with tile offsets."""
        nav = self.init_navigation()
        
        print("\nMinimap offset click test")
        print("Enter tile offsets to click (e.g., '5,3' for 5 east, 3 north)")
        print("Or press ESC to cancel")
        
        # Simple input simulation - in real use would need proper input
        print("\nTesting with offset: +5 tiles east, +5 tiles north")
        
        current = nav.read_world_coordinates()
        if current:
            print(f"Current position: {current}")
            print(f"Target: ({current[0]+5}, {current[1]+5})")
            
            if nav._click_minimap_offset(5, 5):
                print("✓ Minimap click executed")
            else:
                print("✗ Minimap click failed (out of bounds?)")
        else:
            print("✗ Could not read current position")
    
    def test_walk_to_coordinates(self):
        """Walk to absolute world coordinates."""
        nav = self.init_navigation()
        
        print("\nWalk to coordinates test")
        current = nav.read_world_coordinates()
        
        if not current:
            print("✗ Could not read current position")
            return
        
        print(f"Current position: {current}")
        print("\nTest: Walking 10 tiles north")
        
        target_x = current[0]
        target_y = current[1] + 10
        
        print(f"Target: ({target_x}, {target_y})")
        print("Starting walk...\n")
        
        success = nav.walk_to_tile(target_x, target_y)
        
        if success:
            print("\n✓ Successfully reached target!")
            final_pos = nav.read_world_coordinates()
            if final_pos:
                print(f"Final position: {final_pos}")
        else:
            print("\n✗ Failed to reach target")
    
    def test_long_distance_walk(self):
        """Test long distance walking with waypoint chunking."""
        nav = self.init_navigation()
        
        print("\nLong distance walk test")
        current = nav.read_world_coordinates()
        
        if not current:
            print("✗ Could not read current position")
            return
        
        print(f"Current position: {current}")
        print("\nTest: Walking 25 tiles northeast (should chunk into waypoints)")
        
        target_x = current[0] + 18
        target_y = current[1] + 18
        
        print(f"Target: ({target_x}, {target_y})")
        print("Starting walk...\n")
        
        success = nav.walk_to_tile(target_x, target_y)
        
        if success:
            print("\n✓ Successfully completed long distance walk!")
            final_pos = nav.read_world_coordinates()
            if final_pos:
                print(f"Final position: {final_pos}")
        else:
            print("\n✗ Failed to complete walk")
    
    def test_stuck_detection(self):
        """Test stuck detection system."""
        nav = self.init_navigation()
        
        print("\nStuck detection test")
        print("Make sure player is NOT moving, then wait...")
        print("(Checking for 4 seconds)\n")
        
        for i in range(4):
            time.sleep(1)
            is_stuck = nav._is_stuck()
            print(f"Check {i+1}/4: {'STUCK' if is_stuck else 'Moving/Unknown'}")
        
        print("\n✓ Stuck detection test complete")
    
    def test_calibration_info(self):
        """Display calibration information."""
        nav = self.init_navigation()
        
        print("\nMinimap Scale Calibration")
        print(f"Current scale: {nav.minimap_scale} pixels/tile")
        print("\nCalibration procedure (not yet automated):")
        print("1. Note current world coordinates")
        print("2. Walk exactly N tiles in one direction")
        print("3. Measure pixel distance traveled on minimap")
        print("4. Calculate: pixels_traveled / tiles_traveled")
        print("5. Update nav.minimap_scale with result")
        print("\nFor now, scale is estimated at 4.0 pixels/tile")
    
    def test_rotate_camera_to_tile(self):
        """Test rotating camera to make a specific tile visible."""
        osrs = self.init_osrs()
        
        print("\n=== Rotate Camera to Tile Test ===")
        
        # Get current position
        coords_data = osrs.api.get_coords()
        if not coords_data:
            print("✗ Could not read current position")
            return
        
        current_x = coords_data['world']['x']
        current_y = coords_data['world']['y']
        current_plane = coords_data['world']['plane']
        
        print(f"Current position: ({current_x}, {current_y}, plane={current_plane})")
        
        # Prompt for target coordinates
        print("\nEnter target coordinates:")
        print(f"Press ENTER to test with default (+10, +10) from current position")
        print("Or type coordinates in format: x,y")
        print("Example: 3222,3218")
        
        try:
            coords_input = input("Coordinates: ").strip()
            
            if coords_input:
                # Parse custom coordinates
                parts = coords_input.split(',')
                target_x = int(parts[0].strip())
                target_y = int(parts[1].strip())
                target_plane = current_plane
                print(f"\nUsing custom coordinates: ({target_x}, {target_y})")
            else:
                # Use default offset
                target_x = current_x + 10
                target_y = current_y + 10
                target_plane = current_plane
                print(f"\nUsing default: +10 tiles east, +10 tiles north from current position")
        except (ValueError, IndexError) as e:
            print(f"✗ Invalid input format: {e}")
            print("Using default offset instead")
            target_x = current_x + 10
            target_y = current_y + 10
            target_plane = current_plane
        
        print(f"Target: ({target_x}, {target_y}, plane={target_plane})")
        
        # Show current camera state
        camera = osrs.api.get_camera()
        if camera:
            print(f"\nCurrent camera:")
            print(f"  Yaw: {camera.get('yaw')} / 2048")
            print(f"  Pitch: {camera.get('pitch')} / 512")
        
        # Get rotation calculation from API
        print("\nCalculating required rotation...")
        rotation_data = osrs.api.get_camera_rotation_to_tile(target_x, target_y, target_plane)
        
        if not rotation_data:
            print("✗ Failed to get rotation data from API")
            return
        
        print(f"\nRotation data from API:")
        print(f"  Tile currently visible: {rotation_data.get('visible')}")
        print(f"  Current yaw: {rotation_data.get('currentYaw')}")
        print(f"  Target yaw: {rotation_data.get('targetYaw')}")
        print(f"  Yaw distance: {rotation_data.get('yawDistance')} units ({rotation_data.get('direction')})")
        print(f"  Yaw pixels: ~{rotation_data.get('yawPixels')}px")
        print(f"  Current pitch: {rotation_data.get('currentPitch')}")
        print(f"  Target pitch: {rotation_data.get('targetPitch')}")
        print(f"  Pitch distance: {rotation_data.get('pitchDistance')} units ({rotation_data.get('pitchDirection')})")
        print(f"  Pitch pixels: ~{rotation_data.get('pitchPixels')}px")
        
        if rotation_data.get('visible'):
            print("\n✓ Tile is already visible! No rotation needed.")
            if 'screenX' in rotation_data and 'screenY' in rotation_data:
                print(f"  Screen position: ({rotation_data['screenX']}, {rotation_data['screenY']})")
            return
        
        # Execute rotation
        print("\nPress SPACE to execute rotation, or ESC to cancel")
        import keyboard
        while True:
            if keyboard.is_pressed('space'):
                print("\nExecuting rotation...")
                success = osrs.camera.set_camera_to_tile(target_x, target_y, target_plane)
                
                if success:
                    print("\n✓ Camera rotation successful! Tile is now visible.")
                    
                    # Show final camera state
                    final_camera = osrs.api.get_camera()
                    if final_camera:
                        print(f"\nFinal camera state:")
                        print(f"  Yaw: {final_camera.get('yaw')} / 2048")
                        print(f"  Pitch: {final_camera.get('pitch')} / 512")
                    
                    # Get final tile position
                    final_rotation = osrs.api.get_camera_rotation_to_tile(target_x, target_y, target_plane)
                    if final_rotation and final_rotation.get('visible'):
                        if 'screenX' in final_rotation and 'screenY' in final_rotation:
                            print(f"  Tile screen position: ({final_rotation['screenX']}, {final_rotation['screenY']})")
                else:
                    print("\n✗ Camera rotation failed. Tile is not visible.")
                
                break
            elif keyboard.is_pressed('esc'):
                print("\nCancelled.")
                break
            import time
            time.sleep(0.1)
    
    def test_camera_positioning(self):
        """Test new camera positioning system with various distances."""
        import keyboard
        import time
        
        osrs = self.init_osrs()
        
        print("\n" + "="*60)
        print("CAMERA POSITIONING TEST SUITE")
        print("="*60)
        print("\nThis tests the new CameraController system that positions")
        print("the camera to make specific world tiles visible.")
        print("\nSelect test:")
        print("1 - Near tile (3 tiles away)")
        print("2 - Medium tile (10 tiles away)")
        print("3 - Far tile (20 tiles away)")
        print("4 - Custom coordinates")
        print("5 - Extreme angle test (180° behind)")
        print("6 - Scale-only adjustment test")
        print("ESC - Cancel")
        print("="*60)
        
        test_choice = None
        while test_choice is None:
            if keyboard.is_pressed('1'):
                test_choice = 'near'
            elif keyboard.is_pressed('2'):
                test_choice = 'medium'
            elif keyboard.is_pressed('3'):
                test_choice = 'far'
            elif keyboard.is_pressed('4'):
                test_choice = 'custom'
            elif keyboard.is_pressed('5'):
                test_choice = 'extreme'
            elif keyboard.is_pressed('6'):
                test_choice = 'scale'
            elif keyboard.is_pressed('esc'):
                print("\nCancelled.")
                return
            time.sleep(0.1)
        
        time.sleep(0.3)  # Debounce
        
        # Get current player position
        coords = osrs.api.get_coords()
        if not coords or 'world' not in coords:
            print("\n✗ Failed to get player coordinates")
            return
        
        player_x = coords['world']['x']
        player_y = coords['world']['y']
        player_plane = coords['world']['plane']
        
        print(f"\nCurrent position: ({player_x}, {player_y}, plane={player_plane})")
        
        # Calculate target tile based on test choice
        if test_choice == 'near':
            target_x = player_x + 3
            target_y = player_y
            print("\nTarget: 3 tiles east (near distance)")
            print("Expected: High zoom (~600), steep pitch")
            
        elif test_choice == 'medium':
            target_x = player_x + 7
            target_y = player_y + 7
            print("\nTarget: 10 tiles northeast (medium distance)")
            print("Expected: Medium zoom (~450), moderate pitch")
            
        elif test_choice == 'far':
            target_x = player_x + 14
            target_y = player_y + 14
            print("\nTarget: 20 tiles northeast (far distance)")
            print("Expected: Low zoom (~350), shallow pitch")
            
        elif test_choice == 'extreme':
            target_x = player_x - 10
            target_y = player_y
            print("\nTarget: 10 tiles west (180° behind player)")
            print("Expected: Large yaw rotation, medium zoom/pitch")
            
        elif test_choice == 'scale':
            # Just test scale adjustment by targeting current tile
            target_x = player_x
            target_y = player_y
            print("\nTarget: Current tile (scale adjustment only)")
            print("Expected: Only zoom changes, no rotation")
            
        else:  # custom
            try:
                target_x = int(input("Enter target X coordinate: ").strip())
                target_y = int(input("Enter target Y coordinate: ").strip())
                print(f"\nTarget: ({target_x}, {target_y}, plane={player_plane})")
            except ValueError:
                print("\n✗ Invalid coordinates")
                return
        
        # Get camera state before
        camera_before = osrs.api.get_camera()
        if camera_before:
            print(f"\nCamera BEFORE:")
            print(f"  Yaw: {camera_before.get('yaw', 'N/A')}")
            print(f"  Pitch: {camera_before.get('pitch', 'N/A')}")
            print(f"  Scale: {camera_before.get('scale', 'N/A')}")
        
        # Check if tile is visible before adjustment
        rotation_data_before = osrs.api.get_camera_rotation(target_x, target_y, player_plane)
        if rotation_data_before:
            visible_before = rotation_data_before.get('visible', False)
            print(f"  Tile visible: {visible_before}")
        
        print("\nPress SPACE to start camera positioning, ESC to cancel")
        
        while True:
            if keyboard.is_pressed('space'):
                break
            elif keyboard.is_pressed('esc'):
                print("\nCancelled.")
                return
            time.sleep(0.1)
        
        time.sleep(0.3)  # Debounce
        
        # Execute camera positioning
        print("\nPositioning camera...")
        success = osrs.camera.set_camera_to_tile(target_x, target_y, player_plane)
        
        # Get camera state after
        camera_after = osrs.api.get_camera()
        if camera_after:
            print(f"\nCamera AFTER:")
            print(f"  Yaw: {camera_after.get('yaw', 'N/A')}")
            print(f"  Pitch: {camera_after.get('pitch', 'N/A')}")
            print(f"  Scale: {camera_after.get('scale', 'N/A')}")
        
        # Verify tile visibility
        rotation_data_after = osrs.api.get_camera_rotation(target_x, target_y, player_plane)
        if rotation_data_after:
            visible_after = rotation_data_after.get('visible', False)
            print(f"  Tile visible: {visible_after}")
            
            if rotation_data_after.get('screenX') and rotation_data_after.get('screenY'):
                screen_x = rotation_data_after['screenX']
                screen_y = rotation_data_after['screenY']
                print(f"  Screen position: ({screen_x}, {screen_y})")
        
        # Calculate changes
        if camera_before and camera_after:
            yaw_change = camera_after.get('yaw', 0) - camera_before.get('yaw', 0)
            pitch_change = camera_after.get('pitch', 0) - camera_before.get('pitch', 0)
            scale_change = camera_after.get('scale', 0) - camera_before.get('scale', 0)
            
            print(f"\nChanges:")
            print(f"  Yaw: {yaw_change:+d} units")
            print(f"  Pitch: {pitch_change:+d} units")
            print(f"  Scale: {scale_change:+d} units")
        
        # Result summary
        print(f"\n{'='*60}")
        if success:
            print("✓ Camera positioning SUCCESSFUL")
        else:
            print("✗ Camera positioning FAILED")
        print(f"{'='*60}")
    
    def test_camera_calculation_verification(self):
        """Verify camera calculation accuracy by manually setting camera to API-calculated values."""
        import keyboard
        import time
        
        osrs = self.init_osrs()
        
        print("\n=== Camera Calculation Verification ===")
        print("\nThis test verifies if the API's calculated pitch/yaw/scale are correct.")
        print("1. API calculates target camera values for a tile")
        print("2. You manually set the camera to those values")
        print("3. We check if the tile is actually visible at those camera settings")
        
        # Get current position
        coords = osrs.api.get_coords()
        if not coords:
            print("✗ Failed to get player coordinates")
            return
        
        player_x = coords['world']['x']
        player_y = coords['world']['y']
        player_plane = coords['world']['plane']
        
        print(f"\nCurrent position: ({player_x}, {player_y}, plane={player_plane})")
        
        # Get target from user
        try:
            target_x = int(input("Enter target X coordinate: "))
            target_y = int(input("Enter target Y coordinate: "))
        except ValueError:
            print("✗ Invalid coordinates")
            return
        
        print(f"\nTarget: ({target_x}, {target_y}, plane={player_plane})")
        
        # Calculate distance
        dx = target_x - player_x
        dy = target_y - player_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        print(f"Distance: {distance:.1f} tiles")
        
        # Get API's calculated camera values
        rotation_data = osrs.api.get_camera_rotation(target_x, target_y, player_plane)
        if not rotation_data:
            print("✗ Failed to get camera rotation data")
            return
        
        target_yaw = rotation_data.get('targetYaw')
        target_pitch = rotation_data.get('targetPitch')
        target_scale = rotation_data.get('targetScale')
        
        print(f"\n{'='*60}")
        print("API CALCULATED TARGET VALUES:")
        print(f"{'='*60}")
        print(f"Target Yaw:   {target_yaw} / 2048")
        print(f"Target Pitch: {target_pitch} (128=down, 383=horizontal)")
        print(f"Target Scale: {target_scale} (300=zoom out, 650=zoom in)")
        
        # Show calculation details
        angle_radians = rotation_data.get('angleRadians')
        if angle_radians is not None:
            import math
            angle_degrees = angle_radians * 180 / math.pi
            print(f"\nCalculation details:")
            print(f"  dx={dx}, dy={dy}")
            print(f"  atan2(dy, dx) = {angle_degrees:.1f}°")
            print(f"  Converted to yaw: {target_yaw}")
        
        # Convert yaw to compass direction
        yaw_degrees = (target_yaw / 2048) * 360
        direction = "North"
        if 45 < yaw_degrees <= 135:
            direction = "West"
        elif 135 < yaw_degrees <= 225:
            direction = "South"
        elif 225 < yaw_degrees <= 315:
            direction = "East"
        print(f"  Direction: {direction} ({yaw_degrees:.1f}°)")
        
        print(f"\n{'='*60}")
        print("MANUAL VERIFICATION INSTRUCTIONS:")
        print(f"{'='*60}")
        print("1. Use your mouse to manually adjust the camera to:")
        print(f"   - Yaw (compass): {target_yaw}")
        print(f"   - Pitch (angle): {target_pitch}")
        print(f"   - Scale (zoom): {target_scale}")
        print("2. Press SPACE when camera is set correctly")
        print("3. ESC to cancel")
        print(f"{'='*60}")
        
        # Wait for user to set camera
        while True:
            if keyboard.is_pressed('space'):
                time.sleep(0.3)  # Debounce
                break
            elif keyboard.is_pressed('esc'):
                print("\nCancelled.")
                return
            time.sleep(0.1)
        
        # Read actual camera state
        camera = osrs.api.get_camera()
        if not camera:
            print("✗ Failed to read camera state")
            return
        
        actual_yaw = camera.get('yaw', 0)
        actual_pitch = camera.get('pitch', 0)
        actual_scale = camera.get('scale', 0)
        
        print(f"\n{'='*60}")
        print("ACTUAL CAMERA STATE:")
        print(f"{'='*60}")
        print(f"Actual Yaw:   {actual_yaw} (target: {target_yaw}, diff: {actual_yaw - target_yaw:+d})")
        print(f"Actual Pitch: {actual_pitch} (target: {target_pitch}, diff: {actual_pitch - target_pitch:+d})")
        print(f"Actual Scale: {actual_scale} (target: {target_scale}, diff: {actual_scale - target_scale:+d})")
        
        # Check if tile is visible
        rotation_data = osrs.api.get_camera_rotation(target_x, target_y, player_plane)
        if not rotation_data:
            print("✗ Failed to check tile visibility")
            return
        
        is_visible = rotation_data.get('visible', False)
        screen_x = rotation_data.get('screenX', -1)
        screen_y = rotation_data.get('screenY', -1)
        
        print(f"\n{'='*60}")
        print("TILE VISIBILITY CHECK:")
        print(f"{'='*60}")
        print(f"Tile visible: {is_visible}")
        if screen_x >= 0 and screen_y >= 0:
            print(f"Screen position: ({screen_x}, {screen_y})")
            
            # Get viewport center
            viewport_center_x = rotation_data.get('viewportCenterX', 256)
            viewport_center_y = rotation_data.get('viewportCenterY', 167)
            offset_x = screen_x - viewport_center_x
            offset_y = screen_y - viewport_center_y
            print(f"Viewport center: ({viewport_center_x}, {viewport_center_y})")
            print(f"Offset from center: ({offset_x:+d}, {offset_y:+d}) pixels")
        else:
            print(f"Screen position: Not available (tile out of render distance)")
        
        # Summary
        print(f"\n{'='*60}")
        if is_visible:
            if abs(screen_x - rotation_data.get('viewportCenterX', 256)) < 100 and \
               abs(screen_y - rotation_data.get('viewportCenterY', 167)) < 100:
                print("✓ SUCCESS: Tile is visible and reasonably centered")
            else:
                print("⚠ PARTIAL: Tile is visible but far from center")
                print("  This suggests pitch/yaw calculation is roughly correct")
                print("  but may need fine-tuning for centering")
        else:
            print("✗ FAILURE: Tile is NOT visible at calculated camera position")
            print("  The yaw/pitch/scale calculations are incorrect")
            print("  Check the atan2 conversion formula and coordinate system")
        print(f"{'='*60}")
    
    def test_camera_rotation_calibration(self):
        """Test and calibrate pixel-to-yaw/pitch conversion ratios."""
        import keyboard
        import time
        
        osrs = self.init_osrs()
        
        print("\n=== Camera Rotation Calibration Test ===")
        print("\nThis test measures actual yaw/pitch changes from pixel drags")
        print("to verify/calibrate the conversion ratios used in rotation calculations.")
        
        print("\nSelect test type:")
        print("1 - Yaw (horizontal rotation)")
        print("2 - Pitch (vertical rotation)")
        print("ESC - Cancel")
        
        test_type = None
        while test_type is None:
            if keyboard.is_pressed('1'):
                test_type = 'yaw'
            elif keyboard.is_pressed('2'):
                test_type = 'pitch'
            elif keyboard.is_pressed('esc'):
                print("\nCancelled.")
                return
            time.sleep(0.1)
        
        time.sleep(0.3)  # Debounce
        
        if test_type == 'yaw':
            print("\n=== YAW CALIBRATION ===")
            print("Testing horizontal camera rotation (yaw)")
            
            # Get pixel distance from user
            try:
                pixel_input = input("\nEnter pixel drag distance [default 200]: ").strip()
                pixel_distance = int(pixel_input) if pixel_input else 200
            except ValueError:
                print("Invalid input, using default 200")
                pixel_distance = 200
            
            print(f"\nWill perform {pixel_distance}px horizontal drag (right direction)")
            print("Press SPACE to start test, ESC to cancel")
            
            while True:
                if keyboard.is_pressed('space'):
                    break
                elif keyboard.is_pressed('esc'):
                    print("\nCancelled.")
                    return
                time.sleep(0.1)
            
            time.sleep(0.3)  # Debounce
            
            # Record initial yaw
            camera_before = osrs.api.get_camera()
            if not camera_before:
                print("✗ Failed to read initial camera state")
                return
            
            yaw_before = camera_before.get('yaw', 0)
            print(f"\nInitial yaw: {yaw_before}")
            
            # Perform rotation
            print(f"Executing {pixel_distance}px horizontal drag...")
            osrs.window.rotate_camera(min_drag_distance=pixel_distance, direction='right')
            time.sleep(0.5)  # Wait for camera to settle
            
            # Record final yaw
            camera_after = osrs.api.get_camera()
            if not camera_after:
                print("✗ Failed to read final camera state")
                return
            
            yaw_after = camera_after.get('yaw', 0)
            print(f"Final yaw: {yaw_after}")
            
            # Calculate change
            yaw_change = (yaw_after - yaw_before) % 2048
            if yaw_change > 1024:  # Handle wrap-around
                yaw_change = yaw_change - 2048
            
            print(f"\n" + "="*60)
            print(f"YAW CHANGE: {abs(yaw_change)} units")
            print(f"PIXEL DRAG: {pixel_distance} pixels")
            print(f"RATIO: {pixel_distance / abs(yaw_change):.2f} pixels per yaw unit")
            print(f"INVERSE: {abs(yaw_change) / pixel_distance:.4f} yaw units per pixel")
            print("="*60)
            
            # Compare to expected
            expected_yaw_per_200px = 512  # 90 degrees
            expected_ratio = 200 / 512
            actual_ratio = pixel_distance / abs(yaw_change)
            
            print(f"\nExpected ratio (from code): {expected_ratio:.4f} px/unit")
            print(f"Actual ratio (measured): {actual_ratio:.4f} px/unit")
            print(f"Difference: {((actual_ratio - expected_ratio) / expected_ratio * 100):.1f}%")
            
            # Suggest updated conversion
            if abs(yaw_change) > 0:
                suggested_pixels_for_512 = int((512 / abs(yaw_change)) * pixel_distance)
                print(f"\nSuggested: {suggested_pixels_for_512}px ≈ 512 yaw units (90°)")
        
        else:  # pitch
            print("\n=== PITCH CALIBRATION ===")
            print("Testing vertical camera rotation (pitch)")
            
            # Get pixel distance from user
            try:
                pixel_input = input("\nEnter pixel drag distance [default 100]: ").strip()
                pixel_distance = int(pixel_input) if pixel_input else 100
            except ValueError:
                print("Invalid input, using default 100")
                pixel_distance = 100
            
            print(f"\nWill perform {pixel_distance}px vertical drag (down direction)")
            print("Press SPACE to start test, ESC to cancel")
            
            while True:
                if keyboard.is_pressed('space'):
                    break
                elif keyboard.is_pressed('esc'):
                    print("\nCancelled.")
                    return
                time.sleep(0.1)
            
            time.sleep(0.3)  # Debounce
            
            # Record initial pitch
            camera_before = osrs.api.get_camera()
            if not camera_before:
                print("✗ Failed to read initial camera state")
                return
            
            pitch_before = camera_before.get('pitch', 0)
            print(f"\nInitial pitch: {pitch_before}")
            
            # Perform rotation
            print(f"Executing {pixel_distance}px vertical drag...")
            osrs.window.rotate_camera(min_drag_distance=pixel_distance, direction='down', vertical=True)
            time.sleep(0.5)  # Wait for camera to settle
            
            # Record final pitch
            camera_after = osrs.api.get_camera()
            if not camera_after:
                print("✗ Failed to read final camera state")
                return
            
            pitch_after = camera_after.get('pitch', 0)
            print(f"Final pitch: {pitch_after}")
            
            # Calculate change
            pitch_change = abs(pitch_after - pitch_before)
            
            print(f"\n" + "="*60)
            print(f"PITCH CHANGE: {pitch_change} units")
            print(f"PIXEL DRAG: {pixel_distance} pixels")
            print(f"RATIO: {pixel_distance / pitch_change:.2f} pixels per pitch unit")
            print(f"INVERSE: {pitch_change / pixel_distance:.4f} pitch units per pixel")
            print("="*60)
            
            # Compare to expected
            expected_pitch_per_100px = 128
            expected_ratio = 100 / 128
            actual_ratio = pixel_distance / pitch_change if pitch_change > 0 else 0
            
            print(f"\nExpected ratio (from code): {expected_ratio:.4f} px/unit")
            print(f"Actual ratio (measured): {actual_ratio:.4f} px/unit")
            if pitch_change > 0:
                print(f"Difference: {((actual_ratio - expected_ratio) / expected_ratio * 100):.1f}%")
            
            # Suggest updated conversion
            if pitch_change > 0:
                suggested_pixels_for_128 = int((128 / pitch_change) * pixel_distance)
                print(f"\nSuggested: {suggested_pixels_for_128}px ≈ 128 pitch units")
    
    def test_set_camera_yaw(self):
        """Test setting camera yaw to a specific angle."""
        osrs = self.init_osrs()
        
        print("\n=== Set Camera Yaw Test ===")
        
        # Get current camera state
        camera = osrs.api.get_camera()
        if not camera:
            print("✗ Could not read camera state")
            return
        
        current_yaw = camera.get('yaw', 0)
        print(f"Current yaw: {current_yaw} / 2048")
        
        # Convert to degrees for reference
        current_degrees = (current_yaw / 2048) * 360
        print(f"  ({current_degrees:.1f}° clockwise from north)")
        
        # Display cardinal directions for reference
        print("\nYaw reference (0-2048 scale):")
        print("  0 / 2048 = North (0°)")
        print("  512 = West (90° counter-clockwise)")
        print("  1024 = South (180°)")
        print("  1536 = East (270° counter-clockwise / 90° clockwise)")
        
        # Prompt for target yaw
        print("\nChoose rotation method:")
        print("1 - Mouse drag (fast, natural)")
        print("2 - Arrow keys (slower, more precise)")
        print("ESC - Cancel")
        
        method = None
        while method is None:
            if keyboard.is_pressed('1'):
                method = 'mouse'
            elif keyboard.is_pressed('2'):
                method = 'keys'
            elif keyboard.is_pressed('esc'):
                print("\nCancelled.")
                return
            time.sleep(0.1)
        
        time.sleep(0.3)  # Debounce
        
        print(f"\nSelected method: {method}")
        
        # Get target yaw from user
        print("\nEnter target yaw (0-2048) or press ENTER for quick test angles:")
        print("Quick options:")
        print("  [Press ENTER] - Test all cardinal directions")
        print("  Or type a number: e.g., 512 for East, 1024 for South")
        
        try:
            yaw_input = input("Target yaw: ").strip()
            
            if yaw_input:
                # Custom yaw
                target_yaw = int(yaw_input)
                if target_yaw < 0 or target_yaw > 2048:
                    print("✗ Invalid yaw. Must be 0-2048.")
                    return
                
                print(f"\nRotating to yaw {target_yaw}...")
                print("Note: Individual yaw/pitch control removed. Use camera.set_camera_to_tile() for positioning.")
                success = False
                
                if success:
                    print("\n✓ Rotation complete!")
                    # Show final state
                    camera = osrs.api.get_camera()
                    if camera:
                        final_yaw = camera.get('yaw', 0)
                        print(f"Final yaw: {final_yaw} / 2048")
                else:
                    print("\n✗ Rotation failed")
            
            else:
                # Test all cardinal directions
                print("\nTesting cardinal directions in sequence...")
                cardinal_directions = [
                    (0, "North"),
                    (512, "East"),
                    (1024, "South"),
                    (1536, "West"),
                    (0, "North (return)")
                ]
                
                for target_yaw, direction in cardinal_directions:
                    print(f"\n--- Rotating to {direction} (yaw={target_yaw}) ---")
                    print("Note: Individual yaw control removed. Use camera.set_camera_to_tile() for positioning.")
                    success = False
                    
                    if success:
                        print(f"✓ Successfully rotated to {direction}")
                    else:
                        print(f"✗ Failed to rotate to {direction}")
                    
                    # Small delay between rotations
                    time.sleep(1.0)
                
                print("\n✓ Cardinal direction test complete!")
        
        except ValueError as e:
            print(f"✗ Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n✗ Test interrupted by user")
    
    def test_set_camera_pitch(self):
        """Test setting camera pitch to a specific angle."""
        osrs = self.init_osrs()
        
        print("\n=== Set Camera Pitch Test ===")
        
        # Get current camera state
        camera = osrs.api.get_camera()
        if not camera:
            print("✗ Could not read camera state")
            return
        
        current_pitch = camera.get('pitch', 383)
        print(f"Current pitch: {current_pitch} / 383")
        
        # Display pitch reference
        print("\nPitch reference (128-383 scale):")
        print("  128 = Looking straight down (closest view)")
        print("  256 = Medium angle (45°)")
        print("  383 = Most horizontal (looking far)")
        
        # Prompt for method
        print("\nChoose rotation method:")
        print("1 - Mouse drag (fast, natural)")
        print("2 - Arrow keys (slower, more precise)")
        print("ESC - Cancel")
        
        method = None
        while method is None:
            if keyboard.is_pressed('1'):
                method = 'mouse'
            elif keyboard.is_pressed('2'):
                method = 'keys'
            elif keyboard.is_pressed('esc'):
                print("\nCancelled.")
                return
            time.sleep(0.1)
        
        time.sleep(0.3)  # Debounce
        
        print(f"\nSelected method: {method}")
        
        # Get target pitch from user
        print("\nEnter target pitch (128-383) or press ENTER for quick test angles:")
        print("Quick options:")
        print("  [Press ENTER] - Test common pitch angles")
        print("  Or type a number: e.g., 256 for medium, 383 for far view")
        
        try:
            pitch_input = input("Target pitch: ").strip()
            
            if pitch_input:
                # Custom pitch
                target_pitch = int(pitch_input)
                if target_pitch < 128 or target_pitch > 383:
                    print("✗ Invalid pitch. Must be 128-383.")
                    return
                
                print(f"\nAdjusting to pitch {target_pitch}...")
                print("Note: Individual pitch control removed. Use camera.set_camera_to_tile() for positioning.")
                success = False
                
                if success:
                    print("\n✓ Pitch adjustment complete!")
                    # Show final state
                    camera = osrs.api.get_camera()
                    if camera:
                        final_pitch = camera.get('pitch', 383)
                        print(f"Final pitch: {final_pitch} / 383")
                else:
                    print("\n✗ Pitch adjustment failed")
            
            else:
                # Test common pitch angles
                print("\nTesting common pitch angles in sequence...")
                pitch_angles = [
                    (256, "Medium angle (45°)"),
                    (383, "Most Horizontal (far view)"),
                    (128, "Looking Down (close view)"),
                    (256, "Return to Medium")
                ]
                
                for target_pitch, description in pitch_angles:
                    print(f"\n--- Setting pitch to {description} (pitch={target_pitch}) ---")
                    print("Note: Individual pitch control removed. Use camera.set_camera_to_tile() for positioning.")
                    success = False
                    
                    if success:
                        print(f"✓ Successfully set to {description}")
                    else:
                        print(f"✗ Failed to set to {description}")
                    
                    # Small delay between adjustments
                    time.sleep(1.0)
                
                print("\n✓ Pitch angle test complete!")
        
        except ValueError as e:
            print(f"✗ Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n✗ Test interrupted by user")
    
    def run_navigation_tests(self):
        """Run navigation testing menu."""
        self.current_menu = "navigation"
        
        test_map = {
            'c': ("Read Coordinates", self.test_read_coordinates),
            'y': ("Read Camera Yaw", self.test_read_camera_yaw),
            'n': ("Click Compass to North", self.test_click_compass_to_north),
            'm': ("Check Player Moving", self.test_player_moving),
            'o': ("Click Minimap Offset", self.test_minimap_offset_click),
            'w': ("Walk to Coordinates", self.test_walk_to_coordinates),
            'l': ("Long Distance Walk", self.test_long_distance_walk),
            's': ("Test Stuck Detection", self.test_stuck_detection),
            'a': ("Camera Positioning Suite", self.test_camera_positioning),
            'v': ("Verify Camera Calculations", self.test_camera_calculation_verification),
            'k': ("Calibration Info", self.test_calibration_info),
        }
        
        print("\n" + "="*60)
        print("NAVIGATION TESTS")
        print("="*60)
        print("C - Read Coordinates (World & Scene)")
        print("Y - Read Camera Yaw")
        print("N - Click Compass to North")
        print("M - Check Player Moving")
        print("O - Click Minimap Offset (+5, +5)")
        print("W - Walk to Coordinates (+10 north)")
        print("L - Long Distance Walk (25 tiles NE)")
        print("S - Test Stuck Detection")
        print("A - Camera Positioning Suite")
        print("V - Verify Camera Calculations (NEW)")
        print("K - Calibration Info")
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
    
    # =================================================================
    # INTERACTION TESTS
    # =================================================================

    def test_npc_in_viewport(self):
        api = self.init_api()
        osrs = self.init_osrs()

        npcs = api.get_npcs_in_viewport()
        if npcs:
            print(f"✅ Retrieved {len(npcs)} NPCs in viewport:\n")
            for i, npc in enumerate(npcs, 1):
                name = npc.get('name', 'Unknown')
                npc_id = npc.get('id', -1)
                x = npc.get('x', -1)
                y = npc.get('y', -1)
                print(f"  {i:2}. {name} (ID: {npc_id}) - ({x}, {y})")

                if name == "Banker":
                    osrs.window.move_mouse_to((x, y))
                    # osrs.window.click()
        else:
            print("❌ No NPCs in viewport or endpoint not available")
    
    def test_game_object_in_viewport(self):
        api = self.init_api()
        osrs = self.init_osrs()

        objects = api.get_game_objects_in_viewport()
        if objects:
            print(f"✅ Retrieved {len(objects)} objects in viewport:\n")
            for i, obj in enumerate(objects, 1):
                name = obj.get('name', 'Unknown')
                obj_id = obj.get('id', -1)
                x = obj.get('x', -1)
                y = obj.get('y', -1)
                print(f"  {i:2}. {name} (ID: {obj_id}) - ({x}, {y})")

                if obj_id == 10583:
                    osrs.window.move_mouse_to((x, y))
                    # osrs.window.click()
        else:
            print("❌ No NPCs in viewport or endpoint not available")

    def test_find_in_viewport_with_rotation(self):
        """Test find_in_viewport method with camera rotation."""
        osrs = self.init_osrs()
        from config.game_objects import BankObjects
        from config.npcs import Bankers
        
        print("\n=== Testing find_in_viewport ===")
        print("\nChoose what to search for:")
        print("1 - Bank object (Varrock West)")
        print("2 - All Banker NPCs")
        print("3 - Iron rocks")
        print("4 - All Bank objects")
        print("5 - Custom ID(s)")
        
        # Wait for user choice
        choice = None
        entity_ids = None
        entity_type = None
        while choice is None:
            if keyboard.is_pressed('1'):
                entity_ids = 10583  # Varrock West bank booth
                entity_type = "object"
                choice = 1
            elif keyboard.is_pressed('2'):
                entity_ids = Bankers.BANKER.ids  # All banker IDs
                entity_type = "npc"
                choice = 2
            elif keyboard.is_pressed('3'):
                entity_ids = 11364  # Iron rocks
                entity_type = "object"
                choice = 3
            elif keyboard.is_pressed('4'):
                entity_ids = BankObjects.all_interactive()  # All bank IDs
                entity_type = "object"
                choice = 4
            elif keyboard.is_pressed('5'):
                ids_input = input("\nEnter entity ID(s) (comma-separated): ")
                entity_ids = [int(x.strip()) for x in ids_input.split(',')]
                entity_type = input("Enter type (npc/object): ").lower()
                choice = 5
            elif keyboard.is_pressed('esc'):
                return
            time.sleep(0.1)
        
        time.sleep(0.3)  # Debounce
        
        if entity_ids is None or entity_type is None:
            print("✗ No selection made")
            return
        
        print(f"\nSearching for {entity_type}(s) with ID(s) {entity_ids}...")
        results = osrs.find_in_viewport(entity_ids, entity_type, rotate_360=True, timeout=15.0)
        
        if results:
            print(f"\n✅ Found {len(results)} matching {entity_type}(s)!\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.get('name', 'Unknown')} (ID: {result.get('id')})")
                print(f"   Position: ({result.get('x')}, {result.get('y')})")
            
            # Move mouse to the first result if it has hull data
            if results:
                first = results[0]
                hull = first.get('hull', None)
                if hull and hull.get('points'):
                    polygon = Polygon(hull['points'])
                    click_point = polygon.random_point_inside(osrs.window.GAME_AREA)
                    print(f"\n  Moving mouse to first result: {click_point}")
                    osrs.window.move_mouse_to(click_point, in_canvas=True)
        else:
            print(f"\n❌ No matches found after searching with camera rotation")


    # =================================================================
    # MINING SKILL TESTS
    # =================================================================
    
    def test_mining_pickaxe_verification(self):
        """Test pickaxe equipped verification."""
        api = self.init_api()
        from config.items import Tools
        
        print("\nChecking for equipped pickaxe...")
        equipment = api.get_equipment()
        
        if equipment:
            print(f"✓ Retrieved {len(equipment)} equipped items")
            # Slot 3 is weapon slot
            weapon = next((item for item in equipment if item.get('slot') == 3), None)
            
            if weapon:
                weapon_id = weapon.get('id')
                weapon_name = weapon.get('name', 'Unknown')
                print(f"  Weapon slot (3): {weapon_name} (ID: {weapon_id})")
                
                pickaxe_ids = [
                    Tools.BRONZE_PICKAXE.id, Tools.IRON_PICKAXE.id, Tools.STEEL_PICKAXE.id,
                    Tools.MITHRIL_PICKAXE.id, Tools.ADAMANT_PICKAXE.id, Tools.RUNE_PICKAXE.id,
                    Tools.DRAGON_PICKAXE.id, Tools.CRYSTAL_PICKAXE.id
                ]
                
                if weapon_id in pickaxe_ids:
                    print(f"  ✓ Pickaxe detected: {weapon_name}")
                else:
                    print(f"  ✗ Not a pickaxe")
            else:
                print("  ✗ No weapon equipped")
        else:
            print("✗ Could not retrieve equipment data")
    
    def test_mining_xp_tracking(self):
        """Test mining XP stat tracking."""
        api = self.init_api()
        
        print("\nRetrieving Mining stats...")
        stats = api.get_stats()
        
        if stats:
            mining = next((s for s in stats if s['stat'] == 'Mining'), None)
            if mining:
                print(f"✓ Mining Stats:")
                print(f"  Level: {mining['level']}")
                print(f"  Current XP: {mining['xp']:,}")
                print(f"  XP to next level: {mining['xpToNextLevel']:,}")
                print(f"  Next level at: {mining['nextLevelAt']:,}")
                
                # Calculate percentage to next level
                current_xp = mining['xp']
                xp_to_next = mining['xpToNextLevel']
                next_level_xp = mining['nextLevelAt']
                level_start_xp = next_level_xp - (xp_to_next + current_xp - next_level_xp)
                level_progress = ((current_xp - level_start_xp) / (next_level_xp - level_start_xp)) * 100
                print(f"  Progress: {level_progress:.1f}%")
            else:
                print("✗ Mining stat not found")
        else:
            print("✗ Could not retrieve stats")
    
    def test_mining_animation_detection(self):
        """Test mining animation detection."""
        api = self.init_api()
        
        print("\nMonitoring player animation (10 seconds)...")
        print("Start mining now!")
        
        start_time = time.time()
        mining_detected = False
        mining_animation_id = 628
        
        while time.time() - start_time < 10.0:
            player_data = api.get_player()
            if player_data:
                is_animating = player_data.get('isAnimating', False)
                animation_id = player_data.get('animationId', -1)
                
                if is_animating:
                    if animation_id == mining_animation_id:
                        if not mining_detected:
                            print(f"✓ Mining animation detected! (ID: {animation_id})")
                            mining_detected = True
                    else:
                        print(f"  Animating: {animation_id}")
                else:
                    if mining_detected:
                        print("  Mining animation stopped")
                        mining_detected = False
            
            time.sleep(0.2)
        
        print("\nMonitoring complete")
    
    def test_find_ore_rocks(self):
        """Test finding ore rocks in viewport."""
        api = self.init_api()
        osrs = self.init_osrs()
        from config.game_objects import OreRocks
        
        print("\nSearching for ore rocks...")
        objects = api.get_game_objects_in_viewport()
        
        if objects:
            # Define common ore types to check
            ore_types = {
                "Iron": OreRocks.IRON_ORE_ROCK.ids,
                "Copper": OreRocks.COPPER_ORE_ROCK.ids,
                "Tin": OreRocks.TIN_ORE_ROCK.ids,
                "Coal": OreRocks.COAL_ROCK.ids,
                "Mithril": OreRocks.MITHRIL_ORE_ROCK.ids,
                "Adamantite": OreRocks.ADAMANTITE_ORE_ROCK.ids,
                "Runite": OreRocks.RUNITE_ORE_ROCK.ids,
            }
            
            found_ores = {}
            
            for obj in objects:
                obj_id = obj.get('id')
                for ore_name, ore_ids in ore_types.items():
                    if obj_id in ore_ids:
                        if ore_name not in found_ores:
                            found_ores[ore_name] = []
                        found_ores[ore_name].append(obj)
            
            if found_ores:
                print(f"✓ Found {sum(len(v) for v in found_ores.values())} ore rocks:")
                for ore_name, rocks in found_ores.items():
                    print(f"\n  {ore_name} ({len(rocks)} rocks):")
                    for rock in rocks:
                        x, y = rock.get('x', 0), rock.get('y', 0)
                        wx, wy = rock.get('worldX', 0), rock.get('worldY', 0)
                        print(f"    Screen: ({x}, {y}) | World: ({wx}, {wy})")
            else:
                print("✗ No ore rocks found in viewport")
        else:
            print("✗ No objects in viewport")
    
    def test_rock_distance_sorting(self):
        """Test world-coordinate-based rock prioritization."""
        api = self.init_api()
        from config.game_objects import OreRocks
        import math
        
        print("\nTesting rock distance sorting...")
        
        # Get player position
        coords = api.get_coords()
        if not coords or 'world' not in coords:
            print("✗ Could not get player position")
            return
        
        player_pos = coords['world']
        px, py = player_pos.get('x', 0), player_pos.get('y', 0)
        print(f"Player at: ({px}, {py})")
        
        # Get all ore rocks
        objects = api.get_game_objects_in_viewport()
        if not objects:
            print("✗ No objects in viewport")
            return
        
        # Filter for iron rocks (or any common ore)
        all_rock_ids = OreRocks.IRON_ORE_ROCK.ids + OreRocks.COPPER_ORE_ROCK.ids + OreRocks.TIN_ORE_ROCK.ids
        rocks = [obj for obj in objects if obj.get('id') in all_rock_ids]
        
        if not rocks:
            print("✗ No ore rocks found")
            return
        
        print(f"\nFound {len(rocks)} rocks. Sorting by distance...")
        
        # Calculate distances
        for rock in rocks:
            rx, ry = rock.get('worldX', 0), rock.get('worldY', 0)
            distance = math.sqrt((rx - px)**2 + (ry - py)**2)
            rock['distance_2d'] = distance
        
        # Sort by distance
        rocks.sort(key=lambda r: r.get('distance_2d', float('inf')))
        
        print("\nRocks sorted by distance:")
        for i, rock in enumerate(rocks, 1):
            rx, ry = rock.get('worldX', 0), rock.get('worldY', 0)
            dist = rock.get('distance_2d', 0)
            rock_id = rock.get('id')
            print(f"  {i}. World: ({rx}, {ry}) | Distance: {dist:.1f} tiles | ID: {rock_id}")
    
    def test_location_resolution(self):
        """Test location name to coordinates resolution."""
        from config.locations import MiningLocations, BankLocations
        
        print("\nTesting location resolution...")
        
        test_locations = [
            ("varrock_west_mine", MiningLocations),
            ("varrock_west", BankLocations),
            ("lumbridge_swamp_west", MiningLocations),
            ("al_kharid_mine", MiningLocations),
            ("edgeville", BankLocations),
        ]
        
        for location_str, location_class in test_locations:
            location_upper = location_str.upper().replace(" ", "_")
            coord = location_class.find_by_name(location_upper)
            
            if coord:
                print(f"✓ {location_str}: {coord}")
            else:
                print(f"✗ {location_str}: Not found")
        
        # Show all mining locations
        print("\nAll mining locations:")
        all_mines = MiningLocations.all()
        for name, coords in all_mines.items():
            print(f"  {name}: {coords}")
    
    def test_mining_bot_initialization(self):
        """Test mining bot initialization."""
        print("\nTesting mining bot initialization...")
        
        try:
            from client.skills.mining import MiningBot
            
            print("Creating mining bot instance...")
            bot = MiningBot("iron_miner_varrock")
            
            print(f"✓ Bot initialized successfully")
            print(f"  Ore types: {[cfg['name'] for cfg in bot.rock_configs]}")
            print(f"  Rock IDs: {bot.primary_ore['rock_ids']}")
            print(f"  Mine location: {bot.mine_location}")
            print(f"  Bank location: {bot.bank_location}")
            print(f"  Banking enabled: {bot.should_bank}")
            print(f"  Powermine enabled: {bot.powermine}")
            print(f"  XP tracking: {bot.track_xp}")
            print(f"  Respawn detection: {bot.detect_respawn}")
            
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
    
    def test_ore_respawn_detection(self):
        """Test ore respawn detection (requires mining)."""
        api = self.init_api()
        from config.game_objects import OreRocks
        
        print("\nTesting ore respawn detection...")
        print("This test monitors for ore respawn after mining.")
        print("Make sure you're near ore rocks and start mining!")
        
        all_rock_ids = OreRocks.IRON_ORE_ROCK.ids + OreRocks.COPPER_ORE_ROCK.ids + OreRocks.TIN_ORE_ROCK.ids
        mining_animation_id = 628
        
        print("\nWaiting for mining to start...")
        mining_started = False
        timeout = 15.0
        start_time = time.time()
        
        # Wait for mining animation
        while time.time() - start_time < timeout:
            player_data = api.get_player()
            if player_data:
                is_animating = player_data.get('isAnimating', False)
                animation_id = player_data.get('animationId', -1)
                
                if is_animating and animation_id == mining_animation_id:
                    print("✓ Mining detected!")
                    mining_started = True
                    break
            
            time.sleep(0.2)
        
        if not mining_started:
            print("✗ Mining not detected within timeout")
            return
        
        # Wait for mining to stop
        print("\nWaiting for ore to be depleted...")
        while True:
            player_data = api.get_player()
            if player_data:
                is_animating = player_data.get('isAnimating', False)
                animation_id = player_data.get('animationId', -1)
                
                if not is_animating or animation_id != mining_animation_id:
                    print("✓ Mining stopped (ore depleted)")
                    break
            
            time.sleep(0.2)
        
        # Monitor for respawn
        print("\nMonitoring for ore respawn (10 seconds)...")
        respawn_time = time.time()
        
        while time.time() - respawn_time < 10.0:
            objects = api.get_game_objects_in_viewport()
            if objects:
                rocks = [obj for obj in objects if obj.get('id') in all_rock_ids]
                if rocks:
                    elapsed = time.time() - respawn_time
                    print(f"✓ Ore respawned! (after {elapsed:.1f} seconds)")
                    return
            
            time.sleep(0.3)
        
        print("✗ No respawn detected within timeout")
    
    def run_mining_tests(self):
        """Run mining skill testing menu."""
        self.current_menu = "mining"
        
        test_map = {
            'p': ("Pickaxe Verification", self.test_mining_pickaxe_verification),
            'x': ("XP Tracking", self.test_mining_xp_tracking),
            'a': ("Animation Detection", self.test_mining_animation_detection),
            'r': ("Find Ore Rocks", self.test_find_ore_rocks),
            'd': ("Rock Distance Sorting", self.test_rock_distance_sorting),
            'l': ("Location Resolution", self.test_location_resolution),
            'b': ("Mining Bot Initialization", self.test_mining_bot_initialization),
            's': ("Ore Respawn Detection", self.test_ore_respawn_detection),
        }
        
        print("\n" + "="*60)
        print("MINING SKILL TESTS")
        print("="*60)
        print("P - Pickaxe Verification (equipment check)")
        print("X - XP Tracking (mining stats)")
        print("A - Animation Detection (mining animation)")
        print("R - Find Ore Rocks (API object detection)")
        print("D - Rock Distance Sorting (world coordinates)")
        print("L - Location Resolution (config lookup)")
        print("B - Mining Bot Initialization (full bot setup)")
        print("S - Ore Respawn Detection (requires mining)")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    # =================================================================
    # WOODCUTTING TESTS
    # =================================================================
    
    def test_woodcutting_axe_verification(self):
        """Test if player has an axe equipped or in inventory."""
        api = self.init_api()
        from config.skill_mappings import get_all_tool_ids
        
        print("\nChecking for woodcutting axes...")
        
        axe_ids = get_all_tool_ids('woodcutting')
        print(f"Looking for axe IDs: {axe_ids}")
        
        # Check equipment
        equipment = api.get_equipment()
        if equipment:
            weapon_id = equipment.get('weapon', {}).get('id')
            if weapon_id in axe_ids:
                print(f"✓ Axe equipped: ID {weapon_id}")
                return
        
        # Check inventory
        inventory = api.get_inventory()
        if inventory:
            for item in inventory:
                if item and item.get('id') in axe_ids:
                    print(f"✓ Axe in inventory: ID {item['id']}")
                    return
        
        print("✗ No axe found in equipment or inventory")
    
    def test_woodcutting_xp_tracking(self):
        """Test woodcutting XP tracking."""
        api = self.init_api()
        
        print("\nFetching woodcutting stats...")
        
        stats = api.get_stats()
        if not stats:
            print("✗ Could not fetch stats")
            return
        
        wc_stat = stats.get('Woodcutting', {})
        level = wc_stat.get('level', 0)
        xp = wc_stat.get('xp', 0)
        boosted_level = wc_stat.get('boostedLevel', level)
        
        print(f"Woodcutting Level: {level}")
        print(f"Boosted Level: {boosted_level}")
        print(f"Experience: {xp:,}")
        
        # Calculate XP to next level
        def xp_for_level(level):
            total = 0
            for i in range(1, level):
                total += int(i + 300 * (2 ** (i / 7.0)))
            return int(total / 4)
        
        if level < 99:
            next_level_xp = xp_for_level(level + 1)
            xp_remaining = next_level_xp - xp
            print(f"XP to level {level + 1}: {xp_remaining:,}")
    
    def test_woodcutting_animation_detection(self):
        """Test woodcutting animation detection."""
        api = self.init_api()
        
        print("\nMonitoring for woodcutting animation...")
        print("Start cutting a tree!")
        print("Press ESC to stop monitoring")
        
        woodcutting_animation_id = 879
        detected = False
        
        while not keyboard.is_pressed('esc'):
            player_data = api.get_player()
            
            if player_data:
                is_animating = player_data.get('isAnimating', False)
                animation_id = player_data.get('animationId', -1)
                
                if is_animating and animation_id == woodcutting_animation_id:
                    if not detected:
                        print(f"✓ Woodcutting animation detected! (ID: {animation_id})")
                        detected = True
                elif detected and animation_id != woodcutting_animation_id:
                    print(f"  Animation stopped (current: {animation_id})")
                    detected = False
            
            time.sleep(0.3)
        
        time.sleep(0.3)  # Debounce ESC
    
    def test_find_trees(self):
        """Test finding trees using RuneLite API."""
        api = self.init_api()
        from config.game_objects import Trees
        
        print("\nSearching for trees in viewport...")
        
        # Get all objects
        objects = api.get_game_objects_in_viewport()
        if not objects:
            print("✗ No objects found")
            return
        
        print(f"Total objects in viewport: {len(objects)}")
        
        # Filter for different tree types
        tree_types = {
            'Normal': Trees.TREE.ids,
            'Oak': Trees.OAK_TREE.ids,
            'Willow': Trees.WILLOW_TREE.ids,
            'Maple': Trees.MAPLE_TREE.ids,
            'Yew': Trees.YEW_TREE.ids,
            'Magic': Trees.MAGIC_TREE.ids,
        }
        
        for tree_name, tree_ids in tree_types.items():
            trees = [obj for obj in objects if obj.get('id') in tree_ids]
            if trees:
                print(f"\n{tree_name} Trees: {len(trees)}")
                for i, tree in enumerate(trees[:3], 1):  # Show first 3
                    x, y = tree.get('worldX', 0), tree.get('worldY', 0)
                    distance = tree.get('distance', 0)
                    tree_id = tree.get('id')
                    print(f"  {i}. World: ({x}, {y}) | Distance: {distance} | ID: {tree_id}")
    
    def test_tree_distance_sorting(self):
        """Test sorting trees by distance."""
        api = self.init_api()
        from config.game_objects import Trees
        import math
        
        print("\nTesting tree distance sorting...")
        
        # Get player position
        coords = api.get_coords()
        if not coords or 'world' not in coords:
            print("✗ Could not get player position")
            return
        
        player_pos = coords['world']
        px, py = player_pos.get('x', 0), player_pos.get('y', 0)
        print(f"Player at: ({px}, {py})")
        
        # Get all trees (start with yews)
        objects = api.get_game_objects_in_viewport()
        if not objects:
            print("✗ No objects in viewport")
            return
        
        # Filter for yew trees
        all_tree_ids = Trees.YEW_TREE.ids + Trees.OAK_TREE.ids + Trees.WILLOW_TREE.ids
        trees = [obj for obj in objects if obj.get('id') in all_tree_ids]
        
        if not trees:
            print("✗ No trees found")
            return
        
        print(f"\nFound {len(trees)} trees. Sorting by distance...")
        
        # Calculate distances
        for tree in trees:
            tx, ty = tree.get('worldX', 0), tree.get('worldY', 0)
            distance = math.sqrt((tx - px)**2 + (ty - py)**2)
            tree['distance_2d'] = distance
        
        # Sort by distance
        trees.sort(key=lambda t: t.get('distance_2d', float('inf')))
        
        print("\nTrees sorted by distance:")
        for i, tree in enumerate(trees, 1):
            tx, ty = tree.get('worldX', 0), tree.get('worldY', 0)
            dist = tree.get('distance_2d', 0)
            tree_id = tree.get('id')
            print(f"  {i}. World: ({tx}, {ty}) | Distance: {dist:.1f} tiles | ID: {tree_id}")
    
    def test_woodcutting_location_resolution(self):
        """Test woodcutting location name to coordinates resolution."""
        from config.locations import WoodcuttingLocations, BankLocations
        
        print("\nTesting woodcutting location resolution...")
        
        test_locations = [
            ("edgeville_yews", WoodcuttingLocations),
            ("edgeville", BankLocations),
            ("varrock_palace_trees", WoodcuttingLocations),
            ("draynor_willows", WoodcuttingLocations),
            ("grand_exchange_trees", WoodcuttingLocations),
        ]
        
        for location_str, location_class in test_locations:
            location_upper = location_str.upper().replace(" ", "_")
            coord = location_class.find_by_name(location_upper)
            
            if coord:
                print(f"✓ {location_str}: {coord}")
            else:
                print(f"✗ {location_str}: Not found")
        
        # Show all woodcutting locations
        print("\nAll woodcutting locations:")
        all_wc_locs = WoodcuttingLocations.all()
        for name, coords in all_wc_locs.items():
            print(f"  {name}: {coords}")
    
    def test_woodcutting_bot_initialization(self):
        """Test woodcutting bot initialization."""
        print("\nTesting woodcutting bot initialization...")
        
        try:
            from client.skills.woodcutting import WoodcuttingBot
            
            print("Creating woodcutting bot instance...")
            bot = WoodcuttingBot("yew_cutter_edgeville")
            
            print(f"✓ Bot initialized successfully")
            print(f"  Tree types: {[cfg['name'] for cfg in bot.tree_configs]}")
            print(f"  Tree IDs: {bot.primary_tree['tree_ids']}")
            print(f"  Woodcutting location: {bot.wc_location}")
            print(f"  Bank location: {bot.bank_location}")
            print(f"  Banking enabled: {bot.should_bank}")
            print(f"  Powerdrop enabled: {bot.powerdrop}")
            print(f"  XP tracking: {bot.track_xp}")
            print(f"  Respawn detection: {bot.detect_respawn}")
            
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
    
    def test_tree_respawn_detection(self):
        """Test tree respawn detection (requires woodcutting)."""
        api = self.init_api()
        from config.game_objects import Trees
        
        print("\nTesting tree respawn detection...")
        print("This test monitors for tree respawn after cutting.")
        print("Make sure you're near trees and start cutting!")
        
        all_tree_ids = Trees.YEW_TREE.ids + Trees.OAK_TREE.ids + Trees.WILLOW_TREE.ids
        woodcutting_animation_id = 879
        
        print("\nWaiting for woodcutting to start...")
        cutting_started = False
        timeout = 15.0
        start_time = time.time()
        
        # Wait for woodcutting animation
        while time.time() - start_time < timeout:
            player_data = api.get_player()
            if player_data:
                is_animating = player_data.get('isAnimating', False)
                animation_id = player_data.get('animationId', -1)
                
                if is_animating and animation_id == woodcutting_animation_id:
                    print("✓ Woodcutting detected!")
                    cutting_started = True
                    break
            
            time.sleep(0.2)
        
        if not cutting_started:
            print("✗ Woodcutting not detected within timeout")
            return
        
        # Wait for woodcutting to stop
        print("\nWaiting for tree to be depleted...")
        while True:
            player_data = api.get_player()
            if player_data:
                is_animating = player_data.get('isAnimating', False)
                animation_id = player_data.get('animationId', -1)
                
                if not is_animating or animation_id != woodcutting_animation_id:
                    print("✓ Woodcutting stopped (tree depleted)")
                    break
            
            time.sleep(0.2)
        
        # Monitor for respawn
        print("\nMonitoring for tree respawn (90 seconds for yews)...")
        respawn_time = time.time()
        
        while time.time() - respawn_time < 90.0:
            objects = api.get_game_objects_in_viewport()
            if objects:
                trees = [obj for obj in objects if obj.get('id') in all_tree_ids]
                if trees:
                    elapsed = time.time() - respawn_time
                    print(f"✓ Tree respawned! (after {elapsed:.1f} seconds)")
                    return
            
            time.sleep(0.5)
        
        print("✗ No respawn detected within timeout")
    
    def run_woodcutting_tests(self):
        """Run woodcutting skill testing menu."""
        self.current_menu = "woodcutting"
        
        test_map = {
            'a': ("Axe Verification", self.test_woodcutting_axe_verification),
            'x': ("XP Tracking", self.test_woodcutting_xp_tracking),
            'n': ("Animation Detection", self.test_woodcutting_animation_detection),
            't': ("Find Trees", self.test_find_trees),
            'd': ("Tree Distance Sorting", self.test_tree_distance_sorting),
            'l': ("Location Resolution", self.test_woodcutting_location_resolution),
            'b': ("Woodcutting Bot Initialization", self.test_woodcutting_bot_initialization),
            'r': ("Tree Respawn Detection", self.test_tree_respawn_detection),
        }
        
        print("\n" + "="*60)
        print("WOODCUTTING SKILL TESTS")
        print("="*60)
        print("A - Axe Verification (equipment check)")
        print("X - XP Tracking (woodcutting stats)")
        print("N - Animation Detection (woodcutting animation)")
        print("T - Find Trees (API object detection)")
        print("D - Tree Distance Sorting (world coordinates)")
        print("L - Location Resolution (config lookup)")
        print("B - Woodcutting Bot Initialization (full bot setup)")
        print("R - Tree Respawn Detection (requires woodcutting)")
        print("\nESC - Back to Main Menu")
        print("="*60)
        
        self._run_submenu(test_map)
    
    # =================================================================
    # COMBAT TESTS
    # =================================================================
    
    def test_player_combat_state(self):
        """Test reading player combat state (health, prayer, special attack)."""
        print("\n=== Player Combat State Test ===")
        osrs = self.init_osrs()
        
        print("\nReading player combat state...")
        print("\nHealth:")
        health = osrs.combat.get_health()
        max_health = osrs.combat.get_max_health()
        health_percent = osrs.combat.get_health_percent()
        print(f"  Current: {health}/{max_health} ({health_percent}%)")
        
        print("\nPrayer:")
        prayer = osrs.combat.get_prayer()
        max_prayer = osrs.combat.get_max_prayer()
        prayer_percent = osrs.combat.get_prayer_percent()
        print(f"  Current: {prayer}/{max_prayer} ({prayer_percent}%)")
        
        print("\nSpecial Attack:")
        special = osrs.combat.get_special_attack()
        print(f"  Energy: {special}%")
        
        print("\nCombat State:")
        in_combat = osrs.combat.is_player_in_combat()
        print(f"  In Combat: {in_combat}")
        
        target = osrs.combat.get_current_target()
        if target:
            print(f"\nCurrent Target:")
            print(f"  Name: {target.get('name')}")
            print(f"  ID: {target.get('id')}")
            print(f"  Combat Level: {target.get('combatLevel')}")
            print(f"  Health: {target.get('health')}/{target.get('maxHealth')}")
            print(f"  Is Dying: {target.get('isDying')}")
        else:
            print("\n  No current target")
        
        print("\n✓ Player combat state retrieved")
    
    def test_npc_actor_data(self):
        """Test enhanced NPC Actor data from API."""
        print("\n=== NPC Actor Data Test ===")
        api = self.init_api()
        
        print("\nFetching NPCs in viewport with Actor data...")
        npcs = api.get_npcs_in_viewport()
        
        if not npcs:
            print("✗ No NPCs in viewport")
            return
        
        print(f"\n✓ Found {len(npcs)} NPCs in viewport")
        print("\nShowing first 5 NPCs with enhanced data:\n")
        
        for i, npc in enumerate(npcs[:5]):
            print(f"NPC {i+1}:")
            print(f"  Name: {npc.get('name')}")
            print(f"  ID: {npc.get('id')}")
            print(f"  Combat Level: {npc.get('combatLevel')}")
            print(f"  Position: ({npc.get('worldX')}, {npc.get('worldY')})")
            print(f"  Screen: ({npc.get('x')}, {npc.get('y')})")
            print(f"  Interacting With: {npc.get('interactingWith')}")
            print(f"  Is Dying: {npc.get('isDying')}")
            print(f"  Animation ID: {npc.get('animation')}")
            print(f"  Graphic ID: {npc.get('graphicId')}")
            print(f"  Overhead Text: {npc.get('overheadText')}")
            print(f"  Overhead Icon: {npc.get('overheadIcon')}")
            if npc.get('healthRatio') is not None:
                health_percent = int((npc.get('healthRatio') / npc.get('healthScale')) * 100)
                print(f"  Health: {npc.get('healthRatio')}/{npc.get('healthScale')} ({health_percent}%)")
            print()
    
    def test_threshold_checks(self):
        """Test health and prayer threshold checks."""
        print("\n=== Threshold Checks Test ===")
        osrs = self.init_osrs()
        
        threshold = input("\nEnter health threshold % to test (default 50): ").strip()
        health_threshold = int(threshold) if threshold else 50
        
        threshold = input("Enter prayer threshold % to test (default 25): ").strip()
        prayer_threshold = int(threshold) if threshold else 25
        
        print(f"\nTesting thresholds...")
        print(f"  Health threshold: {health_threshold}%")
        print(f"  Prayer threshold: {prayer_threshold}%")
        
        should_eat = osrs.combat.should_eat(health_threshold)
        should_drink = osrs.combat.should_drink_prayer(prayer_threshold)
        
        health_percent = osrs.combat.get_health_percent()
        prayer_percent = osrs.combat.get_prayer_percent()
        
        print(f"\nCurrent Status:")
        print(f"  Health: {health_percent}% - Should eat: {should_eat}")
        print(f"  Prayer: {prayer_percent}% - Should drink: {should_drink}")
        
        print("\n✓ Threshold checks complete")
    
    def test_engage_specific_npc(self):
        """Test engaging a specific NPC in combat."""
        print("\n=== Engage NPC Test ===")
        osrs = self.init_osrs()
        
        npc_id = input("\nEnter NPC ID to attack: ").strip()
        if not npc_id:
            print("✗ No NPC ID provided")
            return
        
        npc_id = int(npc_id)
        attack_option = input("Enter attack option (default 'Attack'): ").strip() or "Attack"
        
        print(f"\nAttempting to engage NPC {npc_id} with option '{attack_option}'...")
        print("This will filter out NPCs already in combat with others.")
        
        success = osrs.combat.engage_npc(npc_id, attack_option)
        
        if success:
            print(f"✓ Successfully engaged NPC!")
            time.sleep(1.0)
            
            # Check if now in combat
            in_combat = osrs.combat.is_player_in_combat()
            print(f"  In combat: {in_combat}")
            
            target = osrs.combat.get_current_target()
            if target:
                print(f"  Target: {target.get('name')} (ID: {target.get('id')})")
                
                # Store target position for loot detection
                target_pos = target.get('position')
                if target_pos:
                    print(f"  Position: ({target_pos['x']}, {target_pos['y']}, plane {target_pos['plane']})")
                    
                    # Wait for target to die
                    print("\nWaiting for target to die (60s timeout)...")
                    if osrs.combat.wait_until_target_dead(timeout=60.0):
                        print("✓ Target died!")
                        
                        # Wait for loot to appear
                        print("\nWaiting for loot to appear (10s timeout, radius 3)...")
                        loot = osrs.combat.wait_for_loot(
                            target_pos['x'], 
                            target_pos['y'], 
                            timeout=10.0, 
                            radius=3
                        )
                        
                        if loot:
                            print(f"✓ Found {len(loot)} loot item(s):")
                            from config.items import Bones, Currency
                            taken, failed = osrs.combat.take_loot(loot, [Bones.BONES, Currency.COINS])
                            for item in taken:
                                print(f"Took {item['name']} x{item['quantity']}")
                            for item in failed:
                                print(f"Failed to take {item['name']} x{item['quantity']}")
                        else:
                            print("⚠ No loot detected (NPC may not have dropped anything)")
                    else:
                        print("✗ Timeout waiting for target to die")
                else:
                    print("⚠ Could not get target position for loot detection")
            else:
                print("⚠ Target has no position data")
        else:
            print("✗ Failed to engage NPC (may not be available)")
    
    def test_eat_specific_food(self):
        """Test eating specific food item."""
        print("\n=== Eat Food Test ===")
        osrs = self.init_osrs()
        
        food_id = input("\nEnter food item ID: ").strip()
        if not food_id:
            print("✗ No food ID provided")
            return
        
        food_id = int(food_id)
        
        print(f"\nAttempting to eat food {food_id}...")
        
        health_before = osrs.combat.get_health()
        print(f"  Health before: {health_before}")
        
        success = osrs.combat.eat_food(food_id)
        
        if success:
            print("✓ Food eaten")
            time.sleep(1.0)
            
            health_after = osrs.combat.get_health() or 0
            print(f"  Health after: {health_after}")
            print(f"  Healed: +{health_after - health_before if health_before else '?'}")
        else:
            print("✗ Failed to eat food (may not be in inventory)")
    
    def test_drink_specific_potion(self):
        """Test drinking specific potion."""
        print("\n=== Drink Potion Test ===")
        osrs = self.init_osrs()
        
        potion_id = input("\nEnter potion item ID: ").strip()
        if not potion_id:
            print("✗ No potion ID provided")
            return
        
        potion_id = int(potion_id)
        
        print(f"\nAttempting to drink potion {potion_id}...")
        
        success = osrs.combat.drink_potion(potion_id)
        
        if success:
            print("✓ Potion consumed")
            time.sleep(1.0)
            
            # Show updated stats (could be boosted combat stats or prayer)
            print("\nUpdated Stats:")
            print(f"  Prayer: {osrs.combat.get_prayer()}/{osrs.combat.get_max_prayer()}")
            print(f"  Special: {osrs.combat.get_special_attack()}%")
        else:
            print("✗ Failed to drink potion (may not be in inventory)")
    
    def test_combat_wait_methods(self):
        """Test combat wait methods (requires being in combat)."""
        print("\n=== Combat Wait Methods Test ===")
        osrs = self.init_osrs()
        
        print("\nThis test requires you to be in combat.")
        print("Options:")
        print("1 - Wait until not in combat")
        print("2 - Wait until target dead")
        
        choice = input("\nSelect test (1 or 2): ").strip()
        
        if choice == "1":
            print("\nWaiting for combat to end (60s timeout)...")
            success = osrs.combat.wait_until_not_in_combat(timeout=60.0)
            if success:
                print("✓ Combat ended")
            else:
                print("✗ Timeout reached (still in combat)")
        
        elif choice == "2":
            print("\nWaiting for target to die (60s timeout)...")
            success = osrs.combat.wait_until_target_dead(timeout=60.0)
            if success:
                print("✓ Target died")
            else:
                print("✗ Timeout reached (target still alive or lost)")
        else:
            print("✗ Invalid choice")
    
    def test_npc_engagement_filtering(self):
        """Test NPC engagement filtering (shows available vs engaged NPCs)."""
        print("\n=== NPC Engagement Filtering Test ===")
        osrs = self.init_osrs()
        
        npc_id = input("\nEnter NPC ID to check: ").strip()
        if not npc_id:
            print("✗ No NPC ID provided")
            return
        
        npc_id = int(npc_id)
        
        print(f"\nChecking engagement status for NPC ID {npc_id}...")
        
        # Get all NPCs with this ID
        npcs = osrs.api.get_npcs_in_viewport()
        if not npcs:
            print("✗ No NPCs in viewport")
            return
        
        matching_npcs = [npc for npc in npcs if npc.get('id') == npc_id]
        
        if not matching_npcs:
            print(f"✗ No NPCs with ID {npc_id} found")
            return
        
        print(f"\n✓ Found {len(matching_npcs)} NPC(s) with ID {npc_id}\n")
        
        player_data = osrs.api.get_player()
        player_name = player_data.get('name') if player_data else None
        
        available_count = 0
        for i, npc in enumerate(matching_npcs):
            interacting = npc.get('interactingWith')
            is_available = interacting is None or interacting == player_name
            
            print(f"NPC {i+1}:")
            print(f"  Name: {npc.get('name')}")
            print(f"  Position: ({npc.get('worldX')}, {npc.get('worldY')})")
            print(f"  Interacting With: {interacting if interacting else 'None'}")
            print(f"  Available to Attack: {'YES' if is_available else 'NO (engaged)'}")
            print()
            
            if is_available:
                available_count += 1
        
        print(f"Summary: {available_count}/{len(matching_npcs)} NPCs available")
        print("✓ Engagement filtering check complete")
    
    def test_reengage_current_target(self):
        """
        Tests reengage current target
        """
        print("Press spacebar once in combat with a target")

        while True:
            if keyboard.is_pressed('space'):
                osrs = self.init_osrs()
                target = osrs.combat.get_current_target()
                if target:
                    print(f"Current target: {target.get('name')} (ID: {target.get('id')})")
                    print("Attempting to re-engage current target...")
                    success = osrs.click_entity(target, "npc", "Attack")
                    if success:
                        print("✓ Re-engagement successful")
                    else:
                        print("✗ Re-engagement failed")
                else:
                    print("✗ No current target to re-engage")
                
                time.sleep(0.5)  # Debounce spacebar
                
            
            time.sleep(0.1)

    def run_combat_tests(self):
        """Run combat testing menu."""
        self.current_menu = "combat"
        
        test_map = {
            's': ("Player Combat State", self.test_player_combat_state),
            'a': ("NPC Actor Data", self.test_npc_actor_data),
            't': ("Threshold Checks", self.test_threshold_checks),
            'e': ("Engage Specific NPC", self.test_engage_specific_npc),
            'f': ("Eat Specific Food", self.test_eat_specific_food),
            'p': ("Drink Specific Potion", self.test_drink_specific_potion),
            'w': ("Combat Wait Methods", self.test_combat_wait_methods),
            'n': ("NPC Engagement Filtering", self.test_npc_engagement_filtering),
            'r': ("Re-engage current target", self.test_reengage_current_target)
        }
        
        print("\n" + "="*60)
        print("COMBAT HANDLER TESTS")
        print("="*60)
        print("S - Player Combat State (health, prayer, special, target)")
        print("A - NPC Actor Data (enhanced NPC information)")
        print("T - Threshold Checks (should_eat, should_drink_prayer)")
        print("E - Engage Specific NPC (filtered by engagement status)")
        print("F - Eat Specific Food (consume food item)")
        print("P - Drink Specific Potion (consume potion)")
        print("W - Combat Wait Methods (wait_until_not_in_combat, wait_until_target_dead)")
        print("N - NPC Engagement Filtering (show available vs engaged)")
        print("R - Re-engage current target")
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
    
    # =================================================================
    # MAGIC TESTS
    # =================================================================
    
    def test_open_magic_tab(self):
        """Test opening the magic tab."""
        print("\n=== Open Magic Tab Test ===")
        osrs = self.init_osrs()
        
        print("\nAttempting to open magic tab...")
        success = osrs.magic.open_magic_tab()
        
        if success:
            print("✓ Magic tab opened successfully")
            print(f"  Is magic tab open: {osrs.magic.is_magic_tab_open()}")
        else:
            print("✗ Failed to open magic tab")
    
    def test_magic_level(self):
        """Test getting magic level from API."""
        print("\n=== Magic Level Test ===")
        osrs = self.init_osrs()
        
        magic_level = osrs.api.get_magic_level()
        if magic_level is not None:
            print(f"✓ Current Magic Level: {magic_level}")
        else:
            print("✗ Failed to get magic level from API")
    
    def test_check_spell_requirements(self):
        """Test checking if player can cast specific spells."""
        print("\n=== Spell Requirements Test ===")
        osrs = self.init_osrs()
        
        from config.spells import StandardSpells
        
        # Test a few common spells
        test_spells = [
            StandardSpells.HIGH_LEVEL_ALCHEMY,
            StandardSpells.VARROCK_TELEPORT,
            StandardSpells.LUMBRIDGE_TELEPORT,
            StandardSpells.FIRE_BLAST,
        ]
        
        print("\nChecking spell requirements:\n")
        for spell in test_spells:
            can_cast = osrs.magic.can_cast_spell(spell)
            has_runes = osrs.magic.has_runes(spell)
            magic_level = osrs.api.get_magic_level()
            
            status = "✓ CAN CAST" if can_cast else "✗ CANNOT CAST"
            print(f"{status} - {spell.name} (Lvl {spell.level_required})")
            print(f"  Your Level: {magic_level}")
            print(f"  Has Runes: {has_runes}")
            if spell.runes_required:
                print(f"  Required Runes:")
                for rune_id, qty in spell.runes_required.items():
                    from config.items import Runes
                    rune = Runes.find_by_id(rune_id)
                    rune_name = rune.name if rune else f"Rune {rune_id}"
                    osrs.inventory.populate()
                    current = osrs.inventory.count_item(rune_id)
                    print(f"    {rune_name}: {current}/{qty}")
            print()
    
    def test_cast_spell(self):
        """Test casting a specific spell."""
        print("\n=== Cast Spell Test ===")
        osrs = self.init_osrs()
        
        from config.spells import StandardSpells
        
        print("\nAvailable spells to test:")
        print("1 - High Level Alchemy")
        print("2 - Varrock Teleport")
        print("3 - Lumbridge Teleport")
        print("4 - Falador Teleport")
        print("5 - Camelot Teleport")
        
        choice = input("\nSelect spell (1-5): ").strip()
        
        spell_map = {
            '1': StandardSpells.HIGH_LEVEL_ALCHEMY,
            '2': StandardSpells.VARROCK_TELEPORT,
            '3': StandardSpells.LUMBRIDGE_TELEPORT,
            '4': StandardSpells.FALADOR_TELEPORT,
            '5': StandardSpells.CAMELOT_TELEPORT,
        }
        
        spell = spell_map.get(choice)
        if not spell:
            print("✗ Invalid choice")
            return
        
        # Check if can cast
        if not osrs.magic.can_cast_spell(spell):
            print(f"✗ Cannot cast {spell.name} - check requirements")
            return
        
        print(f"\nCasting {spell.name}...")
        osrs.magic.cast_spell_on_item(spell, 556)
        return
        success = osrs.magic.cast_spell(spell)
        
        if success:
            print("✓ Spell cast successfully")
            
            # For spells that require target, check if spell is active
            if spell.requires_target:
                time.sleep(0.5)
                if osrs.magic.is_spell_active(spell.name):
                    print("✓ Spell is active and awaiting target")
                    print(f"  Active spell: {spell.name}")
                else:
                    print("⚠ Spell may not require target or already completed")
        else:
            print("✗ Failed to cast spell")
    
    def test_is_spell_active(self):
        """Test detecting active spell state."""
        print("\n=== Is Spell Active Test ===")
        osrs = self.init_osrs()
        
        spell = input("\nEnter spell name to check if active (e.g. 'Varrock Teleport'): ").strip()
        
        while True:
            if keyboard.is_pressed('esc'):
                break
            
            if keyboard.is_pressed('space'):
                is_active = osrs.magic.is_spell_active(spell)
                
                print(f"\n{'✓' if is_active else '✗'} Spell Active: {spell}")
                
                time.sleep(0.5)  # Debounce
            
            time.sleep(0.05)
    
    def test_rune_counting(self):
        """Test rune counting in inventory."""
        print("\n=== Rune Counting Test ===")
        osrs = self.init_osrs()
        
        from config.items import Runes
        
        # Get all runes
        all_runes = [
            Runes.AIR_RUNE,
            Runes.WATER_RUNE,
            Runes.EARTH_RUNE,
            Runes.FIRE_RUNE,
            Runes.MIND_RUNE,
            Runes.BODY_RUNE,
            Runes.COSMIC_RUNE,
            Runes.CHAOS_RUNE,
            Runes.NATURE_RUNE,
            Runes.LAW_RUNE,
            Runes.DEATH_RUNE,
            Runes.BLOOD_RUNE,
            Runes.SOUL_RUNE,
        ]
        
        print("\nCounting runes in inventory:\n")
        osrs.inventory.populate()
        
        found_any = False
        for rune in all_runes:
            count = osrs.inventory.count_item(rune.id)
            if count > 0:
                print(f"✓ {rune.name}: {count}")
                found_any = True
        
        if not found_any:
            print("⚠ No runes found in inventory")
    
    def test_wait_for_spell_cast(self):
        """Test waiting for spell cast animation."""
        print("\n=== Wait for Spell Cast Test ===")
        osrs = self.init_osrs()
        
        from config.spells import StandardSpells
        
        print("\nThis test will cast a spell and wait for the animation.")
        print("Make sure you have the required runes!")
        
        # Use Varrock teleport as it has a clear animation
        spell = StandardSpells.VARROCK_TELEPORT
        
        if not osrs.magic.can_cast_spell(spell):
            print(f"✗ Cannot cast {spell.name} - check requirements")
            return
        
        print(f"\nCasting {spell.name}...")
        success = osrs.magic.cast_spell(spell)
        
        if not success:
            print("✗ Failed to cast spell")
            return
        
        print("Waiting for spell cast animation...")
        animation_detected = osrs.magic.wait_for_spell_cast(timeout=5.0)
        
        if animation_detected:
            print("✓ Spell cast animation detected and completed")
        else:
            print("⚠ Animation not detected (may have already completed)")
    
    def run_magic_tests(self):
        """Run magic testing menu."""
        self.current_menu = "magic"
        
        test_map = {
            'o': ("Open Magic Tab", self.test_open_magic_tab),
            'l': ("Get Magic Level", self.test_magic_level),
            'r': ("Check Spell Requirements", self.test_check_spell_requirements),
            'c': ("Cast Spell", self.test_cast_spell),
            'a': ("Is Spell Active", self.test_is_spell_active),
            'n': ("Count Runes", self.test_rune_counting),
            'w': ("Wait for Spell Cast", self.test_wait_for_spell_cast),
        }
        
        print("\n" + "="*60)
        print("MAGIC HANDLER TESTS")
        print("="*60)
        print("O - Open Magic Tab")
        print("L - Get Magic Level")
        print("R - Check Spell Requirements")
        print("C - Cast Spell")
        print("A - Is Spell Active (requires target spell)")
        print("N - Count Runes in Inventory")
        print("W - Wait for Spell Cast Animation")
        print("\nESC - Return to Main Menu")
        print("="*60)
        
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
            '8': ("Login/Auth", self.run_login_tests),
            '9': ("Color Registry", self.run_registry_tests),
            '0': ("Navigation", self.run_navigation_tests),
            'p': ("Pathfinding", self.run_pathfinding_tests),
            'm': ("Mining Skill", self.run_mining_tests),
            'w': ("Woodcutting Skill", self.run_woodcutting_tests),
            'c': ("Combat Handler", self.run_combat_tests),
            'g': ("Magic Handler", self.run_magic_tests),
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
            print("8 - Login/Authentication Tests")
            print("9 - Color Registry Tests")
            print("0 - Navigation Tests")
            print("P - Pathfinding Tests")
            print("M - Mining Skill Tests")
            print("W - Woodcutting Skill Tests")
            print("C - Combat Handler Tests")
            print("G - Magic Handler Tests (NEW)")
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

