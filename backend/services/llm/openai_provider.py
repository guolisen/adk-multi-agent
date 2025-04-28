"""OpenAI LLM provider implementation for Deepdevflow."""

import os
from typing import Any, Dict, List, Optional, Union, AsyncGenerator

from openai import AsyncOpenAI

from .base import LLMProvider
from backend.utils.config import config


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation."""
    
    def __init__(self):
        """Initialize OpenAI provider with configuration."""
        # Get provider configuration
        provider_config = config.get_llm_config("openai")
        
        # Set up API key from config or environment variable
        api_key = provider_config.get("api_key", "") or os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OpenAI API key is not set in config or environment variables")
        
        # Initialize client
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Get default model and settings
        self.defaults = provider_config.get("defaults", {})
        self.default_model = self.defaults.get("model", "gpt-3.5-turbo")
        self.default_system_message = self.defaults.get("system_message", "You are a helpful AI assistant.")
        
        # Get timeout and retry settings
        self.timeout = provider_config.get("timeout", 60)
        self.retries = provider_config.get("retries", 3)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate text from.
            **kwargs: Additional OpenAI-specific parameters.
            
        Returns:
            The generated text.
        """
        messages = [
            {"role": "system", "content": kwargs.get("system_message", self.default_system_message)},
            {"role": "user", "content": prompt}
        ]
        
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout
        )
        
        return response.choices[0].message.content
    
    async def generate_streaming(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Generate text from a prompt with streaming response.
        
        Args:
            prompt: The prompt to generate text from.
            **kwargs: Additional OpenAI-specific parameters.
            
        Yields:
            Chunks of generated text.
        """
        messages = [
            {"role": "system", "content": kwargs.get("system_message", self.default_system_message)},
            {"role": "user", "content": prompt}
        ]
        
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def generate_with_history(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """Generate text from a conversation history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional OpenAI-specific parameters.
            
        Returns:
            The generated text.
        """
        # Add system message if not present
        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {
                "role": "system", 
                "content": kwargs.get("system_message", self.default_system_message)
            })
        
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout
        )
        
        return response.choices[0].message.content
    
    async def generate_with_history_streaming(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate text from a conversation history with streaming response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional OpenAI-specific parameters.
            
        Yields:
            Chunks of generated text.
        """
        # Add system message if not present
        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {
                "role": "system", 
                "content": kwargs.get("system_message", self.default_system_message)
            })
        
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def get_embedding(self, text: str, **kwargs) -> List[float]:
        """Get embedding for a text.
        
        Args:
            text: The text to get embedding for.
            **kwargs: Additional OpenAI-specific parameters.
            
        Returns:
            The embedding as a list of floats.
        """
        model = kwargs.get("embedding_model", "text-embedding-ada-002")
        
        response = await self.client.embeddings.create(
            model=model,
            input=text,
            timeout=self.timeout
        )
        
        return response.data[0].embedding
