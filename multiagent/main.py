from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import google.generativeai as genai

genai.configure(api_key="AIzaSyC5hya50p1DLxD3CxJoFiSph2E5UYP23CI")

# Define specialized sub-agents
billing_agent = LlmAgent(
    name="Billing",
    model="gemini-2.0-flash",
    instruction="You handle billing and payment-related inquiries.",
    description="Handles billing inquiries."
)
support_agent = LlmAgent(
    name="Support",
    model="gemini-2.0-flash",
    instruction="You provide technical support and troubleshooting assistance.",
    description="Handles technical support requests."
)
# Define the coordinator agent
coordinator = LlmAgent(
    name="HelpDeskCoordinator",
    model="gemini-2.0-flash",
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

model = genai.GenerativeModel("gemini-pro")
response = model.generate_content("Tell me a joke.")
print(response.text)

# Simulate a user query
user_query = "I can't log in."
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
    response = "\n".join([p.text for p in events[-1].content.parts if p.text])

print(response)







