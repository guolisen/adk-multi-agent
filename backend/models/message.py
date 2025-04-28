"""Message model for the Deepdevflow framework."""

from typing import Any, Dict, List, Optional
import json

from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel


class Message(BaseModel):
    """Message model to store chat messages."""

    __tablename__ = "messages"

    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user', 'agent', 'system', etc.
    content = Column(Text, nullable=True)
    content_type = Column(String(50), default="text/plain")  # MIME type
    message_metadata = Column(Text, nullable=True)  # Changed from 'metadata' to avoid reserved keyword
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    tasks = relationship("Task", back_populates="message")

    def __repr__(self) -> str:
        """String representation of the message."""
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"
    
    @property
    def metadata_json(self) -> Dict[str, Any]:
        """Get metadata as JSON."""
        if not self.message_metadata:
            return {}
        return json.loads(self.message_metadata)
    
    @metadata_json.setter
    def metadata_json(self, value: Dict[str, Any]) -> None:
        """Set metadata from JSON."""
        self.message_metadata = json.dumps(value) if value else None
