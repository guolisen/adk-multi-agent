"""Base LLM provider implementation for Deepdevflow."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate text from.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The generated text.
        """
        pass
    
    @abstractmethod
    async def generate_streaming(self, prompt: str, **kwargs):
        """Generate text from a prompt with streaming response.
        
        Args:
            prompt: The prompt to generate text from.
            **kwargs: Additional provider-specific parameters.
            
        Yields:
            Chunks of generated text.
        """
        pass
    
    @abstractmethod
    async def generate_with_history(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """Generate text from a conversation history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The generated text.
        """
        pass
    
    @abstractmethod
    async def generate_with_history_streaming(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ):
        """Generate text from a conversation history with streaming response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional provider-specific parameters.
            
        Yields:
            Chunks of generated text.
        """
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str, **kwargs) -> List[float]:
        """Get embedding for a text.
        
        Args:
            text: The text to get embedding for.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The embedding as a list of floats.
        """
        pass
