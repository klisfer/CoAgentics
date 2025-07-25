# backend/tools/financial_calculator.py

def calculate_simple_interest(principal: float, rate: float, time: float) -> float:
    """
    Calculates simple interest given a principal amount, annual interest rate, and time in years.

    Args:
        principal: The initial amount of money.
        rate: The annual interest rate (as a decimal, e.g., 0.05 for 5%).
        time: The time the money is invested or borrowed for, in years.
        
    Returns:
        The calculated simple interest.
    """
    interest = principal * rate * time
    return round(interest, 2) 