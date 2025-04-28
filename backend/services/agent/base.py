"""Base agent implementation for Deepdevflow."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, AsyncGenerator

from backend.models import Message, Task, Agent as AgentModel


class Agent(ABC):
    """Abstract base class for agents."""
    
    @abstractmethod
    async def process_message(self, message: Message) -> AsyncGenerator[str, None]:
        """Process a message and generate a response.
        
        Args:
            message: The message to process.
            
        Yields:
            Chunks of the response.
        """
        pass
    
    @abstractmethod
    async def create_task(self, message: Message) -> Task:
        """Create a task from a message.
        
        Args:
            message: The message to create a task from.
            
        Returns:
            The created task.
        """
        pass
    
    @abstractmethod
    async def update_task(self, task: Task, message: Optional[Message] = None) -> Task:
        """Update a task.
        
        Args:
            task: The task to update.
            message: Optional message with updated information.
            
        Returns:
            The updated task.
        """
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> Task:
        """Get the status of a task.
        
        Args:
            task_id: The ID of the task to get the status of.
            
        Returns:
            The task.
        """
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> Task:
        """Cancel a task.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            The canceled task.
        """
        pass
    
    @abstractmethod
    async def list_capabilities(self) -> List[str]:
        """List the capabilities of the agent.
        
        Returns:
            A list of capability strings.
        """
        pass
    
    @abstractmethod
    async def to_agent_model(self) -> AgentModel:
        """Convert the agent to an AgentModel.
        
        Returns:
            The agent model representation.
        """
        pass
