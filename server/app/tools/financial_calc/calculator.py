import math
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
import numpy as np

from app.tools.base import ComputationTool, ToolResult

@dataclass
class FinancialCalculationResult:
    """Result of a financial calculation"""
    calculation_type: str
    inputs: Dict[str, Any]
    result: Union[float, Dict[str, float]]
    explanation: str
    assumptions: List[str]

class FinancialCalculatorTool(ComputationTool):
    """
    Financial Calculator Tool for various financial computations
    Supports portfolio optimization, retirement planning, loan calculations, etc.
    """
    
    def __init__(self):
        super().__init__(
            tool_id="financial_calculator",
            name="Financial Calculator",
            description="Perform various financial calculations including portfolio optimization, retirement planning, loan calculations, and investment analysis",
            timeout_seconds=10
        )
    
    async def _compute(self, calculation_type: str, **kwargs) -> ToolResult:
        """Perform financial calculation based on type"""
        try:
            if calculation_type == "compound_interest":
                result = self._calculate_compound_interest(**kwargs)
            elif calculation_type == "retirement_savings":
                result = self._calculate_retirement_savings(**kwargs)
            elif calculation_type == "loan_payment":
                result = self._calculate_loan_payment(**kwargs)
            elif calculation_type == "portfolio_return":
                result = self._calculate_portfolio_return(**kwargs)
            elif calculation_type == "risk_metrics":
                result = self._calculate_risk_metrics(**kwargs)
            elif calculation_type == "asset_allocation":
                result = self._calculate_asset_allocation(**kwargs)
            elif calculation_type == "emergency_fund":
                result = self._calculate_emergency_fund(**kwargs)
            elif calculation_type == "debt_payoff":
                result = self._calculate_debt_payoff(**kwargs)
            elif calculation_type == "investment_growth":
                result = self._calculate_investment_growth(**kwargs)
            elif calculation_type == "tax_efficiency":
                result = self._calculate_tax_efficiency(**kwargs)
            else:
                raise ValueError(f"Unknown calculation type: {calculation_type}")
            
            return ToolResult(
                success=True,
                data=result,
                metadata={
                    "calculation_type": calculation_type,
                    "inputs": kwargs
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Calculation failed: {str(e)}",
                metadata={"calculation_type": calculation_type}
            )
    
    def _calculate_compound_interest(
        self,
        principal: float,
        annual_rate: float,
        years: int,
        compounds_per_year: int = 12
    ) -> FinancialCalculationResult:
        """Calculate compound interest"""
        
        # Convert percentage to decimal if needed
        if annual_rate > 1:
            annual_rate = annual_rate / 100
        
        # Calculate compound interest
        amount = principal * (1 + annual_rate / compounds_per_year) ** (compounds_per_year * years)
        interest_earned = amount - principal
        
        # Calculate year-by-year breakdown
        yearly_breakdown = []
        for year in range(1, years + 1):
            year_amount = principal * (1 + annual_rate / compounds_per_year) ** (compounds_per_year * year)
            yearly_breakdown.append({
                "year": year,
                "balance": round(year_amount, 2),
                "interest_earned": round(year_amount - principal, 2)
            })
        
        return FinancialCalculationResult(
            calculation_type="compound_interest",
            inputs={
                "principal": principal,
                "annual_rate": annual_rate * 100,
                "years": years,
                "compounds_per_year": compounds_per_year
            },
            result={
                "final_amount": round(amount, 2),
                "total_interest": round(interest_earned, 2),
                "effective_annual_rate": round(((amount / principal) ** (1/years) - 1) * 100, 2),
                "yearly_breakdown": yearly_breakdown
            },
            explanation=f"With compound interest, ${principal:,.2f} grows to ${amount:,.2f} over {years} years at {annual_rate*100:.1f}% annual rate.",
            assumptions=[
                f"Interest compounds {compounds_per_year} times per year",
                "No additional contributions",
                "Constant interest rate",
                "No taxes or fees considered"
            ]
        )
    
    def _calculate_retirement_savings(
        self,
        current_age: int,
        retirement_age: int,
        current_savings: float,
        monthly_contribution: float,
        annual_return: float,
        desired_monthly_income: Optional[float] = None
    ) -> FinancialCalculationResult:
        """Calculate retirement savings projections"""
        
        if annual_return > 1:
            annual_return = annual_return / 100
        
        years_to_retirement = retirement_age - current_age
        monthly_return = annual_return / 12
        months_to_retirement = years_to_retirement * 12
        
        # Future value of current savings
        fv_current = current_savings * (1 + annual_return) ** years_to_retirement
        
        # Future value of monthly contributions
        if monthly_return > 0:
            fv_contributions = monthly_contribution * (
                ((1 + monthly_return) ** months_to_retirement - 1) / monthly_return
            )
        else:
            fv_contributions = monthly_contribution * months_to_retirement
        
        total_retirement_savings = fv_current + fv_contributions
        
        # Calculate sustainable withdrawal rate (4% rule)
        annual_withdrawal_4_percent = total_retirement_savings * 0.04
        monthly_withdrawal_4_percent = annual_withdrawal_4_percent / 12
        
        # Calculate replacement ratio if current income provided
        replacement_ratio = None
        if desired_monthly_income:
            replacement_ratio = (monthly_withdrawal_4_percent / desired_monthly_income) * 100
        
        return FinancialCalculationResult(
            calculation_type="retirement_savings",
            inputs={
                "current_age": current_age,
                "retirement_age": retirement_age,
                "current_savings": current_savings,
                "monthly_contribution": monthly_contribution,
                "annual_return": annual_return * 100
            },
            result={
                "projected_retirement_savings": round(total_retirement_savings, 2),
                "value_of_current_savings": round(fv_current, 2),
                "value_of_contributions": round(fv_contributions, 2),
                "monthly_withdrawal_4_percent": round(monthly_withdrawal_4_percent, 2),
                "annual_withdrawal_4_percent": round(annual_withdrawal_4_percent, 2),
                "replacement_ratio_percent": round(replacement_ratio, 1) if replacement_ratio else None
            },
            explanation=f"By age {retirement_age}, you're projected to have ${total_retirement_savings:,.2f} for retirement.",
            assumptions=[
                f"{annual_return*100:.1f}% average annual return",
                "Consistent monthly contributions",
                "4% safe withdrawal rate in retirement",
                "No employer matching included",
                "Inflation not adjusted"
            ]
        )
    
    def _calculate_loan_payment(
        self,
        loan_amount: float,
        annual_rate: float,
        loan_term_years: int,
        extra_payment: float = 0
    ) -> FinancialCalculationResult:
        """Calculate loan payment and payoff scenarios"""
        
        if annual_rate > 1:
            annual_rate = annual_rate / 100
        
        monthly_rate = annual_rate / 12
        num_payments = loan_term_years * 12
        
        # Calculate monthly payment
        if monthly_rate > 0:
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** num_payments
            ) / ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_payment = loan_amount / num_payments
        
        # Calculate with extra payments
        total_monthly = monthly_payment + extra_payment
        
        # Simulate payoff with extra payments
        balance = loan_amount
        payments_made = 0
        total_interest = 0
        
        while balance > 0.01 and payments_made < num_payments * 2:  # Safety cap
            interest_payment = balance * monthly_rate
            principal_payment = min(total_monthly - interest_payment, balance)
            
            balance -= principal_payment
            total_interest += interest_payment
            payments_made += 1
        
        months_saved = num_payments - payments_made
        years_saved = months_saved / 12
        interest_saved = (monthly_payment * num_payments - loan_amount) - total_interest
        
        return FinancialCalculationResult(
            calculation_type="loan_payment",
            inputs={
                "loan_amount": loan_amount,
                "annual_rate": annual_rate * 100,
                "loan_term_years": loan_term_years,
                "extra_payment": extra_payment
            },
            result={
                "monthly_payment": round(monthly_payment, 2),
                "total_monthly_with_extra": round(total_monthly, 2),
                "total_interest_without_extra": round(monthly_payment * num_payments - loan_amount, 2),
                "total_interest_with_extra": round(total_interest, 2),
                "interest_saved": round(interest_saved, 2),
                "months_saved": round(months_saved, 1),
                "years_saved": round(years_saved, 1),
                "payoff_time_with_extra": round(payments_made / 12, 1)
            },
            explanation=f"Monthly payment is ${monthly_payment:,.2f}. With ${extra_payment:,.2f} extra monthly, save ${interest_saved:,.2f} in interest.",
            assumptions=[
                "Fixed interest rate",
                "No prepayment penalties",
                "Extra payments applied to principal",
                "Consistent payment schedule"
            ]
        )
    
    def _calculate_portfolio_return(
        self,
        allocations: Dict[str, float],
        expected_returns: Dict[str, float],
        volatilities: Dict[str, float],
        correlations: Optional[Dict[str, Dict[str, float]]] = None
    ) -> FinancialCalculationResult:
        """Calculate portfolio expected return and risk"""
        
        # Ensure allocations sum to 100%
        total_allocation = sum(allocations.values())
        if abs(total_allocation - 1.0) > 0.01 and abs(total_allocation - 100.0) > 1.0:
            raise ValueError("Allocations must sum to 100% (or 1.0)")
        
        # Normalize allocations if they're in percentage form
        if total_allocation > 1.5:
            allocations = {k: v/100 for k, v in allocations.items()}
        
        # Calculate expected portfolio return
        portfolio_return = sum(
            allocations[asset] * expected_returns[asset] for asset in allocations
        )
        
        # Calculate portfolio variance (simplified - assumes uncorrelated if no correlation matrix)
        portfolio_variance = sum(
            (allocations[asset] ** 2) * (volatilities[asset] ** 2) for asset in allocations
        )
        
        portfolio_volatility = math.sqrt(portfolio_variance)
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return FinancialCalculationResult(
            calculation_type="portfolio_return",
            inputs={
                "allocations": allocations,
                "expected_returns": expected_returns,
                "volatilities": volatilities
            },
            result={
                "expected_annual_return": round(portfolio_return * 100, 2),
                "annual_volatility": round(portfolio_volatility * 100, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "risk_return_ratio": round(portfolio_return / portfolio_volatility, 2) if portfolio_volatility > 0 else None
            },
            explanation=f"Portfolio expected return: {portfolio_return*100:.1f}% with {portfolio_volatility*100:.1f}% volatility.",
            assumptions=[
                "Expected returns are annual",
                "Assets uncorrelated (unless correlation matrix provided)",
                "Normal distribution of returns",
                "Constant volatility"
            ]
        )
    
    def _calculate_emergency_fund(
        self,
        monthly_expenses: float,
        months_coverage: int = 6,
        current_savings: float = 0,
        monthly_savings: float = 0
    ) -> FinancialCalculationResult:
        """Calculate emergency fund requirements"""
        
        target_amount = monthly_expenses * months_coverage
        shortfall = target_amount - current_savings
        
        if monthly_savings > 0:
            months_to_target = max(0, shortfall / monthly_savings)
        else:
            months_to_target = float('inf') if shortfall > 0 else 0
        
        return FinancialCalculationResult(
            calculation_type="emergency_fund",
            inputs={
                "monthly_expenses": monthly_expenses,
                "months_coverage": months_coverage,
                "current_savings": current_savings,
                "monthly_savings": monthly_savings
            },
            result={
                "target_emergency_fund": round(target_amount, 2),
                "current_coverage_months": round(current_savings / monthly_expenses, 1) if monthly_expenses > 0 else 0,
                "shortfall": round(max(0, shortfall), 2),
                "months_to_target": round(months_to_target, 1) if months_to_target != float('inf') else None,
                "years_to_target": round(months_to_target / 12, 1) if months_to_target != float('inf') else None
            },
            explanation=f"Target emergency fund: ${target_amount:,.2f} ({months_coverage} months of expenses).",
            assumptions=[
                f"{months_coverage} months of expenses recommended",
                "Consistent monthly expenses",
                "Emergency fund in liquid savings",
                "No investment growth considered"
            ]
        )
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Define parameter schema"""
        return {
            "type": "object",
            "properties": {
                "calculation_type": {
                    "type": "string",
                    "enum": [
                        "compound_interest", "retirement_savings", "loan_payment",
                        "portfolio_return", "risk_metrics", "asset_allocation",
                        "emergency_fund", "debt_payoff", "investment_growth", "tax_efficiency"
                    ],
                    "description": "Type of financial calculation to perform"
                }
            },
            "required": ["calculation_type"],
            "additionalProperties": True
        } 