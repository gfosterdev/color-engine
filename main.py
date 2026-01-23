from window_util import Window
from mouse_util import MouseMover

def main():
    mouse = MouseMover()
    mouse.move_to(100, 200)
    # window = Window()
    # window.find(title="RuneLite", exact_match=False)
    # if window.window:
    #     window.capture(debug=True)
    #     found = window.find_color((220, 224, 28), tolerance=25)
    #     if found:
    #         print(f"Found color at: {found}")
    #     else:
    #         print("Color not found.")
    


if __name__ == "__main__":
    main()