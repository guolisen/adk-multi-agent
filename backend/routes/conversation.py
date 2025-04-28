"""Conversation routes for Deepdevflow."""

from typing import List, Optional
import sqlalchemy.orm
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import json

from backend.models import (
    Conversation as ConversationModel, 
    Message as MessageModel,
    Session as SessionModel
)
from backend.utils.database import get_session
from backend.services import agent_service
from .schemas import (
    ConversationCreate, 
    ConversationResponse, 
    MessageCreate,
    MessageResponse,
    StreamingResponse
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_session)
):
    """Create a new conversation.
    
    Args:
        conversation_data: The conversation data.
        db: The database session.
        
    Returns:
        The created conversation.
    """
    # Check if session exists
    session = db.query(SessionModel).filter(
        SessionModel.id == conversation_data.session_id
    ).first()
    
    # Raise exception if session not found
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {conversation_data.session_id} not found"
        )
    
    # Create new conversation
    new_conversation = ConversationModel(
        name=conversation_data.name,
        session_id=conversation_data.session_id,
        is_active=conversation_data.is_active,
        conversation_metadata=json.dumps(conversation_data.metadata) if conversation_data.metadata else None  # Changed from metadata to conversation_metadata
    )
    
    # Add to database
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    return new_conversation


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    session_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_session)
):
    """List conversations.
    
    Args:
        session_id: Optional session ID to filter by.
        skip: The number of conversations to skip.
        limit: The maximum number of conversations to return.
        active_only: Whether to return only active conversations.
        db: The database session.
        
    Returns:
        A list of conversations.
    """
    # Query conversations
    query = db.query(ConversationModel)
    
    # Filter by session ID if provided
    if session_id:
        query = query.filter(ConversationModel.session_id == session_id)
    
    # Filter active conversations if requested
    if active_only:
        query = query.filter(ConversationModel.is_active == True)
    
    # Apply pagination
    conversations = query.offset(skip).limit(limit).all()
    
    return conversations


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    include_messages: bool = False,
    db: Session = Depends(get_session)
):
    """Get a conversation by ID.
    
    Args:
        conversation_id: The ID of the conversation to get.
        include_messages: Whether to include messages in the response.
        db: The database session.
        
    Returns:
        The conversation.
    """
    # Query conversation
    query = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id
    )
    
    # Include messages if requested
    if include_messages:
        query = query.options(
            sqlalchemy.orm.joinedload(ConversationModel.messages)
        )
    
    # Get conversation
    conversation = query.first()
    
    # Raise exception if not found
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    return conversation


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    conversation_data: ConversationCreate,
    db: Session = Depends(get_session)
):
    """Update a conversation.
    
    Args:
        conversation_id: The ID of the conversation to update.
        conversation_data: The updated conversation data.
        db: The database session.
        
    Returns:
        The updated conversation.
    """
    # Get conversation
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id
    ).first()
    
    # Raise exception if not found
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Check if session exists
    session = db.query(SessionModel).filter(
        SessionModel.id == conversation_data.session_id
    ).first()
    
    # Raise exception if session not found
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {conversation_data.session_id} not found"
        )
    
    # Update fields
    conversation.name = conversation_data.name
    conversation.session_id = conversation_data.session_id
    conversation.is_active = conversation_data.is_active
    conversation.conversation_metadata = json.dumps(conversation_data.metadata) if conversation_data.metadata else None  # Changed from metadata to conversation_metadata
    
    # Commit changes
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_session)
):
    """Delete a conversation.
    
    Args:
        conversation_id: The ID of the conversation to delete.
        db: The database session.
    """
    # Get conversation
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id
    ).first()
    
    # Raise exception if not found
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Mark as inactive instead of deleting
    conversation.is_active = False
    
    # Commit changes
    db.commit()


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def list_conversation_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session)
):
    """List messages for a conversation.
    
    Args:
        conversation_id: The ID of the conversation to list messages for.
        skip: The number of messages to skip.
        limit: The maximum number of messages to return.
        db: The database session.
        
    Returns:
        A list of messages.
    """
    # Check if conversation exists
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id
    ).first()
    
    # Raise exception if not found
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Query messages
    messages = db.query(MessageModel).filter(
        MessageModel.conversation_id == conversation_id
    ).order_by(
        MessageModel.created_at.asc()
    ).offset(skip).limit(limit).all()
    
    return messages


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: str,
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session)
):
    """Create a new message.
    
    Args:
        conversation_id: The ID of the conversation to create a message for.
        message_data: The message data.
        background_tasks: Background tasks to run.
        db: The database session.
        
    Returns:
        The created message.
    """
    # Check if conversation exists
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id
    ).first()
    
    # Raise exception if not found
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Create new message
    new_message = MessageModel(
        role=message_data.role,
        content=message_data.content,
        content_type=message_data.content_type,
        conversation_id=conversation_id,
        message_metadata=json.dumps(message_data.metadata) if message_data.metadata else None  # Changed from metadata to message_metadata
    )
    
    # Add to database
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # If the message is from a user, process it in the background to generate a response
    if message_data.role == "user":
        background_tasks.add_task(
            process_user_message,
            conversation_id=conversation_id,
            message_id=new_message.id,
            db=db
        )
    
    return new_message


@router.post("/{conversation_id}/chat", response_model=List[StreamingResponse])
async def chat(
    conversation_id: str,
    message_data: MessageCreate,
    db: Session = Depends(get_session)
):
    """Chat with the Deepdevflow system.
    
    This creates a user message and immediately returns a streaming response.
    
    Args:
        conversation_id: The ID of the conversation to chat in.
        message_data: The message data.
        db: The database session.
        
    Returns:
        A streaming response from the system.
    """
    # Check if conversation exists
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conversation_id
    ).first()
    
    # Raise exception if not found
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Create new message
    new_message = MessageModel(
        role="user",
        content=message_data.content,
        content_type=message_data.content_type,
        conversation_id=conversation_id,
        message_metadata=json.dumps(message_data.metadata) if message_data.metadata else None  # Changed from metadata to message_metadata
    )
    
    # Add to database
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Process message and stream response
    return process_message_streaming(new_message, db)


async def process_user_message(conversation_id: str, message_id: str, db: Session):
    """Process a user message in the background.
    
    Args:
        conversation_id: The ID of the conversation.
        message_id: The ID of the message to process.
        db: The database session.
    """
    # Get message
    message = db.query(MessageModel).filter(
        MessageModel.id == message_id
    ).first()
    
    if not message:
        return
    
    # Process message with agent service
    response_text = ""
    async for chunk in agent_service.process_message(message):
        response_text += chunk
    
    # Create response message
    response_message = MessageModel(
        role="assistant",
        content=response_text,
        content_type="text/plain",
        conversation_id=conversation_id,
        message_metadata=json.dumps({"source_message_id": message_id})  # Changed from metadata to message_metadata
    )
    
    # Add to database
    db.add(response_message)
    db.commit()


async def process_message_streaming(message: MessageModel, db: Session):
    """Process a message and stream the response.
    
    Args:
        message: The message to process.
        db: The database session.
        
    Yields:
        StreamingResponse objects with chunks of the response.
    """
    # List to collect all chunks for creating the final message
    all_chunks = []
    
    # Process message with agent service
    async for chunk in agent_service.process_message(message):
        all_chunks.append(chunk)
        
        # Yield chunk
        yield StreamingResponse(
            chunk=chunk,
            done=False,
            metadata={"message_id": message.id}
        )
    
    # Create response message with all chunks
    response_message = MessageModel(
        role="assistant",
        content="".join(all_chunks),
        content_type="text/plain",
        conversation_id=message.conversation_id,
        message_metadata=json.dumps({"source_message_id": message.id})  # Changed from metadata to message_metadata
    )
    
    # Add to database
    db.add(response_message)
    db.commit()
    db.refresh(response_message)
    
    # Yield final chunk with message ID
    yield StreamingResponse(
        chunk="",
        done=True,
        metadata={
            "message_id": message.id,
            "response_message_id": response_message.id
        }
    )
