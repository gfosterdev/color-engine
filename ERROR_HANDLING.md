# Global Error Handling System

## Overview

The global error handling system provides centralized error management with emergency logout and clean shutdown capabilities for all OSRS bots. It handles both Python exceptions and logical failures (color/OCR not found, consecutive task failures).

## Components

### 1. GlobalErrorHandler (`core/error_handler.py`)

Singleton class that manages all error handling across the bot:

- **Emergency Shutdown**: Automatically stops bot, closes interfaces, and attempts logout
- **Error Logging**: Maintains history of errors with full context
- **Severity Detection**: Determines if errors are critical and require shutdown
- **Recovery Attempts**: For non-critical errors, attempts graceful recovery

### 2. BotBase (`core/bot_base.py`)

Abstract base class that all bots should inherit from:

- **Template Method Pattern**: Provides `start()` wrapper with error handling
- **Failure Tracking**: Tracks consecutive task failures
- **Automatic Cleanup**: Ensures cleanup runs even on error
- **State/Task Context**: Captures bot state and task info for error reports

### 3. Enhanced Task Engine (`core/task_engine.py`)

Tasks now track consecutive failures:

- **Failure Counter**: Each task maintains `consecutive_failures` count
- **Critical Detection**: Triggers global handler when failures exceed threshold
- **Better Cleanup**: `TaskQueue.stop()` properly cancels current task

### 4. Anti-Ban Integration (`core/anti_ban.py`)

Logout breaks now integrate with error handling:

- **Logout Failure Detection**: Triggers emergency shutdown if logout fails
- **Login Failure Handling**: Raises critical error if can't log back in
- **Error Context**: Provides detailed context for break-related failures

## Usage

### Creating a New Bot

```python
from core.bot_base import BotBase
from core.state_machine import StateMachine, BotState

class MyBot(BotBase):
    def __init__(self):
        super().__init__()  # Initialize BotBase
        self.osrs = OSRS()
        self.state_machine = StateMachine(BotState.IDLE)
        self.task_queue = TaskQueue("my_bot")
        # ... other initialization

    def _run_loop(self):
        """Main bot logic - respects self.running flag."""
        while self.running:
            # Your bot logic here
            self._do_work()

    def _cleanup(self):
        """Cleanup after bot stops."""
        self._print_statistics()
        # ... other cleanup

# Start the bot
bot = MyBot()
bot.start()  # Automatically handles errors and cleanup
```

### Tracking Task Results

Track task results to enable consecutive failure detection:

```python
def _mine_ore(self):
    """Mine ore with failure tracking."""
    task = MineOreTask(self.osrs, self.ore_object, self.interaction)
    result = task.run()

    # Track result for failure detection
    self._track_task_result("mine_ore", result.success)

    if result.success:
        self.ores_mined += 1
    else:
        print(f"Mining failed: {result.message}")
```

### Using AntiBanDecorator

Wrap actions with anti-ban behaviors:

```python
def _mine_ore(self):
    """Mine with anti-ban wrapper."""
    def mine_action():
        task = MineOreTask(self.osrs, self.ore_object, self.interaction)
        result = task.run()
        self._track_task_result("mine_ore", result.success)
        # ... handle result

    # Execute with anti-ban behaviors (delays, tab switches, etc.)
    self.anti_ban_decorator.wrap_action(mine_action)()
```

## Error Handling Behavior

### Critical Errors (Emergency Shutdown)

These errors trigger immediate emergency shutdown with logout:

- **Python Exceptions**: RuntimeError, OSError, WindowsError, etc.
- **Consecutive Failures**: 3+ task failures in a row
- **Timeout Errors**: Tasks exceeding timeout threshold
- **Login Failures**: Can't log back in after logout break
- **Window Lost**: RuneLite window closed or not found

**Emergency Shutdown Sequence:**

1. Stop bot loop (`running = False`)
2. Stop task queue
3. Close game interfaces
4. Attempt logout (5s timeout)
5. Update state machine (ERROR → STOPPING → IDLE)
6. Print/save statistics

### Non-Critical Errors (Recovery)

These errors trigger recovery attempt:

- **Single Task Failure**: First or second failure of a task
- **Minor Issues**: Temporary color/OCR detection failures

**Recovery Sequence:**

1. Close any open interfaces
2. Transition to RECOVERING state
3. Wait 2 seconds
4. Resume normal operation

### User Interruption (Ctrl+C)

KeyboardInterrupt is caught and results in clean shutdown:

1. Print "Bot stopped by user" message
2. Run cleanup method
3. Exit gracefully (no error state)

## Error Context

All errors are logged with full context:

```python
ErrorContext(
    error=exception,
    error_type="RuntimeError",
    bot_state="MINING",           # Current state machine state
    current_task="mine_ore",      # Current task name
    consecutive_failures=3,       # Failure count
    timestamp=1234567890.0,
    traceback_str="Full traceback..."
)
```

## Configuration

### Failure Threshold

By default, 3 consecutive failures trigger emergency shutdown. This is hardcoded in `BotBase._track_task_result()` but can be adjusted:

```python
# In BotBase or custom bot class
if self._consecutive_task_failures >= 5:  # Increase threshold
    raise RuntimeError(...)
```

### Logout Timeout

Emergency logout has 5-second timeout by default. Configured in `GlobalErrorHandler._attempt_logout_with_timeout()`:

```python
handler._attempt_logout_with_timeout(osrs_client, timeout=10.0)  # Longer timeout
```

## Testing

Run the test suite to verify error handling:

```bash
python test_error_handling.py
```

Tests cover:

- Normal operation with clean shutdown
- Immediate Python exceptions
- Consecutive task failures
- Error context creation and logging
- Critical failure detection

## Migration Guide

### Existing Bots (e.g., MiningBot)

1. **Change inheritance**: `class MiningBot(BotBase):`
2. **Add super init**: `super().__init__()` in `__init__()`
3. **Rename start()**: Rename `start()` method to `_run_loop()`
4. **Create \_cleanup()**: Move cleanup logic to `_cleanup()` method
5. **Track results**: Add `self._track_task_result()` calls
6. **Remove try-except**: Remove manual try-except in start (BotBase handles it)

### Before:

```python
class MiningBot:
    def __init__(self):
        self.running = False
        # ...

    def start(self):
        self.running = True
        try:
            self._run_loop()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.stop()
```

### After:

```python
class MiningBot(BotBase):
    def __init__(self):
        super().__init__()
        # ... (no self.running = False)

    def _run_loop(self):
        # Main loop (no try-except needed)
        while self.running:
            # Bot logic
            pass

    def _cleanup(self):
        # Cleanup operations
        pass
```

## Best Practices

1. **Always track task results**: Call `_track_task_result()` for critical tasks
2. **Use anti-ban decorator**: Wrap repeating actions with `anti_ban_decorator.wrap_action()`
3. **Don't catch everything**: Let critical exceptions propagate to global handler
4. **Validate operations**: Check if operations succeeded before continuing
5. **Provide context**: Transition state machine to ERROR state on failures
6. **Test failure scenarios**: Use test script to verify error handling works

## Troubleshooting

### Bot doesn't stop on errors

- Ensure you're calling `self._track_task_result()` for task failures
- Check that `self.running` flag is respected in `_run_loop()`
- Verify bot inherits from `BotBase`

### Logout not working

- Check OSRS client has valid `logout()` method
- Ensure `osrs` attribute exists on bot instance
- Verify RuneLite window is still open

### Cleanup not running

- Make sure `_cleanup()` method is implemented
- Check for exceptions in cleanup code (wrap in try-except if needed)

### Multiple emergency shutdowns

- Error handler tracks if shutdown already in progress
- Second shutdown attempts are ignored with warning message

## Future Enhancements

Potential improvements to consider:

1. **Configurable thresholds**: Make failure thresholds configurable per bot
2. **Error recovery strategies**: Different recovery actions based on error type
3. **Persistent error log**: Save errors to file for analysis
4. **Email/Discord alerts**: Notify on critical failures
5. **Automatic restart**: Attempt to restart bot after recovery
6. **Graceful degradation**: Continue with reduced functionality on minor errors
