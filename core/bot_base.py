"""
Base class for OSRS bot implementations.

Provides template method pattern with built-in error handling and cleanup.
"""

from abc import ABC, abstractmethod
from typing import Optional
from core.error_handler import GlobalErrorHandler, ErrorContext


class BotBase(ABC):
    """
    Abstract base class for all bot implementations.
    
    Provides consistent error handling, emergency shutdown, and cleanup
    across all bot types. Subclasses implement _run_loop() and _cleanup().
    """
    
    def __init__(self):
        """Initialize bot base."""
        self.running = False
        self.error_handler = GlobalErrorHandler.get_instance()
        self._consecutive_task_failures = 0
        self._last_task_name: Optional[str] = None
    
    @abstractmethod
    def _run_loop(self):
        """
        Main bot execution loop.
        
        Subclasses must implement this method with their bot logic.
        This method should respect self.running flag and exit when False.
        """
        pass
    
    @abstractmethod
    def _cleanup(self):
        """
        Cleanup operations after bot stops.
        
        Subclasses must implement this method to handle:
        - Printing statistics
        - Saving state
        - Releasing resources
        """
        pass
    
    def start(self):
        """
        Start the bot with comprehensive error handling.
        
        This is the main entry point. It wraps _run_loop() with
        error handling and ensures cleanup always runs.
        """
        self.running = True
        
        try:
            print(f"Starting {self.__class__.__name__}...")
            self._run_loop()
            
        except KeyboardInterrupt:
            print("\n" + "="*60)
            print("BOT STOPPED BY USER (Ctrl+C)")
            print("="*60)
            
        except Exception as e:
            # Create error context
            context = ErrorContext(
                error=e,
                error_type=type(e).__name__,
                bot_state=self._get_bot_state(),
                current_task=self._get_current_task(),
                consecutive_failures=self._consecutive_task_failures
            )
            
            # Handle with global error handler
            self.error_handler.handle_error(self, e, context)
            
        finally:
            # Always attempt cleanup
            try:
                self._cleanup()
            except Exception as cleanup_error:
                print(f"\n⚠ Cleanup error: {cleanup_error}")
    
    def stop(self):
        """
        Stop the bot gracefully.
        
        Sets running flag to False, which should cause _run_loop() to exit.
        """
        self.running = False
    
    def _get_bot_state(self) -> Optional[str]:
        """
        Get current bot state for error context.
        
        Override this if bot has a state machine.
        
        Returns:
            Current state name or None
        """
        if hasattr(self, 'state_machine'):
            return self.state_machine.current_state.value  # type: ignore
        return None
    
    def _get_current_task(self) -> Optional[str]:
        """
        Get current task name for error context.
        
        Override this if bot has a task queue.
        
        Returns:
            Current task name or None
        """
        if hasattr(self, 'task_queue') and self.task_queue.current_task:  # type: ignore
            return self.task_queue.current_task.name  # type: ignore
        return self._last_task_name
    
    def _track_task_result(self, task_name: str, success: bool):
        """
        Track task results for failure detection.
        
        Args:
            task_name: Name of the task
            success: Whether task succeeded
        """
        if success:
            self._consecutive_task_failures = 0
        else:
            if self._last_task_name == task_name:
                self._consecutive_task_failures += 1
            else:
                self._consecutive_task_failures = 1
        
        self._last_task_name = task_name
        
        # Check if we should trigger emergency shutdown
        if self._consecutive_task_failures >= 3:
            raise RuntimeError(
                f"Critical failure: Task '{task_name}' failed "
                f"{self._consecutive_task_failures} times consecutively"
            )
    
    @property
    def requires_emergency_shutdown(self) -> bool:
        """
        Check if bot requires emergency shutdown.
        
        Returns:
            True if consecutive failures exceed threshold
        """
        return self._consecutive_task_failures >= 3
