import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentMessage:
    """Standardized message format for agent communication"""
    content: str
    message_type: str = "text"  # text, tool_call, tool_result, system
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    agent_id: Optional[str] = None

@dataclass
class AgentContext:
    """Context information for agent execution"""
    user_id: str
    session_id: str
    conversation_history: List[AgentMessage] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    financial_profile: Dict[str, Any] = field(default_factory=dict)
    current_goal: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)

class BaseAgent(ABC):
    """Base class for all AI agents in the CoAgentics system"""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: List[str] = None,
        max_iterations: int = 10,
        timeout_seconds: int = 300
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        
        self.status = AgentStatus.IDLE
        self.current_iteration = 0
        self.start_time: Optional[float] = None
        self.context: Optional[AgentContext] = None
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self, context: AgentContext):
        """Initialize agent with context"""
        self.context = context
        self.status = AgentStatus.IDLE
        self.current_iteration = 0
        self.start_time = None
        await self._on_initialize()
    
    async def _on_initialize(self):
        """Override in subclasses for custom initialization"""
        pass
    
    async def execute(self, message: str, **kwargs) -> AgentMessage:
        """Main execution method for the agent"""
        if not self.context:
            raise ValueError("Agent must be initialized with context before execution")
        
        self.start_time = time.time()
        self.status = AgentStatus.THINKING
        self.current_iteration = 0
        
        try:
            # Create input message
            input_message = AgentMessage(
                content=message,
                message_type="user",
                agent_id=self.agent_id
            )
            
            # Add to conversation history
            self.context.conversation_history.append(input_message)
            
            # Execute the agent logic
            result = await self._execute_internal(input_message, **kwargs)
            
            # Update status
            self.status = AgentStatus.COMPLETED
            
            # Add result to conversation history
            if isinstance(result, AgentMessage):
                result.agent_id = self.agent_id
                self.context.conversation_history.append(result)
                return result
            else:
                # Convert string result to AgentMessage
                response = AgentMessage(
                    content=str(result),
                    message_type="assistant",
                    agent_id=self.agent_id
                )
                self.context.conversation_history.append(response)
                return response
                
        except asyncio.TimeoutError:
            self.status = AgentStatus.ERROR
            error_msg = f"Agent {self.name} timed out after {self.timeout_seconds} seconds"
            self.logger.error(error_msg)
            return AgentMessage(
                content=f"I'm sorry, but I encountered a timeout while processing your request: {error_msg}",
                message_type="error",
                agent_id=self.agent_id
            )
        except Exception as e:
            self.status = AgentStatus.ERROR
            error_msg = f"Agent {self.name} encountered an error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return AgentMessage(
                content=f"I'm sorry, but I encountered an error while processing your request: {str(e)}",
                message_type="error",
                agent_id=self.agent_id
            )
    
    @abstractmethod
    async def _execute_internal(self, message: AgentMessage, **kwargs) -> Union[str, AgentMessage]:
        """Internal execution logic - must be implemented by subclasses"""
        pass
    
    async def can_handle(self, message: str, context: AgentContext) -> bool:
        """Check if this agent can handle the given message"""
        return await self._can_handle_internal(message, context)
    
    async def _can_handle_internal(self, message: str, context: AgentContext) -> bool:
        """Override in subclasses to define handling criteria"""
        return True
    
    def get_execution_time(self) -> Optional[float]:
        """Get current execution time in seconds"""
        if self.start_time:
            return time.time() - self.start_time
        return None
    
    def is_timeout(self) -> bool:
        """Check if agent execution has timed out"""
        execution_time = self.get_execution_time()
        return execution_time is not None and execution_time > self.timeout_seconds
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get current agent status information"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "execution_time": self.get_execution_time(),
            "capabilities": self.capabilities
        }
    
    def reset(self):
        """Reset agent state"""
        self.status = AgentStatus.IDLE
        self.current_iteration = 0
        self.start_time = None

class ToolCapableAgent(BaseAgent):
    """Base class for agents that can use tools"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_tools: Dict[str, Any] = {}
    
    def register_tool(self, tool_name: str, tool_instance):
        """Register a tool with this agent"""
        self.available_tools[tool_name] = tool_instance
        if tool_name not in self.capabilities:
            self.capabilities.append(f"tool:{tool_name}")
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Use a registered tool"""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available to agent {self.name}")
        
        tool = self.available_tools[tool_name]
        self.logger.info(f"Agent {self.name} using tool: {tool_name}")
        
        try:
            if hasattr(tool, 'execute_async'):
                return await tool.execute_async(**kwargs)
            elif hasattr(tool, 'execute'):
                return tool.execute(**kwargs)
            else:
                return await tool(**kwargs)
        except Exception as e:
            self.logger.error(f"Error using tool {tool_name}: {e}")
            raise 