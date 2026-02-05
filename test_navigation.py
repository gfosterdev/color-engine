"""
Navigation Testing Tool for OSRS Bot.

Interactive testing tool for bot navigation systems. Allows testing pathfinding,
coordinate reading, minimap interaction, and full navigation paths for specific bots.

Features:
- Test coordinate reading (world/scene coordinates)
- Test minimap clicking with yaw rotation
- Test pathfinding between locations
- Test full bot navigation paths (bank -> combat area -> bank)
- Visualize paths and waypoints
- Test stuck detection and re-pathing
- Profile-specific navigation testing

Usage:
    python test_navigation.py
    
    Select bot profile and test navigation features interactively.
"""

import keyboard
import time
import random
import math
import os
from typing import Optional, Dict, List, Tuple, Any
from util import Window
from client.osrs import OSRS
from client.navigation import NavigationManager
from core.config import load_profile
from config.locations import (
    BankLocations,
    TrainingLocations,
    MiningLocations,
    WoodcuttingLocations,
    LocationCategory
)


class NavigationTester:
    """Interactive navigation testing interface."""
    
    def __init__(self, profile_name: Optional[str] = None):
        """
        Initialize navigation tester.
        
        Args:
            profile_name: Optional profile to load (or select interactively)
        """
        print("=" * 70)
        print("OSRS BOT NAVIGATION TESTER")
        print("=" * 70)
        
        # Initialize window connection
        print("\nInitializing window connection...")
        self.window = Window()
        self.window.find(title="RuneLite - xJawj", exact_match=True)
        
        if not self.window.window:
            raise RuntimeError("Could not find RuneLite window!")
        
        print(f"✓ Connected to: {self.window.window['title']}")
        
        # Profile selection
        self.profile_name = profile_name or self._select_profile()
        self.profile_config = load_profile(self.profile_name)
        print(f"✓ Loaded profile: {self.profile_name}")
        
        # Initialize OSRS client
        print("\nInitializing OSRS client...")
        self.osrs = OSRS(self.profile_config)
        self.navigation: NavigationManager = self.osrs.navigation
        print("✓ OSRS client ready")
        
        # Bot-specific data
        self.bot_type = self._detect_bot_type()
        self.bank_location = self._get_bank_location()
        self.combat_area = self._get_combat_area()
        
        print(f"\nBot Type: {self.bot_type}")
        print(f"Bank: {self.bank_location}")
        print(f"Combat Area: {self.combat_area}")
        print("\n" + "=" * 70)
        print("Navigation tester initialized!")
        print("=" * 70 + "\n")
    
    def _select_profile(self) -> str:
        """Prompt user to select a bot profile."""
        print("\n" + "=" * 70)
        print("PROFILE SELECTION")
        print("=" * 70)
        
        # List available profiles
        profiles_dir = "config/profiles"
        profiles = [f.replace('.json', '') for f in os.listdir(profiles_dir) if f.endswith('.json')]
        
        print("\nAvailable profiles:")
        for idx, profile in enumerate(profiles, 1):
            print(f"  {idx}. {profile}")
        
        while True:
            try:
                choice = input("\nSelect profile number: ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(profiles):
                    return profiles[idx]
                print("Invalid selection. Try again.")
            except (ValueError, KeyboardInterrupt):
                print("\nDefaulting to gargoyle_killer_canifis")
                return "gargoyle_killer_canifis"
    
    def _detect_bot_type(self) -> str:
        """Detect bot type from profile name."""
        name = self.profile_name.lower()
        if 'gargoyle' in name:
            return "gargoyle_killer"
        elif 'cow' in name:
            return "cow_killer"
        elif 'yew' in name or 'woodcut' in name:
            return "woodcutter"
        elif 'iron' in name or 'mine' in name or 'miner' in name:
            return "miner"
        else:
            return "unknown"
    
    def _get_bank_location(self) -> Tuple[int, int, int]:
        """Get bank location from profile."""
        try:
            # Try to get from profile
            combat_settings = getattr(self.profile_config, 'combat_settings', None)
            skill_settings = getattr(self.profile_config, 'skill_settings', {})
            
            bank_name = ''
            if combat_settings and isinstance(combat_settings, dict):
                bank_name = combat_settings.get('bank_location', '')
            if not bank_name:
                bank_name = skill_settings.get('bank_location', '')
            
            # Map common bank names to coordinates
            bank_map = {
                'canifis': BankLocations.CANIFIS,
                'varrock_west': BankLocations.VARROCK_WEST,
                'varrock_east': BankLocations.VARROCK_EAST,
                'edgeville': BankLocations.EDGEVILLE,
                'lumbridge': BankLocations.LUMBRIDGE_CASTLE,
                'falador_west': BankLocations.FALADOR_WEST,
                'falador_east': BankLocations.FALADOR_EAST,
            }
            
            bank_key = bank_name.lower().replace(' ', '_')
            if bank_key in bank_map:
                return bank_map[bank_key]
            
            # Default fallback
            return BankLocations.VARROCK_WEST
        except Exception as e:
            print(f"Warning: Could not determine bank location: {e}")
            return BankLocations.VARROCK_WEST
    
    def _get_combat_area(self) -> Optional[Tuple[int, int, int]]:
        """Get combat/training area from profile."""
        try:
            # For combat bots
            combat_settings = getattr(self.profile_config, 'combat_settings', None)
            area_name = ''
            if combat_settings and isinstance(combat_settings, dict):
                area_name = combat_settings.get('combat_area', '')
            
            # Map area names to coordinates
            if area_name and 'gargoyle' in area_name.lower():
                return TrainingLocations.SLAYER_TOWER_GARGOYLES
            elif area_name and 'cow' in area_name.lower():
                return TrainingLocations.LUMBRIDGE_COWS
            
            # For skill bots
            skill_settings = getattr(self.profile_config, 'skill_settings', {})
            if 'mining_location' in skill_settings:
                return MiningLocations.VARROCK_WEST_MINE
            elif 'woodcutting_location' in skill_settings:
                return WoodcuttingLocations.EDGEVILLE_YEWS
            
            return None
        except Exception as e:
            print(f"Warning: Could not determine combat area: {e}")
            return None
    
    # =================================================================
    # TEST METHODS
    # =================================================================
    
    def test_coordinate_reading(self):
        """Test coordinate reading from RuneLite API."""
        print("\n" + "=" * 70)
        print("COORDINATE READING TEST")
        print("=" * 70)
        print("Reading coordinates from RuneLite API...")
        print("Press ESC to stop\n")
        
        while True:
            if keyboard.is_pressed('esc'):
                print("\nTest stopped by user.")
                break
            
            try:
                # Get coordinates from API
                coords = self.navigation.api.get_coords()
                if coords:
                    world = coords.get('world', {})
                    scene = coords.get('local', {})
                    plane = coords.get('plane', 0)
                    
                    print(f"World: ({world.get('x', '?')}, {world.get('y', '?')}, {plane}) | "
                          f"Scene: ({scene.get('x', '?')}, {scene.get('y', '?')})")
                else:
                    print("Failed to read coordinates from API")
                
                time.sleep(0.5)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
    
    def test_camera_reading(self):
        """Test camera yaw reading from RuneLite API."""
        print("\n" + "=" * 70)
        print("CAMERA YAW READING TEST")
        print("=" * 70)
        print("Reading camera yaw from RuneLite API...")
        print("Press ESC to stop\n")
        
        while True:
            if keyboard.is_pressed('esc'):
                print("\nTest stopped by user.")
                break
            
            try:
                camera = self.navigation.api.get_camera()
                if camera:
                    yaw = camera.get('yaw', 0)
                    pitch = camera.get('pitch', 0)
                    print(f"Camera - Yaw: {yaw} (0-2048) | Pitch: {pitch}")
                else:
                    print("Failed to read camera from API")
                
                time.sleep(0.5)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
    
    def test_pathfinding(self):
        """Test pathfinding between two points."""
        print("\n" + "=" * 70)
        print("PATHFINDING TEST")
        print("=" * 70)
        
        # Get current position
        coords = self.navigation.api.get_coords()
        if not coords or 'world' not in coords:
            print("ERROR: Cannot read current coordinates!")
            return
        
        start_x = coords['world']['x']
        start_y = coords['world']['y']
        start_z = coords.get('plane', 0)
        
        print(f"\nCurrent position: ({start_x}, {start_y}, {start_z})")
        print("\nSelect destination:")
        print("  1. Bank location")
        print("  2. Combat/training area")
        print("  3. Custom coordinates")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            dest = self.bank_location
            dest_name = "Bank"
        elif choice == '2':
            if not self.combat_area:
                print("ERROR: No combat area defined for this bot!")
                return
            dest = self.combat_area
            dest_name = "Combat Area"
        elif choice == '3':
            try:
                x = int(input("Enter destination X: "))
                y = int(input("Enter destination Y: "))
                z = int(input("Enter destination Z (plane): "))
                dest = (x, y, z)
                dest_name = f"({x}, {y}, {z})"
            except ValueError:
                print("Invalid coordinates!")
                return
        else:
            print("Invalid choice!")
            return
        
        print(f"\nFinding path from ({start_x}, {start_y}, {start_z}) to {dest_name} {dest}")
        print("Generating path with variance...\n")
        
        # Ensure pathfinding is loaded
        if not self.navigation._ensure_pathfinding_loaded():
            print("ERROR: Pathfinding system not available!")
            print("Run: python scripts/download_collision_data.py")
            return
        
        # Get variance level from profile (use moderate as default)
        variance_map = {'conservative': 0.15, 'moderate': 0.25, 'aggressive': 0.35}
        variance_level = getattr(self.profile_config, 'pathfinding_config', {}).get('variance_level', 'moderate')
        variance = variance_map.get(variance_level, 0.25)
        
        try:
            # Access the global pathfinder
            from client.navigation import _pathfinder
            if _pathfinder is None:
                print("ERROR: Pathfinder not initialized!")
                return
            
            path = _pathfinder.find_path(
                (start_x, start_y, start_z),
                (dest[0], dest[1], dest[2]),
                variance_level=variance_level,
                use_cache=True
            )
            
            if path:
                print(f"✓ Path found! {len(path)} waypoints")
                print(f"  Distance: ~{len(path)} tiles")
                print(f"  Variance: {variance * 100}%")
                
                # Show first and last few waypoints
                print("\nFirst 5 waypoints:")
                for i, wp in enumerate(path[:5]):
                    print(f"  {i+1}. ({wp[0]}, {wp[1]}, {wp[2]})")
                
                if len(path) > 10:
                    print(f"\n  ... {len(path) - 10} more waypoints ...\n")
                    print("Last 5 waypoints:")
                    for i, wp in enumerate(path[-5:], len(path)-4):
                        print(f"  {i}. ({wp[0]}, {wp[1]}, {wp[2]})")
                
                # Ask if user wants to visualize
                visualize = input("\nVisualize path on minimap? (y/n): ").strip().lower()
                if visualize == 'y':
                    self._visualize_path(path)
            else:
                print("✗ No path found! Destination may be unreachable or collision data missing.")
        
        except Exception as e:
            print(f"ERROR: Pathfinding failed - {e}")
            import traceback
            traceback.print_exc()
    
    def test_minimap_click(self):
        """Test minimap clicking at different angles."""
        print("\n" + "=" * 70)
        print("MINIMAP CLICKING TEST")
        print("=" * 70)
        print("\nThis test will click random points on the minimap.")
        print("Watch the player character move around.")
        print("Press ESC to stop\n")
        
        input("Press ENTER to start (make sure you're in a safe area)...")
        
        click_count = 0
        while True:
            if keyboard.is_pressed('esc'):
                print(f"\nTest stopped. Performed {click_count} clicks.")
                break
            
            try:
                # Get current position
                coords = self.navigation.api.get_coords()
                if not coords or 'world' not in coords:
                    print("Cannot read coordinates, skipping...")
                    time.sleep(1)
                    continue
                
                x = coords['world']['x']
                y = coords['world']['y']
                z = coords.get('plane', 0)
                
                # Generate random nearby target (5-10 tiles away)
                angle = random.uniform(0, 2 * 3.14159)
                distance = random.randint(5, 10)
                offset_x = int(distance * math.cos(angle))
                offset_y = int(distance * math.sin(angle))
                target_x = x + offset_x
                target_y = y + offset_y
                
                print(f"Click #{click_count + 1}: Moving from ({x}, {y}) to ({target_x}, {target_y})")
                
                # Click minimap using offset method
                if self.navigation._click_minimap_offset(offset_x, offset_y):
                    click_count += 1
                    # Wait for movement
                    time.sleep(random.uniform(1.5, 3.0))
                else:
                    print("  Failed to click minimap")
                    time.sleep(1)
            
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
    
    def test_walk_to_location(self):
        """Test walking to a specific location."""
        print("\n" + "=" * 70)
        print("WALK TO LOCATION TEST")
        print("=" * 70)
        
        print("\nSelect destination:")
        print("  1. Bank location")
        print("  2. Combat/training area")
        print("  3. Custom coordinates")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            dest = self.bank_location
            dest_name = "Bank"
        elif choice == '2':
            if not self.combat_area:
                print("ERROR: No combat area defined for this bot!")
                return
            dest = self.combat_area
            dest_name = "Combat Area"
        elif choice == '3':
            try:
                x = int(input("Enter destination X: "))
                y = int(input("Enter destination Y: "))
                z = int(input("Enter destination Z (plane): "))
                dest = (x, y, z)
                dest_name = f"({x}, {y}, {z})"
            except ValueError:
                print("Invalid coordinates!")
                return
        else:
            print("Invalid choice!")
            return
        
        print(f"\nWalking to {dest_name} at {dest}")
        print("This will use pathfinding and walk the full path...")
        print("Press ESC during walk to cancel\n")
        
        input("Press ENTER to start walking...")
        
        try:
            success = self.navigation.walk_to_tile(dest[0], dest[1], dest[2])
            if success:
                print(f"✓ Successfully reached {dest_name}!")
            else:
                print(f"✗ Failed to reach {dest_name}")
        except KeyboardInterrupt:
            print("\nWalk cancelled by user")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    def test_bot_navigation_cycle(self):
        """Test full bot navigation cycle (bank -> area -> bank)."""
        print("\n" + "=" * 70)
        print("BOT NAVIGATION CYCLE TEST")
        print("=" * 70)
        
        if not self.combat_area:
            print("ERROR: No combat area defined for this bot!")
            print("This test requires both bank and combat/training area.")
            return
        
        print(f"\nThis will test the full navigation cycle:")
        print(f"  1. Current location -> Bank ({self.bank_location})")
        print(f"  2. Bank -> Combat Area ({self.combat_area})")
        print(f"  3. Combat Area -> Bank")
        print("\nTotal expected time: 5-15 minutes depending on distance")
        
        response = input("\nStart navigation cycle? (y/n): ").strip().lower()
        if response != 'y':
            print("Test cancelled.")
            return
        
        try:
            # Phase 1: Go to bank
            print("\n" + "-" * 70)
            print("PHASE 1: Walking to bank...")
            print("-" * 70)
            success = self.navigation.walk_to_tile(
                self.bank_location[0],
                self.bank_location[1],
                self.bank_location[2]
            )
            if success:
                print("✓ Reached bank!")
            else:
                print("✗ Failed to reach bank")
                return
            
            time.sleep(2)
            
            # Phase 2: Go to combat area
            print("\n" + "-" * 70)
            print("PHASE 2: Walking to combat/training area...")
            print("-" * 70)
            success = self.navigation.walk_to_tile(
                self.combat_area[0],
                self.combat_area[1],
                self.combat_area[2]
            )
            if success:
                print("✓ Reached combat area!")
            else:
                print("✗ Failed to reach combat area")
                return
            
            time.sleep(2)
            
            # Phase 3: Return to bank
            print("\n" + "-" * 70)
            print("PHASE 3: Returning to bank...")
            print("-" * 70)
            success = self.navigation.walk_to_tile(
                self.bank_location[0],
                self.bank_location[1],
                self.bank_location[2]
            )
            if success:
                print("✓ Returned to bank!")
            else:
                print("✗ Failed to return to bank")
                return
            
            print("\n" + "=" * 70)
            print("NAVIGATION CYCLE COMPLETE!")
            print("=" * 70)
            print("✓ All phases completed successfully")
            print("✓ Bot can navigate full cycle")
        
        except KeyboardInterrupt:
            print("\nTest cancelled by user")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    def test_stuck_detection(self):
        """Test stuck detection by monitoring position changes."""
        print("\n" + "=" * 70)
        print("STUCK DETECTION TEST")
        print("=" * 70)
        print("\nMonitoring position for stuck detection...")
        print("Try walking into walls or obstacles to test stuck detection.")
        print("Press ESC to stop\n")
        
        last_pos = None
        stuck_count = 0
        move_count = 0
        
        while True:
            if keyboard.is_pressed('esc'):
                print(f"\nTest stopped. Moves: {move_count}, Stuck detections: {stuck_count}")
                break
            
            try:
                coords = self.navigation.api.get_coords()
                if not coords or 'world' not in coords:
                    time.sleep(0.5)
                    continue
                
                current_pos = (coords['world']['x'], coords['world']['y'])
                
                if last_pos:
                    if current_pos != last_pos:
                        move_count += 1
                        print(f"✓ Position changed: {last_pos} -> {current_pos} (Total moves: {move_count})")
                    else:
                        stuck_count += 1
                        if stuck_count % 5 == 0:
                            print(f"⚠ Position unchanged for {stuck_count} checks - might be stuck!")
                
                last_pos = current_pos
                time.sleep(1)
            
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
    
    def _visualize_path(self, path: List[Tuple[int, int, int]]):
        """
        Visualize path by clicking waypoints on minimap.
        
        Args:
            path: List of (x, y, z) waypoint coordinates
        """
        print("\n" + "=" * 70)
        print("PATH VISUALIZATION")
        print("=" * 70)
        print(f"Showing {min(len(path), 10)} waypoints on minimap...")
        print("Green dots will appear at waypoint locations.")
        print("Press ESC to stop\n")
        
        # Show first 10 waypoints to avoid overwhelming display
        waypoints_to_show = path[::max(1, len(path) // 10)][:10]
        
        for i, (x, y, z) in enumerate(waypoints_to_show, 1):
            if keyboard.is_pressed('esc'):
                print("\nVisualization stopped.")
                break
            
            print(f"Waypoint {i}: ({x}, {y}, {z})")
            # Just hover over the point (don't click to avoid moving)
            # This would require implementing a minimap hover function
            # For now, just display the coordinates
            time.sleep(0.5)
        
        print("\nVisualization complete!")
    
    # =================================================================
    # MENU SYSTEM
    # =================================================================
    
    def show_menu(self):
        """Show main test menu."""
        print("\n" + "=" * 70)
        print("NAVIGATION TEST MENU")
        print("=" * 70)
        print(f"Profile: {self.profile_name}")
        print(f"Bot Type: {self.bot_type}")
        print("-" * 70)
        print("  1. Test coordinate reading")
        print("  2. Test camera yaw reading")
        print("  3. Test pathfinding (calculate path)")
        print("  4. Test minimap clicking")
        print("  5. Test walk to location (single path)")
        print("  6. Test full navigation cycle (bank -> area -> bank)")
        print("  7. Test stuck detection")
        print("  0. Exit")
        print("=" * 70)
    
    def run(self):
        """Run the interactive testing menu."""
        while True:
            self.show_menu()
            choice = input("\nSelect test (0-7): ").strip()
            
            if choice == '0':
                print("\nExiting navigation tester. Goodbye!")
                break
            elif choice == '1':
                self.test_coordinate_reading()
            elif choice == '2':
                self.test_camera_reading()
            elif choice == '3':
                self.test_pathfinding()
            elif choice == '4':
                # Need to import math for minimap test
                import math
                self.test_minimap_click()
            elif choice == '5':
                self.test_walk_to_location()
            elif choice == '6':
                self.test_bot_navigation_cycle()
            elif choice == '7':
                self.test_stuck_detection()
            else:
                print("Invalid choice! Try again.")
            
            input("\nPress ENTER to return to menu...")


def main():
    """Main entry point."""
    try:
        # Optional: Pass profile name as argument
        import sys
        profile_name = sys.argv[1] if len(sys.argv) > 1 else None
        
        tester = NavigationTester(profile_name)
        tester.run()
    
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
