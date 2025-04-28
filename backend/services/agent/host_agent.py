"""Host agent implementation for Deepdevflow using Google ADK."""

import asyncio
import json
import uuid
import logging
from typing import Any, Dict, List, Optional, Union, AsyncGenerator

from google.adk import Agent as ADKAgent, Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.events.event import Event as ADKEvent
from google.adk.events.event_actions import EventActions as ADKEventActions
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext

from backend.models import Message, Task, Agent as AgentModel, TaskState
from backend.utils.config import config
from .base import Agent
from .remote_agent_connection import RemoteAgentConnection

# Setup logging
logger = logging.getLogger(__name__)


class HostAgent(Agent):
    """Host agent implementation using Google ADK."""
    
    def __init__(self):
        """Initialize host agent with configuration."""
        # Get agent configuration
        self.agent_config = config.get_agent_config("host_agent")
        
        # Initialize session and memory services
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        self.artifact_service = InMemoryArtifactService()
        
        # Initialize remote agent connections
        self.remote_agents: Dict[str, RemoteAgentConnection] = {}
        
        # Create ADK agent
        self.adk_agent = self._create_adk_agent()
        
        # Create ADK runner
        self.runner = Runner(
            app_name=config.app_name,
            agent=self.adk_agent,
            session_service=self.session_service,
            memory_service=self.memory_service,
            artifact_service=self.artifact_service
        )
    
    def _create_adk_agent(self) -> ADKAgent:
        """Create Google ADK agent.
        
        Returns:
            The created ADK agent.
        """
        # Get model configuration
        model_name = self.agent_config.get("model", "gpt-3.5-turbo")
        
        # Create agent
        return ADKAgent(
            model=LiteLlm(model=model_name),
            name=self.agent_config.get("name", "Host Agent"),
            instruction=self._get_root_instruction,
            before_model_callback=self._before_model_callback,
            description=self.agent_config.get("description", "Main orchestration agent"),
            tools=[
                self.list_remote_agents,
                self.send_task,
                self.check_task_status
            ]
        )
    
    def _get_root_instruction(self, context: ReadonlyContext) -> str:
        """Get root instruction for the host agent.
        
        Args:
            context: The context to get the instruction from.
            
        Returns:
            The root instruction string.
        """
        # Get the instruction from config
        instruction = self.agent_config.get("instruction", "")
        
        # Get the current state
        state = context.state
        current_agent = self._check_state(context)
        
        # Add available agents to the instruction
        agent_info = []
        for agent in self.remote_agents.values():
            agent_info.append(json.dumps({
                "name": agent.name,
                "description": agent.description
            }))
        agents_str = "\n".join(agent_info)
        
        # Add current agent information
        current_agent_str = current_agent.get("active_agent", "None")
        
        # Format the full instruction
        full_instruction = f"""
{instruction}

Agents:
{agents_str}

Current agent: {current_agent_str}
"""
        return full_instruction
    
    def _check_state(self, context: ReadonlyContext) -> Dict[str, Any]:
        """Check the state of the context.
        
        Args:
            context: The context to check the state of.
            
        Returns:
            A dictionary with state information.
        """
        state = context.state
        if ('session_id' in state and
            'session_active' in state and
            state['session_active'] and
            'agent' in state):
            return {"active_agent": state["agent"]}
        return {"active_agent": "None"}
    
    def _before_model_callback(self, callback_context: CallbackContext, llm_request):
        """Callback before the model is called.
        
        Args:
            callback_context: The callback context.
            llm_request: The LLM request.
        """
        state = callback_context.state
        if 'session_active' not in state or not state['session_active']:
            if 'session_id' not in state:
                state['session_id'] = str(uuid.uuid4())
            state['session_active'] = True
    
    async def list_remote_agents(self):
        """List available remote agents.
        
        Returns:
            A list of remote agent information.
        """
        if not self.remote_agents:
            return []
        
        remote_agent_info = []
        for agent in self.remote_agents.values():
            remote_agent_info.append({
                "name": agent.name,
                "description": agent.description
            })
        return remote_agent_info
    
    async def send_task(self, agent_name: str, message: str, tool_context: ToolContext):
        """Send a task to a remote agent.
        
        Args:
            agent_name: The name of the agent to send the task to.
            message: The message to send to the agent.
            tool_context: The tool context.
            
        Returns:
            A dictionary with the task results.
        """
        if agent_name not in self.remote_agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        # Update state
        state = tool_context.state
        state['agent'] = agent_name
        
        # Get agent
        agent = self.remote_agents[agent_name]
        
        # Create task ID or use existing
        if 'task_id' in state:
            task_id = state['task_id']
        else:
            task_id = str(uuid.uuid4())
        
        # Get session ID
        session_id = state['session_id']
        
        # Create task parameters
        task_params = {
            "id": task_id,
            "sessionId": session_id,
            "message": {
                "role": "user",
                "content": message,
                "metadata": {
                    "conversation_id": session_id,
                    "message_id": str(uuid.uuid4())
                }
            }
        }
        
        # Send task to remote agent
        task = await agent.send_task(task_params)
        
        # Update session state
        state['session_active'] = task.status.state not in [
            TaskState.COMPLETED,
            TaskState.CANCELED,
            TaskState.FAILED,
            TaskState.UNKNOWN,
        ]
        
        # Handle task state
        if task.status.state == TaskState.INPUT_REQUIRED:
            # Force user input back
            tool_context.actions.skip_summarization = True
            tool_context.actions.escalate = True
        elif task.status.state == TaskState.CANCELED:
            raise ValueError(f"Agent {agent_name} task {task.id} is cancelled")
        elif task.status.state == TaskState.FAILED:
            raise ValueError(f"Agent {agent_name} task {task.id} failed")
        
        # Process response
        response = []
        
        # Add message content if available
        if task.status.message:
            response.append(task.status.message.content)
        
        # Add artifacts if available
        if task.artifacts:
            for artifact in task.artifacts:
                response.append(json.dumps(artifact))
        
        return response
    
    async def check_task_status(self, task_id: str):
        """Check the status of a task.
        
        Args:
            task_id: The ID of the task to check.
            
        Returns:
            A dictionary with the task status.
        """
        # Check task status across all agents
        for agent in self.remote_agents.values():
            try:
                task = await agent.get_task_status(task_id)
                if task:
                    return {
                        "id": task.id,
                        "state": str(task.status.state),
                        "agent": agent.name
                    }
            except Exception as e:
                logger.error(f"Error checking task status: {e}")
        
        return {"id": task_id, "state": "UNKNOWN", "agent": "None"}
    
    async def register_remote_agent(self, agent_model: AgentModel) -> bool:
        """Register a remote agent.
        
        Args:
            agent_model: The agent model to register.
            
        Returns:
            True if the agent was registered successfully, False otherwise.
        """
        try:
            # Skip if already registered
            if agent_model.name in self.remote_agents:
                return True
            
            # Create remote agent connection
            agent = RemoteAgentConnection(
                name=agent_model.name,
                description=agent_model.description,
                url=agent_model.url,
                capabilities=agent_model.capabilities_list
            )
            
            # Add to remote agents
            self.remote_agents[agent_model.name] = agent
            
            logger.info(f"Registered remote agent: {agent_model.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register remote agent: {e}")
            return False
    
    async def process_message(self, message: Message) -> AsyncGenerator[str, None]:
        """Process a message and generate a response.
        
        Args:
            message: The message to process.
            
        Yields:
            Chunks of the response.
        """
        # Get or create session
        session_id = str(uuid.uuid4()) if not message.conversation_id else message.conversation_id
        session = self.session_service.get_session(
            app_name=config.app_name,
            user_id="user",  # TODO: Use actual user ID
            session_id=session_id
        )
        
        # Create message for ADK
        adk_message = {
            "role": message.role,
            "content": message.content
        }
        
        # Process message
        async for event in self.runner.run_async(
            user_id="user",  # TODO: Use actual user ID
            session_id=session_id,
            new_message=adk_message
        ):
            if event.content and event.content.role == "model":
                yield event.content.parts[0].text if event.content.parts else ""
    
    async def create_task(self, message: Message) -> Task:
        """Create a task from a message.
        
        Args:
            message: The message to create a task from.
            
        Returns:
            The created task.
        """
        # Create a new task
        task = Task(
            id=str(uuid.uuid4()),
            agent_id=await self._get_agent_id_for_query(message.content),
            message_id=message.id,
            session_id=message.conversation_id,
            state=TaskState.SUBMITTED,
            metadata_json={"source_message_id": message.id}
        )
        
        # Return the task
        return task
    
    async def update_task(self, task: Task, message: Optional[Message] = None) -> Task:
        """Update a task.
        
        Args:
            task: The task to update.
            message: Optional message with updated information.
            
        Returns:
            The updated task.
        """
        # Update task state
        if message:
            # Get appropriate agent for the query
            agent_id = await self._get_agent_id_for_query(message.content)
            
            # Update task
            task.agent_id = agent_id
            task.state = TaskState.WORKING
        
        # Return updated task
        return task
    
    async def get_task_status(self, task_id: str) -> Task:
        """Get the status of a task.
        
        Args:
            task_id: The ID of the task to get the status of.
            
        Returns:
            The task.
        """
        # TODO: Implement task status retrieval from database
        # This is a placeholder implementation
        task = Task(
            id=task_id,
            agent_id="unknown",
            message_id="unknown",
            session_id="unknown",
            state=TaskState.UNKNOWN
        )
        return task
    
    async def cancel_task(self, task_id: str) -> Task:
        """Cancel a task.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            The canceled task.
        """
        # Get task
        task = await self.get_task_status(task_id)
        
        # Update task state
        task.state = TaskState.CANCELED
        
        # Return updated task
        return task
    
    async def list_capabilities(self) -> List[str]:
        """List the capabilities of the agent.
        
        Returns:
            A list of capability strings.
        """
        return self.agent_config.get("capabilities", [])
    
    async def to_agent_model(self) -> AgentModel:
        """Convert the agent to an AgentModel.
        
        Returns:
            The agent model representation.
        """
        return AgentModel(
            name=self.agent_config.get("name", "Host Agent"),
            description=self.agent_config.get("description", "Main orchestration agent"),
            is_remote=False,
            model=self.agent_config.get("model", "gpt-3.5-turbo"),
            instruction=self.agent_config.get("instruction", ""),
            capabilities_list=self.agent_config.get("capabilities", []),
            tools_list=self.agent_config.get("tools", [])
        )
    
    async def _get_agent_id_for_query(self, query: str) -> str:
        """Get the agent ID for a query.
        
        This method analyzes the query and determines which agent would be best
        to handle it based on capabilities and routing strategy.
        
        Args:
            query: The query to analyze.
            
        Returns:
            The ID of the agent to handle the query.
        """
        # TODO: Implement agent selection logic
        # For now, return the host agent ID
        agent_model = await self.to_agent_model()
        return agent_model.id
