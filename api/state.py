from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class State:
    def __init__(self):
        self.current_state: str = "startup"

        # Player state
        self.is_moving: bool = False
        self.animation_state: str = "idle"
        self.current_target: Optional[Dict[str, Any]] = None
        self.game_state: str = "unknown"

        # World state
        self.spawned_items: List[Dict[str, Any]] = []
        self.spawned_npcs: List[Dict[str, Any]] = []
        self.spawned_game_objects: List[Dict[str, Any]] = []

        # Player stats
        self.skills: Dict[str, Dict[str, int]] = {}

        # Interface state
        self.open_interfaces: Dict[str, bool] = {}
        self.sidebar_states: Dict[str, bool] = {}

        # Chat and interactions
        self.recent_chat_messages: List[Dict[str, str]] = []
        self.recent_menu_actions: List[Dict[str, str]] = []

    def movement_changed(self, moving: bool):
        """Update player movement state"""
        self.is_moving = moving
        logger.info(f"Movement changed: {moving}")

    def animation_changed(self, state: str):
        """Update player animation state"""
        self.animation_state = state
        logger.info(f"Animation changed: {state}")

    def target_changed(self, target_type: str, target_id: Optional[int] = None, target_name: Optional[str] = None):
        """Update current target"""
        if target_type == "none":
            self.current_target = None
        else:
            self.current_target = {
                "type": target_type,
                "id": target_id,
                "name": target_name
            }
        logger.info(f"Target changed: {self.current_target}")

    def game_state_changed(self, state: str):
        """Update game state"""
        self.game_state = state
        logger.info(f"Game state changed: {state}")

    def item_spawned(self, item_id: int, quantity: int, x: int, y: int, plane: int):
        """Add spawned item to world state"""
        item = {
            "id": item_id,
            "quantity": quantity,
            "x": x,
            "y": y,
            "plane": plane
        }
        self.spawned_items.append(item)
        logger.info(f"Item spawned: {item}")

    def item_despawned(self, item_id: int, quantity: int, x: int, y: int, plane: int):
        """Remove despawned item from world state"""
        self.spawned_items = [item for item in self.spawned_items
                            if not (item["id"] == item_id and item["x"] == x and item["y"] == y and item["plane"] == plane)]
        logger.info(f"Item despawned: id={item_id}, x={x}, y={y}, plane={plane}")

    def npc_spawned(self, npc_id: int, name: str, x: int, y: int, plane: int, combat_level: int):
        """Add spawned NPC to world state"""
        npc = {
            "id": npc_id,
            "name": name,
            "x": x,
            "y": y,
            "plane": plane,
            "combat_level": combat_level
        }
        self.spawned_npcs.append(npc)
        logger.info(f"NPC spawned: {npc}")

    def npc_despawned(self, npc_id: int, name: str, x: int, y: int, plane: int, combat_level: int):
        """Remove despawned NPC from world state"""
        self.spawned_npcs = [npc for npc in self.spawned_npcs
                           if not (npc["id"] == npc_id and npc["x"] == x and npc["y"] == y and npc["plane"] == plane)]
        logger.info(f"NPC despawned: id={npc_id}, name={name}, x={x}, y={y}, plane={plane}")

    def game_object_spawned(self, object_id: int, x: int, y: int, plane: int):
        """Add spawned game object to world state"""
        obj = {
            "id": object_id,
            "x": x,
            "y": y,
            "plane": plane
        }
        self.spawned_game_objects.append(obj)
        logger.info(f"Game object spawned: {obj}")

    def game_object_despawned(self, object_id: int, x: int, y: int, plane: int):
        """Remove despawned game object from world state"""
        self.spawned_game_objects = [obj for obj in self.spawned_game_objects
                                   if not (obj["id"] == object_id and obj["x"] == x and obj["y"] == y and obj["plane"] == plane)]
        logger.info(f"Game object despawned: id={object_id}, x={x}, y={y}, plane={plane}")

    def actor_death(self, actor_type: str, actor_id: int, name: str, x: int, y: int, plane: int):
        """Handle actor death"""
        logger.info(f"Actor death: type={actor_type}, id={actor_id}, name={name}, x={x}, y={y}, plane={plane}")
        # Remove from spawned lists if applicable
        if actor_type == "npc":
            self.spawned_npcs = [npc for npc in self.spawned_npcs
                               if not (npc["id"] == actor_id and npc["x"] == x and npc["y"] == y and npc["plane"] == plane)]

    def stat_changed(self, skill: str, level: int, xp: int):
        """Update skill stats"""
        self.skills[skill] = {"level": level, "xp": xp}
        logger.info(f"Stat changed: {skill} level={level}, xp={xp}")

    def bank_changed(self):
        """Handle bank container change"""
        logger.info("Bank changed")

    def inventory_changed(self):
        """Handle inventory container change"""
        logger.info("Inventory changed")

    def chat_message(self, msg_type: str, message: str, sender: str):
        """Add chat message"""
        chat_msg = {
            "type": msg_type,
            "message": message,
            "sender": sender
        }
        self.recent_chat_messages.append(chat_msg)
        # Keep only last 50 messages
        if len(self.recent_chat_messages) > 50:
            self.recent_chat_messages = self.recent_chat_messages[-50:]
        logger.info(f"Chat message: {chat_msg}")

    def menu_option_clicked(self, option: str, target: str, action: str):
        """Add menu action"""
        menu_action = {
            "option": option,
            "target": target,
            "action": action
        }
        self.recent_menu_actions.append(menu_action)
        # Keep only last 20 actions
        if len(self.recent_menu_actions) > 20:
            self.recent_menu_actions = self.recent_menu_actions[-20:]
        logger.info(f"Menu option clicked: {menu_action}")

    def interface_opened(self, interface: str, group_id: int):
        """Mark interface as opened"""
        self.open_interfaces[interface] = True
        logger.info(f"Interface opened: {interface} (group_id={group_id})")

    def interface_closed(self, interface: str, group_id: int):
        """Mark interface as closed"""
        self.open_interfaces[interface] = False
        logger.info(f"Interface closed: {interface} (group_id={group_id})")

    def sidebar_state(self, states: Dict[str, bool]):
        """Update sidebar states"""
        self.sidebar_states.update(states)
        logger.info(f"Sidebar state updated: {states}")