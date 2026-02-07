"""
Run the Gargoyle Killer Bot at Slayer Tower.

This script initializes and starts the gargoyle killer bot with the gargoyle_killer_canifis profile.
The bot will:
- Kill gargoyles on floor 2 of Slayer Tower
- Use rock hammer to finish gargoyles
- Loot valuable drops (granite maul, mystic robes, rune items)
- Bank at Canifis
- Navigate through stairs
- Perform anti-ban actions
- Emergency teleport on low health

Requirements:
- 75 Slayer level
- Rock hammer in inventory
- Recommended 70+ combat stats

Press Ctrl+C to stop the bot.
"""

from core.bots.gargoyle_killer import GargoyleKillerBot
import sys
from core.config import DEBUG
from core.state_machine import BotState


def main():
    """Run the gargoyle killer bot."""
    print("="*60)
    print("GARGOYLE KILLER BOT - SLAYER TOWER")
    print("="*60)
    if DEBUG:
        print("\nProfile: gargoyle_killer_canifis")
        print("Location: Slayer Tower (Floor 2 - Gargoyles)")
        print("Bank: Canifis")
        print("\nRequirements:")
        print("  - 75 Slayer level")
        print("  - Rock hammer in inventory (REQUIRED)")
        print("  - Recommended 70+ combat stats")
        print("\nFeatures:")
        print("  - Kills gargoyles (combat level 111)")
        print("  - Automatic rock hammer usage")
        print("  - Loots valuable drops:")
        print("    * Granite maul")
        print("    * Mystic robes (dark)")
        print("    * Rune equipment")
        print("    * Seeds (ranarr, snapdragon)")
        print("  - Banking when inventory full or low food")
        print("  - Stair navigation")
        print("  - Anti-ban behaviors")
        print("  - Emergency teleport on low health")
        print("  - Combat statistics tracking")
        print("="*60)
    print("\nPress Ctrl+C to stop the bot")
    
    try:
        # Create bot instance (profile is loaded inside the constructor)
        bot = GargoyleKillerBot("gargoyle_killer_canifis")
        
        print("\nBot initialized successfully!")
        if DEBUG:
            print(f"Target NPCs: {bot.get_target_npc_ids()}")
            print(f"Combat area: {bot.get_combat_area()}")
            print(f"Loot items: {[item.name for item in bot.get_loot_items()]}")
            print(f"Food: {[item.name for item in bot.get_food_items()]}")
            print(f"Escape threshold: {bot.get_escape_threshold()}%")
            print(f"Food threshold: {bot.get_food_threshold()}%")
        print("\nStarting bot in 3 seconds...")
        
        import time
        time.sleep(3)
        
        # Start the bot (runs indefinitely until Ctrl+C or error)
        print("\nBot started! Press Ctrl+C to stop.\n")
        # bot.start()
        
        # Path test
        path = bot.get_path_to_combat_area()
        bot._start_path_navigation(path, BotState.COMBAT)
        bot.current_step_index = 4
        bot._handle_walking_state()
        
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("Bot stopped by user (Ctrl+C)")
        print("="*60)
        sys.exit(0)
        
    except Exception as e:
        print("\n\n" + "="*60)
        print(f"ERROR: Bot crashed!")
        print(f"Error: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
