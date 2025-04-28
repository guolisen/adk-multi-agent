"""
Async utilities for Streamlit frontend
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine, TypeVar

# Type variable for generic function
T = TypeVar('T')


def run_async(coroutine: Coroutine) -> Any:
    """
    Run an asynchronous coroutine from synchronous Streamlit code
    
    Args:
        coroutine: The asynchronous coroutine to run
        
    Returns:
        The result of the coroutine
    """
    # Create a new event loop in this thread
    loop = asyncio.new_event_loop()
    try:
        # Run the coroutine in the new loop
        return loop.run_until_complete(coroutine)
    finally:
        # Clean up the loop
        loop.close()


def async_cache(ttl_seconds: int = 60):
    """
    Decorator for caching async function results
    
    Args:
        ttl_seconds: Time-to-live in seconds for cached results
        
    Returns:
        Decorated function
    """
    cache = {}
    
    def decorator(func: Callable[..., Coroutine]):
        async def wrapper(*args, **kwargs):
            # Create a cache key from the function name and arguments
            key = str(func.__name__) + str(args) + str(kwargs)
            
            # Check if result is in cache and not expired
            now = asyncio.get_event_loop().time()
            if key in cache and (now - cache[key]['timestamp']) < ttl_seconds:
                return cache[key]['result']
            
            # Call the function and cache result
            result = await func(*args, **kwargs)
            cache[key] = {
                'result': result,
                'timestamp': now
            }
            
            return result
            
        return wrapper
        
    return decorator


class AsyncExecutor:
    """
    Utility class for executing async tasks in the background
    """
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize the async executor
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loop = asyncio.get_event_loop()
        self.tasks = {}
        
    def submit(self, task_id: str, coroutine: Coroutine) -> None:
        """
        Submit a task for execution
        
        Args:
            task_id: Unique identifier for the task
            coroutine: The coroutine to execute
        """
        future = asyncio.run_coroutine_threadsafe(coroutine, self.loop)
        self.tasks[task_id] = future
        
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a running task
        
        Args:
            task_id: The ID of the task to cancel
            
        Returns:
            True if task was successfully cancelled, False otherwise
        """
        if task_id in self.tasks:
            self.tasks[task_id].cancel()
            del self.tasks[task_id]
            return True
        return False
        
    def is_running(self, task_id: str) -> bool:
        """
        Check if a task is still running
        
        Args:
            task_id: The ID of the task to check
            
        Returns:
            True if the task is still running
        """
        return task_id in self.tasks and not self.tasks[task_id].done()
        
    def get_result(self, task_id: str, default: Any = None) -> Any:
        """
        Get the result of a completed task
        
        Args:
            task_id: The ID of the task
            default: Default value to return if task not found or not completed
            
        Returns:
            The task result or default value
        """
        if task_id in self.tasks and self.tasks[task_id].done():
            try:
                result = self.tasks[task_id].result()
                del self.tasks[task_id]
                return result
            except Exception:
                del self.tasks[task_id]
        return default
