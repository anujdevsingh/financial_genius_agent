"""Synthetic transaction data generation (ported from the original notebook).

All data here is fake/sample data for demonstration purposes only.
"""

import datetime
import random

import numpy as np
import pandas as pd

# Categories and the merchants that map to them.
CATEGORIES: dict[str, list[str]] = {
    "Groceries": ["Whole Foods", "Trader Joe's", "Safeway", "Kroger", "Walmart", "Target"],
    "Dining": ["Starbucks", "Chipotle", "McDonald's", "Subway", "Pizza Hut", "Local Restaurant"],
    "Transportation": ["Uber", "Lyft", "Gas Station", "Public Transit", "Car Repair", "Parking"],
    "Shopping": ["Amazon", "Best Buy", "Macy's", "Nike", "Apple Store", "Home Depot"],
    "Entertainment": ["Netflix", "Spotify", "Movie Theater", "Concert Tickets", "Hulu", "Disney+"],
    "Utilities": ["Electric Bill", "Water Bill", "Internet Provider", "Phone Bill", "Gas Bill", "Trash Service"],
    "Housing": ["Rent Payment", "Mortgage Payment", "Home Insurance", "Furniture Store", "Home Repair"],
    "Healthcare": ["Pharmacy", "Doctor Visit", "Dental Checkup", "Health Insurance", "Gym Membership"],
    "Education": ["Tuition", "Textbooks", "Online Course", "School Supplies", "Student Loan Payment"],
    "Income": ["Salary Deposit", "Freelance Payment", "Tax Refund", "Investment Dividend", "Gift"],
}

# Typical (min, max) dollar amount per category.
AMOUNT_RANGES: dict[str, tuple[int, int]] = {
    "Groceries": (30, 200),
    "Dining": (10, 100),
    "Transportation": (5, 150),
    "Shopping": (20, 500),
    "Entertainment": (10, 100),
    "Utilities": (50, 300),
    "Housing": (800, 2500),
    "Healthcare": (20, 500),
    "Education": (50, 1000),
    "Income": (1000, 5000),
}


def generate_transactions(days: int = 90, seed: int = 42) -> pd.DataFrame:
    """Generate a DataFrame of synthetic transactions over the last `days` days.

    Expenses are stored as negative amounts and income as positive, matching
    the original notebook. The returned frame has columns:
    Date, Description, Amount, Category.
    """
    np.random.seed(seed)
    random.seed(seed)

    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    rows = []
    for date in date_range:
        for _ in range(random.randint(1, 5)):
            category = random.choice(list(CATEGORIES.keys()))
            merchant = random.choice(CATEGORIES[category])
            low, high = AMOUNT_RANGES[category]
            amount = round(random.uniform(low, high), 2)
            if category != "Income":
                amount = -amount
            rows.append(
                {"Date": date, "Description": merchant, "Amount": amount, "Category": category}
            )

    df = pd.DataFrame(rows)
    return df.sort_values("Date").reset_index(drop=True)
