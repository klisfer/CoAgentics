import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
from urllib.parse import quote_plus
import json

from app.tools.base import APIBasedTool, ToolResult
from app.core.config import settings

class WebSearchTool(APIBasedTool):
    """
    Web Search Tool for gathering market information and research
    Supports multiple search engines and APIs
    """
    
    def __init__(self, search_engine: str = "serpapi"):
        super().__init__(
            tool_id="web_search",
            name="Web Search Tool",
            description="Search the web for current market information, news, and financial data",
            timeout_seconds=30
        )
        
        self.search_engine = search_engine
        self.api_key = settings.web_search_api_key
        
        # Configure based on search engine
        if search_engine == "serpapi":
            self.base_url = "https://serpapi.com/search"
        elif search_engine == "google_custom":
            self.base_url = "https://www.googleapis.com/customsearch/v1"
        else:
            # Default to a mock search for development
            self.base_url = None
    
    async def _test_connection(self):
        """Test API connection"""
        if not self.api_key and self.search_engine != "mock":
            self.logger.warning(f"No API key provided for {self.search_engine} search")
            return
        
        try:
            # Test with a simple query
            await self._search_internal("test", max_results=1)
            self.logger.info(f"{self.search_engine} search API connection successful")
        except Exception as e:
            self.logger.warning(f"Search API test failed: {e}")
    
    async def _execute_internal(self, query: str, max_results: int = 5, **kwargs) -> ToolResult:
        """Execute web search"""
        try:
            results = await self._search_internal(query, max_results, **kwargs)
            
            return ToolResult(
                success=True,
                data=results,
                metadata={
                    "query": query,
                    "max_results": max_results,
                    "search_engine": self.search_engine,
                    "results_count": len(results.get("results", []))
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}",
                metadata={"query": query, "search_engine": self.search_engine}
            )
    
    async def _search_internal(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        """Internal search implementation"""
        if self.search_engine == "serpapi":
            return await self._serpapi_search(query, max_results, **kwargs)
        elif self.search_engine == "google_custom":
            return await self._google_custom_search(query, max_results, **kwargs)
        else:
            return await self._mock_search(query, max_results, **kwargs)
    
    async def _serpapi_search(self, query: str, max_results: int, **kwargs) -> Dict[str, Any]:
        """Search using SerpAPI"""
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": min(max_results, 10),
            "gl": "us",
            "hl": "en"
        }
        
        # Add financial/market specific parameters
        if any(term in query.lower() for term in ["stock", "market", "finance", "investment"]):
            params["tbm"] = "nws"  # News search for financial queries
        
        async with self._session.get(self.base_url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            
            return self._format_serpapi_results(data)
    
    async def _google_custom_search(self, query: str, max_results: int, **kwargs) -> Dict[str, Any]:
        """Search using Google Custom Search API"""
        params = {
            "key": self.api_key,
            "cx": kwargs.get("custom_search_engine_id"),  # Need to be configured
            "q": query,
            "num": min(max_results, 10)
        }
        
        async with self._session.get(self.base_url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            
            return self._format_google_results(data)
    
    async def _mock_search(self, query: str, max_results: int, **kwargs) -> Dict[str, Any]:
        """Mock search for development/testing"""
        self.logger.info(f"Mock search for: {query}")
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Generate mock results based on query type
        if "market" in query.lower() or "stock" in query.lower():
            return {
                "search_query": query,
                "results": [
                    {
                        "title": "Current Market Trends and Analysis",
                        "url": "https://example.com/market-analysis",
                        "snippet": "Today's market shows mixed signals with technology stocks leading gains while energy sector faces challenges...",
                        "source": "Financial News"
                    },
                    {
                        "title": "S&P 500 Index Performance",
                        "url": "https://example.com/sp500",
                        "snippet": "The S&P 500 index has shown resilience this quarter with a 3.2% gain driven by strong earnings reports...",
                        "source": "Market Watch"
                    }
                ],
                "total_results": max_results,
                "search_time": 0.5,
                "mock_data": True
            }
        else:
            return {
                "search_query": query,
                "results": [
                    {
                        "title": f"Information about {query}",
                        "url": "https://example.com/info",
                        "snippet": f"Relevant information and insights about {query} from reliable sources...",
                        "source": "General Source"
                    }
                ],
                "total_results": max_results,
                "search_time": 0.5,
                "mock_data": True
            }
    
    def _format_serpapi_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format SerpAPI results"""
        results = []
        
        # Handle organic results
        for item in data.get("organic_results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": item.get("displayed_link", "")
            })
        
        # Handle news results for financial queries
        for item in data.get("news_results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": item.get("source", ""),
                "date": item.get("date", "")
            })
        
        return {
            "search_query": data.get("search_parameters", {}).get("q", ""),
            "results": results,
            "total_results": len(results),
            "search_time": data.get("search_metadata", {}).get("processing_time_ms", 0) / 1000
        }
    
    def _format_google_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format Google Custom Search results"""
        results = []
        
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": item.get("displayLink", "")
            })
        
        return {
            "search_query": data.get("queries", {}).get("request", [{}])[0].get("searchTerms", ""),
            "results": results,
            "total_results": int(data.get("searchInformation", {}).get("totalResults", 0)),
            "search_time": float(data.get("searchInformation", {}).get("searchTime", 0))
        }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Define parameter schema"""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string"
                },
                "max_results": {
                    "type": "integer",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20,
                    "description": "Maximum number of search results to return"
                }
            },
            "required": ["query"]
        }
    
    def _get_return_schema(self) -> Dict[str, Any]:
        """Define return schema"""
        return {
            "type": "object",
            "properties": {
                "search_query": {"type": "string"},
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "url": {"type": "string"},
                            "snippet": {"type": "string"},
                            "source": {"type": "string"}
                        }
                    }
                },
                "total_results": {"type": "integer"},
                "search_time": {"type": "number"}
            }
        }
    
    async def search_financial_news(self, query: str, max_results: int = 5) -> ToolResult:
        """Specialized method for financial news search"""
        financial_query = f"{query} finance market news"
        return await self.execute_async(query=financial_query, max_results=max_results)
    
    async def search_market_data(self, symbol: str, max_results: int = 3) -> ToolResult:
        """Specialized method for market data search"""
        market_query = f"{symbol} stock price market analysis"
        return await self.execute_async(query=market_query, max_results=max_results)
    
    async def search_company_info(self, company: str, max_results: int = 5) -> ToolResult:
        """Specialized method for company information search"""
        company_query = f"{company} company financial information investor relations"
        return await self.execute_async(query=company_query, max_results=max_results) 