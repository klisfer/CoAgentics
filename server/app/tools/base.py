import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
import time

logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    """Standardized result format for tool execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    tool_name: Optional[str] = None

class BaseTool(ABC):
    """Base class for all tools in the CoAgentics system"""
    
    def __init__(
        self,
        tool_id: str,
        name: str,
        description: str,
        version: str = "1.0.0",
        timeout_seconds: int = 30
    ):
        self.tool_id = tool_id
        self.name = name
        self.description = description
        self.version = version
        self.timeout_seconds = timeout_seconds
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the tool - override in subclasses"""
        try:
            await self._initialize_internal()
            self._initialized = True
            self.logger.info(f"Tool {self.name} initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize tool {self.name}: {e}")
            return False
    
    async def _initialize_internal(self):
        """Override in subclasses for custom initialization"""
        pass
    
    async def execute_async(self, **kwargs) -> ToolResult:
        """Asynchronous execution wrapper"""
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._execute_internal(**kwargs),
                timeout=self.timeout_seconds
            )
            
            execution_time = time.time() - start_time
            
            if isinstance(result, ToolResult):
                result.execution_time = execution_time
                result.tool_name = self.name
                return result
            else:
                # Convert result to ToolResult
                return ToolResult(
                    success=True,
                    data=result,
                    execution_time=execution_time,
                    tool_name=self.name
                )
                
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tool {self.name} timed out after {self.timeout_seconds} seconds"
            self.logger.error(error_msg)
            return ToolResult(
                success=False,
                error=error_msg,
                execution_time=execution_time,
                tool_name=self.name
            )
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tool {self.name} error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return ToolResult(
                success=False,
                error=error_msg,
                execution_time=execution_time,
                tool_name=self.name
            )
    
    def execute(self, **kwargs) -> ToolResult:
        """Synchronous execution wrapper"""
        return asyncio.run(self.execute_async(**kwargs))
    
    @abstractmethod
    async def _execute_internal(self, **kwargs) -> Union[Any, ToolResult]:
        """Internal execution logic - must be implemented by subclasses"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for documentation and validation"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "parameters": self._get_parameters_schema(),
            "return_type": self._get_return_schema()
        }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Override in subclasses to define parameter schema"""
        return {}
    
    def _get_return_schema(self) -> Dict[str, Any]:
        """Override in subclasses to define return schema"""
        return {"type": "object"}
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters - override in subclasses"""
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "initialized": self._initialized,
            "timeout_seconds": self.timeout_seconds
        }

class APIBasedTool(BaseTool):
    """Base class for tools that interact with external APIs"""
    
    def __init__(self, *args, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = api_key
        self.base_url = base_url
        self._session = None
    
    async def _initialize_internal(self):
        """Initialize API session"""
        import aiohttp
        self._session = aiohttp.ClientSession()
        
        # Test API connection if test endpoint available
        if hasattr(self, '_test_connection'):
            await self._test_connection()
    
    async def _test_connection(self):
        """Override in subclasses to test API connection"""
        pass
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        if not self._session:
            raise RuntimeError("Tool not properly initialized - session not available")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint
        
        # Add authentication if API key is provided
        headers = kwargs.get('headers', {})
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
        kwargs['headers'] = headers
        
        async with self._session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self._session:
            await self._session.close()

class ComputationTool(BaseTool):
    """Base class for tools that perform computations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_enabled = kwargs.get('cache_enabled', True)
        self._cache: Dict[str, Any] = {}
    
    def _get_cache_key(self, **kwargs) -> str:
        """Generate cache key from parameters"""
        import hashlib
        import json
        
        # Sort parameters for consistent hashing
        sorted_params = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(sorted_params.encode()).hexdigest()
    
    async def _execute_internal(self, **kwargs) -> Union[Any, ToolResult]:
        """Execute with caching support"""
        if self.cache_enabled:
            cache_key = self._get_cache_key(**kwargs)
            if cache_key in self._cache:
                self.logger.debug(f"Cache hit for {self.name}")
                return self._cache[cache_key]
        
        result = await self._compute(**kwargs)
        
        if self.cache_enabled and cache_key:
            self._cache[cache_key] = result
        
        return result
    
    @abstractmethod
    async def _compute(self, **kwargs) -> Union[Any, ToolResult]:
        """Perform the actual computation - must be implemented by subclasses"""
        pass
    
    def clear_cache(self):
        """Clear the computation cache"""
        self._cache.clear()
        self.logger.info(f"Cache cleared for {self.name}") 