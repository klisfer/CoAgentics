
"""web_search_agent for finding information using google search"""

from google.adk import Agent
from google.adk.tools import google_search

from . import prompt

MODEL = "gemini-2.5-flash"

web_search_agent = Agent(
    model=MODEL,
    name="web_search_agent",
    instruction=prompt.FINANCE_GENIE_PROMPT,
    output_key="web_search_agent_output",
    tools=[google_search],
)