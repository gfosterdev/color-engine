from time import sleep
from window_util import Window

def main():
    window = Window()
    window.find(title="RuneLite - xJawj", exact_match=True)
    if window.window:
        window.capture(debug=True)
        found = window.find_color_region((190, 25, 25), tolerance=0, debug=True)
        # mouse_color = window.get_color_at_mouse()
        # print(f"Color at mouse position: {mouse_color}")
        if found:
            print(f"Found color at: {found}")
            print(f"Moving mouse to: {found.center()}")
            window.move_mouse_to(found.center())
            for i in range(5):
                sleep(0.2)
                window.move_mouse_to(found.random_point())
        else:
            print("Color not found.")
    


if __name__ == "__main__":
    main()