from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import google.generativeai as genai
from google.adk.models.lite_llm import LiteLlm
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("<<MultiAgentTest>>")

genai.configure(api_key="")
os.environ['OPENAI_API_KEY'] = ''
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
MODEL_GPT_4O = "gpt-3.5-turbo-0125"


# Define specialized sub-agents
billing_agent = LlmAgent(
    name="Billing",
    model=LiteLlm(model=MODEL_GPT_4O),
    instruction="You handle billing and payment-related inquiries.",
    description="Handles billing inquiries."
)
support_agent = LlmAgent(
    name="Support",
    model=LiteLlm(model=MODEL_GPT_4O),
    instruction="You provide technical support and troubleshooting assistance.",
    description="Handles technical support requests."
)
# Define the coordinator agent
coordinator = LlmAgent(
    name="HelpDeskCoordinator",
    model=LiteLlm(model=MODEL_GPT_4O),
    instruction="Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
    description="Main help desk router.",
    sub_agents=[billing_agent, support_agent]
)
# For ADK compatibility, the root agent must be named `root_agent`
root_agent = coordinator

runner = Runner(
        app_name="test_agent",
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),)


# Simulate a user query
user_query = "I can't log in gmail, help to give advice."
#user_query = "my billing is not working, help to give advice."
user_id = "test_user"
session_id = "test_session"

# Create a session
session = runner.session_service.create_session(
    app_name="test_agent",
    user_id=user_id,
    state={},
    session_id=session_id,
)

# Create a content object with the user query
content = types.Content(
    role="user", 
    parts=[types.Part.from_text(text=user_query)]
)

# Run the agent with the correct parameters
events = list(runner.run(
    user_id=user_id, 
    session_id=session.id, 
    new_message=content
))

# Process the events to get the response
response = ""
if events and events[-1].content and events[-1].content.parts:
    for event in events:
        logger.info(f"Event: {event.author}, Actions: {event.actions}")
        response = "\n".join([p.text for p in events[-1].content.parts if p.text])

print(response)







