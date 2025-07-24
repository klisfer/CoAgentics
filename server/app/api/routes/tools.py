from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from app.tools.web_search.web_search_tool import WebSearchTool
from app.tools.financial_calc.calculator import FinancialCalculatorTool
from app.api.dependencies.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tools", tags=["tools"])

# Pydantic models for requests
class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 5

class FinancialCalculationRequest(BaseModel):
    calculation_type: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    tool_name: str

@router.post("/web-search", response_model=ToolResponse)
async def web_search(
    request: WebSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Perform web search using the integrated search tool"""
    try:
        # Initialize web search tool (using mock by default for development)
        search_tool = WebSearchTool(search_engine="mock")
        await search_tool.initialize()
        
        # Execute search
        result = await search_tool.execute_async(
            query=request.query,
            max_results=request.max_results
        )
        
        return ToolResponse(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time,
            tool_name=result.tool_name or "web_search"
        )
        
    except Exception as e:
        logger.error(f"Web search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Web search failed: {str(e)}"
        )

@router.post("/financial-search")
async def financial_search(
    request: WebSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Perform financial-specific web search"""
    try:
        search_tool = WebSearchTool(search_engine="mock")
        await search_tool.initialize()
        
        result = await search_tool.search_financial_news(
            query=request.query,
            max_results=request.max_results
        )
        
        return ToolResponse(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time,
            tool_name=result.tool_name or "financial_search"
        )
        
    except Exception as e:
        logger.error(f"Financial search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Financial search failed: {str(e)}"
        )

@router.post("/calculate", response_model=ToolResponse)
async def financial_calculation(
    request: FinancialCalculationRequest,
    current_user: User = Depends(get_current_user)
):
    """Perform financial calculations"""
    try:
        calculator = FinancialCalculatorTool()
        await calculator.initialize()
        
        # Execute calculation
        result = await calculator.execute_async(
            calculation_type=request.calculation_type,
            **request.parameters
        )
        
        return ToolResponse(
            success=result.success,
            data=result.data,
            error=result.error,
            execution_time=result.execution_time,
            tool_name=result.tool_name or "financial_calculator"
        )
        
    except Exception as e:
        logger.error(f"Financial calculation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Calculation failed: {str(e)}"
        )

@router.get("/calculate/types")
async def get_calculation_types(current_user: User = Depends(get_current_user)):
    """Get available calculation types"""
    return {
        "calculation_types": [
            {
                "type": "compound_interest",
                "name": "Compound Interest Calculator",
                "description": "Calculate compound interest growth over time",
                "required_params": ["principal", "annual_rate", "years"],
                "optional_params": ["compounds_per_year"]
            },
            {
                "type": "retirement_savings",
                "name": "Retirement Savings Calculator",
                "description": "Project retirement savings based on contributions and returns",
                "required_params": ["current_age", "retirement_age", "current_savings", "monthly_contribution", "annual_return"],
                "optional_params": ["desired_monthly_income"]
            },
            {
                "type": "loan_payment",
                "name": "Loan Payment Calculator",
                "description": "Calculate loan payments and payoff scenarios",
                "required_params": ["loan_amount", "annual_rate", "loan_term_years"],
                "optional_params": ["extra_payment"]
            },
            {
                "type": "portfolio_return",
                "name": "Portfolio Return Calculator",
                "description": "Calculate portfolio expected return and risk",
                "required_params": ["allocations", "expected_returns", "volatilities"],
                "optional_params": ["correlations"]
            },
            {
                "type": "emergency_fund",
                "name": "Emergency Fund Calculator",
                "description": "Calculate emergency fund requirements",
                "required_params": ["monthly_expenses"],
                "optional_params": ["months_coverage", "current_savings", "monthly_savings"]
            }
        ]
    }

@router.post("/calculate/compound-interest")
async def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12,
    current_user: User = Depends(get_current_user)
):
    """Quick compound interest calculation endpoint"""
    try:
        calculator = FinancialCalculatorTool()
        await calculator.initialize()
        
        result = await calculator.execute_async(
            calculation_type="compound_interest",
            principal=principal,
            annual_rate=annual_rate,
            years=years,
            compounds_per_year=compounds_per_year
        )
        
        return result.data if result.success else {"error": result.error}
        
    except Exception as e:
        logger.error(f"Compound interest calculation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Calculation failed: {str(e)}"
        )

@router.post("/calculate/retirement")
async def calculate_retirement_savings(
    current_age: int,
    retirement_age: int,
    current_savings: float,
    monthly_contribution: float,
    annual_return: float,
    desired_monthly_income: Optional[float] = None,
    current_user: User = Depends(get_current_user)
):
    """Quick retirement savings calculation endpoint"""
    try:
        calculator = FinancialCalculatorTool()
        await calculator.initialize()
        
        result = await calculator.execute_async(
            calculation_type="retirement_savings",
            current_age=current_age,
            retirement_age=retirement_age,
            current_savings=current_savings,
            monthly_contribution=monthly_contribution,
            annual_return=annual_return,
            desired_monthly_income=desired_monthly_income
        )
        
        return result.data if result.success else {"error": result.error}
        
    except Exception as e:
        logger.error(f"Retirement calculation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Calculation failed: {str(e)}"
        )

@router.get("/search/market/{symbol}")
async def search_market_data(
    symbol: str,
    max_results: int = 3,
    current_user: User = Depends(get_current_user)
):
    """Search for market data for a specific symbol"""
    try:
        search_tool = WebSearchTool(search_engine="mock")
        await search_tool.initialize()
        
        result = await search_tool.search_market_data(
            symbol=symbol,
            max_results=max_results
        )
        
        return {
            "symbol": symbol,
            "search_results": result.data if result.success else None,
            "error": result.error if not result.success else None
        }
        
    except Exception as e:
        logger.error(f"Market data search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Market search failed: {str(e)}"
        )

@router.get("/tools/status")
async def get_tools_status(current_user: User = Depends(get_current_user)):
    """Get status of all available tools"""
    try:
        # Initialize tools to check status
        web_search = WebSearchTool(search_engine="mock")
        calculator = FinancialCalculatorTool()
        
        web_search_status = await web_search.initialize()
        calculator_status = await calculator.initialize()
        
        return {
            "tools": [
                {
                    "name": "Web Search Tool",
                    "id": "web_search",
                    "status": "available" if web_search_status else "unavailable",
                    "description": "Search the web for financial and market information"
                },
                {
                    "name": "Financial Calculator",
                    "id": "financial_calculator", 
                    "status": "available" if calculator_status else "unavailable",
                    "description": "Perform various financial calculations and analysis"
                }
            ],
            "total_tools": 2,
            "available_tools": sum([web_search_status, calculator_status])
        }
        
    except Exception as e:
        logger.error(f"Error getting tools status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving tools status"
        ) 