"""API schemas for Deepdevflow routes."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import uuid


class TaskStateEnum(str, Enum):
    """Task state enumeration."""
    
    SUBMITTED = "submitted"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    INPUT_REQUIRED = "input_required"
    UNKNOWN = "unknown"


class MessageBase(BaseModel):
    """Base message schema."""
    
    role: str = Field(description="Role of the message sender (user, assistant, system)")
    content: str = Field(description="Content of the message")
    content_type: Optional[str] = Field(
        default="text/plain", 
        description="MIME type of the content"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the message"
    )


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    
    conversation_id: str = Field(description="ID of the conversation")


class MessageResponse(MessageBase):
    """Schema for message response."""
    
    id: str = Field(description="ID of the message")
    conversation_id: str = Field(description="ID of the conversation")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        
        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation schema."""
    
    name: str = Field(description="Name of the conversation")
    is_active: bool = Field(default=True, description="Whether the conversation is active")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the conversation"
    )


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    
    session_id: str = Field(description="ID of the session")


class ConversationResponse(ConversationBase):
    """Schema for conversation response."""
    
    id: str = Field(description="ID of the conversation")
    session_id: str = Field(description="ID of the session")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    messages: Optional[List[MessageResponse]] = Field(
        default=None,
        description="Messages in the conversation"
    )

    class Config:
        """Pydantic configuration."""
        
        from_attributes = True


class SessionBase(BaseModel):
    """Base session schema."""
    
    name: str = Field(description="Name of the session")
    user_id: Optional[str] = Field(default=None, description="ID of the user")
    is_active: bool = Field(default=True, description="Whether the session is active")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the session"
    )
    expiry_days: Optional[int] = Field(default=30, description="Number of days until session expires")

    class Config:
        """Additional configuration."""
        
        # Map the Pydantic field to a differently named model attribute
        fields = {
            "metadata": {"alias": "session_metadata"}
        }


class SessionCreate(SessionBase):
    """Schema for creating a session."""
    
    pass


class SessionResponse(SessionBase):
    """Schema for session response."""
    
    id: str = Field(description="ID of the session")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    conversations: Optional[List[ConversationResponse]] = Field(
        default=None,
        description="Conversations in the session"
    )

    class Config:
        """Pydantic configuration."""
        
        from_attributes = True
        fields = {
            "metadata": {"alias": "session_metadata"}
        }


class AgentBase(BaseModel):
    """Base agent schema."""
    
    name: str = Field(description="Name of the agent")
    description: Optional[str] = Field(default=None, description="Description of the agent")
    url: Optional[str] = Field(default=None, description="URL of the agent")
    is_active: bool = Field(default=True, description="Whether the agent is active")
    is_remote: bool = Field(default=False, description="Whether the agent is remote")
    model: Optional[str] = Field(default=None, description="Model used by the agent")
    instruction: Optional[str] = Field(default=None, description="Instruction for the agent")
    capabilities: Optional[List[str]] = Field(
        default=None,
        description="Capabilities of the agent"
    )
    tools: Optional[List[str]] = Field(
        default=None,
        description="Tools available to the agent"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the agent"
    )


class AgentCreate(AgentBase):
    """Schema for creating an agent."""
    
    pass


class AgentResponse(AgentBase):
    """Schema for agent response."""
    
    id: str = Field(description="ID of the agent")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        
        from_attributes = True


class TaskBase(BaseModel):
    """Base task schema."""
    
    agent_id: str = Field(description="ID of the agent")
    message_id: str = Field(description="ID of the message")
    session_id: str = Field(description="ID of the session")
    state: TaskStateEnum = Field(default=TaskStateEnum.SUBMITTED, description="State of the task")
    artifacts: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Artifacts produced by the task"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the task"
    )


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    
    pass


class TaskResponse(TaskBase):
    """Schema for task response."""
    
    id: str = Field(description="ID of the task")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        
        from_attributes = True


class StreamingResponse(BaseModel):
    """Schema for streaming response."""
    
    chunk: str = Field(description="Chunk of the response")
    done: bool = Field(description="Whether this is the last chunk")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the chunk"
    )
