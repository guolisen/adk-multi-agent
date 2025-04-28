"""Agent routes for Deepdevflow."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from backend.models import Agent as AgentModel
from backend.utils.database import get_session
from backend.services import agent_service
from .schemas import AgentCreate, AgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_session)
):
    """Create a new agent.
    
    Args:
        agent_data: The agent data.
        db: The database session.
        
    Returns:
        The created agent.
    """
    # Create new agent
    new_agent = AgentModel(
        name=agent_data.name,
        description=agent_data.description,
        url=agent_data.url,
        is_active=agent_data.is_active,
        is_remote=agent_data.is_remote,
        model=agent_data.model,
        instruction=agent_data.instruction,
        capabilities=json.dumps(agent_data.capabilities) if agent_data.capabilities else None,
        tools=json.dumps(agent_data.tools) if agent_data.tools else None,
        agent_metadata=json.dumps(agent_data.metadata) if agent_data.metadata else None  # Changed from metadata to agent_metadata
    )
    
    # Add to database
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    
    # Register with agent service
    if agent_data.is_remote:
        success = await agent_service.register_agent(new_agent)
        
        if not success:
            # Mark as inactive if registration failed
            new_agent.is_active = False
            db.commit()
            db.refresh(new_agent)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register agent with agent service"
            )
    
    return new_agent


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    remote_only: Optional[bool] = None,
    db: Session = Depends(get_session)
):
    """List agents.
    
    Args:
        skip: The number of agents to skip.
        limit: The maximum number of agents to return.
        active_only: Whether to return only active agents.
        remote_only: Whether to return only remote agents.
        db: The database session.
        
    Returns:
        A list of agents.
    """
    # Query agents
    query = db.query(AgentModel)
    
    # Filter active agents if requested
    if active_only:
        query = query.filter(AgentModel.is_active == True)
    
    # Filter remote agents if requested
    if remote_only is not None:
        query = query.filter(AgentModel.is_remote == remote_only)
    
    # Apply pagination
    agents = query.offset(skip).limit(limit).all()
    
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_session)
):
    """Get an agent by ID.
    
    Args:
        agent_id: The ID of the agent to get.
        db: The database session.
        
    Returns:
        The agent.
    """
    # Get agent
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    
    # Raise exception if not found
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentCreate,
    db: Session = Depends(get_session)
):
    """Update an agent.
    
    Args:
        agent_id: The ID of the agent to update.
        agent_data: The updated agent data.
        db: The database session.
        
    Returns:
        The updated agent.
    """
    # Get agent
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    
    # Raise exception if not found
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Store old remote status
    was_remote = agent.is_remote
    
    # Update fields
    agent.name = agent_data.name
    agent.description = agent_data.description
    agent.url = agent_data.url
    agent.is_active = agent_data.is_active
    agent.is_remote = agent_data.is_remote
    agent.model = agent_data.model
    agent.instruction = agent_data.instruction
    agent.capabilities = json.dumps(agent_data.capabilities) if agent_data.capabilities else None
    agent.tools = json.dumps(agent_data.tools) if agent_data.tools else None
    agent.agent_metadata = json.dumps(agent_data.metadata) if agent_data.metadata else None  # Changed from metadata to agent_metadata
    
    # Commit changes
    db.commit()
    db.refresh(agent)
    
    # Register with agent service if now remote
    if agent.is_remote and (not was_remote or agent.is_active):
        success = await agent_service.register_agent(agent)
        
        if not success:
            # Mark as inactive if registration failed
            agent.is_active = False
            db.commit()
            db.refresh(agent)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register agent with agent service"
            )
    
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    db: Session = Depends(get_session)
):
    """Delete an agent.
    
    Args:
        agent_id: The ID of the agent to delete.
        db: The database session.
    """
    # Get agent
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    
    # Raise exception if not found
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Mark as inactive instead of deleting
    agent.is_active = False
    
    # Commit changes
    db.commit()
    
    # Unregister from agent service
    if agent.is_remote:
        await agent_service.unregister_agent(agent_id)


@router.post("/{agent_id}/register", response_model=AgentResponse)
async def register_agent(
    agent_id: str,
    db: Session = Depends(get_session)
):
    """Register an agent with the agent service.
    
    Args:
        agent_id: The ID of the agent to register.
        db: The database session.
        
    Returns:
        The registered agent.
    """
    # Get agent
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    
    # Raise exception if not found
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Ensure agent is remote
    if not agent.is_remote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent must be remote to register"
        )
    
    # Register with agent service
    success = await agent_service.register_agent(agent)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register agent with agent service"
        )
    
    # Mark as active
    agent.is_active = True
    
    # Commit changes
    db.commit()
    db.refresh(agent)
    
    return agent


@router.post("/{agent_id}/unregister", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_agent(
    agent_id: str,
    db: Session = Depends(get_session)
):
    """Unregister an agent from the agent service.
    
    Args:
        agent_id: The ID of the agent to unregister.
        db: The database session.
    """
    # Get agent
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    
    # Raise exception if not found
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Ensure agent is remote
    if not agent.is_remote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent must be remote to unregister"
        )
    
    # Unregister from agent service
    success = await agent_service.unregister_agent(agent_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unregister agent from agent service"
        )
    
    # Mark as inactive
    agent.is_active = False
    
    # Commit changes
    db.commit()
