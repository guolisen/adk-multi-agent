"""
Settings page for Deepdevflow Streamlit UI
"""

import streamlit as st
import os
from typing import Dict, Any

from frontend.utils.config_loader import load_config, update_config_value


def show_settings_page():
    """Display the settings page."""
    st.title("Settings")
    
    # Create tabs for different settings categories
    tab1, tab2, tab3 = st.tabs(["LLM Settings", "UI Settings", "System Settings"])
    
    # LLM Settings tab
    with tab1:
        show_llm_settings()
    
    # UI Settings tab
    with tab2:
        show_ui_settings()
    
    # System Settings tab
    with tab3:
        show_system_settings()


def show_llm_settings():
    """Display LLM settings."""
    st.header("LLM Provider Settings")
    
    # Get current configuration
    config = load_config()
    llm_config = config.get("llm", {})
    
    # Default provider selection
    providers = ["openai", "litellm", "ollama", "anthropic"]
    current_provider = llm_config.get("default_provider", "openai")
    
    selected_provider = st.selectbox(
        "Default LLM Provider",
        options=providers,
        index=providers.index(current_provider) if current_provider in providers else 0
    )
    
    if selected_provider != current_provider:
        if update_config_value("llm.default_provider", selected_provider):
            st.success(f"Default provider updated to {selected_provider}")
            # Update session state
            st.session_state.llm_provider = selected_provider
    
    # Provider-specific settings
    st.subheader(f"{selected_provider.capitalize()} Settings")
    
    if selected_provider == "openai":
        show_openai_settings(llm_config.get("openai", {}))
    elif selected_provider == "litellm":
        show_litellm_settings(llm_config.get("litellm", {}))
    elif selected_provider == "ollama":
        show_ollama_settings(llm_config.get("ollama", {}))
    elif selected_provider == "anthropic":
        show_anthropic_settings(llm_config.get("anthropic", {}))


def show_openai_settings(provider_config: Dict[str, Any]):
    """
    Display OpenAI settings.
    
    Args:
        provider_config: Provider configuration
    """
    # API Key
    api_key_env = provider_config.get("api_key_env_var", "OPENAI_API_KEY")
    api_key = os.environ.get(api_key_env, "")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_api_key = st.text_input(
            "API Key", 
            value=api_key,
            type="password",
            help="Your OpenAI API key. This will be stored in your environment variable."
        )
    
    with col2:
        if st.button("Save API Key", use_container_width=True):
            if new_api_key:
                # In a real application, you would store this securely
                # For this demo, we'll just show a success message
                os.environ[api_key_env] = new_api_key
                st.success("API key saved successfully")
            else:
                st.warning("API key cannot be empty")
    
    # Default model settings
    st.subheader("Default Model Settings")
    
    defaults = provider_config.get("defaults", {})
    
    models = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    ]
    
    current_model = defaults.get("model", "gpt-3.5-turbo")
    
    selected_model = st.selectbox(
        "Default Model",
        options=models,
        index=models.index(current_model) if current_model in models else 0
    )
    
    if selected_model != current_model:
        if update_config_value("llm.openai.defaults.model", selected_model):
            st.success(f"Default model updated to {selected_model}")
    
    # Temperature
    current_temp = defaults.get("temperature", 0.7)
    temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=current_temp, step=0.1)
    
    if temp != current_temp:
        if update_config_value("llm.openai.defaults.temperature", temp):
            st.success(f"Default temperature updated to {temp}")
    
    # System message
    current_sys_msg = defaults.get("system_message", "You are a helpful AI assistant.")
    sys_msg = st.text_area("Default System Message", value=current_sys_msg)
    
    if sys_msg != current_sys_msg:
        if update_config_value("llm.openai.defaults.system_message", sys_msg):
            st.success("Default system message updated")


def show_litellm_settings(provider_config: Dict[str, Any]):
    """
    Display LiteLLM settings.
    
    Args:
        provider_config: Provider configuration
    """
    st.info("LiteLLM is a unified interface to many LLM providers.")
    
    # Server URL
    current_url = provider_config.get("server_url", "http://localhost:4000")
    
    url = st.text_input("LiteLLM Server URL", value=current_url)
    
    if url != current_url:
        if update_config_value("llm.litellm.server_url", url):
            st.success(f"LiteLLM server URL updated to {url}")
    
    # API Key
    api_key_env = provider_config.get("api_key_env_var", "LITELLM_API_KEY")
    api_key = os.environ.get(api_key_env, "")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_api_key = st.text_input(
            "API Key", 
            value=api_key,
            type="password",
            help="Your LiteLLM API key (if required)"
        )
    
    with col2:
        if st.button("Save API Key", key="save_litellm_key", use_container_width=True):
            if new_api_key:
                os.environ[api_key_env] = new_api_key
                st.success("API key saved successfully")
            else:
                st.warning("API key cannot be empty")
    
    # Model settings
    defaults = provider_config.get("defaults", {})
    
    models = [
        "openai/gpt-4",
        "openai/gpt-3.5-turbo",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-sonnet"
    ]
    
    current_model = defaults.get("model", "openai/gpt-3.5-turbo")
    
    # Allow custom model input
    model_input = st.text_input(
        "Model Name", 
        value=current_model,
        help="Enter the model name in format provider/model"
    )
    
    if model_input != current_model:
        if update_config_value("llm.litellm.defaults.model", model_input):
            st.success(f"Default model updated to {model_input}")


def show_ollama_settings(provider_config: Dict[str, Any]):
    """
    Display Ollama settings.
    
    Args:
        provider_config: Provider configuration
    """
    st.info("Ollama allows running LLMs locally.")
    
    # Server URL
    current_url = provider_config.get("server_url", "http://localhost:11434")
    
    url = st.text_input("Ollama Server URL", value=current_url)
    
    if url != current_url:
        if update_config_value("llm.ollama.server_url", url):
            st.success(f"Ollama server URL updated to {url}")
    
    # Model settings
    defaults = provider_config.get("defaults", {})
    
    models = [
        "llama3",
        "llama3:8b",
        "llama3:70b",
        "mistral",
        "mistral-small",
        "mistral-medium",
        "codellama",
        "phi3"
    ]
    
    current_model = defaults.get("model", "llama3")
    
    # Allow model selection or custom input
    custom_model = st.checkbox("Use custom model name")
    
    if custom_model:
        model_input = st.text_input("Custom Model Name", value=current_model)
        selected_model = model_input
    else:
        selected_model = st.selectbox(
            "Default Model",
            options=models,
            index=models.index(current_model) if current_model in models else 0
        )
    
    if selected_model != current_model:
        if update_config_value("llm.ollama.defaults.model", selected_model):
            st.success(f"Default model updated to {selected_model}")


def show_anthropic_settings(provider_config: Dict[str, Any]):
    """
    Display Anthropic settings.
    
    Args:
        provider_config: Provider configuration
    """
    # API Key
    api_key_env = provider_config.get("api_key_env_var", "ANTHROPIC_API_KEY")
    api_key = os.environ.get(api_key_env, "")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_api_key = st.text_input(
            "API Key", 
            value=api_key,
            type="password",
            help="Your Anthropic API key"
        )
    
    with col2:
        if st.button("Save API Key", key="save_anthropic_key", use_container_width=True):
            if new_api_key:
                os.environ[api_key_env] = new_api_key
                st.success("API key saved successfully")
            else:
                st.warning("API key cannot be empty")
    
    # Default model settings
    st.subheader("Default Model Settings")
    
    defaults = provider_config.get("defaults", {})
    
    models = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]
    
    current_model = defaults.get("model", "claude-3-sonnet-20240229")
    
    selected_model = st.selectbox(
        "Default Model",
        options=models,
        index=models.index(current_model) if current_model in models else 0
    )
    
    if selected_model != current_model:
        if update_config_value("llm.anthropic.defaults.model", selected_model):
            st.success(f"Default model updated to {selected_model}")


def show_ui_settings():
    """Display UI settings."""
    st.header("User Interface Settings")
    
    # Get current configuration
    config = load_config()
    ui_config = config.get("ui", {})
    
    # Theme settings
    st.subheader("Theme Settings")
    
    theme_config = config.get("theme", {})
    
    # Color picker for primary color
    primary_color = theme_config.get("primary_color", "#1E88E5")
    new_primary_color = st.color_picker("Primary Color", primary_color)
    
    if new_primary_color != primary_color:
        if update_config_value("theme.primary_color", new_primary_color):
            st.success("Primary color updated")
    
    # Messages per page
    messages_per_page = ui_config.get("messages_per_page", 50)
    new_messages_per_page = st.slider(
        "Messages Per Page",
        min_value=10,
        max_value=100,
        value=messages_per_page,
        step=5
    )
    
    if new_messages_per_page != messages_per_page:
        if update_config_value("ui.messages_per_page", new_messages_per_page):
            st.success(f"Messages per page updated to {new_messages_per_page}")
    
    # Streaming toggle
    enable_streaming = ui_config.get("enable_streaming", True)
    new_enable_streaming = st.checkbox("Enable Streaming", value=enable_streaming)
    
    if new_enable_streaming != enable_streaming:
        if update_config_value("ui.enable_streaming", new_enable_streaming):
            st.success(f"Streaming {'enabled' if new_enable_streaming else 'disabled'}")
    
    # Show agent details toggle
    show_agent_details = ui_config.get("show_agent_details", True)
    new_show_agent_details = st.checkbox("Show Agent Details", value=show_agent_details)
    
    if new_show_agent_details != show_agent_details:
        if update_config_value("ui.show_agent_details", new_show_agent_details):
            st.success(f"Agent details display {'enabled' if new_show_agent_details else 'disabled'}")


def show_system_settings():
    """Display system settings."""
    st.header("System Settings")
    
    # Get current configuration
    config = load_config()
    
    # API URL
    current_api_url = config.get("api_url", "http://localhost:8000")
    
    api_url = st.text_input("Backend API URL", value=current_api_url)
    
    if api_url != current_api_url:
        if update_config_value("api_url", api_url):
            st.success(f"API URL updated to {api_url}")
    
    # Debug mode
    debug_mode = config.get("app", {}).get("debug", False)
    new_debug_mode = st.checkbox("Debug Mode", value=debug_mode)
    
    if new_debug_mode != debug_mode:
        if update_config_value("app.debug", new_debug_mode):
            st.success(f"Debug mode {'enabled' if new_debug_mode else 'disabled'}")
    
    # Database settings
    st.subheader("Database Settings")
    
    db_config = config.get("database", {})
    conn_string = db_config.get("connection_string", "sqlite:///data/deepdevflow.db")
    
    new_conn_string = st.text_input("Database Connection String", value=conn_string)
    
    if new_conn_string != conn_string:
        if update_config_value("database.connection_string", new_conn_string):
            st.success(f"Database connection string updated")
            st.warning("You will need to restart the application for this change to take effect")
