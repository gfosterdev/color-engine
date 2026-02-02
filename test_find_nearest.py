"""
Quick test for the new /find_nearest API endpoint.
Tests finding both game objects and NPCs by ID.
"""

from client.runelite_api import RuneLiteAPI


def test_find_nearest():
    """Test the find_nearest_by_id endpoint."""
    api = RuneLiteAPI()
    
    print("="*60)
    print("Testing /find_nearest API Endpoint")
    print("="*60)
    
    # Test with a common bank object ID (Varrock West Bank booth)
    print("\n1. Testing with Bank Booth ID (10583) as OBJECT:")
    bank_result = api.get_nearest_by_id(10583, "object")
    if bank_result:
        print(f"   Result: {bank_result}")
        if bank_result.get('found'):
            print(f"   ✓ Found {bank_result.get('type')}")
            print(f"   World: ({bank_result.get('worldX')}, {bank_result.get('worldY')}, {bank_result.get('plane')})")
            print(f"   Distance: {bank_result.get('distance')} tiles")
        else:
            print("   ✗ Not found")
    else:
        print("   ✗ API request failed")
    
    # Test with a common NPC ID (Man - ID 1)
    print("\n2. Testing with Man NPC ID (1) as NPC:")
    npc_result = api.get_nearest_by_id(1, "npc")
    if npc_result:
        print(f"   Result: {npc_result}")
        if npc_result.get('found'):
            print(f"   ✓ Found {npc_result.get('type')}: {npc_result.get('name', 'N/A')}")
            print(f"   World: ({npc_result.get('worldX')}, {npc_result.get('worldY')}, {npc_result.get('plane')})")
            print(f"   Distance: {npc_result.get('distance')} tiles")
        else:
            print("   ✗ Not found")
    else:
        print("   ✗ API request failed")
    
    # Test with an ID that likely doesn't exist
    print("\n3. Testing with non-existent NPC ID (99999):")
    invalid_result = api.get_nearest_by_id(99999, "npc")
    if invalid_result:
        print(f"   Result: {invalid_result}")
        if not invalid_result.get('found'):
            print("   ✓ Correctly returned not found")
        else:
            print(f"   Unexpected: Found something")
    else:
        print("   ✗ API request failed")
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_find_nearest()
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
