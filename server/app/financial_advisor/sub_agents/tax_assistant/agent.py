
"""tax_assistant for helping user with tax related queries"""

from google.adk import Agent
from google.adk.tools import google_search

from . import prompt

MODEL = "gemini-2.5-pro"

tax_consultant_agent = Agent(
    model=MODEL,
    name="tax_consultant_agent",
    instruction=prompt.TAX_CONSULATENT_PROMPT,
    output_key="tax_consultant_agent_output",
    tools=[google_search],
)
