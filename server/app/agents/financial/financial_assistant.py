import asyncio
from typing import Dict, Any, List, Optional, Union
import json

from app.agents.base import BaseAgent, ToolCapableAgent, AgentMessage, AgentContext
from app.core.config import settings

class FinancialAssistant(ToolCapableAgent):
    """
    Financial Assistant Agent - Provides general financial advice and analysis
    Based on the CoAgentics architecture diagram
    """
    
    def __init__(self):
        super().__init__(
            agent_id="financial_assistant",
            name="Financial Assistant",
            description="Provides general financial advice, market insights, and basic financial planning",
            capabilities=[
                "financial_advice",
                "market_analysis", 
                "basic_planning",
                "portfolio_review",
                "financial_education"
            ]
        )
        
        # Financial domains this agent handles
        self.financial_domains = [
            "budgeting",
            "savings",
            "basic_investing",
            "debt_management",
            "insurance",
            "financial_planning_basics"
        ]
    
    async def _can_handle_internal(self, message: str, context: AgentContext) -> bool:
        """Check if this agent can handle financial queries"""
        financial_keywords = [
            "budget", "save", "invest", "money", "financial", "finance",
            "debt", "credit", "insurance", "portfolio", "market", "stock",
            "bond", "fund", "expense", "income", "retirement", "401k",
            "ira", "tax", "loan", "mortgage", "emergency fund"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in financial_keywords)
    
    async def _execute_internal(self, message: AgentMessage, **kwargs) -> Union[str, AgentMessage]:
        """Execute financial assistant logic"""
        self.logger.info(f"Financial Assistant processing: {message.content}")
        
        try:
            # Analyze the query type
            query_type = await self._analyze_query_type(message.content)
            
            # Get user financial context
            financial_context = self._get_financial_context()
            
            # Process based on query type
            if query_type == "market_analysis":
                response = await self._handle_market_analysis(message.content, financial_context)
            elif query_type == "portfolio_review":
                response = await self._handle_portfolio_review(message.content, financial_context)
            elif query_type == "budgeting":
                response = await self._handle_budgeting(message.content, financial_context)
            elif query_type == "investment_advice":
                response = await self._handle_investment_advice(message.content, financial_context)
            elif query_type == "debt_management":
                response = await self._handle_debt_management(message.content, financial_context)
            else:
                response = await self._handle_general_financial(message.content, financial_context)
            
            return AgentMessage(
                content=response,
                message_type="assistant",
                metadata={
                    "query_type": query_type,
                    "agent": "financial_assistant",
                    "confidence": 0.8
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in financial assistant: {e}")
            return AgentMessage(
                content="I apologize, but I encountered an issue while processing your financial query. Could you please rephrase your question?",
                message_type="error"
            )
    
    async def _analyze_query_type(self, query: str) -> str:
        """Analyze the type of financial query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["market", "stock", "price", "performance"]):
            return "market_analysis"
        elif any(word in query_lower for word in ["portfolio", "allocation", "diversification"]):
            return "portfolio_review"
        elif any(word in query_lower for word in ["budget", "spending", "expense"]):
            return "budgeting"
        elif any(word in query_lower for word in ["invest", "investment", "buy", "sell"]):
            return "investment_advice"
        elif any(word in query_lower for word in ["debt", "loan", "credit card", "payoff"]):
            return "debt_management"
        else:
            return "general_financial"
    
    def _get_financial_context(self) -> Dict[str, Any]:
        """Get user's financial context from the session"""
        if not self.context:
            return {}
        
        return {
            "risk_tolerance": self.context.financial_profile.get("risk_tolerance", "moderate"),
            "investment_experience": self.context.financial_profile.get("investment_experience", "beginner"),
            "financial_goals": self.context.financial_profile.get("financial_goals", []),
            "age_group": self.context.user_preferences.get("age_group", "unknown"),
            "income_level": self.context.user_preferences.get("income_level", "unknown")
        }
    
    async def _handle_market_analysis(self, query: str, context: Dict[str, Any]) -> str:
        """Handle market analysis queries"""
        # In a real implementation, this would call market data APIs
        # For now, provide educational response
        
        response = """
I can help you understand market trends and analysis. Here are some key points for market analysis:

**Current Market Considerations:**
• Market volatility is normal and expected
• Diversification remains key to managing risk
• Long-term investing typically outperforms market timing
• Economic indicators to watch include inflation, employment, and GDP growth

**Analysis Framework:**
• Fundamental analysis: Company financials and industry trends
• Technical analysis: Price patterns and trading volumes
• Market sentiment: Investor confidence and behavior

Would you like me to focus on a specific market sector or investment type?
"""
        
        # Use web search tool if available
        if "web_search" in self.available_tools:
            try:
                search_results = await self.use_tool("web_search", query=f"current market trends {query}")
                if search_results:
                    response += f"\n\n**Recent Market Data:**\n{search_results}"
            except Exception as e:
                self.logger.warning(f"Web search failed: {e}")
        
        return response
    
    async def _handle_portfolio_review(self, query: str, context: Dict[str, Any]) -> str:
        """Handle portfolio review and allocation advice"""
        risk_tolerance = context.get("risk_tolerance", "moderate")
        
        allocation_suggestions = {
            "conservative": {"stocks": 30, "bonds": 60, "cash": 10},
            "moderate": {"stocks": 60, "bonds": 35, "cash": 5},
            "aggressive": {"stocks": 80, "bonds": 15, "cash": 5}
        }
        
        suggested_allocation = allocation_suggestions.get(risk_tolerance, allocation_suggestions["moderate"])
        
        response = f"""
**Portfolio Review Based on Your {risk_tolerance.title()} Risk Profile:**

**Recommended Asset Allocation:**
• Stocks: {suggested_allocation['stocks']}%
• Bonds: {suggested_allocation['bonds']}%
• Cash/Cash Equivalents: {suggested_allocation['cash']}%

**Portfolio Diversification Tips:**
• Spread investments across different sectors
• Consider both domestic and international exposure
• Include small, mid, and large-cap stocks
• Mix growth and value investments

**Regular Review Schedule:**
• Monthly: Check for major imbalances
• Quarterly: Rebalance if needed
• Annually: Review and adjust strategy

Would you like specific recommendations for any asset class or have questions about rebalancing?
"""
        return response
    
    async def _handle_budgeting(self, query: str, context: Dict[str, Any]) -> str:
        """Handle budgeting and expense management"""
        response = """
**Budgeting Fundamentals:**

**The 50/30/20 Rule:**
• 50% - Needs (housing, utilities, groceries, minimum debt payments)
• 30% - Wants (entertainment, dining out, subscriptions)
• 20% - Savings and debt repayment

**Budgeting Steps:**
1. Track your income and expenses for a month
2. Categorize expenses as needs vs. wants
3. Identify areas where you can cut back
4. Set realistic savings goals
5. Monitor and adjust regularly

**Common Budget Categories:**
• Housing (rent/mortgage, utilities)
• Transportation (car payment, gas, insurance)
• Food (groceries, dining out)
• Healthcare
• Entertainment
• Savings/Emergency Fund
• Debt Repayment

**Tips for Success:**
• Use budgeting apps or spreadsheets
• Review weekly
• Allow for some flexibility
• Celebrate small wins

What specific aspect of budgeting would you like help with?
"""
        return response
    
    async def _handle_investment_advice(self, query: str, context: Dict[str, Any]) -> str:
        """Handle investment advice queries"""
        experience = context.get("investment_experience", "beginner")
        
        if experience == "beginner":
            response = """
**Investment Basics for Beginners:**

**Start Here:**
• Emergency fund first (3-6 months expenses)
• Pay off high-interest debt
• Take advantage of employer 401(k) match
• Consider low-cost index funds

**Investment Accounts:**
• 401(k) - Employer-sponsored retirement
• IRA - Individual retirement account
• Roth IRA - Tax-free growth
• Taxable brokerage account

**Basic Investment Options:**
• Index Funds - Diversified, low fees
• ETFs - Flexible, tradeable
• Target-Date Funds - Auto-adjusting
• Individual stocks - Higher risk/reward

**Key Principles:**
• Start early, even with small amounts
• Diversify your investments
• Keep fees low
• Don't try to time the market
• Stay consistent with contributions

Would you like me to explain any of these concepts in more detail?
"""
        else:
            response = """
**Intermediate Investment Strategies:**

**Portfolio Optimization:**
• Asset allocation based on goals and timeline
• Tax-loss harvesting opportunities
• Rebalancing strategies
• International diversification

**Advanced Options:**
• Sector-specific ETFs
• REITs for real estate exposure
• Individual stock analysis
• Options strategies (for experienced investors)

**Tax Considerations:**
• Traditional vs. Roth contributions
• Asset location strategies
• Tax-efficient fund placement
• Capital gains management

What specific investment strategy or product would you like to explore?
"""
        return response
    
    async def _handle_debt_management(self, query: str, context: Dict[str, Any]) -> str:
        """Handle debt management strategies"""
        response = """
**Debt Management Strategies:**

**Debt Repayment Methods:**

**1. Debt Avalanche:**
• Pay minimums on all debts
• Put extra money toward highest interest rate debt
• Most cost-effective mathematically

**2. Debt Snowball:**
• Pay minimums on all debts
• Put extra money toward smallest balance
• Provides psychological wins

**Debt Consolidation Options:**
• Personal loans with lower interest rates
• Balance transfer credit cards (0% intro APR)
• Home equity loans (if you own a home)

**Credit Card Strategy:**
• Pay more than the minimum
• Avoid new charges while paying off debt
• Consider calling for lower interest rates
• Use automatic payments

**Prevention Tips:**
• Build an emergency fund
• Live below your means
• Track spending regularly
• Avoid lifestyle inflation

**When to Seek Help:**
• Debt exceeds 40% of income
• Only making minimum payments
• Using credit for basic needs
• Consider credit counseling

What type of debt are you primarily dealing with?
"""
        return response
    
    async def _handle_general_financial(self, query: str, context: Dict[str, Any]) -> str:
        """Handle general financial questions"""
        response = """
I'm here to help with your financial questions! I can assist with:

**Financial Planning:**
• Budgeting and expense tracking
• Savings strategies
• Emergency fund planning
• Retirement planning basics

**Investment Guidance:**
• Investment basics and education
• Portfolio allocation advice
• Risk assessment
• Investment account types

**Debt Management:**
• Debt payoff strategies
• Credit improvement
• Loan considerations

**Insurance & Protection:**
• Insurance needs assessment
• Risk management basics

**Tax Planning:**
• Basic tax strategies
• Retirement account tax advantages
• Tax-efficient investing

Could you be more specific about what financial topic you'd like to explore? I'm here to provide personalized advice based on your situation.
"""
        return response 