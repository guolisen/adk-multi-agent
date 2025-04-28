"""
Deepdevflow - Main Streamlit Frontend Application
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add the project root to the path so we can import from our modules
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# Import pages
from frontend.pages.home import show_home_page
from frontend.pages.conversation import show_conversation_page
from frontend.pages.agents import show_agents_page
from frontend.pages.settings import show_settings_page

# Import services
from frontend.services.api_client import ApiClient
from frontend.utils.config_loader import load_config

# Page configuration
st.set_page_config(
    page_title="Deepdevflow",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
def load_css():
    with open(os.path.join(root_path, "frontend", "styles", "main.css")) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """Main application entry point."""
    # Load CSS
    try:
        load_css()
    except FileNotFoundError:
        pass  # CSS file will be created later
    
    # Initialize API client
    config = load_config()
    api_client = ApiClient(
        base_url=config.get("api_url", "http://localhost:8000")
    )
    
    # Set up session state if not initialized
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    if "api_client" not in st.session_state:
        st.session_state.api_client = api_client
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "openai"
    
    # Create sidebar navigation
    with st.sidebar:
        st.title("Deepdevflow")
        st.markdown("---")
        
        if st.button("Home", key="nav_home", use_container_width=True):
            st.session_state.page = "home"
            st.experimental_rerun()
        
        if st.button("Conversations", key="nav_conversations", use_container_width=True):
            st.session_state.page = "conversations"
            st.experimental_rerun()
        
        if st.button("Agents", key="nav_agents", use_container_width=True):
            st.session_state.page = "agents"
            st.experimental_rerun()
        
        if st.button("Settings", key="nav_settings", use_container_width=True):
            st.session_state.page = "settings"
            st.experimental_rerun()
        
        st.markdown("---")
        
        # Display current LLM provider
        st.caption(f"LLM Provider: {st.session_state.llm_provider}")
    
    # Display page based on selection
    if st.session_state.page == "home":
        show_home_page()
    elif st.session_state.page == "conversations":
        show_conversation_page()
    elif st.session_state.page == "agents":
        show_agents_page()
    elif st.session_state.page == "settings":
        show_settings_page()
    else:
        show_home_page()


if __name__ == "__main__":
    main()
