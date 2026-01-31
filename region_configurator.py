"""
Interactive Region Configuration Tool

Helps capture and define regions accurately for the OSRS bot.
Use this tool to visually define regions by clicking two corners.
"""

import cv2
import numpy as np
from util import Window, Region
from client.runelite_api import RuneLiteAPI
import keyboard
import time
import ctypes


class RegionConfigurator:
    """Interactive tool for capturing and defining regions."""
    
    def __init__(self):
        self.window = Window()
        self.window.find(title="RuneLite - xJawj", exact_match=True)
        self.api = RuneLiteAPI()
        
        if not self.window.window:
            raise RuntimeError("Could not find RuneLite window!")
        
        self.regions = {}  # Store defined regions
        self.current_region = None
        print(f"Connected to: {self.window.window['title']}")
        print(f"Window position: ({self.window.window['x']}, {self.window.window['y']})")
        print(f"Window size: {self.window.window['width']}x{self.window.window['height']}")
    
    def get_mouse_position(self):
        """Get current mouse position relative to window."""
        viewport = self.api.get_viewport_data()
        if not viewport:
            print("Could not get viewport data from API")
            return
        x = int(viewport.get('canvasMouseX', -1))
        y = int(viewport.get('canvasMouseY', -1))
        
        return x, y
    
    def capture_region_interactive(self):
        """Capture a region by clicking two corners."""
        print("\n" + "="*60)
        print("CAPTURE NEW REGION")
        print("="*60)
        print("Instructions:")
        print("1. Position mouse at TOP-LEFT corner of the region")
        print("2. Press SPACE to capture first corner")
        print("3. Position mouse at BOTTOM-RIGHT corner")
        print("4. Press SPACE to capture second corner")
        print("5. Press ESC to cancel")
        print("="*60)
        
        # Capture screenshot for reference
        self.window.capture()
        
        # Wait for first corner
        print("\nWaiting for TOP-LEFT corner (press SPACE)...")
        corner1 = None
        while corner1 is None:
            if keyboard.is_pressed('space'):
                x, y = self.get_mouse_position()
                corner1 = (x, y)
                print(f"✓ Corner 1: ({x}, {y})")
                time.sleep(0.3)  # Debounce
            elif keyboard.is_pressed('esc'):
                print("✗ Cancelled")
                return None
            time.sleep(0.05)
        
        # Wait for second corner
        print("\nWaiting for BOTTOM-RIGHT corner (press SPACE)...")
        corner2 = None
        while corner2 is None:
            x, y = self.get_mouse_position()
            # Show live preview
            print(f"\rCurrent position: ({x:3}, {y:3}) | Preview size: {abs(x-corner1[0]):3}x{abs(y-corner1[1]):3}", end='')
            
            if keyboard.is_pressed('space'):
                corner2 = (x, y)
                print(f"\n✓ Corner 2: ({x}, {y})")
                time.sleep(0.3)  # Debounce
            elif keyboard.is_pressed('esc'):
                print("\n✗ Cancelled")
                return None
            time.sleep(0.05)
        
        # Calculate region bounds
        x1, y1 = corner1
        x2, y2 = corner2
        
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        
        region = Region(x, y, w, h)
        
        print(f"\n✓ Region captured: ({x}, {y}, {w}, {h})")
        return region
    
    def visualize_region(self, region: Region, name: str = "Preview"):
        """Show visualization of the region on screenshot."""
        self.window.capture()
        
        if self.window.screenshot is None:
            print("✗ No screenshot available")
            return
        
        annotated = self.window.screenshot.copy()
        
        # Draw rectangle
        color = (0, 255, 0)  # Green
        cv2.rectangle(
            annotated,
            (region.x, region.y),
            (region.x + region.width, region.y + region.height),
            color,
            2
        )
        
        # Draw crosshair at center
        center = region.center()
        cv2.drawMarker(
            annotated,
            center,
            color,
            cv2.MARKER_CROSS,
            20,
            2
        )
        
        # Add label
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            annotated,
            name,
            (region.x + 2, region.y - 5),
            font,
            0.5,
            (0, 255, 0),
            1
        )
        
        # Save preview
        cv2.imwrite('region_preview.png', annotated)
        print(f"✓ Preview saved to: region_preview.png")
    
    def test_region_ocr(self, region: Region):
        """Test OCR on the defined region."""
        print("\nTesting OCR on region...")
        self.window.capture()
        text = self.window.read_text(region, debug=True)
        print(f"OCR Result: '{text}'" if text else "OCR Result: (no text detected)")
    
    def define_region(self):
        """Complete workflow to define and save a region."""
        # Capture region
        region = self.capture_region_interactive()
        if region is None:
            return
        
        # Visualize
        self.visualize_region(region, "New Region")
        
        # Get name
        print("\n" + "="*60)
        name = input("Enter region name (e.g., BANK_TITLE_REGION): ").strip()
        
        if not name:
            print("✗ No name provided, region not saved")
            return
        
        # Get comment
        comment = input("Enter description (optional): ").strip()
        
        # Save to collection
        self.regions[name] = {
            'region': region,
            'comment': comment if comment else ""
        }
        
        print(f"\n✓ Region '{name}' saved to session")
        
        # Ask if they want to test OCR
        # test_ocr = input("\nTest OCR on this region? (y/n): ").strip().lower()
        # if test_ocr == 'y':
        #     self.test_region_ocr(region)
        
        # Show visualization with name
        self.visualize_region(region, name)
    
    def list_regions(self):
        """List all defined regions in this session."""
        if not self.regions:
            print("\n✗ No regions defined yet")
            return
        
        print("\n" + "="*60)
        print("DEFINED REGIONS")
        print("="*60)
        for name, data in self.regions.items():
            r = data['region']
            comment = data['comment']
            print(f"{name:35} -> ({r.x:3}, {r.y:3}, {r.width:3}x{r.height:3})")
            if comment:
                print(f"  {comment}")
    
    def visualize_all_regions(self):
        """Show all defined regions on one screenshot."""
        if not self.regions:
            print("\n✗ No regions to visualize")
            return
        
        self.window.capture()
        
        if self.window.screenshot is None:
            print("✗ No screenshot available")
            return
        
        annotated = self.window.screenshot.copy()
        
        import random
        for name, data in self.regions.items():
            region = data['region']
            
            # Random color for each region
            color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            
            # Draw rectangle
            cv2.rectangle(
                annotated,
                (region.x, region.y),
                (region.x + region.width, region.y + region.height),
                color,
                2
            )
            
            # Add label
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(
                annotated,
                name,
                (region.x + 2, region.y - 5),
                font,
                0.4,
                color,
                1
            )
        
        cv2.imwrite('all_regions_preview.png', annotated)
        print(f"\n✓ All regions preview saved to: all_regions_preview.png")
    
    def export_to_file(self):
        """Export regions to Python code for regions.py."""
        if not self.regions:
            print("\n✗ No regions to export")
            return
        
        print("\n" + "="*60)
        print("EXPORT REGIONS")
        print("="*60)
        print("Copy and paste this into config/regions.py:\n")
        
        for name, data in self.regions.items():
            r = data['region']
            comment = data['comment']
            comment_str = f"  # {comment}" if comment else ""
            print(f"{name} = Region({r.x}, {r.y}, {r.width}, {r.height}){comment_str}")
        
        print("\n" + "="*60)
        
        # Also save to file
        with open('regions_export.txt', 'w') as f:
            for name, data in self.regions.items():
                r = data['region']
                comment = data['comment']
                comment_str = f"  # {comment}" if comment else ""
                f.write(f"{name} = Region({r.x}, {r.y}, {r.width}, {r.height}){comment_str}\n")
        
        print("✓ Also saved to: regions_export.txt")
    
    def run(self):
        """Main interactive loop."""
        print("\n" + "="*60)
        print("REGION CONFIGURATOR")
        print("="*60)
        print("This tool helps you define regions accurately")
        print("="*60)
        
        while True:
            print("\n" + "="*60)
            print("MENU")
            print("="*60)
            print("1 - Define New Region")
            print("2 - List Defined Regions")
            print("3 - Visualize All Regions")
            print("4 - Export to File")
            print("5 - Show Mouse Position (live)")
            print("ESC - Exit")
            print("="*60)
            
            while True:
                if keyboard.is_pressed('1'):
                    self.define_region()
                    time.sleep(0.3)
                    break
                elif keyboard.is_pressed('2'):
                    self.list_regions()
                    time.sleep(0.3)
                    break
                elif keyboard.is_pressed('3'):
                    self.visualize_all_regions()
                    time.sleep(0.3)
                    break
                elif keyboard.is_pressed('4'):
                    self.export_to_file()
                    time.sleep(0.3)
                    break
                elif keyboard.is_pressed('5'):
                    self.show_mouse_position_live()
                    time.sleep(0.3)
                    break
                elif keyboard.is_pressed('esc'):
                    print("\n✓ Exiting Region Configurator")
                    if self.regions:
                        save = input("\nExport regions before exit? (y/n): ").strip().lower()
                        if save == 'y':
                            self.export_to_file()
                    return
                
                time.sleep(0.05)
    
    def show_mouse_position_live(self):
        """Show live mouse position - useful for finding coordinates."""
        print("\n" + "="*60)
        print("LIVE MOUSE POSITION")
        print("="*60)
        print("Move your mouse over the RuneLite window")
        print("Press ESC to return to menu")
        print("="*60 + "\n")
        
        self.window.capture()
        
        try:
            while True:
                if keyboard.is_pressed('esc'):
                    print("\n")
                    time.sleep(0.3)
                    return
                
                x, y = self.get_mouse_position()
                
                # Get color at current position if within bounds
                w = self.window.window
                color_str = ""
                if w and 0 <= x < w['width'] and 0 <= y < w['height'] and self.window.screenshot is not None:
                    b, g, r = self.window.screenshot[y, x]
                    color_str = f" | RGB: ({r:3}, {g:3}, {b:3})"
                
                print(f"\rPosition: ({x:3}, {y:3}){color_str}     ", end='', flush=True)
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("\n")


if __name__ == "__main__":
    print("="*60)
    print("OSRS BOT - REGION CONFIGURATOR")
    print("="*60)
    print("\nMake sure RuneLite is running in FIXED mode!")
    print("This tool will help you define regions accurately.\n")
    
    try:
        configurator = RegionConfigurator()
        configurator.run()
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✓ Region Configurator closed.")
