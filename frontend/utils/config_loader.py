"""
Configuration loader for the Deepdevflow frontend
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "api_url": "http://localhost:8000",
    "theme": {
        "primary_color": "#1E88E5",
        "secondary_color": "#FFC107",
        "background_color": "#FFFFFF",
        "text_color": "#333333"
    },
    "llm": {
        "default_provider": "openai",
        "api_key_env_var": "OPENAI_API_KEY"
    },
    "ui": {
        "messages_per_page": 50,
        "enable_streaming": True,
        "show_agent_details": True
    }
}


def load_config() -> Dict[str, Any]:
    """
    Load configuration from file or use default if file doesn't exist
    
    Returns:
        Dict containing configuration values
    """
    # Try to find configuration file
    config_path = os.environ.get(
        "DEEPDEVFLOW_CONFIG_PATH", 
        str(Path(__file__).parent.parent.parent / "config" / "frontend_config.yaml")
    )
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                config_data = yaml.safe_load(file)
                
            # Merge with default config to ensure all required keys exist
            return merge_configs(DEFAULT_CONFIG, config_data)
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
    # Return default config if loading fails
    return DEFAULT_CONFIG


def merge_configs(default_config: Dict, custom_config: Dict) -> Dict:
    """
    Merge custom configuration with defaults, preserving nested structure
    
    Args:
        default_config: Default configuration dict
        custom_config: Custom configuration to merge in
        
    Returns:
        Merged configuration dict
    """
    result = default_config.copy()
    
    for key, value in custom_config.items():
        if (
            key in result and 
            isinstance(result[key], dict) and 
            isinstance(value, dict)
        ):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
            
    return result


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to file
    
    Args:
        config: Configuration dict to save
        
    Returns:
        True if successful, False otherwise
    """
    config_path = os.environ.get(
        "DEEPDEVFLOW_CONFIG_PATH", 
        str(Path(__file__).parent.parent.parent / "config" / "frontend_config.yaml")
    )
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Write config to file
        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value by key
    
    Args:
        key: Dot-separated path to the config value (e.g. "llm.default_provider")
        default: Default value to return if key not found
        
    Returns:
        Configuration value or default
    """
    config = load_config()
    parts = key.split('.')
    
    # Navigate through nested dicts
    current = config
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
            
    return current


def update_config_value(key: str, value: Any) -> bool:
    """
    Update a specific configuration value
    
    Args:
        key: Dot-separated path to the config value
        value: New value to set
        
    Returns:
        True if successful, False otherwise
    """
    config = load_config()
    parts = key.split('.')
    
    # Navigate to the parent dict that contains the target key
    current = config
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    # Set the value
    current[parts[-1]] = value
    
    # Save updated config
    return save_config(config)
