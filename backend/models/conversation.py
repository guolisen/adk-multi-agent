"""Conversation model for the Deepdevflow framework."""

from typing import List, Optional
from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class Conversation(BaseModel):
    """Conversation model to store chat conversations."""

    __tablename__ = "conversations"

    name = Column(String(255), nullable=False, default="New Conversation")
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    conversation_metadata = Column(Text, nullable=True)  # Changed from 'metadata' which is reserved
    
    # Relationships
    session = relationship("Session", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", 
                           cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of the conversation."""
        return f"<Conversation(id={self.id}, name={self.name}, session_id={self.session_id})>"
