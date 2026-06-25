"""Capability 5 - Agents with LangGraph.

The conversational financial advisor. We use LangGraph's prebuilt ReAct agent,
which wires the LLM to the financial tools (calculators + RAG knowledge lookup)
and runs the reason -> act -> observe loop. A MemorySaver checkpointer gives
the agent stateful, multi-turn conversations per `thread_id`.
"""

from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from fingenius.config import get_llm
from fingenius.tools import ALL_TOOLS

SYSTEM_PROMPT = (
    "You are FinGenius, a friendly and knowledgeable personal finance advisor.\n"
    "- Use the financial_knowledge_lookup tool for advice questions so your "
    "guidance is grounded in established best practices.\n"
    "- Use the calculator tools for any budgeting, loan, debt, emergency-fund, "
    "or investment math instead of computing it yourself.\n"
    "- Explain results clearly and in plain language. Format money with a $ and "
    "two decimals. Keep answers concise and actionable.\n"
    "- You are an educational tool, not a licensed financial advisor; remind the "
    "user to consult a professional for major decisions when appropriate."
)


@lru_cache(maxsize=1)
def build_agent():
    """Build (and cache) the LangGraph financial advisor agent."""
    return create_react_agent(
        model=get_llm(),
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),
    )


def chat(message: str, thread_id: str = "default") -> str:
    """Send one user message to the agent and return its text reply.

    Conversation state is kept per `thread_id`, so repeated calls with the same
    id continue the same conversation.
    """
    agent = build_agent()
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke({"messages": [("user", message)]}, config=config)
    return result["messages"][-1].content
