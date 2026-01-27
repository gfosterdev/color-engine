"""
Download pre-built collision map data from RuneLite shortest-path plugin repository.

This script downloads the collision-map.zip file (~50MB) which contains pre-computed
walkability data for all OSRS regions. The data is updated weekly by the RuneLite
community via automated GitHub Actions.

Usage:
    python scripts/download_collision_data.py
"""

import os
import sys
import requests
from pathlib import Path

# GitHub repository URL for the collision map
COLLISION_MAP_URL = "https://github.com/Skretzo/shortest-path/raw/refs/heads/master/src/main/resources/collision-map.zip"

# Local path to store the collision map
UTIL_DATA_DIR = Path(__file__).parent.parent / "util" / "data"
OUTPUT_PATH = UTIL_DATA_DIR / "collision-map.zip"


def download_collision_map():
    """Download the collision map ZIP file from GitHub."""
    print("=" * 60)
    print("OSRS Collision Map Downloader")
    print("=" * 60)
    print()
    print(f"Downloading from: {COLLISION_MAP_URL}")
    print(f"Saving to: {OUTPUT_PATH}")
    print()
    
    # Create directory if it doesn't exist
    UTIL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if file already exists
    if OUTPUT_PATH.exists():
        response = input(f"File already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Download cancelled.")
            return False
    
    try:
        print("Downloading... (this may take a few minutes, ~50MB)")
        
        # Stream download with progress
        response = requests.get(COLLISION_MAP_URL, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(OUTPUT_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show progress
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB)", end='')
        
        print()  # New line after progress
        print()
        print("✓ Download complete!")
        print(f"✓ File saved to: {OUTPUT_PATH}")
        print(f"✓ File size: {OUTPUT_PATH.stat().st_size / 1024 / 1024:.1f} MB")
        print()
        print("The collision map is ready to use for pathfinding.")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error downloading file: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = download_collision_map()
    sys.exit(0 if success else 1)
