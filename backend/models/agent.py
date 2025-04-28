"""Agent model for the Deepdevflow framework."""

from typing import Any, Dict, List, Optional
import json

from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class Agent(BaseModel):
    """Agent model to store registered agents."""

    __tablename__ = "agents"

    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    url = Column(String(255), nullable=True)  # Remote agent URL if applicable
    is_active = Column(Boolean, default=True)
    is_remote = Column(Boolean, default=False)
    model = Column(String(255), nullable=True)  # LLM model used by the agent
    instruction = Column(Text, nullable=True)  # Agent instruction/prompt
    capabilities = Column(Text, nullable=True)  # JSON serialized capabilities
    tools = Column(Text, nullable=True)  # JSON serialized tools
    agent_metadata = Column(Text, nullable=True)  # JSON serialized metadata, renamed from 'metadata' which is reserved
    
    # Relationships
    tasks = relationship("Task", back_populates="agent")

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"<Agent(id={self.id}, name={self.name}, is_remote={self.is_remote})>"
    
    @property
    def capabilities_list(self) -> List[str]:
        """Get capabilities as a list."""
        if not self.capabilities:
            return []
        return json.loads(self.capabilities)
    
    @capabilities_list.setter
    def capabilities_list(self, value: List[str]) -> None:
        """Set capabilities from a list."""
        self.capabilities = json.dumps(value) if value else None
        
    @property
    def tools_list(self) -> List[str]:
        """Get tools as a list."""
        if not self.tools:
            return []
        return json.loads(self.tools)
    
    @tools_list.setter
    def tools_list(self, value: List[str]) -> None:
        """Set tools from a list."""
        self.tools = json.dumps(value) if value else None
        
    @property
    def metadata_json(self) -> Dict[str, Any]:
        """Get metadata as JSON."""
        if not self.agent_metadata:
            return {}
        return json.loads(self.agent_metadata)
    
    @metadata_json.setter
    def metadata_json(self, value: Dict[str, Any]) -> None:
        """Set metadata from JSON."""
        self.agent_metadata = json.dumps(value) if value else None
