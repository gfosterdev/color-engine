from window_util import Window

def main():
    window = Window()
    window.find(title="RuneLite", exact_match=False)
    window.capture(debug=True)
    if window.window:
        print(f"Window found: {window.window}")
        print(f"dimensions: {window.window['width']}x{window.window['height']} at ({window.window['x']}, {window.window['y']})")


if __name__ == "__main__":
    main()