"""
Run the Yew Woodcutting Bot at Edgeville.

This script initializes and starts the woodcutting bot with the yew_cutter_edgeville profile.
The bot will:
- Cut yew trees at Edgeville (south of bank)
- Bank at Edgeville bank when inventory is full
- Track XP gains
- Use respawn detection for efficient tree cutting
- Perform anti-ban actions

Press Ctrl+C to stop the bot.
"""

from client.skills.woodcutting import WoodcuttingBot
import sys


def main():
    """Run the woodcutting bot."""
    print("="*60)
    print("YEW WOODCUTTING BOT - EDGEVILLE")
    print("="*60)
    print("\nProfile: yew_cutter_edgeville")
    print("Location: Edgeville yew trees (south of bank)")
    print("Bank: Edgeville bank")
    print("\nFeatures:")
    print("  - Automatic banking when full")
    print("  - XP tracking and gain monitoring")
    print("  - Tree respawn detection")
    print("  - Anti-ban behaviors")
    print("  - Birds nest collection")
    print("\nPress Ctrl+C to stop the bot")
    print("="*60)
    
    try:
        # Create bot instance
        bot = WoodcuttingBot("yew_cutter_edgeville")
        
        print("\nBot initialized successfully!")
        print(f"Trees: {[cfg['name'] for cfg in bot.tree_configs]}")
        print(f"Location: {bot.wc_location}")
        print(f"Bank: {bot.bank_location}")
        print("\nStarting bot in 3 seconds...")
        
        import time
        time.sleep(3)
        
        # Start the bot
        bot.start()
        
    except KeyboardInterrupt:
        print("\n\nBot stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
