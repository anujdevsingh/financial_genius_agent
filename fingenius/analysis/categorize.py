"""Capability 1 - Structured Output: transaction categorization.

Uses OpenAI structured output via LangChain's `.with_structured_output()` so the
model returns a validated Pydantic object instead of free-form text we have to
parse by hand (which is what the original notebook did).
"""

import pandas as pd
from pydantic import BaseModel, Field

from fingenius.config import get_llm
from fingenius.data import CATEGORIES

_CATEGORY_NAMES = tuple(CATEGORIES.keys())


class TransactionCategory(BaseModel):
    """Structured result of categorizing a single transaction."""

    category: str = Field(description="The most appropriate category for the transaction.")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in the categorization, 0 to 1."
    )
    reasoning: str = Field(description="Brief explanation for the categorization.")


_SYSTEM = (
    "You are a financial transaction categorizer. Categorize each transaction "
    "into exactly one of these categories: " + ", ".join(_CATEGORY_NAMES) + "."
)


def categorize_transaction(description: str, amount: float) -> TransactionCategory:
    """Categorize a single transaction and return a structured result."""
    llm = get_llm().with_structured_output(TransactionCategory)
    direction = "spent" if amount < 0 else "received"
    user = (
        f"Transaction: {description}\n"
        f"Amount: ${abs(amount):.2f} {direction}\n\n"
        "Categorize it."
    )
    return llm.invoke([("system", _SYSTEM), ("human", user)])


def categorize_dataframe(df: pd.DataFrame, sample_size: int | None = None,
                         random_state: int = 42) -> pd.DataFrame:
    """Categorize transactions in a DataFrame.

    Returns a copy with Predicted_Category, Confidence and Reasoning columns
    (and a Correct column when a ground-truth Category column is present).
    """
    work = df if sample_size is None else df.sample(sample_size, random_state=random_state)
    work = work.copy()

    results = [categorize_transaction(r.Description, r.Amount) for r in work.itertuples()]
    work["Predicted_Category"] = [r.category for r in results]
    work["Confidence"] = [r.confidence for r in results]
    work["Reasoning"] = [r.reasoning for r in results]
    if "Category" in work.columns:
        work["Correct"] = work["Category"] == work["Predicted_Category"]
    return work
