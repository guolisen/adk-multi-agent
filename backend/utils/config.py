"""Configuration utility module for Deepdevflow."""

import os
import yaml
from typing import Any, Dict, Optional


class Config:
    """Configuration class for Deepdevflow."""
    
    _instance = None
    _config = None
    _llm_config = None
    _agent_config = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_configs()
        return cls._instance
    
    def _load_configs(self):
        """Load all configuration files."""
        base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        
        # Load main config
        main_config_path = os.path.join(base_path, "config.yaml")
        with open(main_config_path, "r") as file:
            self._config = yaml.safe_load(file)
        
        # Load LLM config
        llm_config_path = os.path.join(base_path, "llm_config.yaml")
        with open(llm_config_path, "r") as file:
            self._llm_config = yaml.safe_load(file)
        
        # Load agent config
        agent_config_path = os.path.join(base_path, "agent_config.yaml")
        with open(agent_config_path, "r") as file:
            self._agent_config = yaml.safe_load(file)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value from the main config."""
        parts = key.split(".")
        value = self._config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def get_llm_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get LLM configuration for a specific provider or all providers."""
        if provider:
            return self._llm_config.get(provider, {})
        return self._llm_config
    
    def get_agent_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """Get agent configuration for a specific section or all sections."""
        if section:
            return self._agent_config.get(section, {})
        return self._agent_config
    
    @property
    def app_name(self) -> str:
        """Get application name."""
        return self.get("app.name", "Deepdevflow")
    
    @property
    def app_version(self) -> str:
        """Get application version."""
        return self.get("app.version", "0.1.0")
    
    @property
    def debug_mode(self) -> bool:
        """Get debug mode."""
        return self.get("app.debug", False)
    
    @property
    def server_host(self) -> str:
        """Get server host."""
        return self.get("server.host", "127.0.0.1")
    
    @property
    def server_port(self) -> int:
        """Get server port."""
        return self.get("server.port", 8000)
    
    @property
    def default_llm_provider(self) -> str:
        """Get default LLM provider."""
        return self.get("llm.default_provider", "openai")
    
    @property
    def default_agent(self) -> str:
        """Get default agent."""
        return self.get("agent.default_agent", "host_agent")


# Create a singleton instance
config = Config()
