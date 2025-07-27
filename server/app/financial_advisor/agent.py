"""financial_advisor: acts as personal finance consultant"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
# from .sub_agents.financial_assistant import data_analyst_agent
# from .sub_agents.financial_advisor import financial_advisor_agent
# from .sub_agents.optimizer_assistant import optimizer_agent
# from .sub_agents.clarifying_agent import clarifying_agent
# from .sub_agents.triage_assistant import triage_assitant

from .sub_agents.tax_assistant import tax_consultant_agent
from .sub_agents.investment_assistant import investment_advisor_agent
from .sub_agents.insurance_assistant import insurance_advisor_agent
from .sub_agents.budget_agent import budgeting_agent
from .sub_agents.loan_agent import loan_guardian_agent_agent

MODEL = "gemini-2.5-pro"
  # Or a deployed URL like https://your-host.com


financial_coordinator = LlmAgent(
    name="master_financial_planner",
    model=MODEL,
    description=(
        "Acts as the central decision-maker coordinating between specialized finance agents. "
        "When a user question arrives, it first delegates to a triage agent to determine the type of query: "
        "(1) General finance knowledge, (2) Related to user's current investments, or (3) Focused on future financial goals. "
        "If no clarification is needed, route the query to the financial assistant. "
        "If clarification is needed, it engages the clarifying agent to collect additional inputs from the user, "
        "then forwards the enriched query to the financial advisor. "
        "Finally, it invokes the optimizer agent to enhance the recommendation. "
        "Returns a comprehensive response including direct insights and optimized financial strategies."
    ),
    instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
    output_key="master_financial_planner_output",
    tools=[
        # AgentTool(agent=triage_assitant),
        # AgentTool(agent=clarifying_agent),
        # AgentTool(agent=data_analyst_agent),
        # AgentTool(agent=financial_advisor_agent),
        # AgentTool(agent=optimizer_agent),
    ],
)

root_agent = financial_coordinator
