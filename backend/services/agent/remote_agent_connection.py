"""Remote agent connection implementation for Deepdevflow."""

import json
import uuid
import logging
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
import httpx

from backend.models import Task, TaskState
from backend.utils.config import config

# Setup logging
logger = logging.getLogger(__name__)


class RemoteAgentConnection:
    """Connection to a remote agent."""
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        url: str, 
        capabilities: List[str] = None
    ):
        """Initialize remote agent connection.
        
        Args:
            name: The name of the remote agent.
            description: The description of the remote agent.
            url: The URL of the remote agent.
            capabilities: The capabilities of the remote agent.
        """
        self.name = name
        self.description = description
        self.url = url
        self.capabilities = capabilities or []
        
        # Get connection settings
        connection_config = config.get_agent_config("connection")
        self.timeout = connection_config.get("timeout", 30)
        self.retries = connection_config.get("retries", 3)
        self.retry_delay = connection_config.get("retry_delay", 1)
        
        # Initialize client
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
        # Initialize pending tasks
        self.pending_tasks = set()
    
    async def send_task(self, task_params: Dict[str, Any]) -> Task:
        """Send a task to the remote agent.
        
        Args:
            task_params: The task parameters to send.
            
        Returns:
            The task response.
        """
        task_id = task_params.get("id", str(uuid.uuid4()))
        
        # Store task ID in pending tasks
        self.pending_tasks.add(task_id)
        
        try:
            # Send task to remote agent
            response = await self.client.post(
                f"{self.url}/task/send",
                json=task_params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Create task from response
            task = self._create_task_from_response(result, task_id, task_params)
            
            # Remove from pending tasks if completed
            if task.status.state in [
                TaskState.COMPLETED,
                TaskState.CANCELED,
                TaskState.FAILED
            ]:
                self.pending_tasks.remove(task_id)
            
            return task
        except Exception as e:
            logger.error(f"Error sending task to remote agent {self.name}: {e}")
            
            # Remove from pending tasks
            if task_id in self.pending_tasks:
                self.pending_tasks.remove(task_id)
            
            # Create error task
            task = Task(
                id=task_id,
                agent_id="unknown",
                message_id="unknown",
                session_id=task_params.get("sessionId", "unknown"),
                state=TaskState.FAILED,
                metadata_json={
                    "error": str(e),
                    "agent": self.name
                }
            )
            
            return task
    
    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get the status of a task.
        
        Args:
            task_id: The ID of the task to get the status of.
            
        Returns:
            The task status or None if not found.
        """
        try:
            # Skip if not in pending tasks
            if task_id not in self.pending_tasks:
                return None
            
            # Send status request to remote agent
            response = await self.client.get(
                f"{self.url}/task/status/{task_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Create task from response
            task = self._create_task_from_response(result, task_id)
            
            # Remove from pending tasks if completed
            if task.status.state in [
                TaskState.COMPLETED,
                TaskState.CANCELED,
                TaskState.FAILED
            ]:
                self.pending_tasks.remove(task_id)
            
            return task
        except Exception as e:
            logger.error(f"Error getting task status from remote agent {self.name}: {e}")
            return None
    
    async def cancel_task(self, task_id: str) -> Optional[Task]:
        """Cancel a task.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            The canceled task or None if not found.
        """
        try:
            # Skip if not in pending tasks
            if task_id not in self.pending_tasks:
                return None
            
            # Send cancel request to remote agent
            response = await self.client.post(
                f"{self.url}/task/cancel/{task_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Create task from response
            task = self._create_task_from_response(result, task_id)
            
            # Remove from pending tasks
            self.pending_tasks.remove(task_id)
            
            return task
        except Exception as e:
            logger.error(f"Error canceling task on remote agent {self.name}: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if the remote agent is healthy.
        
        Returns:
            True if the remote agent is healthy, False otherwise.
        """
        try:
            # Send health check request to remote agent
            response = await self.client.get(
                f"{self.url}/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Check response
            result = response.json()
            
            return result.get("status") == "ok"
        except Exception as e:
            logger.error(f"Error checking health of remote agent {self.name}: {e}")
            return False
    
    def _create_task_from_response(
        self, 
        response: Dict[str, Any], 
        task_id: str,
        task_params: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a task from a response.
        
        Args:
            response: The response from the remote agent.
            task_id: The ID of the task.
            task_params: The original task parameters, if available.
            
        Returns:
            The created task.
        """
        # Get task data from response
        task_data = response.get("result", {})
        
        # Get metadata
        metadata = {}
        if task_params:
            metadata["request"] = task_params
        if "error" in response:
            metadata["error"] = response["error"]
        
        # Get session ID
        session_id = task_params.get("sessionId", "unknown") if task_params else "unknown"
        
        # Get message ID
        message_id = "unknown"
        if task_params and "message" in task_params and "metadata" in task_params["message"]:
            message_id = task_params["message"]["metadata"].get("message_id", "unknown")
        
        # Create task
        task = Task(
            id=task_id,
            agent_id="unknown",  # TODO: Get actual agent ID
            message_id=message_id,
            session_id=session_id,
            state=self._parse_task_state(task_data.get("status", {}).get("state", "unknown")),
            metadata_json=metadata
        )
        
        # Set task artifacts
        if "artifacts" in task_data:
            task.artifacts_json = task_data["artifacts"]
        
        return task
    
    def _parse_task_state(self, state_str: str) -> TaskState:
        """Parse a task state string to a TaskState enum.
        
        Args:
            state_str: The task state string to parse.
            
        Returns:
            The parsed TaskState enum value.
        """
        try:
            return TaskState[state_str.upper()]
        except (KeyError, AttributeError):
            return TaskState.UNKNOWN
