from __future__ import annotations

import os
import operator
import typing

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict, Annotated
import typing, operator, os

# Load environment variables
load_dotenv()

# Initialize the model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Define state schema
class SupportState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    should_escalate: bool
    issue_type: str
    user_tier: str  # "vip" or "standard"

# Routing logic
def route_by_tier(state: SupportState) -> str:
    return "vip_path" if state.get("user_tier") == "vip" else "standard_path"

def check_user_tier_node(state: SupportState) -> dict:
    first_message = state["messages"][0].content.lower()
    if "vip" in first_message or "premium" in first_message:
        return {"user_tier": "vip"}
    return {"user_tier": "standard"}

# VIP agent node
def vip_agent_node(state: SupportState) -> dict:
    prompt = f"You are a VIP support assistant. Respond concisely and professionally to:\n\n{state['messages'][-1].content}"
    response = model.invoke([HumanMessage(content=prompt)])
    print("VIP Agent Response:", response.content)
    return {"should_escalate": False}

# Standard agent node
def standard_agent_node(state: SupportState) -> dict:
    prompt = f"You are a standard support assistant. Respond politely and clearly to:\n\n{state['messages'][-1].content}"
    response = model.invoke([HumanMessage(content=prompt)])
    print("Standard Agent Response:", response.content)
    return {"should_escalate": True}

# Build graph
def build_graph():
    workflow = StateGraph(SupportState)
    workflow.add_node("check_tier", check_user_tier_node)
    workflow.add_node("vip_agent", vip_agent_node)
    workflow.add_node("standard_agent", standard_agent_node)
    workflow.set_entry_point("check_tier")
    workflow.add_conditional_edges(
        "check_tier",
        route_by_tier,
        {"vip_path": "vip_agent", "standard_path": "standard_agent"},
    )
    workflow.add_edge("vip_agent", END)
    workflow.add_edge("standard_agent", END)
    return workflow.compile()

# Main
def main() -> None:
    graph = build_graph()

    vip_result = graph.invoke({
        "messages": [HumanMessage(content="I'm a VIP customer, please check my order")],
        "should_escalate": False,
        "issue_type": "",
        "user_tier": "",
    })
    print("VIP result:", vip_result.get("user_tier"), vip_result.get("should_escalate"))

    standard_result = graph.invoke({
        "messages": [HumanMessage(content="Check my order status")],
        "should_escalate": False,
        "issue_type": "",
        "user_tier": "",
    })
    print("Standard result:", standard_result.get("user_tier"), standard_result.get("should_escalate"))

if __name__ == "__main__":
    main()