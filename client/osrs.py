from util import Window, Region

# Regions
INTERACT_TEXT_REGION = Region(12, 28, 350, 20)  # x,y,w,h

# Color References
BANK = (190, 25, 25)

class OSRS:
    def __init__(self):
        self.window = Window()
        self.window.find(title="RuneLite - xJawj", exact_match=True)
    
    def open_bank(self):
        if self.window.window:
            self.window.capture()
            found = self.window.find_color_region(BANK)
            if found:
                self.window.move_mouse_to(found.random_point())
                if self.validate_interact_text("Bank"):
                    print("CLICK")
                    return True
            else:
                print("Bank color not found on screen.")
        return False

    def validate_interact_text(self, expected_text):
        if self.window.window:
            self.window.capture()
            text = self.window.read_text(INTERACT_TEXT_REGION, debug=True)
            if expected_text in text:
                print(f"Found expected text: {expected_text}")
                return True
            else:
                print(f"Expected text '{expected_text}' not found. Extracted text: {text}")
                return False
        return False