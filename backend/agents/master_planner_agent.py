import os
import google.generativeai as genai
from backend.research.context_analyzer import analyze_prompt
from backend.tools.financial_calculator import FinancialCalculatorTool
from backend.sub_agents.triage_agent.agent import TriageAgent
from backend.sub_agents.financial_calculator_agent.agent import FinancialCalculatorAgent
from backend.sub_agents.general_query_agent.agent import GeneralQueryAgent

class MasterPlannerAgent:
    def __init__(self):
        """
        Initializes the Master Planner Agent and its sub-agents.
        """
        self.triage_agent = TriageAgent()
        self.calculator_agent = FinancialCalculatorAgent()
        self.general_query_agent = GeneralQueryAgent()

    def process_prompt(self, prompt: str) -> str:
        """
        Orchestrates the entire process from triage to final response.

        1.  Classifies the prompt using the TriageAgent.
        2.  Delegates to the appropriate sub-agent.
        3.  Returns the sub-agent's response.
        """
        
        # 1. Triage the user's prompt
        category = self.triage_agent.triage_prompt(prompt)
        
        print(f"Triage category: {category}") # For debugging

        # 2. Delegate to the appropriate sub-agent
        if category == "calculator_request":
            return self.calculator_agent.process_prompt(prompt)
        elif category == "general_query":
            return self.general_query_agent.process_prompt(prompt)
        # We can add more categories and agents here in the future
        else:
            # Default fallback
            return self.general_query_agent.process_prompt(prompt) 