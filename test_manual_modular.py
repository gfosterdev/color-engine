"""
Manual testing file for OSRS bot features - Modular Testing System.

Test each component in isolation without initializing unnecessary dependencies.
Navigate using number keys and submenus.
"""

import keyboard
import time
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
        option = "Talk-To"
        target = "Town Crier"

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
            time.sleep(.2)
            self.window.move_mouse_to((slot.region.x + slot.region.width, slot.region.y))
            time.sleep(.2)
            self.window.move_mouse_to((slot.region.x, slot.region.y + slot.region.height))
            time.sleep(.2)
            self.window.move_mouse_to((slot.region.x + slot.region.width, slot.region.y + slot.region.height))
            time.sleep(.2)

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
    
    def test_gameobject_find_bank_api(self):
        """Find bank booth via api"""
        api = self.init_api()
        osrs = self.init_osrs()

        bank_booth = api.get_game_object_in_viewport(10583)
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
        

        game_object = api.get_game_object_in_viewport(obj_id)
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
                # for point in points:
                #     osrs.window.move_mouse_to((point.get('x'), point.get('y')))
                #     time.sleep(0.2)
                for _ in range(5):
                    rand = polygon.random_point_inside(osrs.window.GAME_AREA)
                    osrs.window.move_mouse_to(rand)
                    time.sleep(0.5)

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
        

        npc_object = api.get_npc_in_viewport(npc_id)
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
        success = osrs.click_npc(npc_id, action)
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
        success = osrs.click_game_object(obj_id, action)
        print("✓ Click successful" if success else "✗ Click failed")

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
            password = input("\nEnter password (or press Ctrl+C to cancel): ").strip()
            
            if not password:
                print("✗ No password entered")
                return
            
            osrs = self.init_osrs()
            print("\nAttempting login...")
            result = osrs.login(password)
            
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
            's': ("Inventory Status", self.test_inventory_status),
            'o': ("Check if Open", self.test_inventory_open_check),
            't': ("Test slot regions", self.test_inventory_regions),
            '1': ("Click Slot 0", self.test_click_inventory_slot),
            '3': ("Find Item by Color", self.test_find_inventory_item),
        }
        
        print("\n" + "="*60)
        print("INVENTORY MODULE TESTS")
        print("="*60)
        print("S - Inventory Status")
        print("O - Check if Open")
        print("T - Test slot regions")
        print("1 - Click Slot")
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
            's': ("Find Game Object via ID", self.test_gameobject_find_api),
            'c': ("Click on Game Object via ID", self.test_click_on_gameobject),
            'l': ("Find NPC via ID", self.test_npc_find_api),
            'k': ("Click on NPC via ID", self.test_click_on_npc),
            '1': ("Find Iron Ore", self.test_gameobject_find_ore),
            '2': ("Interact with Ore", self.test_gameobject_interact_ore),
            '3': ("Find Bank Booth", self.test_gameobject_find_bank),
            'e': ("Find Bank Booth (api)", self.test_gameobject_find_bank_api),
            '4': ("Find Custom Color", self.test_gameobject_custom_color),
            '5': ("Right-Click Menu", self.test_gameobject_right_click),
            '6': ("Find NPCS in Viewport", self.test_npc_in_viewport),
            '7': ("Find Game Objects in Viewport", self.test_game_object_in_viewport)
        }
        
        print("\n" + "="*60)
        print("GAME OBJECT INTERACTION TESTS")
        print("="*60)
        print("S - Find Game Object by ID")
        print("C - Click on Game Object by ID")
        print("L - Find NPC by ID")
        print("K - Click on NPC by ID")
        print("1 - Find Iron Ore")
        print("2 - Interact with Ore")
        print("3 - Find Bank Booth")
        print("e - Find Bank Booth (API)")
        print("4 - Find Custom Color")
        print("5 - Right-Click Menu Test")
        print("6 - Find NPCS in Viewport")
        print("7 - Find Game Objects in Viewport")
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
            '8': ("Login/Auth", self.run_login_tests),
            '9': ("Color Registry", self.run_registry_tests),
            '0': ("Navigation", self.run_navigation_tests),
            'p': ("Pathfinding", self.run_pathfinding_tests),
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
            print("P - Pathfinding Tests (NEW)")
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
