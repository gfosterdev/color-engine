"""
Anti-ban randomization layer for OSRS bot.

Implements human-like behaviors including random idle actions, camera movements,
tab switching, simulated misclicks, fatigue patterns, and break scheduling.
"""

from typing import Callable, List, Optional
from dataclasses import dataclass
import time
import random
from core.config import AntiBanConfig, BreakConfig
from util import Window


@dataclass
class BreakSchedule:
    """Represents a scheduled break."""
    start_time: float
    duration: float  # seconds
    break_type: str = "idle"  # 'idle' or 'logout'
    reason: str = "scheduled_break"


class AntiBanManager:
    """
    Manages anti-ban behaviors to make bot actions appear more human.
    
    Implements various randomization strategies to avoid detection patterns.
    """
    
    def __init__(self, window: Window, config: AntiBanConfig, break_config: Optional[BreakConfig] = None, osrs_client=None):
        """
        Initialize anti-ban manager.
        
        Args:
            window: Window instance for interactions
            config: Anti-ban configuration
            break_config: Break configuration (optional)
            osrs_client: OSRS client instance for logout/login (optional)
        """
        self.window = window
        self.config = config
        self.break_config = break_config or BreakConfig()
        self.osrs_client = osrs_client
        self.last_idle_action = time.time()
        self.last_camera_movement = time.time()
        self.last_tab_switch = time.time()
        self.next_break: Optional[BreakSchedule] = None
        self.next_logout_break: Optional[BreakSchedule] = None
        self.action_count = 0
        self.fatigue_level = 0.0  # 0.0 to 1.0
        
        if self.config.enabled:
            self._schedule_next_break()
            if self.break_config.logout_breaks_enabled and self.osrs_client:
                self._schedule_next_logout_break()
    
    def should_perform_idle_action(self) -> bool:
        """
        Check if it's time for a random idle action.
        
        Returns:
            True if idle action should be performed
        """
        if not self.config.enabled or not self.config.idle_actions:
            return False
        
        elapsed = time.time() - self.last_idle_action
        threshold = random.uniform(
            self.config.idle_frequency_min,
            self.config.idle_frequency_max
        )
        
        return elapsed >= threshold
    
    def perform_idle_action(self) -> None:
        """Perform a random idle action (look around, check stats, etc.)."""
        if not self.config.enabled:
            return
        
        actions = [
            self._random_mouse_movement,
            self._check_stats_tab,
            self._random_camera_angle,
            self._hover_random_location
        ]
        
        # Select random action
        action = random.choice(actions)
        action()
        
        self.last_idle_action = time.time()
    
    def _random_mouse_movement(self) -> None:
        """Move mouse to a random location without clicking."""
        if not self.window.window:
            return
        
        # Random point in game window
        x = random.randint(50, 700)
        y = random.randint(50, 450)
        
        self.window.move_mouse_to((x, y))
        time.sleep(random.uniform(0.5, 2.0))
    
    def _check_stats_tab(self) -> None:
        """Open and briefly view the stats tab."""
        import keyboard
        
        # Press F1 for stats
        keyboard.press_and_release('f1')
        time.sleep(random.uniform(1.0, 3.0))
        
        # Return to inventory (F4)
        keyboard.press_and_release('f4')
        time.sleep(random.uniform(0.3, 0.6))
    
    def _random_camera_angle(self) -> None:
        """Perform a random camera movement."""
        if not self.window.window or not self.config.camera_movements:
            return
        
        # rotate_camera only takes min_drag_distance parameter
        min_drag = random.randint(50, 200)
        self.window.rotate_camera(min_drag_distance=min_drag)
        
        self.last_camera_movement = time.time()
    
    def _hover_random_location(self) -> None:
        """Hover mouse over a random location briefly."""
        if not self.window.window:
            return
        
        x = random.randint(100, 650)
        y = random.randint(100, 400)
        
        self.window.move_mouse_to((x, y))
        time.sleep(random.uniform(0.3, 1.5))
    
    def should_take_break(self) -> tuple[bool, str]:
        """
        Check if it's time for a scheduled break.
        
        Returns:
            Tuple of (should_break, break_type) where break_type is 'idle' or 'logout'
        """
        if not self.config.enabled:
            return (False, "none")
        
        current_time = time.time()
        
        # Check logout break first (higher priority)
        if self.next_logout_break and current_time >= self.next_logout_break.start_time:
            return (True, "logout")
        
        # Check regular idle break
        if self.next_break and current_time >= self.next_break.start_time:
            return (True, "idle")
        
        return (False, "none")
    
    def take_break(self, break_type: str = "idle") -> None:
        """
        Take a scheduled break.
        
        Args:
            break_type: Type of break to take ('idle' or 'logout')
        """
        if break_type == "logout":
            self._take_logout_break()
        else:
            self._take_idle_break()
    
    def _take_idle_break(self) -> None:
        """Take an idle break (stay logged in)."""
        if not self.next_break:
            return
        
        print(f"\n{'='*50}")
        print(f"TAKING IDLE BREAK - {self.next_break.reason}")
        print(f"Duration: {self.next_break.duration / 60:.1f} minutes")
        print(f"{'='*50}\n")
        
        # Perform idle activities during break
        break_end = time.time() + self.next_break.duration
        
        while time.time() < break_end:
            # Occasionally move mouse or check tabs
            if random.random() < 0.3:
                self.perform_idle_action()
            
            # Sleep for a bit
            time.sleep(random.uniform(10, 30))
        
        print("Idle break finished, resuming bot...")
        
        # Schedule next break
        self._schedule_next_break()
        
        # Reset fatigue
        self.fatigue_level = 0.0
    
    def _take_logout_break(self) -> None:
        """Take a logout break (logout, wait, login back)."""
        if not self.next_logout_break or not self.osrs_client:
            return
        
        print(f"\n{'='*50}")
        print(f"TAKING LOGOUT BREAK")
        print(f"Duration: {self.next_logout_break.duration / 60:.1f} minutes")
        print(f"{'='*50}\n")
        
        # Perform logout
        print("Logging out...")
        logout_success = False
        try:
            logout_success = self.osrs_client.logout()
            if logout_success:
                print("Successfully logged out")
            else:
                print("WARNING: Logout failed")
        except Exception as e:
            print(f"ERROR: Logout exception: {e}")
            # Trigger error handler for logout failure
            try:
                from core.error_handler import GlobalErrorHandler, ErrorContext
                handler = GlobalErrorHandler.get_instance()
                context = ErrorContext(
                    error=e,
                    error_type="LogoutFailure",
                    bot_state="BREAK",
                    current_task="logout_break"
                )
                # Note: We don't have bot_instance here, so just log the error
                handler._log_error(context)
                handler._print_error(context)
            except ImportError:
                pass
            return
        
        if logout_success:
            # Wait for break duration
            break_minutes = self.next_logout_break.duration / 60
            print(f"Waiting {break_minutes:.1f} minutes before logging back in...")
            time.sleep(self.next_logout_break.duration)
            
            # Login back
            print("Logging back in...")
            max_login_attempts = 3
            for attempt in range(max_login_attempts):
                try:
                    if self.osrs_client.login_from_profile():
                        print("Successfully logged back in")
                        break
                    else:
                        print(f"Login attempt {attempt + 1} failed, retrying...")
                        time.sleep(random.uniform(5, 10))
                except Exception as e:
                    print(f"Login exception: {e}")
                    time.sleep(random.uniform(5, 10))
            else:
                print("WARNING: Failed to log back in after multiple attempts!")
                # This is a critical failure - raise exception to trigger emergency shutdown
                raise RuntimeError("Failed to log back in after logout break")
        
        print("Logout break finished, resuming bot...")
        
        # Schedule next logout break
        self._schedule_next_logout_break()
        
        # Reset fatigue completely after logout break
        self.fatigue_level = 0.0
    
    def _schedule_next_break(self) -> None:
        """Schedule the next break."""
        if not self.config.enabled or not self.break_config.enabled:
            return
        
        # Random time until next break (in minutes)
        minutes_until_break = random.uniform(
            self.break_config.frequency_min,
            self.break_config.frequency_max
        )
        
        # Random break duration (in minutes)
        break_duration_minutes = random.uniform(
            self.break_config.duration_min,
            self.break_config.duration_max
        )
        
        self.next_break = BreakSchedule(
            start_time=time.time() + (minutes_until_break * 60),
            duration=break_duration_minutes * 60,
            break_type="idle",
            reason="scheduled_break"
        )
        
        print(f"Next idle break scheduled in {minutes_until_break:.1f} minutes "
              f"for {break_duration_minutes:.1f} minutes")
    
    def _schedule_next_logout_break(self) -> None:
        """Schedule the next logout break."""
        if not self.config.enabled or not self.break_config.logout_breaks_enabled or not self.osrs_client:
            return
        
        # Random time until next logout break (in minutes)
        minutes_until_break = random.uniform(
            self.break_config.logout_frequency_min,
            self.break_config.logout_frequency_max
        )
        
        # Random logout break duration (in minutes)
        break_duration_minutes = random.uniform(
            self.break_config.logout_duration_min,
            self.break_config.logout_duration_max
        )
        
        self.next_logout_break = BreakSchedule(
            start_time=time.time() + (minutes_until_break * 60),
            duration=break_duration_minutes * 60,
            break_type="logout",
            reason="logout_break"
        )
        
        print(f"Next logout break scheduled in {minutes_until_break:.1f} minutes "
              f"for {break_duration_minutes:.1f} minutes")
    
    def apply_action_delay(self) -> None:
        """
        Apply a randomized delay between actions.
        Delay increases with fatigue to simulate human tiredness.
        """
        base_delay = random.uniform(0.5, 1.5)
        
        # Increase delay based on fatigue
        if self.config.fatigue_simulation:
            fatigue_multiplier = 1.0 + (self.fatigue_level * 0.5)
            base_delay *= fatigue_multiplier
        
        time.sleep(base_delay)
        
        # Increment fatigue slightly with each action
        self.action_count += 1
        if self.config.fatigue_simulation:
            self.fatigue_level = min(1.0, self.fatigue_level + 0.001)
    
    def simulate_misclick(self) -> bool:
        """
        Occasionally simulate a misclick (miss the target slightly).
        
        Returns:
            True if misclick should be simulated
        """
        if not self.config.enabled or not self.config.random_misclicks:
            return False
        
        # Low probability of misclick (1-3%)
        return random.random() < random.uniform(0.01, 0.03)
    
    def add_reaction_delay(self) -> None:
        """
        Add a human-like reaction delay before actions.
        Varies based on fatigue and randomization.
        """
        # Base reaction time: 150-400ms
        reaction_time = random.uniform(0.15, 0.40)
        
        # Increase with fatigue
        if self.config.fatigue_simulation:
            reaction_time *= (1.0 + self.fatigue_level * 0.3)
        
        time.sleep(reaction_time)
    
    def perform_attention_shift(self) -> None:
        """
        Simulate shifting attention away from the game briefly.
        """
        if not self.config.enabled or not self.config.attention_shifts:
            return
        
        # Occasionally look away
        if random.random() < 0.05:  # 5% chance
            print("Attention shift: Looking away briefly...")
            time.sleep(random.uniform(2.0, 5.0))
    
    def randomize_tab_switching(self) -> None:
        """Occasionally switch to random game tabs."""
        if not self.config.enabled or not self.config.tab_switching:
            return
        
        elapsed = time.time() - self.last_tab_switch
        
        # Check tabs every 5-15 minutes
        if elapsed >= random.uniform(300, 900):
            import keyboard
            
            # Random tab (F1-F7)
            tab = f"f{random.randint(1, 7)}"
            keyboard.press_and_release(tab)
            time.sleep(random.uniform(0.5, 2.0))
            
            # Return to inventory
            keyboard.press_and_release('esc')
            time.sleep(random.uniform(0.3, 0.6))
            
            self.last_tab_switch = time.time()
    
    def get_fatigue_level(self) -> float:
        """
        Get current fatigue level.
        
        Returns:
            Fatigue level from 0.0 (fresh) to 1.0 (exhausted)
        """
        return self.fatigue_level
    
    def reset_fatigue(self) -> None:
        """Reset fatigue level (after a break)."""
        self.fatigue_level = 0.0
    
    def get_status(self) -> dict:
        """
        Get anti-ban manager status.
        
        Returns:
            Dictionary with status information
        """
        next_break_minutes = None
        if self.next_break:
            next_break_minutes = (self.next_break.start_time - time.time()) / 60
        
        next_logout_break_minutes = None
        if self.next_logout_break:
            next_logout_break_minutes = (self.next_logout_break.start_time - time.time()) / 60
        
        return {
            "enabled": self.config.enabled,
            "actions_performed": self.action_count,
            "fatigue_level": f"{self.fatigue_level * 100:.1f}%",
            "next_idle_break_in_minutes": f"{next_break_minutes:.1f}" if next_break_minutes else "N/A",
            "next_logout_break_in_minutes": f"{next_logout_break_minutes:.1f}" if next_logout_break_minutes else "N/A",
            "last_idle_action_seconds_ago": time.time() - self.last_idle_action
        }


class AntiBanDecorator:
    """
    Decorator class to wrap bot actions with anti-ban behaviors.
    """
    
    def __init__(self, anti_ban: AntiBanManager):
        """
        Initialize decorator.
        
        Args:
            anti_ban: AntiBanManager instance
        """
        self.anti_ban = anti_ban
    
    def wrap_action(self, action: Callable) -> Callable:
        """
        Wrap an action with anti-ban behaviors.
        
        Args:
            action: Function to wrap
            
        Returns:
            Wrapped function
        """
        def wrapped(*args, **kwargs):
            # Check if break is needed
            should_break, break_type = self.anti_ban.should_take_break()
            if should_break:
                self.anti_ban.take_break(break_type)
            
            # Perform random idle action occasionally
            if self.anti_ban.should_perform_idle_action():
                self.anti_ban.perform_idle_action()
            
            # Add reaction delay
            self.anti_ban.add_reaction_delay()
            
            # Execute the actual action
            result = action(*args, **kwargs)
            
            # Apply action delay
            self.anti_ban.apply_action_delay()
            
            # Occasional tab switching
            self.anti_ban.randomize_tab_switching()
            
            # Attention shifts
            self.anti_ban.perform_attention_shift()
            
            return result
        
        return wrapped
