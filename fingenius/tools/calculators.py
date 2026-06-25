"""Capability 4 - Function Calling: financial calculators exposed as LangChain
tools. The original notebook hand-rolled a JSON router to pick a function; with
LangChain tools the LLM selects and fills these automatically via tool calling.
"""

from langchain_core.tools import tool


@tool
def calculate_budget_allocation(monthly_income: float) -> dict:
    """Calculate a 50/30/20 budget (needs/wants/savings) from monthly income."""
    return {
        "needs": monthly_income * 0.5,
        "wants": monthly_income * 0.3,
        "savings": monthly_income * 0.2,
    }


@tool
def calculate_emergency_fund(monthly_expenses: float, months: int = 6) -> dict:
    """Calculate a recommended emergency fund (default 6 months of expenses)."""
    return {"emergency_fund": monthly_expenses * months, "months": months}


@tool
def calculate_debt_payoff(principal: float, annual_interest_rate: float,
                          monthly_payment: float) -> dict:
    """Calculate months to pay off a debt and the total interest paid.

    annual_interest_rate is a percentage, e.g. 18 for 18%.
    """
    monthly_rate = annual_interest_rate / 12 / 100
    remaining = principal
    total_interest = 0.0
    num_payments = 0

    while remaining > 0:
        interest = remaining * monthly_rate
        if monthly_payment <= interest:
            return {"error": "Monthly payment too low to cover interest"}
        principal_payment = min(monthly_payment - interest, remaining)
        remaining -= principal_payment
        total_interest += interest
        num_payments += 1
        if num_payments > 1200:  # 100-year cap
            break

    return {
        "months": num_payments,
        "years": num_payments / 12,
        "total_interest": total_interest,
    }


@tool
def calculate_investment_growth(principal: float, annual_return: float, years: int,
                                monthly_contribution: float = 0) -> dict:
    """Project investment growth with optional monthly contributions.

    annual_return is a percentage, e.g. 8 for 8%.
    """
    monthly_rate = annual_return / 12 / 100
    num_months = int(years * 12)
    value = principal
    for _ in range(num_months):
        value = value * (1 + monthly_rate) + monthly_contribution

    total_contributions = monthly_contribution * num_months
    return {
        "final_value": value,
        "initial_investment": principal,
        "total_contributions": total_contributions,
        "interest_earned": value - principal - total_contributions,
    }


@tool
def calculate_loan_payment(principal: float, annual_interest_rate: float,
                           years: int) -> dict:
    """Calculate the monthly payment and total cost of a fixed-rate loan.

    annual_interest_rate is a percentage, e.g. 4.5 for 4.5%.
    """
    monthly_rate = annual_interest_rate / 12 / 100
    num_payments = years * 12

    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        factor = (1 + monthly_rate) ** num_payments
        monthly_payment = principal * (monthly_rate * factor) / (factor - 1)

    total_cost = monthly_payment * num_payments
    return {
        "monthly_payment": monthly_payment,
        "total_cost": total_cost,
        "total_interest": total_cost - principal,
    }


CALCULATOR_TOOLS = [
    calculate_budget_allocation,
    calculate_emergency_fund,
    calculate_debt_payoff,
    calculate_investment_growth,
    calculate_loan_payment,
]
