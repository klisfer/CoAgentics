"""Main agent that coordinates all sub-agents for financial advice."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import preload_memory_tool
from sub_agents.triage_agent.agent import triage_agent
from sub_agents.clarifying_agent.agent import clarifying_agent
from sub_agents.financial_advisor.agent import financial_advisor_agent
from sub_agents.optimizer_assistant.agent import optimizer_agent
from sub_agents.financial_assistant.agent import financial_assistant_agent
from prompts import MASTER_COORDINATOR_PROMPT

MODEL = "gemini-2.5-pro"

root_agent = Agent(
    name="master_financial_planner",
    model=MODEL,
    description=(
        "Acts as the central decision-maker coordinating between specialized finance agents. "
        "It uses a long-term Memory Bank to recall user preferences across sessions."
    ),
    instruction=MASTER_COORDINATOR_PROMPT,
    tools=[
        preload_memory_tool.PreloadMemoryTool(),
        AgentTool(agent=triage_agent),
        AgentTool(agent=clarifying_agent),
        AgentTool(agent=financial_assistant_agent),
        AgentTool(agent=financial_advisor_agent),
        AgentTool(agent=optimizer_agent),
    ],
)