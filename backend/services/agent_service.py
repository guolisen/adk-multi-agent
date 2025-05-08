"""Agent service for Deepdevflow."""

import logging
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
import uuid

from sqlalchemy.orm import Session as DBSession

from backend.models import Agent as AgentModel, Task, Message, TaskState
from backend.utils.config import config
from backend.utils.database import get_session
from backend.services.agent import Agent, HostAgent, RemoteAgentConnection

# Setup logging
logger = logging.getLogger(__name__)


class AgentService:
    """Agent service that manages all agents."""
    
    _instance = None
    _agents = {}
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize agent service."""
        # Create host agent
        self._host_agent = HostAgent()
        
        # Register host agent as a managed agent
        # Note: We're calling the async method from a non-async context
        # This won't await the coroutine and is just creating a placeholder
        # The actual registration will happen in the first async call to get_agent or similar
        self._agents["host_agent"] = self._host_agent
        logger.info("Host agent initialized (async registration pending)")
        
        # Load registered agents from database
        self._load_agents_from_db()
    
    async def _register_host_agent(self):
        """Register host agent as a managed agent."""
        try:
            # Convert host agent to model
            agent_model = await self._host_agent.to_agent_model()
            
            # Register in memory
            self._agents["host_agent"] = self._host_agent
            
            logger.info("Host agent registered")
        except Exception as e:
            logger.error(f"Failed to register host agent: {e}")
    
    def _load_agents_from_db(self):
        """Load registered agents from database."""
        try:
            # Get database session
            with get_session() as db:
                # Get all active remote agents
                agents = db.query(AgentModel).filter(
                    AgentModel.is_active == True,
                    AgentModel.is_remote == True
                ).all()
                
                # Store agents for later async registration
                self._pending_db_agents = agents
                logger.info(f"Found {len(agents)} remote agents in DB (async registration pending)")
        except Exception as e:
            logger.error(f"Failed to load agents from database: {e}")
    
    async def _register_db_agents(self):
        """Register agents loaded from the database."""
        if hasattr(self, '_pending_db_agents'):
            for agent in self._pending_db_agents:
                try:
                    # Register with host agent
                    success = await self._host_agent.register_remote_agent(agent)
                    
                    if success:
                        logger.info(f"Registered remote agent from DB: {agent.name}")
                except Exception as e:
                    logger.error(f"Failed to register remote agent {agent.name}: {e}")
            
            # Clear pending agents
            delattr(self, '_pending_db_agents')
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to get.
            
        Returns:
            The agent or None if not found.
        """
        # Ensure host agent is properly registered
        await self._register_host_agent()
        
        # Ensure DB agents are registered
        if hasattr(self, '_pending_db_agents'):
            await self._register_db_agents()
        
        # Check if agent is in memory
        if agent_id in self._agents:
            return self._agents[agent_id]
        
        # Check if it's the host agent ID
        host_agent_model = await self._host_agent.to_agent_model()
        if agent_id == host_agent_model.id:
            return self._host_agent
        
        # Get agent from database
        try:
            with get_session() as db:
                agent_model = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
                
                if agent_model:
                    # Register with host agent if remote
                    if agent_model.is_remote:
                        success = await self._host_agent.register_remote_agent(agent_model)
                        
                        if success:
                            # The host agent now has a connection to this remote agent
                            logger.info(f"Registered remote agent: {agent_model.name}")
                            
                            # TODO: Return appropriate remote agent interface
                            return self._host_agent
                    else:
                        # TODO: Return appropriate local agent implementation
                        pass
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
        
        return None
    
    async def register_agent(self, agent_model: AgentModel) -> bool:
        """Register an agent.
        
        Args:
            agent_model: The agent model to register.
            
        Returns:
            True if the agent was registered successfully, False otherwise.
        """
        # Ensure host agent is properly registered
        await self._register_host_agent()
        
        try:
            # Save to database
            with get_session() as db:
                # Check if agent already exists
                existing = db.query(AgentModel).filter(AgentModel.name == agent_model.name).first()
                
                if existing:
                    # Update existing agent
                    for key, value in agent_model.to_dict().items():
                        if key != "id" and key != "created_at":
                            setattr(existing, key, value)
                    
                    # Save changes
                    db.commit()
                    
                    # Get updated model
                    agent_model = existing
                else:
                    # Add new agent
                    db.add(agent_model)
                    db.commit()
                    db.refresh(agent_model)
            
            # Register with host agent if remote
            if agent_model.is_remote:
                success = await self._host_agent.register_remote_agent(agent_model)
                
                if not success:
                    logger.error(f"Failed to register remote agent with host agent: {agent_model.name}")
                    return False
            
            logger.info(f"Registered agent: {agent_model.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent.
        
        Args:
            agent_id: The ID of the agent to unregister.
            
        Returns:
            True if the agent was unregistered successfully, False otherwise.
        """
        # Ensure host agent is properly registered
        await self._register_host_agent()
        
        try:
            # Update database
            with get_session() as db:
                agent_model = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
                
                if agent_model:
                    # Mark as inactive
                    agent_model.is_active = False
                    
                    # Save changes
                    db.commit()
                
                    logger.info(f"Unregistered agent: {agent_model.name}")
                    return True
                else:
                    logger.error(f"Agent not found: {agent_id}")
                    return False
        except Exception as e:
            logger.error(f"Failed to unregister agent: {e}")
            return False
    
    async def list_agents(self) -> List[AgentModel]:
        """List all registered agents.
        
        Returns:
            A list of agent models.
        """
        # Ensure host agent is properly registered
        await self._register_host_agent()
        
        # Ensure DB agents are registered
        if hasattr(self, '_pending_db_agents'):
            await self._register_db_agents()
            
        try:
            with get_session() as db:
                return db.query(AgentModel).filter(AgentModel.is_active == True).all()
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []
    
    async def process_message(self, message: Message) -> AsyncGenerator[str, None]:
        """Process a message and generate a response.
        
        Args:
            message: The message to process.
            
        Yields:
            Chunks of the response.
        """
        # Determine which agent should handle this message
        agent_id = await self._route_message(message)
        
        # Get the agent
        agent = await self.get_agent(agent_id)
        
        if not agent:
            yield "Sorry, no agent is available to process your message."
            return
        
        # Create a task for this message
        task = await agent.create_task(message)
        
        # Save task to database
        try:
            with get_session() as db:
                db.add(task)
                db.commit()
        except Exception as e:
            logger.error(f"Failed to save task: {e}")
        
        # Process the message
        async for chunk in agent.process_message(message):
            yield chunk
    
    async def _route_message(self, message: Message) -> str:
        """Route a message to the appropriate agent.
        
        Args:
            message: The message to route.
            
        Returns:
            The ID of the agent to route the message to.
        """
        # TODO: Implement sophisticated routing logic
        # For now, just return the host agent
        host_agent_model = await self._host_agent.to_agent_model()
        return host_agent_model.id


# Create a singleton instance
agent_service = AgentService()
