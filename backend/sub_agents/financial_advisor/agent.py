"""Financial advisor agent for providing personalized financial advice."""

from google.adk import Agent
from prompts import FINANCIAL_ADVISOR_PROMPT

MODEL = "gemini-2.5-pro"

financial_advisor_agent = Agent(
    model=MODEL,
    name="financial_advisor_agent",
    instruction=FINANCIAL_ADVISOR_PROMPT,
    output_key="financial_advisor_agent_output",
) 