"""
Global error handling system for OSRS bot.

Provides centralized error handling with emergency logout and clean shutdown.
"""

import traceback
import time
from typing import Optional, Any
from dataclasses import dataclass
from enum import Enum


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    LOW = "low"          # Minor issues, can continue
    MEDIUM = "medium"    # Significant issues, may need recovery
    HIGH = "high"        # Critical issues, should stop bot
    CRITICAL = "critical"  # Immediate shutdown required


@dataclass
class ErrorContext:
    """Context information for error handling."""
    error: Exception
    error_type: str
    bot_state: Optional[str] = None
    current_task: Optional[str] = None
    consecutive_failures: int = 0
    timestamp: Optional[float] = None
    traceback_str: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if not self.traceback_str:
            self.traceback_str = traceback.format_exc()


class GlobalErrorHandler:
    """
    Singleton error handler for bot-wide error management.
    
    Handles both Python exceptions and logical failures (color/OCR not found),
    attempts emergency logout, and ensures clean shutdown.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.error_log = []
        self.max_log_entries = 100
        self.emergency_shutdown_triggered = False
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'GlobalErrorHandler':
        """Get the singleton instance."""
        return cls()
    
    def handle_error(self, bot_instance: Any, error: Exception, 
                     context: Optional[ErrorContext] = None) -> bool:
        """
        Handle an error with emergency shutdown procedures.
        
        Args:
            bot_instance: Bot instance (must have osrs, state_machine, task_queue attributes)
            error: Exception that occurred
            context: Optional error context information
            
        Returns:
            True if error handled successfully, False otherwise
        """
        if context is None:
            context = ErrorContext(
                error=error,
                error_type=type(error).__name__,
                traceback_str=traceback.format_exc()
            )
        
        # Log the error
        self._log_error(context)
        
        # Print error details
        self._print_error(context)
        
        # Determine severity
        severity = self._determine_severity(context)
        
        # Handle based on severity
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            return self._emergency_shutdown(bot_instance, context)
        else:
            return self._attempt_recovery(bot_instance, context)
    
    def is_critical_failure(self, task_result, consecutive_count: int = 0) -> bool:
        """
        Determine if a task result represents a critical failure.
        
        Args:
            task_result: TaskResult object
            consecutive_count: Number of consecutive failures
            
        Returns:
            True if failure is critical and requires emergency shutdown
        """
        # Threshold for consecutive failures
        if consecutive_count >= 3:
            return True
        
        # Check for critical error indicators
        if task_result.error:
            return True
        
        # Check for specific failure messages
        critical_messages = [
            "timed out",
            "timeout",
            "cannot find window",
            "window closed",
            "connection lost"
        ]
        
        message_lower = task_result.message.lower()
        for critical_msg in critical_messages:
            if critical_msg in message_lower:
                return True
        
        return False
    
    def _determine_severity(self, context: ErrorContext) -> ErrorSeverity:
        """Determine error severity."""
        # Critical Python exceptions
        critical_exceptions = [
            "SystemExit",
            "KeyboardInterrupt",
            "MemoryError"
        ]
        
        if context.error_type in critical_exceptions:
            return ErrorSeverity.CRITICAL
        
        # High severity based on consecutive failures
        if context.consecutive_failures >= 3:
            return ErrorSeverity.HIGH
        
        # High severity based on error type
        high_severity_exceptions = [
            "RuntimeError",
            "WindowsError",
            "OSError",
            "IOError"
        ]
        
        if context.error_type in high_severity_exceptions:
            return ErrorSeverity.HIGH
        
        # Medium severity for task failures
        if context.consecutive_failures >= 1:
            return ErrorSeverity.MEDIUM
        
        return ErrorSeverity.LOW
    
    def _emergency_shutdown(self, bot_instance: Any, context: ErrorContext) -> bool:
        """
        Perform emergency shutdown with logout attempt.
        
        Args:
            bot_instance: Bot instance
            context: Error context
            
        Returns:
            True if shutdown completed successfully
        """
        if self.emergency_shutdown_triggered:
            print("Emergency shutdown already in progress...")
            return False
        
        self.emergency_shutdown_triggered = True
        
        print("\n" + "="*60)
        print("EMERGENCY SHUTDOWN INITIATED")
        print("="*60)
        
        success = True
        
        # Step 1: Stop main loop
        print("1. Stopping bot activity...")
        try:
            if hasattr(bot_instance, 'running'):
                bot_instance.running = False
                print("   ✓ Bot loop stopped")
        except Exception as e:
            print(f"   ✗ Failed to stop bot loop: {e}")
            success = False
        
        # Step 2: Stop task queue
        print("2. Stopping task queue...")
        try:
            if hasattr(bot_instance, 'task_queue'):
                bot_instance.task_queue.stop()
                print("   ✓ Task queue stopped")
        except Exception as e:
            print(f"   ✗ Failed to stop task queue: {e}")
            success = False
        
        # Step 3: Close interfaces
        print("3. Closing game interfaces...")
        try:
            if hasattr(bot_instance, 'osrs'):
                bot_instance.osrs.interfaces.close_interface()
                time.sleep(0.5)
                print("   ✓ Interfaces closed")
        except Exception as e:
            print(f"   ✗ Failed to close interfaces: {e}")
            success = False
        
        # Step 4: Attempt logout with timeout
        print("4. Attempting emergency logout...")
        try:
            if hasattr(bot_instance, 'osrs'):
                logout_success = self._attempt_logout_with_timeout(
                    bot_instance.osrs, 
                    timeout=5.0
                )
                if logout_success:
                    print("   ✓ Successfully logged out")
                else:
                    print("   ✗ Logout failed or timed out")
                    success = False
        except Exception as e:
            print(f"   ✗ Logout error: {e}")
            success = False
        
        # Step 5: Transition state machine
        print("5. Updating state machine...")
        try:
            if hasattr(bot_instance, 'state_machine'):
                from core.state_machine import BotState
                bot_instance.state_machine.transition(BotState.ERROR, context.error_type)
                bot_instance.state_machine.transition(BotState.STOPPING, "Emergency shutdown")
                bot_instance.state_machine.transition(BotState.IDLE, "Shutdown complete")
                print("   ✓ State machine updated")
        except Exception as e:
            print(f"   ✗ State machine error: {e}")
            success = False
        
        # Step 6: Preserve statistics
        print("6. Saving statistics...")
        try:
            if hasattr(bot_instance, '_print_statistics'):
                bot_instance._print_statistics()
                print("   ✓ Statistics saved")
        except Exception as e:
            print(f"   ✗ Failed to save statistics: {e}")
        
        print("="*60)
        print("EMERGENCY SHUTDOWN COMPLETE")
        print("="*60 + "\n")
        
        return success
    
    def _attempt_logout_with_timeout(self, osrs_client, timeout: float = 5.0) -> bool:
        """
        Attempt logout with timeout protection.
        
        Args:
            osrs_client: OSRS client instance
            timeout: Maximum seconds to wait for logout
            
        Returns:
            True if logout succeeded within timeout
        """
        start_time = time.time()
        
        try:
            # Attempt logout
            result = osrs_client.logout()
            
            # Check if we exceeded timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"   ⚠ Logout took {elapsed:.1f}s (exceeded {timeout}s timeout)")
                return False
            
            return result
        except Exception as e:
            print(f"   ⚠ Logout exception: {e}")
            return False
    
    def _attempt_recovery(self, bot_instance: Any, context: ErrorContext) -> bool:
        """
        Attempt to recover from non-critical error.
        
        Args:
            bot_instance: Bot instance
            context: Error context
            
        Returns:
            True if recovery succeeded
        """
        print("\n" + "="*60)
        print("ATTEMPTING ERROR RECOVERY")
        print("="*60)
        
        try:
            # Close any open interfaces
            if hasattr(bot_instance, 'osrs'):
                bot_instance.osrs.interfaces.close_interface()
                time.sleep(1.0)
            
            # Transition to RECOVERING state
            if hasattr(bot_instance, 'state_machine'):
                from core.state_machine import BotState
                bot_instance.state_machine.transition(
                    BotState.RECOVERING, 
                    f"Recovering from {context.error_type}"
                )
                time.sleep(2.0)
            
            print("✓ Recovery attempt complete")
            print("="*60 + "\n")
            return True
            
        except Exception as e:
            print(f"✗ Recovery failed: {e}")
            print("="*60 + "\n")
            return False
    
    def _log_error(self, context: ErrorContext):
        """Log error to internal log."""
        self.error_log.append(context)
        
        # Trim log if too large
        if len(self.error_log) > self.max_log_entries:
            self.error_log = self.error_log[-self.max_log_entries:]
    
    def _print_error(self, context: ErrorContext):
        """Print error details to console."""
        print("\n" + "!"*60)
        print("ERROR DETECTED")
        print("!"*60)
        print(f"Error Type: {context.error_type}")
        print(f"Error: {context.error}")
        if context.bot_state:
            print(f"Bot State: {context.bot_state}")
        if context.current_task:
            print(f"Current Task: {context.current_task}")
        if context.consecutive_failures > 0:
            print(f"Consecutive Failures: {context.consecutive_failures}")
        print(f"\nTraceback:")
        print(context.traceback_str)
        print("!"*60 + "\n")
    
    def get_error_summary(self) -> dict:
        """Get summary of logged errors."""
        if not self.error_log:
            return {"total_errors": 0}
        
        error_types = {}
        for error_ctx in self.error_log:
            error_types[error_ctx.error_type] = error_types.get(error_ctx.error_type, 0) + 1
        
        return {
            "total_errors": len(self.error_log),
            "error_types": error_types,
            "most_recent": self.error_log[-1].error_type if self.error_log else None
        }
    
    def reset(self):
        """Reset error handler state (for testing)."""
        self.error_log = []
        self.emergency_shutdown_triggered = False
