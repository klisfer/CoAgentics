
"""data_analyst_agent for finding information using google search"""

from google.adk import Agent
from google.adk.tools import google_search

from . import prompt

MODEL = "gemini-2.5-pro"

data_analyst_agent = Agent(
    model=MODEL,
    name="financial_assitant",
    instruction=prompt.FINANCE_GENIE_PROMPT,
    output_key="market_data_analysis_output",
    tools=[google_search],
)
