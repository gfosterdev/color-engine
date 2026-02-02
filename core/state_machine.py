"""
State machine for managing complex bot workflows.

Provides a finite state machine (FSM) for tracking and transitioning
between different bot states (e.g., MINING, BANKING, WALKING).
"""

from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import time


class BotState(Enum):
    """Core bot states."""
    IDLE = "idle"
    STARTING = "starting"
    STOPPING = "stopping"
    
    # Movement states
    WALKING = "walking"
    NAVIGATING = "navigating"
    
    # Generic skilling states
    GATHERING = "gathering"  # Generic resource gathering (mining, woodcutting, fishing, etc.)
    
    # Specific skilling states (for backwards compatibility)
    MINING = "mining"
    WOODCUTTING = "woodcutting"
    FISHING = "fishing"
    SMITHING = "smithing"
    COOKING = "cooking"
    
    # Banking states
    BANKING = "banking"
    BANK_OPEN = "bank_open"
    DEPOSITING = "depositing"
    WITHDRAWING = "withdrawing"
    
    # Combat states
    COMBAT = "combat"
    ATTACKING = "attacking"
    LOOTING = "looting"
    EATING = "eating"
    
    # Interface states
    SHOPPING = "shopping"
    DIALOGUE = "dialogue"
    LEVEL_UP = "level_up"
    
    # Error states
    ERROR = "error"
    RECOVERING = "recovering"
    STUCK = "stuck"
    
    # Anti-ban states
    IDLE_ACTION = "idle_action"
    CAMERA_MOVEMENT = "camera_movement"
    BREAK = "break"


@dataclass
class StateTransition:
    """Represents a state transition with conditions."""
    from_state: BotState
    to_state: BotState
    condition: Optional[Callable[[], bool]] = None
    action: Optional[Callable[[], Any]] = None
    timestamp: float = field(default_factory=time.time)


class StateMachine:
    """
    Finite state machine for bot workflow management.
    
    Manages state transitions with validation and history tracking.
    """
    
    def __init__(self, initial_state: BotState = BotState.IDLE):
        """
        Initialize the state machine.
        
        Args:
            initial_state: Starting state
        """
        self.current_state = initial_state
        self.previous_state: Optional[BotState] = None
        self.state_history: List[StateTransition] = []
        self.valid_transitions: Dict[BotState, List[BotState]] = {}
        self.state_entered_at: float = time.time()
        self.state_callbacks: Dict[BotState, List[Callable]] = {}
        
        # Set up default valid transitions
        self._setup_default_transitions()
    
    def _setup_default_transitions(self):
        """Define valid state transitions."""
        # Any state can transition to these
        universal_targets = [BotState.IDLE, BotState.ERROR, BotState.STOPPING, BotState.BREAK]
        
        # Define specific transitions
        transitions = {
            BotState.IDLE: [BotState.STARTING, BotState.WALKING, BotState.GATHERING,
                           BotState.MINING, BotState.WOODCUTTING, BotState.FISHING],
            
            BotState.STARTING: [BotState.GATHERING, BotState.MINING, BotState.WOODCUTTING, 
                               BotState.FISHING, BotState.WALKING, BotState.COMBAT],
            
            BotState.GATHERING: [BotState.BANKING, BotState.WALKING, BotState.IDLE_ACTION],
            BotState.MINING: [BotState.BANKING, BotState.WALKING, BotState.IDLE_ACTION],
            BotState.WOODCUTTING: [BotState.BANKING, BotState.WALKING, BotState.IDLE_ACTION],
            BotState.FISHING: [BotState.BANKING, BotState.WALKING, BotState.COOKING],
            
            BotState.WALKING: [BotState.GATHERING, BotState.MINING, BotState.WOODCUTTING, 
                              BotState.FISHING, BotState.BANKING, BotState.IDLE, BotState.COMBAT],
            
            BotState.BANKING: [BotState.BANK_OPEN, BotState.WALKING],
            BotState.BANK_OPEN: [BotState.DEPOSITING, BotState.WITHDRAWING, BotState.IDLE],
            BotState.DEPOSITING: [BotState.WALKING, BotState.GATHERING, BotState.MINING, BotState.WOODCUTTING],
            BotState.WITHDRAWING: [BotState.WALKING, BotState.GATHERING, BotState.MINING, BotState.WOODCUTTING],
            
            BotState.COMBAT: [BotState.ATTACKING, BotState.EATING, BotState.LOOTING],
            BotState.ATTACKING: [BotState.LOOTING, BotState.EATING, BotState.IDLE],
            BotState.LOOTING: [BotState.COMBAT, BotState.BANKING, BotState.IDLE],
            BotState.EATING: [BotState.COMBAT, BotState.BANKING],
            
            BotState.DIALOGUE: [BotState.IDLE, BotState.BANKING, BotState.SHOPPING],
            BotState.LEVEL_UP: [BotState.IDLE, BotState.GATHERING, BotState.MINING, BotState.WOODCUTTING],
            
            BotState.ERROR: [BotState.RECOVERING, BotState.STOPPING],
            BotState.RECOVERING: [BotState.IDLE, BotState.ERROR],
            BotState.STUCK: [BotState.RECOVERING, BotState.ERROR],
            
            BotState.IDLE_ACTION: [BotState.GATHERING, BotState.MINING, BotState.WOODCUTTING, BotState.IDLE],
            BotState.CAMERA_MOVEMENT: [BotState.GATHERING, BotState.MINING, BotState.WOODCUTTING, BotState.IDLE],
            BotState.BREAK: [BotState.IDLE, BotState.STARTING],
        }
        
        # Add universal targets to all states
        for state in BotState:
            self.valid_transitions[state] = transitions.get(state, []) + universal_targets
    
    def can_transition(self, to_state: BotState) -> bool:
        """
        Check if transition to target state is valid.
        
        Args:
            to_state: Target state
            
        Returns:
            True if transition is allowed
        """
        if self.current_state == to_state:
            return True
        
        valid = self.valid_transitions.get(self.current_state, [])
        return to_state in valid
    
    def transition(self, to_state: BotState, reason: str = "", 
                   action: Optional[Callable] = None) -> bool:
        """
        Transition to a new state.
        
        Args:
            to_state: Target state
            reason: Reason for transition (for logging)
            action: Optional action to execute during transition
            
        Returns:
            True if transition was successful
        """
        if not self.can_transition(to_state):
            print(f"Invalid transition: {self.current_state.value} -> {to_state.value}")
            return False
        
        # Store previous state
        self.previous_state = self.current_state
        
        # Execute transition action if provided
        if action:
            try:
                action()
            except Exception as e:
                print(f"Transition action failed: {e}")
                return False
        
        # Perform transition
        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            action=action
        )
        
        self.state_history.append(transition)
        self.current_state = to_state
        self.state_entered_at = time.time()
        
        # Trigger callbacks for new state
        self._trigger_callbacks(to_state)
        
        print(f"State transition: {self.previous_state.value} -> {to_state.value}" +
              (f" ({reason})" if reason else ""))
        
        return True
    
    def get_time_in_state(self) -> float:
        """
        Get time spent in current state.
        
        Returns:
            Seconds in current state
        """
        return time.time() - self.state_entered_at
    
    def get_valid_transitions(self) -> List[BotState]:
        """
        Get list of valid transitions from current state.
        
        Returns:
            List of valid target states
        """
        return self.valid_transitions.get(self.current_state, [])
    
    def add_state_callback(self, state: BotState, callback: Callable) -> None:
        """
        Register a callback to execute when entering a state.
        
        Args:
            state: State to watch
            callback: Function to call when state is entered
        """
        if state not in self.state_callbacks:
            self.state_callbacks[state] = []
        
        self.state_callbacks[state].append(callback)
    
    def _trigger_callbacks(self, state: BotState) -> None:
        """
        Trigger all callbacks for a state.
        
        Args:
            state: State that was entered
        """
        callbacks = self.state_callbacks.get(state, [])
        
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                print(f"State callback error for {state.value}: {e}")
    
    def get_history(self, limit: int = 10) -> List[StateTransition]:
        """
        Get recent state transition history.
        
        Args:
            limit: Maximum number of transitions to return
            
        Returns:
            List of recent transitions
        """
        return self.state_history[-limit:]
    
    def reset(self, to_state: BotState = BotState.IDLE) -> None:
        """
        Reset the state machine.
        
        Args:
            to_state: State to reset to
        """
        self.current_state = to_state
        self.previous_state = None
        self.state_entered_at = time.time()
        # Keep history for debugging
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current state machine status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "time_in_state": self.get_time_in_state(),
            "valid_transitions": [s.value for s in self.get_valid_transitions()],
            "history_length": len(self.state_history)
        }
