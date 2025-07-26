
"""optimizer_assistant Agent for optimizing the portfolio or plan for better returns or results"""

from google.adk import Agent

from . import prompt

MODEL="gemini-2.5-pro"

optimizer_agent = Agent(
    model=MODEL,
    name="optimizer_agent",
    instruction=prompt.RISK_ANALYST_PROMPT,
    output_key="optimizer_assistant_output",
)
