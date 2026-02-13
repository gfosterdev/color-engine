import threading
import time
import uvicorn
import keyboard
import logging
from state import State
import server as server

# Add logging configuration right after imports
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def run_server():
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    state = State()
    server.app.state.state = state

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()


    print("Server started. Press ESC to exit.")
    try:
        while True:
            if keyboard.is_pressed('esc'):
                print("ESC pressed. Exiting...")
                break
            
            if keyboard.is_pressed('space'):
                print(f"State: {state.current_state}")
                time.sleep(0.5) # Sleep to prevent multiple prints from a single key press
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting...")
    # No explicit server shutdown; thread will exit when main program exits
