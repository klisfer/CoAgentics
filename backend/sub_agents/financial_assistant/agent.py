"""
The financial assistant agent is responsible for answering general financial questions.

It uses a web search tool to provide up-to-date information without requiring
any personal context from the user.
"""

from google.adk import Agent
from google.adk.tools import google_search
from prompts import FINANCIAL_ASSISTANT_PROMPT

MODEL = "gemini-2.5-pro"

financial_assistant_agent = Agent(
    model=MODEL,
    name="financial_assistant",
    instruction=FINANCIAL_ASSISTANT_PROMPT,
    output_key="financial_assistant_output",
    tools=[google_search],
) 