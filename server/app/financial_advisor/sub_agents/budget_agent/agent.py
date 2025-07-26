"""budget_agent for answering user questions about budgeting"""

from google.adk import Agent

from . import prompt

MODEL = "gemini-2.5-flash"

budgeting_agent = Agent(
    model=MODEL,
    name="budgeting_agent",
    instruction=prompt.BUDGETING_AGENT_PROMPT,
    output_key="budgeting_agent_output",
)
