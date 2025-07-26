
"""insurance_advisor_agent for helping with insurance related """

from google.adk import Agent

from . import prompt

MODEL = "gemini-2.5-pro"

financial_advisor_agent = Agent(
    model=MODEL,
    name="financial_advisor_agent",
    instruction=prompt.EXECUTION_ANALYST_PROMPT,
    output_key="financial_advisor_agent_output",
)
