"""
Home page for Deepdevflow Streamlit UI
"""

import streamlit as st
import asyncio
import datetime
from typing import List, Dict, Any

from frontend.utils.async_utils import run_async


def show_home_page():
    """Display the home page."""
    st.title("Deepdevflow")
    st.header("Multi-agent Framework")
    
    # Welcome section
    with st.container():
        st.markdown("""
        ### Welcome to Deepdevflow
        
        Deepdevflow is a powerful multi-agent framework built with Google's Agent Development Kit (ADK).
        It allows you to create, manage, and orchestrate conversations between multiple AI agents.
        """)
    
    # Quick stats
    with st.container():
        st.subheader("Quick Stats")
        
        col1, col2, col3 = st.columns(3)
        
        # Get stats from API asynchronously
        stats = get_stats()
        
        with col1:
            st.metric("Active Sessions", stats["sessions"])
            
        with col2:
            st.metric("Active Conversations", stats["conversations"])
            
        with col3:
            st.metric("Registered Agents", stats["agents"])
    
    # Recent activity
    with st.container():
        st.subheader("Recent Activity")
        
        # Get recent sessions from API
        recent_sessions = get_recent_sessions()
        
        if not recent_sessions:
            st.info("No recent activity. Start a new conversation to get started!")
        else:
            # Display recent sessions in a table
            session_data = []
            for session in recent_sessions:
                session_data.append({
                    "Name": session["name"],
                    "Created": format_timestamp(session["created_at"]),
                    "Conversations": len(session.get("conversations", [])),
                    "Last Activity": format_timestamp(session["updated_at"])
                })
            
            st.dataframe(
                session_data,
                column_config={
                    "Name": st.column_config.TextColumn("Session Name"),
                    "Created": st.column_config.TextColumn("Created"),
                    "Conversations": st.column_config.NumberColumn("Conversations"),
                    "Last Activity": st.column_config.TextColumn("Last Activity")
                },
                use_container_width=True,
                hide_index=True
            )
    
    # Quick actions
    with st.container():
        st.subheader("Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("New Session", type="primary", use_container_width=True):
                show_new_session_dialog()
                
        with col2:
            if st.button("Manage Agents", use_container_width=True):
                st.session_state.page = "agents"
                st.experimental_rerun()
    
    # Recent messages across all conversations
    with st.container():
        st.subheader("Latest Messages")
        
        # Get recent messages from API
        recent_messages = get_recent_messages()
        
        if not recent_messages:
            st.info("No messages yet. Start a conversation to see messages here!")
        else:
            for message in recent_messages:
                with st.chat_message(message["role"]):
                    # Truncate long messages
                    content = message["content"]
                    if len(content) > 300:
                        content = content[:297] + "..."
                    
                    st.write(content)
                    st.caption(f"From {message['conversation_name']} - {format_timestamp(message['created_at'])}")


def get_stats() -> Dict[str, int]:
    """Get system stats."""
    # In a real implementation, this would call the API client
    # For now, we'll return mock data
    try:
        api_client = st.session_state.api_client
        
        # Get stats asynchronously
        result = run_async(get_stats_async())
        return result
    except Exception as e:
        st.error(f"Error getting stats: {str(e)}")
        return {"sessions": 0, "conversations": 0, "agents": 0}


async def get_stats_async() -> Dict[str, int]:
    """Get system stats asynchronously."""
    try:
        api_client = st.session_state.api_client
        
        # Run these in parallel
        sessions_task = api_client.list_sessions()
        agents_task = api_client.list_agents()
        
        # Wait for both tasks to complete
        sessions, agents = await asyncio.gather(sessions_task, agents_task)
        
        # Count conversations across all sessions
        conversation_count = 0
        for session in sessions:
            # Get conversations for session
            conversations = await api_client.list_conversations(session_id=session["id"])
            conversation_count += len(conversations)
        
        return {
            "sessions": len(sessions),
            "conversations": conversation_count,
            "agents": len(agents)
        }
    except Exception as e:
        # In case of error, return zeros
        return {"sessions": 0, "conversations": 0, "agents": 0}


def get_recent_sessions() -> List[Dict[str, Any]]:
    """Get recent sessions."""
    try:
        api_client = st.session_state.api_client
        
        # Get sessions asynchronously
        sessions = run_async(api_client.list_sessions(active_only=True))
        
        # Sort by updated_at descending
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("updated_at", s.get("created_at", "")),
            reverse=True
        )
        
        # Return top 5
        return sorted_sessions[:5]
    except Exception as e:
        st.error(f"Error getting recent sessions: {str(e)}")
        return []


def get_recent_messages() -> List[Dict[str, Any]]:
    """Get recent messages across all conversations."""
    try:
        # This would be implemented by fetching messages from the API
        # For now, we'll return mock data
        return [
            {
                "role": "user",
                "content": "Hello, I'm looking for information about machine learning frameworks.",
                "created_at": "2025-04-27T22:05:30Z",
                "conversation_name": "ML Discussion"
            },
            {
                "role": "assistant",
                "content": "Hi there! I'd be happy to help with information about machine learning frameworks. Some popular ones include TensorFlow, PyTorch, scikit-learn, and JAX. Each has different strengths. What specific aspects are you interested in?",
                "created_at": "2025-04-27T22:05:45Z",
                "conversation_name": "ML Discussion"
            },
            {
                "role": "user",
                "content": "Can you help me troubleshoot a deployment issue?",
                "created_at": "2025-04-27T21:50:10Z",
                "conversation_name": "Deployment Help"
            }
        ]
    except Exception as e:
        st.error(f"Error getting recent messages: {str(e)}")
        return []


def show_new_session_dialog():
    """Show dialog to create a new session."""
    with st.form("new_session_form"):
        st.subheader("Create New Session")
        
        session_name = st.text_input("Session Name", value=f"Session {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        user_id = st.text_input("User ID (Optional)")
        
        submitted = st.form_submit_button("Create")
        
        if submitted:
            try:
                api_client = st.session_state.api_client
                
                # Create session asynchronously
                session = run_async(api_client.create_session(
                    name=session_name,
                    user_id=user_id if user_id else None
                ))
                
                st.session_state.current_session_id = session["id"]
                st.success(f"Session '{session_name}' created successfully!")
                
                # Redirect to conversations page
                st.session_state.page = "conversations"
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error creating session: {str(e)}")


def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp string for display."""
    try:
        # Parse ISO format timestamp
        dt = datetime.datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        
        # Check if it's today
        today = datetime.datetime.now().date()
        if dt.date() == today:
            return f"Today, {dt.strftime('%H:%M')}"
        
        # Check if it's yesterday
        yesterday = today - datetime.timedelta(days=1)
        if dt.date() == yesterday:
            return f"Yesterday, {dt.strftime('%H:%M')}"
        
        # Otherwise show date and time
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return timestamp_str  # Return original if parsing fails
