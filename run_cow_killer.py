"""
Run the Cow Killer Bot in Lumbridge.

This script initializes and starts the cow killer bot with the cow_killer_lumbridge profile.
The bot will:
- Kill cows in Lumbridge east cow pens
- Loot cowhides
- Bank at Lumbridge castle top floor
- Navigate through gates and stairs
- Perform anti-ban actions

Press Ctrl+C to stop the bot.
"""

from core.bots.cow_killer import CowKillerBot
import sys


def main():
    """Run the cow killer bot."""
    print("="*60)
    print("COW KILLER BOT - LUMBRIDGE")
    print("="*60)
    print("\nProfile: cow_killer_lumbridge")
    print("Location: Lumbridge east cow pens")
    print("Bank: Lumbridge castle top floor")
    print("\nFeatures:")
    print("  - Kills adult cows (excludes calves)")
    print("  - Automatic cowhide looting")
    print("  - Banking when inventory full")
    print("  - Gate and stair navigation")
    print("  - Anti-ban behaviors")
    print("  - Combat statistics tracking")
    print("\nPress Ctrl+C to stop the bot")
    print("="*60)
    
    try:
        # Create bot instance (profile is loaded inside the constructor)
        bot = CowKillerBot("cow_killer_lumbridge")
        
        print("\nBot initialized successfully!")
        print(f"Target NPCs: {bot.get_target_npc_ids()}")
        print(f"Combat area: {bot.get_combat_area()}")
        print(f"Loot items: {[item.name for item in bot.get_loot_items()]}")
        print(f"Food: {[item.name for item in bot.get_food_items()]}")
        print("\nStarting bot in 3 seconds...")
        
        import time
        time.sleep(3)
        
        # Start the bot
        bot.start()
        
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("SHUTDOWN INITIATED")
        print("="*60)
        print("\nBot stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print("\n\n" + "="*60)
        print("ERROR")
        print("="*60)
        print(f"\nFailed to run bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
