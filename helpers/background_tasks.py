# helpers/background_tasks.py
"""
Background Task Manager for Non-blocking Operations
Handles long-running operations in the background to prevent user blocking.
"""

import asyncio
import logging
from typing import Callable, Any, Dict, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """
    Manages background tasks to prevent blocking of user interactions.
    
    Features:
    - Non-blocking task execution
    - Task tracking and monitoring
    - Error handling and reporting
    - Resource cleanup
    """
    
    def __init__(self):
        self._tasks: Dict[str, asyncio.Task] = {}
        self._results: Dict[str, Any] = {}
        self._errors: Dict[str, Exception] = {}
        self._lock = asyncio.Lock()
        
    async def submit_task(
        self, 
        func: Callable, 
        *args, 
        task_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Submit a task for background execution.
        
        Args:
            func: Function to execute
            *args: Function arguments
            task_id: Optional task ID (auto-generated if not provided)
            **kwargs: Function keyword arguments
            
        Returns:
            str: Task ID for tracking
        """
        if task_id is None:
            task_id = str(uuid4())
            
        async def _run_task():
            try:
                logger.debug(f"Starting background task {task_id}")
                result = await func(*args, **kwargs)
                async with self._lock:
                    self._results[task_id] = result
                logger.debug(f"Completed background task {task_id}")
            except Exception as e:
                logger.error(f"Background task {task_id} failed: {e}")
                async with self._lock:
                    self._errors[task_id] = e
                # Re-raise to ensure task is marked as failed
                raise
            finally:
                # Clean up completed task
                async with self._lock:
                    self._tasks.pop(task_id, None)
        
        # Create and track the task
        task = asyncio.create_task(_run_task())
        async with self._lock:
            self._tasks[task_id] = task
            
        logger.info(f"Submitted background task {task_id}")
        return task_id
    
    async def get_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Get the result of a background task.
        
        Args:
            task_id: Task ID
            timeout: Optional timeout for waiting
            
        Returns:
            Any: Task result
            
        Raises:
            Exception: If task failed
            asyncio.TimeoutError: If timeout exceeded
        """
        # Check if we already have the result
        async with self._lock:
            if task_id in self._results:
                return self._results.pop(task_id)
            if task_id in self._errors:
                raise self._errors.pop(task_id)
        
        # Wait for task completion
        task = self._tasks.get(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
            
        try:
            if timeout:
                await asyncio.wait_for(task, timeout=timeout)
            else:
                await task
                
            # Check results again
            async with self._lock:
                if task_id in self._results:
                    return self._results.pop(task_id)
                if task_id in self._errors:
                    raise self._errors.pop(task_id)
                    
            # If we get here, task completed but no result was stored
            return None
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            # Store error for future retrieval
            async with self._lock:
                self._errors[task_id] = e
            raise
    
    def is_running(self, task_id: str) -> bool:
        """Check if a task is still running."""
        return task_id in self._tasks
    
    def get_status(self, task_id: str) -> str:
        """Get task status."""
        if task_id in self._results:
            return "completed"
        if task_id in self._errors:
            return "failed"
        if task_id in self._tasks:
            return "running"
        return "unknown"
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a background task."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.cancel()
                self._tasks.pop(task_id, None)
                return True
            return False
    
    async def cleanup(self):
        """Cancel all running tasks and cleanup resources."""
        async with self._lock:
            # Cancel all tasks
            for task in self._tasks.values():
                task.cancel()
            
            # Wait for tasks to finish cancellation
            if self._tasks:
                await asyncio.gather(*self._tasks.values(), return_exceptions=True)
            
            # Clear all data
            self._tasks.clear()
            self._results.clear()
            self._errors.clear()


# Global background task manager instance
_background_task_manager: Optional[BackgroundTaskManager] = None


async def get_background_task_manager() -> BackgroundTaskManager:
    """Get the global background task manager instance."""
    global _background_task_manager
    if _background_task_manager is None:
        _background_task_manager = BackgroundTaskManager()
    return _background_task_manager


async def cleanup_background_task_manager():
    """Clean up the global background task manager."""
    global _background_task_manager
    if _background_task_manager:
        await _background_task_manager.cleanup()
        _background_task_manager = None