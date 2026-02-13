from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from typing import Optional, Dict, Any

app = FastAPI()
app.state.state = None  # Initialize state to None, will be set in test.py

# Pydantic models for event data
class MovementChanged(BaseModel):
    moving: bool

class AnimationChanged(BaseModel):
    state: str  # "idle", "dead", "interacting"

class TargetChanged(BaseModel):
    type: str  # "npc", "player", "none"
    id: Optional[int] = None
    name: Optional[str] = None

class StateChanged(BaseModel):
    state: str  # GameState name

class ItemEvent(BaseModel):
    id: int
    quantity: int
    x: int
    y: int
    plane: int

class NpcEvent(BaseModel):
    id: int
    name: str
    x: int
    y: int
    plane: int
    combatLevel: int

class GameObjectEvent(BaseModel):
    id: int
    x: int
    y: int
    plane: int

class ActorDeath(BaseModel):
    type: str  # "npc"
    id: int
    name: str
    x: int
    y: int
    plane: int

class StatChanged(BaseModel):
    skill: str
    level: int
    xp: int

class ContainerChanged(BaseModel):
    pass  # Empty body

class ChatMessage(BaseModel):
    type: str
    message: str
    sender: str

class MenuOptionClicked(BaseModel):
    option: str
    target: str
    action: str

class InterfaceEvent(BaseModel):
    interface: str
    groupId: int

class SidebarState(BaseModel):
    combat: Optional[bool] = None
    skills: Optional[bool] = None
    summary: Optional[bool] = None
    inventory: Optional[bool] = None
    equipment: Optional[bool] = None
    prayer: Optional[bool] = None
    magic: Optional[bool] = None
    grouping: Optional[bool] = None
    account: Optional[bool] = None
    friends: Optional[bool] = None
    logout: Optional[bool] = None
    settings: Optional[bool] = None
    emotes: Optional[bool] = None
    music: Optional[bool] = None

# Endpoints
@app.post("/movement_changed")
async def movement_changed(data: MovementChanged):
    app.state.state.movement_changed(data.moving)
    return {"status": "ok"}

@app.post("/animation_changed")
async def animation_changed(data: AnimationChanged):
    app.state.state.animation_changed(data.state)
    return {"status": "ok"}

@app.post("/target_changed")
async def target_changed(data: TargetChanged):
    app.state.state.target_changed(data.type, data.id, data.name)
    return {"status": "ok"}

@app.post("/state_changed")
async def state_changed(data: StateChanged):
    app.state.state.game_state_changed(data.state)
    return {"status": "ok"}

@app.post("/item_spawned")
async def item_spawned(data: ItemEvent):
    app.state.state.item_spawned(data.id, data.quantity, data.x, data.y, data.plane)
    return {"status": "ok"}

@app.post("/item_despawned")
async def item_despawned(data: ItemEvent):
    app.state.state.item_despawned(data.id, data.quantity, data.x, data.y, data.plane)
    return {"status": "ok"}

@app.post("/npc_spawned")
async def npc_spawned(data: NpcEvent):
    app.state.state.npc_spawned(data.id, data.name, data.x, data.y, data.plane, data.combatLevel)
    return {"status": "ok"}

@app.post("/npc_despawned")
async def npc_despawned(data: NpcEvent):
    app.state.state.npc_despawned(data.id, data.name, data.x, data.y, data.plane, data.combatLevel)
    return {"status": "ok"}

@app.post("/game_object_spawned")
async def game_object_spawned(data: GameObjectEvent):
    app.state.state.game_object_spawned(data.id, data.x, data.y, data.plane)
    return {"status": "ok"}

@app.post("/game_object_despawned")
async def game_object_despawned(data: GameObjectEvent):
    app.state.state.game_object_despawned(data.id, data.x, data.y, data.plane)
    return {"status": "ok"}

@app.post("/actor_death")
async def actor_death(data: ActorDeath):
    app.state.state.actor_death(data.type, data.id, data.name, data.x, data.y, data.plane)
    return {"status": "ok"}

@app.post("/stat_changed")
async def stat_changed(data: StatChanged):
    app.state.state.stat_changed(data.skill, data.level, data.xp)
    return {"status": "ok"}

@app.post("/bank_changed")
async def bank_changed(data: ContainerChanged):
    app.state.state.bank_changed()
    return {"status": "ok"}

@app.post("/inventory_changed")
async def inventory_changed(data: ContainerChanged):
    app.state.state.inventory_changed()
    return {"status": "ok"}

@app.post("/chat_message")
async def chat_message(data: ChatMessage):
    app.state.state.chat_message(data.type, data.message, data.sender)
    return {"status": "ok"}

@app.post("/menu_option_clicked")
async def menu_option_clicked(data: MenuOptionClicked):
    app.state.state.menu_option_clicked(data.option, data.target, data.action)
    return {"status": "ok"}

@app.post("/interface_opened")
async def interface_opened(data: InterfaceEvent):
    app.state.state.interface_opened(data.interface, data.groupId)
    return {"status": "ok"}

@app.post("/interface_closed")
async def interface_closed(data: InterfaceEvent):
    app.state.state.interface_closed(data.interface, data.groupId)
    return {"status": "ok"}

@app.post("/sidebar_state")
async def sidebar_state(data: SidebarState):
    app.state.state.sidebar_state(data.dict(exclude_unset=True))
    return {"status": "ok"}

# To run: uvicorn server:app --reload