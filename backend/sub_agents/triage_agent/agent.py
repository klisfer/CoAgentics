"""Triage agent for determining the type of financial query."""

from google.adk import Agent
from prompts import TRIAGE_PROMPT

MODEL = "gemini-2.5-pro"

triage_agent = Agent(
    model=MODEL,
    name="triage_agent",
    instruction=TRIAGE_PROMPT,
    output_key="triage_agent_output",
) 