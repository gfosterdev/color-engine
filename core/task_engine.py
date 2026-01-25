"""
Task automation framework for OSRS bot.

Provides Task and TaskQueue abstractions for managing complex bot workflows.
"""

from typing import Optional, List, Callable, Any, Dict
from dataclasses import dataclass, field
from enum import Enum
import time
import random


class TaskStatus(Enum):
    """Status of a task execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = 0  # Must execute immediately (e.g., eat food when low health)
    HIGH = 1      # Important tasks (e.g., bank when inventory full)
    NORMAL = 2    # Regular tasks (e.g., mine ore, chop trees)
    LOW = 3       # Optional tasks (e.g., anti-ban actions)


@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    retry_recommended: bool = False
    error: Optional[Exception] = None


class Task:
    """
    Base class for bot tasks.
    
    Tasks represent atomic actions or workflows that the bot can execute.
    Subclass this to create specific task implementations.
    """
    
    def __init__(self, name: str, priority: TaskPriority = TaskPriority.NORMAL):
        """
        Initialize a task.
        
        Args:
            name: Human-readable task name
            priority: Task priority level
        """
        self.name = name
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.max_retries = 3
        self.retry_delay_min = 1.0
        self.retry_delay_max = 3.0
        self.timeout = 30.0  # seconds
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
    
    def validate_preconditions(self) -> TaskResult:
        """
        Check if preconditions for task execution are met.
        
        Override this to add validation logic.
        
        Returns:
            TaskResult indicating if preconditions are satisfied
        """
        return TaskResult(success=True, message="Preconditions satisfied")
    
    def execute(self) -> TaskResult:
        """
        Execute the task.
        
        Override this to implement task logic.
        
        Returns:
            TaskResult with execution outcome
        """
        raise NotImplementedError("Task subclasses must implement execute()")
    
    def handle_failure(self, result: TaskResult) -> TaskResult:
        """
        Handle task failure.
        
        Override this to add custom failure handling.
        
        Args:
            result: The failed TaskResult
            
        Returns:
            TaskResult indicating recovery action
        """
        return result
    
    def estimate_duration(self) -> float:
        """
        Estimate task execution time in seconds.
        
        Override this to provide better estimates.
        
        Returns:
            Estimated seconds to complete
        """
        return 5.0
    
    def run(self) -> TaskResult:
        """
        Run the task with full lifecycle management.
        
        Returns:
            TaskResult with final outcome
        """
        self.status = TaskStatus.RUNNING
        self.started_at = time.time()
        
        try:
            # Validate preconditions
            precondition_result = self.validate_preconditions()
            if not precondition_result.success:
                self.status = TaskStatus.FAILED
                return precondition_result
            
            # Execute with retry logic
            attempts = 0
            last_result = None
            
            while attempts < self.max_retries:
                attempts += 1
                
                # Check timeout
                if self.started_at and (time.time() - self.started_at) > self.timeout:
                    self.status = TaskStatus.FAILED
                    return TaskResult(
                        success=False,
                        message=f"Task '{self.name}' timed out after {self.timeout}s"
                    )
                
                # Execute task
                result = self.execute()
                
                if result.success:
                    self.status = TaskStatus.COMPLETED
                    self.completed_at = time.time()
                    return result
                
                last_result = result
                
                # Check if retry is recommended
                if not result.retry_recommended or attempts >= self.max_retries:
                    break
                
                # Wait before retry with randomization
                delay = random.uniform(self.retry_delay_min, self.retry_delay_max)
                time.sleep(delay)
            
            # Task failed after retries
            self.status = TaskStatus.FAILED
            self.completed_at = time.time()
            
            # Try to handle failure
            if last_result:
                return self.handle_failure(last_result)
            
            return TaskResult(
                success=False,
                message=f"Task '{self.name}' failed after {attempts} attempts"
            )
        
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.completed_at = time.time()
            return TaskResult(
                success=False,
                message=f"Task '{self.name}' raised exception: {str(e)}",
                error=e
            )
    
    def cancel(self):
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
    
    def __lt__(self, other):
        """Compare tasks by priority for queue ordering."""
        return self.priority.value < other.priority.value


class TaskQueue:
    """
    Priority queue for managing task execution.
    
    Automatically executes tasks based on priority and manages task lifecycle.
    """
    
    def __init__(self, name: str = "default"):
        """
        Initialize task queue.
        
        Args:
            name: Name for this queue
        """
        self.name = name
        self.tasks: List[Task] = []
        self.running = False
        self.paused = False
        self.current_task: Optional[Task] = None
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to the queue.
        
        Args:
            task: Task to add
        """
        self.tasks.append(task)
        # Sort by priority (lower priority value = higher priority)
        self.tasks.sort()
    
    def add_tasks(self, tasks: List[Task]) -> None:
        """
        Add multiple tasks to the queue.
        
        Args:
            tasks: List of tasks to add
        """
        self.tasks.extend(tasks)
        self.tasks.sort()
    
    def get_next_task(self) -> Optional[Task]:
        """
        Get the next pending task by priority.
        
        Returns:
            Next task or None if queue is empty
        """
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                return task
        return None
    
    def execute_next(self) -> Optional[TaskResult]:
        """
        Execute the next task in the queue.
        
        Returns:
            TaskResult or None if no tasks available
        """
        if self.paused:
            return None
        
        task = self.get_next_task()
        
        if not task:
            return None
        
        self.current_task = task
        result = task.run()
        
        # Move task to appropriate list
        self.tasks.remove(task)
        
        if result.success:
            self.completed_tasks.append(task)
        else:
            self.failed_tasks.append(task)
        
        self.current_task = None
        
        return result
    
    def execute_all(self) -> List[TaskResult]:
        """
        Execute all tasks in the queue.
        
        Returns:
            List of TaskResults
        """
        self.running = True
        results = []
        
        while self.running and not self.paused:
            result = self.execute_next()
            
            if result is None:
                break
            
            results.append(result)
        
        self.running = False
        return results
    
    def pause(self) -> None:
        """Pause task execution."""
        self.paused = True
    
    def resume(self) -> None:
        """Resume task execution."""
        self.paused = False
    
    def stop(self) -> None:
        """Stop task execution."""
        self.running = False
        if self.current_task:
            self.current_task.cancel()
    
    def clear(self) -> None:
        """Clear all pending tasks."""
        self.tasks = [
            task for task in self.tasks
            if task.status == TaskStatus.RUNNING
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get queue status.
        
        Returns:
            Dictionary with queue statistics
        """
        pending = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)
        running = sum(1 for t in self.tasks if t.status == TaskStatus.RUNNING)
        
        return {
            "name": self.name,
            "running": self.running,
            "paused": self.paused,
            "pending_tasks": pending,
            "running_tasks": running,
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "current_task": self.current_task.name if self.current_task else None
        }
    
    def estimate_time_remaining(self) -> float:
        """
        Estimate total time to complete all pending tasks.
        
        Returns:
            Estimated seconds
        """
        total = 0.0
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                total += task.estimate_duration()
        return total
