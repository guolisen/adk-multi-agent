"""
Agents page for Deepdevflow Streamlit UI
"""

import streamlit as st
import asyncio
import datetime
from typing import List, Dict, Any, Optional

from frontend.utils.async_utils import run_async


def show_agents_page():
    """Display the agents page."""
    st.title("Agent Management")
    
    # Tabs for different agent views
    tab1, tab2 = st.tabs(["Agent List", "Add New Agent"])
    
    # Agent List tab
    with tab1:
        show_agent_list()
    
    # Add New Agent tab
    with tab2:
        show_add_agent_form()


def show_agent_list():
    """Display the list of agents."""
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_remote = st.checkbox("Show Remote", value=True)
    
    with col2:
        show_local = st.checkbox("Show Local", value=True)
        
    with col3:
        show_inactive = st.checkbox("Show Inactive", value=False)
    
    # Get agents from API
    agents = get_agents(show_inactive)
    
    # Filter agents based on selections
    if not show_remote:
        agents = [a for a in agents if not a.get("is_remote", False)]
        
    if not show_local:
        agents = [a for a in agents if a.get("is_remote", False)]
    
    # Display agents
    if not agents:
        st.info("No agents found. Add a new agent to get started.")
    else:
        # Convert to dataframe for display
        agent_data = []
        for agent in agents:
            agent_data.append({
                "ID": agent["id"],
                "Name": agent["name"],
                "Description": agent["description"] or "",
                "Type": "Remote" if agent.get("is_remote", False) else "Local",
                "Status": "Active" if agent.get("is_active", True) else "Inactive",
                "Model": agent.get("model", ""),
                "URL": agent.get("url", "") if agent.get("is_remote", False) else ""
            })
        
        # Display agent table with selection
        selected_indices = st.dataframe(
            agent_data,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Name": st.column_config.TextColumn("Name"),
                "Description": st.column_config.TextColumn("Description"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Model": st.column_config.TextColumn("Model", width="small"),
                "URL": st.column_config.TextColumn("URL")
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Agent details section
        st.subheader("Agent Details")
        
        # Select an agent to view details
        agent_options = [(a["id"], a["name"]) for a in agents]
        
        if agent_options:
            selected_agent_id = st.selectbox(
                "Select Agent",
                options=[a[0] for a in agent_options],
                format_func=lambda x: next((a[1] for a in agent_options if a[0] == x), x)
            )
            
            # Get selected agent
            selected_agent = next((a for a in agents if a["id"] == selected_agent_id), None)
            
            if selected_agent:
                show_agent_details(selected_agent)


def show_agent_details(agent: Dict[str, Any]):
    """
    Display agent details.
    
    Args:
        agent: The agent to show details for
    """
    # Create columns for layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Agent basic info
        st.markdown(f"### {agent['name']}")
        st.markdown(f"**Description:** {agent['description'] or 'N/A'}")
        st.markdown(f"**Type:** {'Remote' if agent.get('is_remote', False) else 'Local'}")
        st.markdown(f"**Status:** {'Active' if agent.get('is_active', True) else 'Inactive'}")
        st.markdown(f"**Model:** {agent.get('model', 'N/A')}")
        
        if agent.get("is_remote", False):
            st.markdown(f"**URL:** {agent.get('url', 'N/A')}")
        
        # Capabilities
        capabilities = agent.get("capabilities", [])
        if isinstance(capabilities, str):
            try:
                capabilities = eval(capabilities)
            except:
                capabilities = []
                
        if capabilities:
            st.markdown("### Capabilities")
            for cap in capabilities:
                st.markdown(f"- {cap}")
        else:
            st.markdown("### Capabilities\nNo capabilities defined.")
        
        # Tools
        tools = agent.get("tools", [])
        if isinstance(tools, str):
            try:
                tools = eval(tools)
            except:
                tools = []
                
        if tools:
            st.markdown("### Tools")
            for tool in tools:
                st.markdown(f"- {tool}")
        else:
            st.markdown("### Tools\nNo tools defined.")
        
        # Instruction/Prompt
        if agent.get("instruction"):
            st.markdown("### Instruction/Prompt")
            st.markdown(f"```\n{agent['instruction']}\n```")
    
    with col2:
        # Agent actions
        if agent.get("is_remote", False):
            if agent.get("is_active", True):
                if st.button("Unregister Agent", key=f"unregister_{agent['id']}", use_container_width=True):
                    unregister_agent(agent["id"])
            else:
                if st.button("Register Agent", key=f"register_{agent['id']}", type="primary", use_container_width=True):
                    register_agent(agent["id"])
        
        if st.button("Edit Agent", key=f"edit_{agent['id']}", use_container_width=True):
            st.session_state.edit_agent_id = agent["id"]
            st.experimental_rerun()
            
        if st.button("Delete Agent", key=f"delete_{agent['id']}", type="secondary", use_container_width=True):
            if delete_agent(agent["id"]):
                st.success(f"Agent '{agent['name']}' deleted successfully")
                st.experimental_rerun()


def show_add_agent_form():
    """Display form to add a new agent."""
    st.subheader("Add New Agent")
    
    # Check if we're editing an agent
    editing = False
    agent_to_edit = None
    
    if "edit_agent_id" in st.session_state and st.session_state.edit_agent_id:
        # Get agent details
        agent_to_edit = get_agent(st.session_state.edit_agent_id)
        
        if agent_to_edit:
            editing = True
            st.info(f"Editing agent: {agent_to_edit['name']}")
        else:
            st.error(f"Agent with ID {st.session_state.edit_agent_id} not found")
            st.session_state.edit_agent_id = None
    
    # Create form
    with st.form("agent_form"):
        # Basic info
        name = st.text_input(
            "Agent Name", 
            value=agent_to_edit["name"] if editing else ""
        )
        
        description = st.text_area(
            "Agent Description", 
            value=agent_to_edit.get("description", "") if editing else ""
        )
        
        # Agent type
        is_remote = st.checkbox(
            "Is Remote Agent", 
            value=agent_to_edit.get("is_remote", False) if editing else False
        )
        
        # Display fields based on type
        if is_remote:
            url = st.text_input(
                "Agent URL", 
                value=agent_to_edit.get("url", "") if editing else ""
            )
        else:
            url = ""
            
            # Model selection (only for local agents)
            model_options = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet", "claude-3-opus", "llama3", "mistral"]
            model = st.selectbox(
                "Model", 
                options=model_options,
                index=model_options.index(agent_to_edit.get("model", "gpt-3.5-turbo")) if editing and agent_to_edit.get("model") in model_options else 0
            )
            
            # Instruction/prompt (only for local agents)
            instruction = st.text_area(
                "Instruction/Prompt", 
                value=agent_to_edit.get("instruction", "") if editing else "",
                height=150
            )
        
        # Capabilities (for both types)
        capabilities_str = st.text_area(
            "Capabilities (one per line)", 
            value="\n".join(eval(agent_to_edit.get("capabilities", "[]")) if editing and isinstance(agent_to_edit.get("capabilities"), str) else agent_to_edit.get("capabilities", [])) if editing else "",
            help="Enter each capability on a new line"
        )
        
        # Tools (for both types)
        tools_str = st.text_area(
            "Tools (one per line)", 
            value="\n".join(eval(agent_to_edit.get("tools", "[]")) if editing and isinstance(agent_to_edit.get("tools"), str) else agent_to_edit.get("tools", [])) if editing else "",
            help="Enter each tool on a new line"
        )
        
        # Active status
        is_active = st.checkbox(
            "Is Active", 
            value=agent_to_edit.get("is_active", True) if editing else True
        )
        
        # Submit button
        submit_label = "Update Agent" if editing else "Create Agent"
        submitted = st.form_submit_button(submit_label, type="primary")
        
        # Cancel button for editing
        if editing:
            cancel = st.form_submit_button("Cancel")
            if cancel:
                st.session_state.edit_agent_id = None
                st.experimental_rerun()
        
        # Process form submission
        if submitted:
            # Parse capabilities and tools
            capabilities = [cap.strip() for cap in capabilities_str.split("\n") if cap.strip()]
            tools = [tool.strip() for tool in tools_str.split("\n") if tool.strip()]
            
            # Build agent data
            agent_data = {
                "name": name,
                "description": description,
                "is_remote": is_remote,
                "capabilities": capabilities,
                "tools": tools,
                "is_active": is_active
            }
            
            # Add type-specific fields
            if is_remote:
                agent_data["url"] = url
            else:
                agent_data["model"] = model
                agent_data["instruction"] = instruction
            
            try:
                if editing:
                    # Update existing agent
                    updated_agent = update_agent(agent_to_edit["id"], agent_data)
                    if updated_agent:
                        st.success(f"Agent '{name}' updated successfully")
                        st.session_state.edit_agent_id = None
                        st.experimental_rerun()
                else:
                    # Create new agent
                    new_agent = create_agent(agent_data)
                    if new_agent:
                        st.success(f"Agent '{name}' created successfully")
                        st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")


def get_agents(include_inactive: bool = False) -> List[Dict[str, Any]]:
    """
    Get agents from API.
    
    Args:
        include_inactive: Whether to include inactive agents
        
    Returns:
        List of agents
    """
    try:
        api_client = st.session_state.api_client
        return run_async(api_client.list_agents(active_only=not include_inactive))
    except Exception as e:
        st.error(f"Error getting agents: {str(e)}")
        return []


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    """
    Get agent by ID.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        The agent data or None if not found
    """
    try:
        api_client = st.session_state.api_client
        return run_async(api_client.get_agent(agent_id))
    except Exception as e:
        st.error(f"Error getting agent: {str(e)}")
        return None


def create_agent(agent_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new agent.
    
    Args:
        agent_data: The agent data
        
    Returns:
        The created agent data or None if failed
    """
    try:
        api_client = st.session_state.api_client
        
        # Call API to create agent
        return run_async(api_client.create_agent(
            name=agent_data["name"],
            description=agent_data["description"],
            url=agent_data.get("url"),
            is_remote=agent_data["is_remote"],
            model=agent_data.get("model"),
            instruction=agent_data.get("instruction"),
            capabilities=agent_data["capabilities"],
            tools=agent_data["tools"]
        ))
    except Exception as e:
        raise Exception(f"Failed to create agent: {str(e)}")


def update_agent(agent_id: str, agent_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing agent.
    
    Args:
        agent_id: The agent ID
        agent_data: The updated agent data
        
    Returns:
        The updated agent data or None if failed
    """
    # This would be implemented to call the API to update the agent
    # For now, we'll just return a success message
    st.success(f"Agent '{agent_data['name']}' would be updated (API not implemented)")
    return agent_data


def delete_agent(agent_id: str) -> bool:
    """
    Delete an agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        api_client = st.session_state.api_client
        
        # This would call the actual API
        # For now we'll just simulate success
        st.success(f"Agent would be deleted (API not implemented)")
        return True
    except Exception as e:
        st.error(f"Error deleting agent: {str(e)}")
        return False


def register_agent(agent_id: str) -> bool:
    """
    Register a remote agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        api_client = st.session_state.api_client
        run_async(api_client.register_agent(agent_id))
        return True
    except Exception as e:
        st.error(f"Error registering agent: {str(e)}")
        return False


def unregister_agent(agent_id: str) -> bool:
    """
    Unregister a remote agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        api_client = st.session_state.api_client
        run_async(api_client.unregister_agent(agent_id))
        return True
    except Exception as e:
        st.error(f"Error unregistering agent: {str(e)}")
        return False
