import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass

from app.agents.base import BaseAgent, ToolCapableAgent, AgentMessage, AgentContext, AgentStatus
from app.core.config import settings

@dataclass
class AgentPlan:
    """Represents a plan for agent execution"""
    agent_type: str
    priority: int
    reasoning: str
    expected_tools: List[str]
    context_requirements: List[str]

class MasterPlannerAgent(ToolCapableAgent):
    """
    Master Planner Agent - Orchestrates other agents and creates execution plans
    Acts as the central coordinator in the CoAgentics system
    """
    
    def __init__(self):
        super().__init__(
            agent_id="master_planner",
            name="Master Planner",
            description="Orchestrates and coordinates other agents to handle complex user requests",
            capabilities=[
                "agent_orchestration",
                "task_decomposition",
                "planning",
                "coordination",
                "context_management"
            ]
        )
        
        # Registry of available agents
        self.available_agents: Dict[str, BaseAgent] = {}
        
        # Task decomposition patterns
        self.task_patterns = {
            "financial_analysis": ["research_context", "financial_assistant", "financial_advisor"],
            "investment_advice": ["research_context", "financial_assistant", "financial_advisor", "optimizer"],
            "portfolio_optimization": ["financial_assistant", "optimizer", "research_context"],
            "market_research": ["research_context", "web_search", "financial_assistant"],
            "financial_planning": ["financial_assistant", "financial_advisor", "optimizer"]
        }
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the master planner"""
        self.available_agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
    
    async def _can_handle_internal(self, message: str, context: AgentContext) -> bool:
        """Master planner can handle any message by delegating to appropriate agents"""
        return True  # Master planner is always available as fallback
    
    async def _execute_internal(self, message: AgentMessage, **kwargs) -> Union[str, AgentMessage]:
        """Execute master planner orchestration logic"""
        self.logger.info(f"Master Planner processing: {message.content}")
        
        try:
            # Analyze the request and create execution plan
            plan = await self._create_execution_plan(message.content)
            
            if not plan:
                return AgentMessage(
                    content="I'm not sure how to handle that request. Could you please provide more specific details?",
                    message_type="assistant"
                )
            
            # Execute the plan
            result = await self._execute_plan(plan, message)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in master planner: {e}")
            return AgentMessage(
                content="I encountered an issue while planning your request. Let me try a simpler approach.",
                message_type="error"
            )
    
    async def _create_execution_plan(self, query: str) -> Optional[List[AgentPlan]]:
        """Create an execution plan based on the user query"""
        query_lower = query.lower()
        
        # Analyze query to determine task type
        task_type = self._classify_task(query_lower)
        
        if task_type not in self.task_patterns:
            # Default plan - use most relevant single agent
            best_agent = await self._find_best_agent(query)
            if best_agent:
                return [AgentPlan(
                    agent_type=best_agent,
                    priority=1,
                    reasoning=f"Single agent {best_agent} can handle this query",
                    expected_tools=[],
                    context_requirements=[]
                )]
            return None
        
        # Create multi-agent plan
        agent_sequence = self.task_patterns[task_type]
        plan = []
        
        for i, agent_type in enumerate(agent_sequence):
            plan.append(AgentPlan(
                agent_type=agent_type,
                priority=i + 1,
                reasoning=f"Step {i + 1}: {agent_type} for {task_type}",
                expected_tools=self._get_expected_tools(agent_type),
                context_requirements=self._get_context_requirements(agent_type)
            ))
        
        return plan
    
    def _classify_task(self, query: str) -> str:
        """Classify the task type based on query content"""
        if any(word in query for word in ["optimize", "allocation", "rebalance"]):
            return "portfolio_optimization"
        elif any(word in query for word in ["invest", "investment", "should i buy"]):
            return "investment_advice"
        elif any(word in query for word in ["market", "trend", "research", "analysis"]):
            return "market_research"
        elif any(word in query for word in ["plan", "planning", "retirement", "goal"]):
            return "financial_planning"
        elif any(word in query for word in ["analyze", "review", "performance"]):
            return "financial_analysis"
        else:
            return "general_financial"
    
    async def _find_best_agent(self, query: str) -> Optional[str]:
        """Find the best single agent to handle a query"""
        if not self.context:
            return "financial_assistant"  # Default fallback
        
        # Check which agents can handle this query
        suitable_agents = []
        for agent_id, agent in self.available_agents.items():
            if await agent.can_handle(query, self.context):
                suitable_agents.append(agent_id)
        
        # Return the most specific agent
        priority_order = [
            "financial_advisor", 
            "optimizer", 
            "financial_assistant", 
            "research_context"
        ]
        
        for preferred_agent in priority_order:
            if preferred_agent in suitable_agents:
                return preferred_agent
        
        return suitable_agents[0] if suitable_agents else "financial_assistant"
    
    def _get_expected_tools(self, agent_type: str) -> List[str]:
        """Get expected tools for an agent type"""
        tool_mapping = {
            "research_context": ["web_search", "document_search"],
            "financial_assistant": ["financial_calculator"],
            "financial_advisor": ["financial_calculator", "web_search"],
            "optimizer": ["financial_calculator", "optimization_tools"]
        }
        return tool_mapping.get(agent_type, [])
    
    def _get_context_requirements(self, agent_type: str) -> List[str]:
        """Get context requirements for an agent type"""
        context_mapping = {
            "research_context": ["market_data", "news_context"],
            "financial_assistant": ["user_profile", "financial_goals"],
            "financial_advisor": ["user_profile", "financial_goals", "risk_tolerance"],
            "optimizer": ["portfolio_data", "constraints", "objectives"]
        }
        return context_mapping.get(agent_type, [])
    
    async def _execute_plan(self, plan: List[AgentPlan], original_message: AgentMessage) -> AgentMessage:
        """Execute the planned sequence of agents"""
        results = []
        current_context = original_message.content
        
        for step in plan:
            self.logger.info(f"Executing plan step: {step.agent_type}")
            
            # Get the agent
            agent = self.available_agents.get(step.agent_type)
            if not agent:
                self.logger.warning(f"Agent {step.agent_type} not available, skipping")
                continue
            
            try:
                # Initialize agent with current context
                await agent.initialize(self.context)
                
                # Execute agent
                result = await agent.execute(current_context)
                results.append({
                    "agent": step.agent_type,
                    "result": result.content,
                    "metadata": result.metadata
                })
                
                # Update context for next agent
                current_context = f"{current_context}\n\nPrevious analysis: {result.content}"
                
            except Exception as e:
                self.logger.error(f"Error executing agent {step.agent_type}: {e}")
                results.append({
                    "agent": step.agent_type,
                    "error": str(e)
                })
        
        # Synthesize final response
        final_response = await self._synthesize_results(results, original_message.content)
        
        return AgentMessage(
            content=final_response,
            message_type="assistant",
            metadata={
                "execution_plan": [step.agent_type for step in plan],
                "agent_results": len(results),
                "master_planner": True
            }
        )
    
    async def _synthesize_results(self, results: List[Dict[str, Any]], original_query: str) -> str:
        """Synthesize results from multiple agents into a coherent response"""
        if not results:
            return "I wasn't able to process your request with the available agents."
        
        # Filter out error results
        successful_results = [r for r in results if "error" not in r]
        
        if not successful_results:
            return "I encountered some issues while processing your request. Please try rephrasing your question."
        
        if len(successful_results) == 1:
            # Single agent result
            return successful_results[0]["result"]
        
        # Multiple agent results - create comprehensive response
        synthesis = "Based on my analysis using multiple specialized agents, here's what I found:\n\n"
        
        for i, result in enumerate(successful_results, 1):
            agent_name = result["agent"].replace("_", " ").title()
            synthesis += f"**{agent_name} Analysis:**\n"
            synthesis += f"{result['result']}\n\n"
        
        synthesis += "**Summary:**\n"
        synthesis += "I've coordinated multiple specialized agents to provide you with comprehensive insights. "
        synthesis += "Each analysis complements the others to give you a well-rounded perspective on your financial question."
        
        return synthesis
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status"""
        return {
            "available_agents": list(self.available_agents.keys()),
            "agent_count": len(self.available_agents),
            "supported_patterns": list(self.task_patterns.keys()),
            "master_planner_status": self.status.value
        } 