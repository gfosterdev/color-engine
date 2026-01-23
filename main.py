from window_finder import find_window

def main():
    window = find_window("RuneLite", exact_match=False)
    if window:
        print(f"Window found: {window}")
        print(f"dimensions: {window['width']}x{window['height']} at ({window['x']}, {window['y']})")


if __name__ == "__main__":
    main()