"""
API Client for communicating with the Deepdevflow backend
"""

import httpx
import json
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)


class ApiClient:
    """
    HTTP client for interacting with the Deepdevflow backend API
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the backend API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close the underlying HTTP client"""
        await self.client.aclose()
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Any = None,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: HTTP headers
            
        Returns:
            API response as a dictionary
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        try:
            if data is not None:
                if isinstance(data, dict):
                    data = json.dumps(data)
                
            response = await self.client.request(
                method=method,
                url=url,
                content=data,
                params=params,
                headers=default_headers
            )
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
                
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            
            # Try to parse error response
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
                
            raise Exception(f"API error: {error_message}")
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
    
    # Session endpoints
    
    async def create_session(self, name: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new session
        
        Args:
            name: Session name
            user_id: Optional user ID
            
        Returns:
            Created session data
        """
        data = {
            "name": name,
            "user_id": user_id
        }
        
        return await self._request("POST", "/sessions", data=data)
    
    async def list_sessions(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List sessions
        
        Args:
            active_only: Whether to return only active sessions
            
        Returns:
            List of sessions
        """
        params = {"active_only": active_only}
        return await self._request("GET", "/sessions", params=params)
    
    async def get_session(self, session_id: str, include_conversations: bool = False) -> Dict[str, Any]:
        """
        Get session by ID
        
        Args:
            session_id: Session ID
            include_conversations: Whether to include conversations in response
            
        Returns:
            Session data
        """
        params = {"include_conversations": include_conversations}
        return await self._request("GET", f"/sessions/{session_id}", params=params)
    
    # Conversation endpoints
    
    async def create_conversation(self, session_id: str, name: str) -> Dict[str, Any]:
        """
        Create a new conversation
        
        Args:
            session_id: Session ID
            name: Conversation name
            
        Returns:
            Created conversation data
        """
        data = {
            "session_id": session_id,
            "name": name
        }
        
        return await self._request("POST", "/conversations", data=data)
    
    async def list_conversations(
        self, 
        session_id: Optional[str] = None, 
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List conversations
        
        Args:
            session_id: Optional session ID to filter by
            active_only: Whether to return only active conversations
            
        Returns:
            List of conversations
        """
        params = {
            "active_only": active_only
        }
        
        if session_id:
            params["session_id"] = session_id
            
        return await self._request("GET", "/conversations", params=params)
    
    async def get_conversation(
        self, 
        conversation_id: str, 
        include_messages: bool = False
    ) -> Dict[str, Any]:
        """
        Get conversation by ID
        
        Args:
            conversation_id: Conversation ID
            include_messages: Whether to include messages in response
            
        Returns:
            Conversation data
        """
        params = {"include_messages": include_messages}
        return await self._request("GET", f"/conversations/{conversation_id}", params=params)
    
    # Message endpoints
    
    async def list_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        List messages in a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages
        """
        return await self._request("GET", f"/conversations/{conversation_id}/messages")
    
    async def create_message(
        self,
        conversation_id: str,
        content: str,
        role: str = "user",
        content_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new message
        
        Args:
            conversation_id: Conversation ID
            content: Message content
            role: Message sender role
            content_type: Content MIME type
            metadata: Optional metadata
            
        Returns:
            Created message data
        """
        data = {
            "role": role,
            "content": content,
            "content_type": content_type,
            "conversation_id": conversation_id
        }
        
        if metadata:
            data["metadata"] = metadata
            
        return await self._request("POST", f"/conversations/{conversation_id}/messages", data=data)
    
    async def stream_chat(
        self,
        conversation_id: str,
        content: str,
        role: str = "user",
        content_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a message and receive streaming response
        
        Args:
            conversation_id: Conversation ID
            content: Message content
            role: Message sender role
            content_type: Content MIME type
            metadata: Optional metadata
            
        Yields:
            Streaming response chunks
        """
        data = {
            "role": role,
            "content": content,
            "content_type": content_type,
            "conversation_id": conversation_id
        }
        
        if metadata:
            data["metadata"] = metadata
        
        url = f"{self.base_url}/conversations/{conversation_id}/chat"
        headers = {"Content-Type": "application/json"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST", 
                    url, 
                    content=json.dumps(data), 
                    headers=headers
                ) as response:
                    async for chunk in response.aiter_lines():
                        if chunk:
                            try:
                                yield json.loads(chunk)
                            except json.JSONDecodeError:
                                logger.error(f"Failed to decode JSON chunk: {chunk}")
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            raise Exception(f"Streaming failed: {str(e)}")
    
    # Agent endpoints
    
    async def list_agents(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List agents
        
        Args:
            active_only: Whether to return only active agents
            
        Returns:
            List of agents
        """
        params = {"active_only": active_only}
        return await self._request("GET", "/agents", params=params)
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent data
        """
        return await self._request("GET", f"/agents/{agent_id}")
    
    async def create_agent(
        self,
        name: str,
        description: str,
        url: Optional[str] = None,
        is_remote: bool = False,
        model: Optional[str] = None,
        instruction: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new agent
        
        Args:
            name: Agent name
            description: Agent description
            url: Optional URL for remote agents
            is_remote: Whether the agent is remote
            model: Optional model name
            instruction: Optional instruction/prompt
            capabilities: Optional list of capabilities
            tools: Optional list of tools
            metadata: Optional metadata
            
        Returns:
            Created agent data
        """
        data = {
            "name": name,
            "description": description,
            "is_remote": is_remote
        }
        
        if url:
            data["url"] = url
            
        if model:
            data["model"] = model
            
        if instruction:
            data["instruction"] = instruction
            
        if capabilities:
            data["capabilities"] = capabilities
            
        if tools:
            data["tools"] = tools
            
        if metadata:
            data["metadata"] = metadata
            
        return await self._request("POST", "/agents", data=data)
    
    async def register_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Register an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Registered agent data
        """
        return await self._request("POST", f"/agents/{agent_id}/register")
    
    async def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent
        
        Args:
            agent_id: Agent ID
        """
        await self._request("POST", f"/agents/{agent_id}/unregister")
