"""Task model for the Deepdevflow framework."""

from typing import Any, Dict, List, Optional
import json
import enum

from sqlalchemy import Column, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .base import BaseModel


class TaskState(enum.Enum):
    """Possible states for a task."""
    
    SUBMITTED = "submitted"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    INPUT_REQUIRED = "input_required"
    UNKNOWN = "unknown"


class Task(BaseModel):
    """Task model to store agent tasks."""

    __tablename__ = "tasks"

    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    state = Column(Enum(TaskState), default=TaskState.SUBMITTED)
    artifacts = Column(Text, nullable=True)  # JSON serialized artifacts
    task_metadata = Column(Text, nullable=True)  # JSON serialized metadata, renamed from 'metadata' which is reserved
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    message = relationship("Message", back_populates="tasks")
    session = relationship("Session")

    def __repr__(self) -> str:
        """String representation of the task."""
        return f"<Task(id={self.id}, agent_id={self.agent_id}, state={self.state})>"
    
    @property
    def artifacts_json(self) -> List[Dict[str, Any]]:
        """Get artifacts as JSON."""
        if not self.artifacts:
            return []
        return json.loads(self.artifacts)
    
    @artifacts_json.setter
    def artifacts_json(self, value: List[Dict[str, Any]]) -> None:
        """Set artifacts from JSON."""
        self.artifacts = json.dumps(value) if value else None
        
    @property
    def metadata_json(self) -> Dict[str, Any]:
        """Get metadata as JSON."""
        if not self.task_metadata:
            return {}
        return json.loads(self.task_metadata)
    
    @metadata_json.setter
    def metadata_json(self, value: Dict[str, Any]) -> None:
        """Set metadata from JSON."""
        self.task_metadata = json.dumps(value) if value else None
