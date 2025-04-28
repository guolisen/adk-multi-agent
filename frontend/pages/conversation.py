"""
Conversation page for Deepdevflow Streamlit UI
"""

import streamlit as st
import asyncio
import datetime
import uuid
from typing import List, Dict, Any, Optional

from frontend.utils.async_utils import run_async


def show_conversation_page():
    """Display the conversation page."""
    st.title("Conversations")
    
    # Check if we have a selected session
    if "current_session_id" not in st.session_state or not st.session_state.current_session_id:
        show_session_selector()
    else:
        # Show conversation interface
        show_conversation_interface(st.session_state.current_session_id)


def show_session_selector():
    """Display the session selector."""
    st.info("Please select a session to view conversations")
    
    # Get sessions from API
    sessions = get_sessions()
    
    if not sessions:
        st.warning("No active sessions found")
        
        # Show button to create a new session
        if st.button("Create New Session", type="primary"):
            show_new_session_dialog()
        
        # Link to home page
        st.write("Or return to the [home page](#home) to get started")
    else:
        # Create a selectbox to choose session
        session_options = [(s["id"], f"{s['name']} (Created: {format_timestamp(s['created_at'])})") for s in sessions]
        
        selected_session_id = st.selectbox(
            "Select Session",
            options=[s[0] for s in session_options],
            format_func=lambda x: next((s[1] for s in session_options if s[0] == x), x)
        )
        
        if st.button("Open Session", type="primary"):
            st.session_state.current_session_id = selected_session_id
            st.experimental_rerun()


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
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error creating session: {str(e)}")


def show_conversation_interface(session_id: str):
    """
    Display the conversation interface.
    
    Args:
        session_id: The session ID to show conversations for
    """
    # Get session details
    session = get_session(session_id)
    
    # If no session found, show selector
    if not session:
        st.error("Session not found")
        st.session_state.current_session_id = None
        st.experimental_rerun()
        return
    
    # Display session info
    st.subheader(f"Session: {session['name']}")
    
    # Check if we have a selected conversation
    if "current_conversation_id" not in st.session_state or not st.session_state.current_conversation_id:
        show_conversation_selector(session_id)
    else:
        # Get conversation details
        conversation = get_conversation(st.session_state.current_conversation_id)
        
        # If conversation not found or doesn't belong to this session, show selector
        if not conversation or conversation["session_id"] != session_id:
            st.error("Conversation not found or belongs to a different session")
            st.session_state.current_conversation_id = None
            st.experimental_rerun()
            return
        
        # Show chat interface
        show_chat_interface(conversation)


def show_conversation_selector(session_id: str):
    """
    Display the conversation selector.
    
    Args:
        session_id: The session ID to show conversations for
    """
    # Get conversations from API
    conversations = get_conversations(session_id)
    
    # Create columns for layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if not conversations:
            st.info("No conversations found for this session")
        else:
            # Create a selectbox to choose conversation
            conversation_options = [(c["id"], c["name"]) for c in conversations]
            
            selected_conversation_id = st.selectbox(
                "Select Conversation",
                options=[c[0] for c in conversation_options],
                format_func=lambda x: next((c[1] for c in conversation_options if c[0] == x), x)
            )
            
            if st.button("Open Conversation", type="primary"):
                st.session_state.current_conversation_id = selected_conversation_id
                st.experimental_rerun()
    
    with col2:
        # Show button to create a new conversation
        if st.button("New Conversation", type="primary", use_container_width=True):
            show_new_conversation_dialog(session_id)
            
        # Change session button
        if st.button("Change Session", use_container_width=True):
            st.session_state.current_session_id = None
            st.experimental_rerun()


def show_new_conversation_dialog(session_id: str):
    """
    Show dialog to create a new conversation.
    
    Args:
        session_id: The session ID to create a conversation for
    """
    with st.form("new_conversation_form"):
        st.subheader("Create New Conversation")
        
        conversation_name = st.text_input("Conversation Name", value=f"Conversation {datetime.datetime.now().strftime('%H:%M:%S')}")
        
        submitted = st.form_submit_button("Create")
        
        if submitted:
            try:
                api_client = st.session_state.api_client
                
                # Create conversation asynchronously
                conversation = run_async(api_client.create_conversation(
                    session_id=session_id,
                    name=conversation_name
                ))
                
                st.session_state.current_conversation_id = conversation["id"]
                st.success(f"Conversation '{conversation_name}' created successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error creating conversation: {str(e)}")


def show_chat_interface(conversation: Dict[str, Any]):
    """
    Display the chat interface.
    
    Args:
        conversation: The conversation data
    """
    # Chat header with title and actions
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"📝 {conversation['name']}")
    
    with col2:
        if st.button("Back to Conversations", use_container_width=True):
            st.session_state.current_conversation_id = None
            st.experimental_rerun()
    
    # Get messages from API
    messages = get_messages(conversation["id"])
    
    # Display messages
    st.markdown("---")
    
    # Chat message container
    message_container = st.container()
    
    # Input area at the bottom
    with st.container():
        # Text input for message
        user_input = st.chat_input("Type your message here...")
        
        # Handle user input
        if user_input:
            # Set a placeholder for the user message
            with message_container:
                with st.chat_message("user"):
                    st.write(user_input)
                
                # Add a placeholder for the response
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    response_placeholder.info("Thinking...")
            
            # Process message
            process_message(conversation["id"], user_input, response_placeholder)
    
    # Display messages
    with message_container:
        if not messages:
            st.info("No messages yet. Start the conversation by typing a message below.")
        else:
            # Display messages in reverse order so newest appear at the bottom
            for message in reversed(messages):
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
                    # If message has metadata, show it as a small caption
                    if message.get("metadata"):
                        metadata = message["metadata"]
                        if isinstance(metadata, str):
                            try:
                                metadata = json.loads(metadata)
                            except:
                                pass
                        
                        # Show creation time if available
                        if "created_at" in message:
                            st.caption(f"{format_timestamp(message['created_at'])}")


def process_message(conversation_id: str, content: str, response_placeholder: Any):
    """
    Process a user message and update the response placeholder.
    
    Args:
        conversation_id: The conversation ID
        content: The message content
        response_placeholder: Streamlit placeholder for the response
    """
    try:
        api_client = st.session_state.api_client
        
        # Option 1: Create message and then fetch response
        # Use this approach if you want separate API calls for sending and receiving
        message = run_async(api_client.create_message(
            conversation_id=conversation_id,
            content=content,
            role="user"
        ))
        
        # Simulate response (this would normally come from the API)
        # In a real implementation, you'd wait for the agent to process the message
        # and then fetch the response from the API
        import time
        time.sleep(1)
        
        # Update placeholder with response
        response_placeholder.write("This is a response from the agent. In a real implementation, this would come from the backend API after processing by the appropriate agent.")
        
        # Option 2: Stream response (uncomment to use)
        # This approach uses a streaming API endpoint to get real-time responses
        """
        # Initialize response text
        response_text = ""
        
        # Stream response
        async def stream_response():
            try:
                async for chunk in api_client.stream_chat(
                    conversation_id=conversation_id,
                    content=content
                ):
                    nonlocal response_text
                    # Update response text with new chunk
                    if 'chunk' in chunk:
                        response_text += chunk['chunk']
                        # Update the UI
                        response_placeholder.write(response_text)
            except Exception as e:
                st.error(f"Error streaming response: {str(e)}")
                
        # Run the streaming function
        run_async(stream_response())
        """
        
        # Refresh the messages (optional)
        # st.experimental_rerun()
    except Exception as e:
        response_placeholder.error(f"Error processing message: {str(e)}")


def get_sessions() -> List[Dict[str, Any]]:
    """Get active sessions."""
    try:
        api_client = st.session_state.api_client
        return run_async(api_client.list_sessions(active_only=True))
    except Exception as e:
        st.error(f"Error getting sessions: {str(e)}")
        return []


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session by ID."""
    try:
        api_client = st.session_state.api_client
        return run_async(api_client.get_session(session_id=session_id))
    except Exception as e:
        st.error(f"Error getting session: {str(e)}")
        return None


def get_conversations(session_id: str) -> List[Dict[str, Any]]:
    """Get conversations for a session."""
    try:
        api_client = st.session_state.api_client
        return run_async(api_client.list_conversations(session_id=session_id, active_only=True))
    except Exception as e:
        st.error(f"Error getting conversations: {str(e)}")
        return []


def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get conversation by ID."""
    try:
        api_client = st.session_state.api_client
        return run_async(api_client.get_conversation(conversation_id=conversation_id))
    except Exception as e:
        st.error(f"Error getting conversation: {str(e)}")
        return None


def get_messages(conversation_id: str) -> List[Dict[str, Any]]:
    """Get messages for a conversation."""
    try:
        api_client = st.session_state.api_client
        return run_async(api_client.list_messages(conversation_id=conversation_id))
    except Exception as e:
        st.error(f"Error getting messages: {str(e)}")
        return []


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
