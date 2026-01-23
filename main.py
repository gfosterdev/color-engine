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
            sleep(1)
            window.move_mouse_to((found.x, found.y))
            sleep(1)
            window.move_mouse_to((found.x + found.width, found.y))
            sleep(1)
            window.move_mouse_to((found.x + found.width, found.y + found.height))
            sleep(1)
            window.move_mouse_to((found.x, found.y + found.height))
        else:
            print("Color not found.")
    


if __name__ == "__main__":
    main()