"""
Test script for RuneLite HTTP Server Plugin API
Showcases various endpoints and functionality available through the plugin.

Usage:
    python test_runelite_api.py

Interactive Menu:
    - Select individual API tests by number (1-8)
    - Each test runs independently
    - Press Enter after each test to return to menu
    - Option 5 allows testing custom endpoints with raw JSON output
    - Option 0 to quit

Requirements:
    - RuneLite must be running
    - HTTP Server plugin must be enabled
    - Must be logged into OSRS
"""

import requests
import json
import time
from typing import Any, Dict, List, Optional, Union


class RuneLiteAPI:
    """Wrapper class for RuneLite HTTP Server plugin API."""
    
    def __init__(self, host='localhost', port=8080):
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        
    def _get(self, endpoint: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
        """Make GET request to API endpoint."""
        response = None
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", timeout=2)
            response.raise_for_status()
            
            # Handle empty responses that aren't valid JSON
            if not response.text or response.text.strip() == '':
                return None
            
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            # JSONDecodeError means response was received but wasn't valid JSON
            if response:
                print(f"❌ Error parsing JSON from /{endpoint}: {e}")
                print(f"   Response text: {response.text[:100]}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error accessing /{endpoint}: {e}")
            return None
    
    def get_stats(self) -> Optional[List[Dict[str, Any]]]:
        """Get all player stats (skills, levels, XP)."""
        result = self._get("stats")
        return result if isinstance(result, list) else None
    
    def get_inventory(self) -> Optional[List[Dict[str, Any]]]:
        """Get inventory items."""
        result = self._get("inventory")
        return result if isinstance(result, list) else None
    
    def get_equipment(self) -> Optional[List[Dict[str, Any]]]:
        """Get equipped items."""
        result = self._get("equipment")
        return result if isinstance(result, list) else None
    
    def is_server_running(self) -> bool:
        """Check if HTTP server is responding."""
        try:
            response = self.session.get(f"{self.base_url}/stats", timeout=1)
            return response.status_code == 200
        except:
            return False
    
    def call_endpoint(self, endpoint: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
        """Call any custom endpoint."""
        return self._get(endpoint)
    
    def discover_endpoints(self) -> Dict[str, bool]:
        """Test common endpoints to see which are available."""
        endpoints = [
            'stats', 'inventory', 'equipment', 'bank', 'location', 
            'health', 'prayer', 'run-energy', 'xp', 'combat', 'events',
            'world', 'position', 'skills', 'player', 'animation'
        ]
        results = {}
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}/{endpoint}", timeout=1)
                results[endpoint] = response.status_code == 200
            except:
                results[endpoint] = False
        return results


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_connection(api: RuneLiteAPI):
    """Test API connection."""
    print_section("Testing Connection")
    if api.is_server_running():
        print("✅ Successfully connected to RuneLite HTTP Server")
        print(f"   API URL: {api.base_url}")
    else:
        print("❌ Failed to connect to RuneLite HTTP Server")
        print("   Make sure:")
        print("   1. RuneLite is running")
        print("   2. HTTP Server plugin is enabled")
        print("   3. You are logged into the game")
        return False
    return True


def test_stats(api: RuneLiteAPI):
    """Test and display player stats."""
    print_section("Player Stats")
    stats = api.get_stats()
    
    if not stats:
        print("❌ Could not retrieve stats")
        return
    
    print(f"✅ Retrieved {len(stats)} skills\n")
    
    # Display combat stats
    combat_skills = ["Attack", "Strength", "Defence", "Hitpoints", "Ranged", "Prayer", "Magic"]
    print("🗡️  Combat Stats:")
    for stat in stats:
        if stat['stat'] in combat_skills:
            boosted_indicator = ""
            if stat['boostedLevel'] != stat['level']:
                diff = stat['boostedLevel'] - stat['level']
                boosted_indicator = f" ({diff:+d})"
            print(f"   {stat['stat']:12} - Level: {stat['boostedLevel']}{boosted_indicator} | XP: {stat['xp']:,}")
    
    # Display gathering skills
    gathering_skills = ["Mining", "Fishing", "Woodcutting", "Farming", "Hunter"]
    print("\n⛏️  Gathering Skills:")
    for stat in stats:
        if stat['stat'] in gathering_skills:
            print(f"   {stat['stat']:12} - Level: {stat['level']} | XP: {stat['xp']:,}")
    
    # Find highest skill
    highest = max(stats, key=lambda x: x['level'])
    print(f"\n🏆 Highest Skill: {highest['stat']} (Level {highest['level']})")
    
    # Calculate total level
    total_level = sum(stat['level'] for stat in stats)
    print(f"📊 Total Level: {total_level}")


def test_inventory(api: RuneLiteAPI):
    """Test and display inventory."""
    print_section("Inventory")
    inventory = api.get_inventory()
    
    if inventory is None:
        print("❌ Could not retrieve inventory")
        return
    
    # Filter out empty slots
    items = [item for item in inventory if item.get('id', -1) != -1]
    
    if not items:
        print("📦 Inventory is empty")
        return
    
    print(f"✅ Found {len(items)} items in inventory\n")
    
    for i, item in enumerate(items, 1):
        item_name = item.get('name', 'Unknown')
        item_id = item.get('id', 0)
        quantity = item.get('quantity', 1)
        
        quantity_str = f"x{quantity}" if quantity > 1 else ""
        print(f"   {i:2}. {item_name} (ID: {item_id}) {quantity_str}")


def test_equipment(api: RuneLiteAPI):
    """Test and display equipped items."""
    print_section("Equipment")
    equipment = api.get_equipment()
    
    if equipment is None:
        print("❌ Could not retrieve equipment")
        return
    
    # Filter out empty slots
    equipped = [item for item in equipment if item.get('id', -1) != -1]
    
    if not equipped:
        print("👔 No equipment worn")
        return
    
    print(f"✅ Found {len(equipped)} equipped items\n")
    
    # Equipment slot names
    slot_names = {
        0: "Head", 1: "Cape", 2: "Neck", 3: "Weapon", 4: "Body",
        5: "Shield", 6: "Legs", 7: "Hands", 8: "Feet", 9: "Ring",
        10: "Ammo"
    }
    
    for item in equipped:
        slot = item.get('slot', -1)
        slot_name = slot_names.get(slot, f"Slot {slot}")
        item_name = item.get('name', 'Unknown')
        item_id = item.get('id', 0)
        
        print(f"   {slot_name:8} - {item_name} (ID: {item_id})")


def test_realtime_monitoring(api: RuneLiteAPI):
    """Monitor stats in real-time."""
    print_section("Real-time Monitoring")
    print("Monitoring HP and Prayer every 2 seconds...")
    print("Press Ctrl+C to stop\n")
    
    try:
        last_hp = None
        last_prayer = None
        
        for i in range(10):  # Monitor for 20 seconds
            stats = api.get_stats()
            if stats:
                hp_stat = next((s for s in stats if s['stat'] == 'Hitpoints'), None)
                prayer_stat = next((s for s in stats if s['stat'] == 'Prayer'), None)
                
                if hp_stat and prayer_stat:
                    hp = hp_stat['boostedLevel']
                    hp_max = hp_stat['level']
                    prayer = prayer_stat['boostedLevel']
                    prayer_max = prayer_stat['level']
                    
                    # Detect changes
                    hp_change = ""
                    prayer_change = ""
                    
                    if last_hp is not None and hp != last_hp:
                        diff = hp - last_hp
                        hp_change = f" ({diff:+d})"
                    
                    if last_prayer is not None and prayer != last_prayer:
                        diff = prayer - last_prayer
                        prayer_change = f" ({diff:+d})"
                    
                    # Create HP and Prayer bars
                    hp_percent = hp / hp_max
                    prayer_percent = prayer / prayer_max
                    
                    hp_bar = "█" * int(hp_percent * 20) + "░" * (20 - int(hp_percent * 20))
                    prayer_bar = "█" * int(prayer_percent * 20) + "░" * (20 - int(prayer_percent * 20))
                    
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] ❤️  HP: {hp}/{hp_max} {hp_bar}{hp_change}")
                    print(f"{'':11}🙏 Prayer: {prayer}/{prayer_max} {prayer_bar}{prayer_change}\n")
                    
                    last_hp = hp
                    last_prayer = prayer
            
            time.sleep(2)
        
        print("✅ Monitoring complete")
        
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")


def test_endpoint_discovery(api: RuneLiteAPI):
    """Discover which endpoints are available."""
    print_section("Endpoint Discovery")
    print("Testing common endpoint patterns...\n")
    
    results = api.discover_endpoints()
    
    available = [k for k, v in results.items() if v]
    unavailable = [k for k, v in results.items() if not v]
    
    print("✅ Available Endpoints:")
    for endpoint in available:
        print(f"   /{endpoint}")
    
    print(f"\n❌ Unavailable Endpoints ({len(unavailable)}):")
    for endpoint in unavailable:
        print(f"   /{endpoint}")
    
    print(f"\n📊 Summary: {len(available)}/{len(results)} endpoints active")
    

def test_custom_endpoint(api: RuneLiteAPI):
    """Test a custom endpoint."""
    print_section("Custom Endpoint Test")
    print("Known working endpoints: stats, inventory, equipment")
    print("Tip: Use option 4 to discover all available endpoints")
    endpoint = input("\nEnter endpoint name: ").strip()
    
    if not endpoint:
        print("❌ No endpoint provided")
        return
    
    print(f"\n🔍 Calling /{endpoint}...")
    result = api.call_endpoint(endpoint)
    
    if result is None:
        print("❌ No data returned")
        return
    
    print("\n✅ Response received:")
    print("\n" + "="*70)
    print(json.dumps(result, indent=2))
    print("="*70)


def compare_with_current_system():
    """Compare API approach vs current CV approach."""
    print_section("API vs Computer Vision Comparison")
    
    print("\n📊 Current System (Computer Vision):")
    print("   ✅ Can click on game objects")
    print("   ✅ Can detect colors on screen")
    print("   ✅ Works with any client")
    print("   ❌ Slow (OCR, image processing)")
    print("   ❌ Unreliable (lighting, overlays)")
    print("   ❌ Can't see exact item IDs")
    print("   ❌ Can't see exact coordinates")
    
    print("\n🌐 RuneLite HTTP API:")
    print("   ✅ Fast (instant JSON response)")
    print("   ✅ Accurate (exact game state)")
    print("   ✅ Detailed (item IDs, exact XP, coordinates)")
    print("   ✅ No visual parsing needed")
    print("   ❌ Requires RuneLite plugin")
    print("   ❌ Still needs CV for clicking")
    
    print("\n💡 Recommended Hybrid Approach:")
    print("   ✓ Use API for game state detection")
    print("   ✓ Use CV for finding and clicking objects")
    print("   ✓ Best of both worlds!")


def print_menu():
    """Display the main menu."""
    print("\n" + "="*70)
    print("  🎮 RuneLite HTTP Server API - Interactive Test Menu")
    print("="*70)
    print("\n📡 API Endpoints:")
    print("  1 - Test Connection")
    print("  2 - Get Player Stats")
    print("  3 - Get Inventory")
    print("  4 - Discover All Endpoints")
    print("  5 - Get Equipment")
    print("  6 - Custom Endpoint (raw JSON)")
    print("\n📊 Monitoring:")
    print("  7 - Real-time HP/Prayer Monitor")
    print("\n📖 Information:")
    print("  8 - API vs CV Comparison")
    print("\n🔄 Batch Operations:")
    print("  9 - Run All Tests")
    print("\n❌ Exit:")
    print("  0 - Quit")
    print("\n" + "="*70)


def main():
    """Run interactive test menu."""
    print("\n" + "🎮" * 35)
    print("  RuneLite HTTP Server Plugin API Test Suite")
    print("🎮" * 35)
    
    api = RuneLiteAPI()
    
    # Initial connection check
    if not test_connection(api):
        print("\n⚠️  Warning: Could not connect to API")
        print("   You can still use the menu, but API calls will fail")
        input("\nPress Enter to continue...")
    
    while True:
        print_menu()
        choice = input("\nSelect an option (0-9): ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        
        elif choice == '1':
            test_connection(api)
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            test_stats(api)
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            test_inventory(api)
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            test_endpoint_discovery(api)
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            test_equipment(api)
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            test_custom_endpoint(api)
            input("\nPress Enter to continue...")
        
        elif choice == '7':
            test_realtime_monitoring(api)
            input("\nPress Enter to continue...")
        
        elif choice == '8':
            compare_with_current_system()
            input("\nPress Enter to continue...")
        
        elif choice == '9':
            print_section("Running All Tests")
            test_stats(api)
            test_inventory(api)
            test_equipment(api)
            compare_with_current_system()
            print("\n✅ All tests completed!")
            input("\nPress Enter to continue...")
        
        else:
            print("\n❌ Invalid option. Please select 0-9.")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
