"""Clarifying agent for gathering additional context from users."""

from google.adk import Agent
from prompts import CLARIFYING_PROMPT

MODEL = "gemini-2.5-pro"

clarifying_agent = Agent(
    model=MODEL,
    name="clarifying_agent",
    instruction=CLARIFYING_PROMPT,
    output_key="clarifying_agent_output",
) 