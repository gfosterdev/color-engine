"""
Test the status line functionality in skill bots.

This script demonstrates the persistent status line that updates
in place showing bot state, inventory, resources gathered, and runtime.
"""

from client.skills.woodcutting import WoodcuttingBot
from client.skills.mining import MiningBot
import sys


def test_woodcutting_status():
    """Test woodcutting bot with status line."""
    print("="*70)
    print("TESTING WOODCUTTING BOT STATUS LINE")
    print("="*70)
    print("\nThe status line will show:")
    print("  - Current bot state (GATHERING, BANKING, WALKING)")
    print("  - Inventory capacity (X/28)")
    print("  - Logs cut count")
    print("  - Banking trips count")
    print("  - Birds nests found")
    print("  - Total runtime (HH:MM:SS)")
    print("\nPress Ctrl+C to stop\n")
    print("="*70)
    
    try:
        bot = WoodcuttingBot("yew_cutter_edgeville")
        bot.start()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")


def test_mining_status():
    """Test mining bot with status line."""
    print("="*70)
    print("TESTING MINING BOT STATUS LINE")
    print("="*70)
    print("\nThe status line will show:")
    print("  - Current bot state (GATHERING, BANKING, WALKING)")
    print("  - Inventory capacity (X/28)")
    print("  - Ores mined count")
    print("  - Banking trips count")
    print("  - Total runtime (HH:MM:SS)")
    print("\nPress Ctrl+C to stop\n")
    print("="*70)
    
    try:
        bot = MiningBot("iron_miner_varrock")
        bot.start()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")


if __name__ == "__main__":
    # Choose which bot to test
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "mining":
            test_mining_status()
        elif sys.argv[1].lower() == "woodcutting":
            test_woodcutting_status()
        else:
            print("Usage: python test_status_line.py [woodcutting|mining]")
    else:
        # Default to woodcutting
        test_woodcutting_status()
