from time import sleep
from util import Window, Region
import keyboard
from client.osrs import OSRS

INTERACT_TEXT_REGION = Region(12, 28, 350, 20)  # x,y,w,h

def extract_region():
    window = Window()
    window.find(title="RuneLite - xJawj", exact_match=True)
    if window.window:
        while True:
            if keyboard.is_pressed('space'):
                window.print_mouse_position()
                sleep(0.2)  # Small delay to avoid multiple triggers
            elif keyboard.is_pressed('esc'):
                print("Exiting...")
                break

def extract_text():
    window = Window()
    window.find(title="RuneLite - xJawj", exact_match=True)
    if window.window:
        while True:
            if keyboard.is_pressed('space'):
                window.capture()
                text = window.read_text_paddle(INTERACT_TEXT_REGION, debug=True)
                print(f"Extracted Text: {text}")
                sleep(0.2)  # Small delay to avoid multiple triggers
            elif keyboard.is_pressed('esc'):
                print("Exiting...")
                break

def main():
    osrs = OSRS()
    if osrs.find_bank():
        print("Bank found successfully.")
        osrs.open_bank()
    else:
        print("Failed to find bank.")
    


if __name__ == "__main__":
    main()