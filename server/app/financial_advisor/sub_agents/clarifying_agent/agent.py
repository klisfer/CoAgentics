"""clarifying_agent for asking follow up question to answer user question better"""

from google.adk import Agent

from . import prompt

MODEL = "gemini-2.5-flash"

clarifying_agent = Agent(
    model=MODEL,
    name="clarifying_agent",
    instruction=prompt.EXECUTION_ANALYST_PROMPT,
    output_key="clarifying_agent_output",
)
