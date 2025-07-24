import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from app.agents.base import BaseAgent, AgentContext, AgentMessage
from app.agents.planning.master_planner import MasterPlannerAgent
from app.agents.financial.financial_assistant import FinancialAssistant
from app.tools.web_search.web_search_tool import WebSearchTool
from app.tools.financial_calc.calculator import FinancialCalculatorTool

logger = logging.getLogger(__name__)

@dataclass
class AgentRegistration:
    """Agent registration information"""
    agent: BaseAgent
    priority: int
    enabled: bool = True

class AgentManager:
    """
    Central agent management service for the CoAgentics system
    Handles agent registration, routing, and orchestration
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentRegistration] = {}
        self.tools: Dict[str, Any] = {}
        self.master_planner: Optional[MasterPlannerAgent] = None
        self._initialized = False
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self):
        """Initialize the agent manager and register all agents"""
        if self._initialized:
            return
        
        try:
            # Initialize tools first
            await self._initialize_tools()
            
            # Register agents
            await self._register_agents()
            
            # Initialize master planner
            await self._initialize_master_planner()
            
            self._initialized = True
            self.logger.info("Agent Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Agent Manager: {e}")
            raise
    
    async def _initialize_tools(self):
        """Initialize all tools"""
        
        # Web Search Tool
        web_search_tool = WebSearchTool(search_engine="mock")  # Use mock for development
        await web_search_tool.initialize()
        self.tools["web_search"] = web_search_tool
        
        # Financial Calculator Tool
        calculator_tool = FinancialCalculatorTool()
        await calculator_tool.initialize()
        self.tools["financial_calculator"] = calculator_tool
        
        self.logger.info(f"Initialized {len(self.tools)} tools")
    
    async def _register_agents(self):
        """Register all available agents"""
        
        # Financial Assistant Agent
        financial_assistant = FinancialAssistant()
        financial_assistant.register_tool("web_search", self.tools["web_search"])
        financial_assistant.register_tool("financial_calculator", self.tools["financial_calculator"])
        
        self.register_agent(financial_assistant, priority=2)
        
        # Additional agents can be registered here
        # research_agent = ResearchAgent()
        # self.register_agent(research_agent, priority=3)
        
        self.logger.info(f"Registered {len(self.agents)} agents")
    
    async def _initialize_master_planner(self):
        """Initialize and configure the master planner"""
        self.master_planner = MasterPlannerAgent()
        
        # Register all agents with the master planner
        for agent_id, registration in self.agents.items():
            if registration.enabled:
                self.master_planner.register_agent(registration.agent)
        
        # Register tools with master planner
        for tool_name, tool in self.tools.items():
            self.master_planner.register_tool(tool_name, tool)
        
        self.logger.info("Master planner initialized and configured")
    
    def register_agent(self, agent: BaseAgent, priority: int = 5, enabled: bool = True):
        """Register an agent with the manager"""
        registration = AgentRegistration(
            agent=agent,
            priority=priority,
            enabled=enabled
        )
        
        self.agents[agent.agent_id] = registration
        self.logger.info(f"Registered agent: {agent.name} (ID: {agent.agent_id})")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        registration = self.agents.get(agent_id)
        return registration.agent if registration and registration.enabled else None
    
    def enable_agent(self, agent_id: str):
        """Enable an agent"""
        if agent_id in self.agents:
            self.agents[agent_id].enabled = True
            self.logger.info(f"Enabled agent: {agent_id}")
    
    def disable_agent(self, agent_id: str):
        """Disable an agent"""
        if agent_id in self.agents:
            self.agents[agent_id].enabled = False
            self.logger.info(f"Disabled agent: {agent_id}")
    
    async def process_message(self, message: str, context: AgentContext) -> AgentMessage:
        """Process a message using the appropriate agent(s)"""
        
        if not self._initialized:
            await self.initialize()
        
        try:
            # If master planner is available, use it for orchestration
            if self.master_planner:
                await self.master_planner.initialize(context)
                response = await self.master_planner.execute(message)
                return response
            
            # Fallback: Find the best single agent
            best_agent = await self._find_best_agent(message, context)
            if best_agent:
                await best_agent.initialize(context)
                response = await best_agent.execute(message)
                return response
            
            # No suitable agent found
            return AgentMessage(
                content="I'm sorry, but I'm not able to handle that request at the moment. Please try rephrasing your question.",
                message_type="error",
                metadata={"error": "no_suitable_agent"}
            )
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)
            return AgentMessage(
                content="I encountered an error while processing your request. Please try again.",
                message_type="error",
                metadata={"error": str(e)}
            )
    
    async def _find_best_agent(self, message: str, context: AgentContext) -> Optional[BaseAgent]:
        """Find the best agent to handle a message"""
        
        suitable_agents = []
        
        # Check which agents can handle the message
        for agent_id, registration in self.agents.items():
            if not registration.enabled:
                continue
            
            try:
                can_handle = await registration.agent.can_handle(message, context)
                if can_handle:
                    suitable_agents.append((registration.agent, registration.priority))
            except Exception as e:
                self.logger.warning(f"Error checking if agent {agent_id} can handle message: {e}")
        
        if not suitable_agents:
            return None
        
        # Sort by priority (lower number = higher priority)
        suitable_agents.sort(key=lambda x: x[1])
        
        return suitable_agents[0][0]
    
    def get_all_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all registered agents"""
        status_list = []
        
        for agent_id, registration in self.agents.items():
            agent_status = registration.agent.get_status_info()
            agent_status.update({
                "enabled": registration.enabled,
                "priority": registration.priority,
                "tools_available": len(getattr(registration.agent, 'available_tools', {}))
            })
            status_list.append(agent_status)
        
        # Add master planner status if available
        if self.master_planner:
            mp_status = self.master_planner.get_status_info()
            mp_status.update({
                "enabled": True,
                "priority": 1,
                "type": "orchestrator",
                "registered_agents": len(self.master_planner.available_agents)
            })
            status_list.insert(0, mp_status)  # Master planner first
        
        return status_list
    
    def get_tools_status(self) -> Dict[str, Any]:
        """Get status of all tools"""
        tools_status = {}
        
        for tool_name, tool in self.tools.items():
            tools_status[tool_name] = {
                "name": tool.name,
                "initialized": getattr(tool, '_initialized', False),
                "version": getattr(tool, 'version', 'unknown'),
                "description": getattr(tool, 'description', '')
            }
        
        return tools_status
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents and tools"""
        
        health_status = {
            "agent_manager": "healthy",
            "agents": {},
            "tools": {},
            "master_planner": "unavailable",
            "total_agents": len(self.agents),
            "enabled_agents": 0,
            "total_tools": len(self.tools)
        }
        
        # Check agents
        for agent_id, registration in self.agents.items():
            if registration.enabled:
                health_status["enabled_agents"] += 1
                health_status["agents"][agent_id] = {
                    "status": registration.agent.status.value,
                    "enabled": True
                }
            else:
                health_status["agents"][agent_id] = {
                    "status": "disabled",
                    "enabled": False
                }
        
        # Check tools
        for tool_name, tool in self.tools.items():
            try:
                # Basic health check - try to get tool info
                tool_info = tool.get_info()
                health_status["tools"][tool_name] = "healthy"
            except Exception as e:
                health_status["tools"][tool_name] = f"error: {str(e)}"
        
        # Check master planner
        if self.master_planner:
            health_status["master_planner"] = "healthy"
        
        return health_status
    
    async def shutdown(self):
        """Shutdown agent manager and cleanup resources"""
        
        self.logger.info("Shutting down Agent Manager")
        
        # Cleanup tools
        for tool_name, tool in self.tools.items():
            try:
                if hasattr(tool, 'cleanup'):
                    await tool.cleanup()
            except Exception as e:
                self.logger.warning(f"Error cleaning up tool {tool_name}: {e}")
        
        # Reset agents
        for agent_id, registration in self.agents.items():
            try:
                registration.agent.reset()
            except Exception as e:
                self.logger.warning(f"Error resetting agent {agent_id}: {e}")
        
        self._initialized = False
        self.logger.info("Agent Manager shutdown complete") 