from fingenius.tools.calculators import CALCULATOR_TOOLS
from fingenius.tools.knowledge_tool import financial_knowledge_lookup
from fingenius.tools.transaction_tools import (
    categorize_transaction,
    find_similar_transactions,
)

# All tools the agent can call.
ALL_TOOLS = [
    *CALCULATOR_TOOLS,
    financial_knowledge_lookup,
    categorize_transaction,
    find_similar_transactions,
]

__all__ = [
    "ALL_TOOLS",
    "CALCULATOR_TOOLS",
    "financial_knowledge_lookup",
    "categorize_transaction",
    "find_similar_transactions",
]
