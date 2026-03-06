from __future__ import annotations

import os
import operator
import typing

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END


model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

load_dotenv()

class SupportState(typing.TypedDict):
    messages: typing.Annotated[list[BaseMessage], operator.add]
    should_escalate: bool
    issue_type: str
    user_tier: str  # "vip" or "standard"


def route_by_tier(state: SupportState) -> str:
    """Route based on user tier."""
    if state.get("user_tier") == "vip":
        return "vip_path"
    return "standard_path"


def check_user_tier_node(state: SupportState) -> dict:
    """Decide if user is VIP or standard (mock implementation)."""
    first_message = state["messages"][0].content.lower()
    if "vip" in first_message or "premium" in first_message:
        return {"user_tier": "vip"}
    return {"user_tier": "standard"}


def vip_agent_node(state: SupportState) -> dict:
    """VIP path: fast lane, no escalation."""
    # This demonstrates using a LangChain chat model.
    if os.getenv("OPENAI_API_KEY"):
        model = langchain_openai.ChatOpenAI(temperature=0)
        prompt = (
            "You are a VIP support assistant. Respond concisely and professionally "
            "to the user message:\n\n"
            f"{state['messages'][-1].content}"
        )
        try:
            _ = model.generate_messages([langchain_core.messages.HumanMessage(content=prompt)])
        except Exception:
            pass

    return {"should_escalate": False}


def standard_agent_node(state: SupportState) -> dict:
    """Standard path: may escalate."""
    # For demo purposes, we mark escalation as True.
    return {"should_escalate": True}


def build_graph():
    workflow = StateGraph(SupportState)
    workflow.add_node("check_tier", check_user_tier_node)
    workflow.add_node("vip_agent", vip_agent_node)
    workflow.add_node("standard_agent", standard_agent_node)
    workflow.set_entry_point("check_tier")
    workflow.add_conditional_edges(
        "check_tier",
        route_by_tier,
        {
            "vip_path": "vip_agent",
            "standard_path": "standard_agent",
        },
    )
    workflow.add_edge("vip_agent", END)
    workflow.add_edge("standard_agent", END)
    return workflow.compile()


def main() -> None:
    graph = build_graph()

    vip_result = graph.invoke(
        {
            "messages": [HumanMessage(content="I'm a VIP customer, please check my order")],
            "should_escalate": False,
            "issue_type": "",
            "user_tier": "",
        }
    )
    print("VIP result:", vip_result.get("user_tier"), vip_result.get("should_escalate"))

    standard_result = graph.invoke(
        {
            "messages": [HumanMessage(content="Check my order status")],
            "should_escalate": False,
            "issue_type": "",
            "user_tier": "",
        }
    )
    print(
        "Standard result:", standard_result.get("user_tier"), standard_result.get("should_escalate")
    )


if __name__ == "__main__":
    main()