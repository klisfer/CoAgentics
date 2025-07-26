
"""investment_advisor_agent for helping with investment relate queries"""

from google.adk import Agent
from google.adk.tools import google_search
from . import prompt

MODEL = "gemini-2.5-flash"

investment_advisor_agent = Agent(
    model=MODEL,
    name="investment_advisor_agent",
    instruction=prompt.INVESTMENT_ADVISOR_PROMPT,
    output_key="investment_advisor_agent_output",
    tools=[google_search],
)
