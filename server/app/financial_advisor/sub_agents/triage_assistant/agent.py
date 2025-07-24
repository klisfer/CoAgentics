
"""triage_assitant for accessing question for its intent"""

from google.adk import Agent

from . import prompt

MODEL = "gemini-2.5-pro"

triage_assitant = Agent(
    model=MODEL,
    name="triage_assitant",
    instruction=prompt.EXECUTION_ANALYST_PROMPT,
    output_key="triage_assitant_output",
)
