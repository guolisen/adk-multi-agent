"""Session routes for Deepdevflow."""

from typing import List, Optional
import sqlalchemy.orm
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.models import Session as SessionModel, Conversation as ConversationModel
from backend.utils.database import get_session
from .schemas import SessionCreate, SessionResponse, ConversationResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_session)
):
    """Create a new session.
    
    Args:
        session_data: The session data.
        db: The database session.
        
    Returns:
        The created session.
    """
    # Create new session
    new_session = SessionModel(
        name=session_data.name,
        user_id=session_data.user_id,
        is_active=session_data.is_active,
        session_metadata=session_data.metadata,  # Using session_metadata instead of metadata
        expiry_days=session_data.expiry_days
    )
    
    # Add to database
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return new_session


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_session)
):
    """List sessions.
    
    Args:
        skip: The number of sessions to skip.
        limit: The maximum number of sessions to return.
        active_only: Whether to return only active sessions.
        db: The database session.
        
    Returns:
        A list of sessions.
    """
    # Query sessions
    query = db.query(SessionModel)
    
    # Filter active sessions if requested
    if active_only:
        query = query.filter(SessionModel.is_active == True)
    
    # Apply pagination
    sessions = query.offset(skip).limit(limit).all()
    
    return sessions


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    include_conversations: bool = False,
    db: Session = Depends(get_session)
):
    """Get a session by ID.
    
    Args:
        session_id: The ID of the session to get.
        include_conversations: Whether to include conversations in the response.
        db: The database session.
        
    Returns:
        The session.
    """
    # Query session
    query = db.query(SessionModel).filter(SessionModel.id == session_id)
    
    # Include conversations if requested
    if include_conversations:
        query = query.options(
            sqlalchemy.orm.joinedload(SessionModel.conversations)
        )
    
    # Get session
    session = query.first()
    
    # Raise exception if not found
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    return session


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_data: SessionCreate,
    db: Session = Depends(get_session)
):
    """Update a session.
    
    Args:
        session_id: The ID of the session to update.
        session_data: The updated session data.
        db: The database session.
        
    Returns:
        The updated session.
    """
    # Get session
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    # Raise exception if not found
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    # Update fields
    session.name = session_data.name
    session.user_id = session_data.user_id
    session.is_active = session_data.is_active
    session.session_metadata = session_data.metadata  # Using session_metadata instead of metadata
    session.expiry_days = session_data.expiry_days
    
    # Commit changes
    db.commit()
    db.refresh(session)
    
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_session)
):
    """Delete a session.
    
    Args:
        session_id: The ID of the session to delete.
        db: The database session.
    """
    # Get session
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    # Raise exception if not found
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    # Mark as inactive instead of deleting
    session.is_active = False
    
    # Commit changes
    db.commit()


@router.get("/{session_id}/conversations", response_model=List[ConversationResponse])
async def list_session_conversations(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_session)
):
    """List conversations for a session.
    
    Args:
        session_id: The ID of the session to list conversations for.
        skip: The number of conversations to skip.
        limit: The maximum number of conversations to return.
        active_only: Whether to return only active conversations.
        db: The database session.
        
    Returns:
        A list of conversations.
    """
    # Check if session exists
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    # Raise exception if not found
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    # Query conversations
    query = db.query(ConversationModel).filter(
        ConversationModel.session_id == session_id
    )
    
    # Filter active conversations if requested
    if active_only:
        query = query.filter(ConversationModel.is_active == True)
    
    # Apply pagination
    conversations = query.offset(skip).limit(limit).all()
    
    return conversations
