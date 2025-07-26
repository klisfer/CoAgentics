
"""insurance_advisor_agent for helping with insurance relate queries"""

from google.adk import Agent

from . import prompt

MODEL = "gemini-2.5-pro"

insurance_advisor_agent = Agent(
    model=MODEL,
    name="insurance_advisor_agent",
    instruction=prompt.INSURANCE_ADVISOR_PROMPT,
    output_key="insurance_advisor_agent_output",
)
