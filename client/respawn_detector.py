"""
Respawn detection system for gathering skill resource nodes.
Uses dual detection: player animation + object polling for maximum reliability.
"""

from typing import Optional
import time
from core.config import DEBUG


class RespawnDetector:
    """
    Detects when a depleted resource node has respawned.
    
    Uses two methods:
    1. Animation detection - player stops performing gather animation
    2. Object polling - resource object disappears from viewport
    
    Supports configurable animation IDs for different skills.
    """
    
    def __init__(self, api, animation_id: int, enabled: bool = True):
        """
        Initialize respawn detector.
        
        Args:
            api: RuneLiteAPI instance
            animation_id: Animation ID for the gathering action (e.g., 628 for mining)
            enabled: Whether to use respawn detection
        """
        self.api = api
        self.animation_id = animation_id
        self.enabled = enabled
        self.last_animation_check = 0
        self.animation_check_interval = 0.6  # Check every 0.6s (game tick)
    
    def wait_for_respawn(self, target_object_id: int, target_x: int, target_y: int, 
                        max_wait: float = 10.0, use_animation: bool = True) -> bool:
        """
        Wait for a resource node to respawn (become depleted).
        
        Args:
            target_object_id: Game object ID being gathered
            target_x: World X coordinate of target
            target_y: World Y coordinate of target
            max_wait: Maximum time to wait in seconds
            use_animation: If True, also check player animation
        
        Returns:
            True if respawn detected, False if timeout or error
        """
        if not self.enabled:
            return True
        
        start_time = time.time()
        
        if DEBUG:
            print(f"\nWaiting for node depletion (max {max_wait}s)...")
        
        while time.time() - start_time < max_wait:
            # Method 1: Check if player stopped animating
            if use_animation and self._check_animation_stopped():
                print("✓ Player stopped gathering animation")
                return True
            
            # Method 2: Check if object disappeared
            if self._check_object_disappeared(target_object_id, target_x, target_y):
                print("✓ Resource node depleted")
                return True
            
            time.sleep(0.6)  # Game tick interval
        
        print("✗ Respawn detection timeout")
        return False
    
    def is_player_gathering(self) -> bool:
        """
        Check if player is currently performing gathering animation.
        
        Returns:
            True if player is animating with gathering animation, False otherwise
        """
        player = self.api.get_player()
        if not player:
            return False
        
        current_animation = player.get('animationId')
        return current_animation == self.animation_id
    
    def _check_animation_stopped(self) -> bool:
        """
        Check if player has stopped performing gathering animation.
        
        Returns:
            True if animation stopped, False if still animating or can't determine
        """
        current_time = time.time()
        
        # Throttle animation checks
        if current_time - self.last_animation_check < self.animation_check_interval:
            return False
        
        self.last_animation_check = current_time
        
        player = self.api.get_player()
        if not player:
            return False
        
        current_animation = player.get('animationId')
        
        # If animation is -1 or not matching, player stopped gathering
        if current_animation == -1 or current_animation != self.animation_id:
            return True
        
        return False
    
    def _check_object_disappeared(self, object_id: int, x: int, y: int) -> bool:
        """
        Check if a specific object at coordinates has disappeared from viewport.
        
        Args:
            object_id: Game object ID to check
            x: World X coordinate
            y: World Y coordinate
        
        Returns:
            True if object not found at location, False if still present
        """
        # Use get_entity_in_viewport to check if object exists at exact world coordinates
        entity = self.api.get_entity_in_viewport(
            object_id, 
            "object", 
            world_x=x, 
            world_y=y
        )
        
        # If entity not found at location, it has disappeared
        return entity is None
