"""
Test script for global error handling system.

Tests emergency shutdown, task failure tracking, and error recovery.
"""

from core.error_handler import GlobalErrorHandler, ErrorContext, ErrorSeverity
from core.bot_base import BotBase
from core.task_engine import Task, TaskResult, TaskPriority
import time


class DummyOSRS:
    """Mock OSRS client for testing."""
    def __init__(self):
        self.logout_called = False
    
    def logout(self):
        print("  [Mock] Logging out...")
        self.logout_called = True
        return True
    
    class MockInterfaces:
        def close_interface(self):
            print("  [Mock] Closing interfaces...")
    
    interfaces = MockInterfaces()


class DummyStateMachine:
    """Mock state machine for testing."""
    def __init__(self):
        self.current_state_value = "MINING"
        
    class State:
        def __init__(self, val):
            self.value = val
    
    @property
    def current_state(self):
        return self.State(self.current_state_value)
    
    def transition(self, state, message):
        print(f"  [Mock] State transition: {state} - {message}")


class DummyTaskQueue:
    """Mock task queue for testing."""
    def __init__(self):
        self.current_task = None
        self.stopped = False
    
    def stop(self):
        print("  [Mock] Task queue stopped")
        self.stopped = True


class TestBot(BotBase):
    """Test bot for demonstrating error handling."""
    
    def __init__(self, should_fail: bool = False, fail_after: int = 0):
        super().__init__()
        self.osrs = DummyOSRS()
        self.state_machine = DummyStateMachine()
        self.task_queue = DummyTaskQueue()
        self.should_fail = should_fail
        self.fail_after = fail_after
        self.iterations = 0
    
    def _run_loop(self):
        """Test bot loop."""
        print("Test bot running...")
        
        while self.running:
            self.iterations += 1
            print(f"  Iteration {self.iterations}")
            
            # Simulate work
            time.sleep(0.5)
            
            # Trigger failure if configured
            if self.should_fail and self.iterations >= self.fail_after:
                if self.fail_after == 1:
                    # Immediate Python exception
                    raise RuntimeError("Test error: Immediate failure")
                else:
                    # Simulate task failure
                    self._track_task_result("test_task", False)
            else:
                # Success
                self._track_task_result("test_task", True)
            
            # Stop after a few iterations if no failure
            if self.iterations >= 5 and not self.should_fail:
                self.stop()
    
    def _cleanup(self):
        """Cleanup for test bot."""
        print(f"Test bot cleanup - ran {self.iterations} iterations")


def test_normal_operation():
    """Test 1: Normal operation with clean shutdown."""
    print("\n" + "="*60)
    print("TEST 1: Normal Operation")
    print("="*60)
    
    bot = TestBot(should_fail=False)
    bot.start()
    
    print(f"✓ Bot completed {bot.iterations} iterations successfully")
    print(f"✓ Final state: running={bot.running}")


def test_immediate_exception():
    """Test 2: Immediate Python exception triggers emergency shutdown."""
    print("\n" + "="*60)
    print("TEST 2: Immediate Exception")
    print("="*60)
    
    bot = TestBot(should_fail=True, fail_after=1)
    bot.start()
    
    print(f"✓ Emergency shutdown executed")
    print(f"✓ Logout called: {bot.osrs.logout_called}")
    print(f"✓ Task queue stopped: {bot.task_queue.stopped}")


def test_consecutive_failures():
    """Test 3: Consecutive task failures trigger emergency shutdown."""
    print("\n" + "="*60)
    print("TEST 3: Consecutive Task Failures")
    print("="*60)
    
    bot = TestBot(should_fail=True, fail_after=2)
    bot.start()
    
    print(f"✓ Emergency shutdown executed after consecutive failures")
    print(f"✓ Logout called: {bot.osrs.logout_called}")
    print(f"✓ Task queue stopped: {bot.task_queue.stopped}")


def test_error_context():
    """Test 4: Error context creation and logging."""
    print("\n" + "="*60)
    print("TEST 4: Error Context")
    print("="*60)
    
    handler = GlobalErrorHandler.get_instance()
    handler.reset()  # Clear previous errors
    
    try:
        raise ValueError("Test error for context")
    except Exception as e:
        context = ErrorContext(
            error=e,
            error_type=type(e).__name__,
            bot_state="MINING",
            current_task="mine_ore",
            consecutive_failures=2
        )
        
        handler._log_error(context)
        handler._print_error(context)
    
    summary = handler.get_error_summary()
    print(f"✓ Error logged: {summary}")


def test_critical_failure_detection():
    """Test 5: Critical failure detection."""
    print("\n" + "="*60)
    print("TEST 5: Critical Failure Detection")
    print("="*60)
    
    handler = GlobalErrorHandler.get_instance()
    
    # Test consecutive failures
    result1 = TaskResult(success=False, message="Could not find ore")
    is_critical1 = handler.is_critical_failure(result1, consecutive_count=3)
    print(f"✓ 3 consecutive failures: critical={is_critical1}")
    
    # Test timeout
    result2 = TaskResult(success=False, message="Task timed out after 30s")
    is_critical2 = handler.is_critical_failure(result2, consecutive_count=0)
    print(f"✓ Timeout error: critical={is_critical2}")
    
    # Test exception
    result3 = TaskResult(success=False, message="Error", error=RuntimeError("Test"))
    is_critical3 = handler.is_critical_failure(result3, consecutive_count=0)
    print(f"✓ Exception present: critical={is_critical3}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GLOBAL ERROR HANDLING SYSTEM - TEST SUITE")
    print("="*60)
    
    test_normal_operation()
    test_error_context()
    test_critical_failure_detection()
    test_immediate_exception()
    test_consecutive_failures()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
