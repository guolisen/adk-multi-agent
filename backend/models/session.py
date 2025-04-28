"""Session model for the Deepdevflow framework."""

from typing import List, Optional
from sqlalchemy import Column, String, Boolean, Text, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel


class Session(BaseModel):
    """Session model to store user sessions."""

    __tablename__ = "sessions"

    name = Column(String(255), nullable=False, default="New Session")
    user_id = Column(String(255), nullable=True)  # Can be null for anonymous sessions
    is_active = Column(Boolean, default=True)
    session_metadata = Column(Text, nullable=True)  # JSON serialized metadata, renamed from 'metadata' which is reserved
    expiry_days = Column(Integer, default=30)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="session", 
                                cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of the session."""
        return f"<Session(id={self.id}, name={self.name}, is_active={self.is_active})>"
