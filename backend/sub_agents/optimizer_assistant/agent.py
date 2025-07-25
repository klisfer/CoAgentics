"""Optimizer assistant for enhancing financial advice and strategies."""

from google.adk import Agent
from prompts import OPTIMIZER_PROMPT

MODEL = "gemini-2.5-pro"

optimizer_agent = Agent(
    model=MODEL,
    name="optimizer_agent",
    instruction=OPTIMIZER_PROMPT,
    output_key="optimizer_agent_output",
) 