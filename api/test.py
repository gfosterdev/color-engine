import threading
import time
import uvicorn
import keyboard
import logging
from state import State
import server

# Add logging configuration right after imports
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def run_server():
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    state = State()
    server.app.state.state = state
    server.toggle({
        "movement_changed": True,
        "animation_changed": False,
        "target_changed": True,
        "state_changed": True,
        "item_spawned": False,
        "item_despawned": False,
        "npc_despawned": False,
        "actor_death": False,
        "stat_changed": False,
        "bank_changed": False,
        "inventory_changed": False,
        "chat_message": False,
        "menu_option_clicked": False,
        "interface_opened": False,
        "interface_closed": False,
        "sidebar_state": False,
        "game_object_spawned": False,
        "game_object_despawned": False
    })

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
