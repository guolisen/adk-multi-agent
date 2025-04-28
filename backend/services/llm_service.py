"""LLM service for Deepdevflow."""

from typing import Any, Dict, List, Optional, Union, AsyncGenerator
import logging

from backend.utils.config import config
from backend.services.llm import LLMProvider, OpenAIProvider

# Setup logging
logger = logging.getLogger(__name__)


class LLMService:
    """LLM service that manages different providers."""
    
    _instance = None
    _providers = {}
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._initialize_providers()
        return cls._instance
    
    def _initialize_providers(self):
        """Initialize all enabled providers."""
        llm_config = config.get_llm_config()
        
        # Initialize OpenAI provider if enabled
        if llm_config.get("openai", {}).get("enabled", False):
            try:
                self._providers["openai"] = OpenAIProvider()
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")
        
        # TODO: Add more providers like Ollama, LiteLLM, etc.
        
        # Set default provider
        self._default_provider = config.default_llm_provider
        if self._default_provider not in self._providers:
            available_providers = list(self._providers.keys())
            if available_providers:
                self._default_provider = available_providers[0]
                logger.warning(
                    f"Default provider '{config.default_llm_provider}' not available. "
                    f"Using '{self._default_provider}' instead."
                )
            else:
                logger.error("No LLM providers available")
    
    def get_provider(self, provider_name: Optional[str] = None) -> LLMProvider:
        """Get a specific provider or the default provider.
        
        Args:
            provider_name: The name of the provider to get. If None, returns the default provider.
            
        Returns:
            The provider instance.
            
        Raises:
            ValueError: If the provider is not available.
        """
        provider_name = provider_name or self._default_provider
        
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        return self._providers[provider_name]
    
    async def generate(self, prompt: str, provider_name: Optional[str] = None, **kwargs) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate text from.
            provider_name: The name of the provider to use. If None, uses the default provider.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The generated text.
        """
        provider = self.get_provider(provider_name)
        return await provider.generate(prompt, **kwargs)
    
    async def generate_streaming(
        self, 
        prompt: str, 
        provider_name: Optional[str] = None, 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate text from a prompt with streaming response.
        
        Args:
            prompt: The prompt to generate text from.
            provider_name: The name of the provider to use. If None, uses the default provider.
            **kwargs: Additional provider-specific parameters.
            
        Yields:
            Chunks of generated text.
        """
        provider = self.get_provider(provider_name)
        async for chunk in provider.generate_streaming(prompt, **kwargs):
            yield chunk
    
    async def generate_with_history(
        self, 
        messages: List[Dict[str, str]], 
        provider_name: Optional[str] = None, 
        **kwargs
    ) -> str:
        """Generate text from a conversation history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            provider_name: The name of the provider to use. If None, uses the default provider.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The generated text.
        """
        provider = self.get_provider(provider_name)
        return await provider.generate_with_history(messages, **kwargs)
    
    async def generate_with_history_streaming(
        self, 
        messages: List[Dict[str, str]], 
        provider_name: Optional[str] = None, 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate text from a conversation history with streaming response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            provider_name: The name of the provider to use. If None, uses the default provider.
            **kwargs: Additional provider-specific parameters.
            
        Yields:
            Chunks of generated text.
        """
        provider = self.get_provider(provider_name)
        async for chunk in provider.generate_with_history_streaming(messages, **kwargs):
            yield chunk
    
    async def get_embedding(
        self, 
        text: str, 
        provider_name: Optional[str] = None, 
        **kwargs
    ) -> List[float]:
        """Get embedding for a text.
        
        Args:
            text: The text to get embedding for.
            provider_name: The name of the provider to use. If None, uses the default provider.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The embedding as a list of floats.
        """
        provider = self.get_provider(provider_name)
        return await provider.get_embedding(text, **kwargs)


# Create a singleton instance
llm_service = LLMService()
