"""
Example usage of test_navigation.py

This example shows how to programmatically use the NavigationTester class
for automated testing or integration into other test suites.
"""

from test_navigation import NavigationTester


def example_basic_usage():
    """Basic usage: Create tester and run interactive menu."""
    # Create tester with automatic profile selection
    tester = NavigationTester()
    
    # Run interactive menu
    tester.run()


def example_profile_specific():
    """Profile-specific usage: Load specific bot profile."""
    # Create tester for gargoyle killer bot
    tester = NavigationTester(profile_name="gargoyle_killer_canifis")
    
    # Run interactive menu
    tester.run()


def example_programmatic_testing():
    """Programmatic testing: Call specific tests without menu."""
    # Create tester
    tester = NavigationTester(profile_name="gargoyle_killer_canifis")
    
    print("Running automated test sequence...")
    
    # Test 1: Read coordinates
    print("\n1. Testing coordinate reading...")
    # Note: Individual tests are designed for interactive use
    # For automated testing, you'd need to modify them
    
    # Test 2: Test pathfinding
    print("\n2. Testing pathfinding...")
    tester.test_pathfinding()
    
    print("\nAutomated test sequence complete!")


def example_custom_locations():
    """Test navigation to custom coordinates."""
    # Create tester
    tester = NavigationTester(profile_name="gargoyle_killer_canifis")
    
    # Get current position
    coords = tester.navigation.api.get_coordinates()
    if coords and 'world' in coords:
        x = coords['world']['x']
        y = coords['world']['y']
        z = coords.get('plane', 0)
        print(f"Current position: ({x}, {y}, {z})")
        
        # Test pathfinding to custom location
        # Example: 50 tiles north
        target_x = x
        target_y = y + 50
        target_z = z
        
        print(f"Testing path to: ({target_x}, {target_y}, {target_z})")
        
        # Calculate path
        path = tester.navigation.pathfinder.find_path(
            x, y, z,
            target_x, target_y, target_z,
            variance=0.25
        )
        
        if path:
            print(f"Path found with {len(path)} waypoints!")
        else:
            print("No path found!")


def example_bot_cycle_test():
    """Test full bot navigation cycle."""
    # Create tester for specific bot
    tester = NavigationTester(profile_name="gargoyle_killer_canifis")
    
    print("=" * 70)
    print("AUTOMATED BOT CYCLE TEST")
    print("=" * 70)
    
    # This would test the full cycle
    # Note: This is a long-running test (5-15 minutes)
    tester.test_bot_navigation_cycle()


def example_continuous_monitoring():
    """Example of continuous coordinate monitoring for debugging."""
    import time
    import keyboard
    
    tester = NavigationTester(profile_name="gargoyle_killer_canifis")
    
    print("Monitoring player position (Press ESC to stop)...")
    print("Format: World (x, y, z) | Distance from bank")
    
    bank = tester.bank_location
    
    while True:
        if keyboard.is_pressed('esc'):
            break
        
        coords = tester.navigation.api.get_coordinates()
        if coords and 'world' in coords:
            x = coords['world']['x']
            y = coords['world']['y']
            z = coords.get('plane', 0)
            
            # Calculate distance to bank
            import math
            dist = math.sqrt((x - bank[0])**2 + (y - bank[1])**2)
            
            print(f"Position: ({x}, {y}, {z}) | Distance to bank: {dist:.1f} tiles")
        
        time.sleep(1)


def example_validate_bot_setup():
    """Validate that bot profile has correct navigation setup."""
    profile_name = "gargoyle_killer_canifis"
    
    print(f"Validating navigation setup for: {profile_name}")
    
    try:
        tester = NavigationTester(profile_name=profile_name)
        
        print("\n✓ Profile loaded successfully")
        print(f"  Bot Type: {tester.bot_type}")
        print(f"  Bank Location: {tester.bank_location}")
        print(f"  Combat Area: {tester.combat_area}")
        
        # Check if pathfinding is available
        if tester.navigation.pathfinder:
            print("✓ Pathfinding system available")
        else:
            print("✗ Pathfinding system not available")
        
        # Check if collision data is loaded
        stats = tester.navigation.get_pathfinding_stats()
        if stats.get('collision_data_loaded'):
            print("✓ Collision data loaded")
            print(f"  Tile count: {stats.get('tile_count', 0)}")
        else:
            print("✗ Collision data not loaded")
            print("  Run: python scripts/download_collision_data.py")
        
        print("\nNavigation setup validation complete!")
        
    except Exception as e:
        print(f"✗ Validation failed: {e}")


# Main examples menu
if __name__ == "__main__":
    print("=" * 70)
    print("NAVIGATION TESTING EXAMPLES")
    print("=" * 70)
    print("\nSelect an example to run:")
    print("  1. Basic usage (interactive menu)")
    print("  2. Profile-specific usage")
    print("  3. Programmatic testing")
    print("  4. Custom locations testing")
    print("  5. Bot cycle test (5-15 min)")
    print("  6. Continuous monitoring")
    print("  7. Validate bot setup")
    print("  0. Exit")
    print("=" * 70)
    
    choice = input("\nSelect example (0-7): ").strip()
    
    if choice == '1':
        example_basic_usage()
    elif choice == '2':
        example_profile_specific()
    elif choice == '3':
        example_programmatic_testing()
    elif choice == '4':
        example_custom_locations()
    elif choice == '5':
        example_bot_cycle_test()
    elif choice == '6':
        example_continuous_monitoring()
    elif choice == '7':
        example_validate_bot_setup()
    elif choice == '0':
        print("Goodbye!")
    else:
        print("Invalid choice!")
