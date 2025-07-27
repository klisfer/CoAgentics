"""loan_guardian_agent_agent for helping with loan-related queries"""

from google.adk import Agent
from google.adk.tools import google_search
from . import prompt

MODEL = "gemini-2.5-flash"

loan_guardian_agent_agent = Agent(
    model=MODEL,
    name="loan_guardian_agent",
    instruction=prompt.LOAN_GUARDIAN_AGENT_PROMPT,
    output_key="loan_guardian_agent_agent_output",
    tools=[google_search],
)
