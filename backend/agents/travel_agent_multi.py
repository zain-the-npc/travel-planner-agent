"""
Multi-agent LangGraph: two nodes wired explicitly.

  researcher  -> calls MCP tools (flights, places), gathers raw data
  budget_agent -> pure LLM reasoning: checks costs against user's budget,
                  flags overruns, suggests what to cut if needed

This replaces the single ReAct agent with real multi-step orchestration.

Run:
    py backend/agents/travel_agent_multi.py
"""

import asyncio
import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END

load_dotenv()

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PLACES_SERVER = os.path.join(THIS_DIR, "..", "mcp_servers", "places_server.py")
FLIGHTS_SERVER = os.path.join(THIS_DIR, "..", "mcp_servers", "flights_server.py")


# --- Shared state passed between nodes ---
class TripState(TypedDict):
    origin: str
    destination_city: str
    destination_airport: str
    departure_date: str
    budget: float
    research_output: str
    final_answer: str


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
_research_agent = None


async def get_research_agent():
    global _research_agent
    if _research_agent is None:
        client = MultiServerMCPClient(
            {
                "places": {"command": "py", "args": [PLACES_SERVER], "transport": "stdio"},
                "flights": {"command": "py", "args": [FLIGHTS_SERVER], "transport": "stdio"},
            }
        )
        tools = await client.get_tools()
        _research_agent = create_react_agent(llm, tools)
    return _research_agent


# --- Node 1: researcher - calls MCP tools ---
async def researcher_node(state: TripState) -> dict:
    agent = await get_research_agent()
    prompt = (
        f"Find flight options from {state['origin']} to {state['destination_airport']} "
        f"on {state['departure_date']}, and 4 attractions in {state['destination_city']}. "
        f"List raw prices and names clearly."
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    return {"research_output": result["messages"][-1].content}


# --- Node 2: budget agent - pure reasoning, no tools ---
async def budget_node(state: TripState) -> dict:
    prompt = (
        f"The user's total budget is ${state['budget']}.\n\n"
        f"Here is the research data (flights + attractions):\n{state['research_output']}\n\n"
        "Task: Pick the cheapest sensible flight option, estimate ~$40/day for food+local "
        "transport over a 4-day trip, and check if the total fits the budget. "
        "If it doesn't fit, say what to cut or suggest a cheaper flight option. "
        "Respond with a clear final itinerary + budget breakdown, formatted with headers."
    )
    response = await llm.ainvoke(prompt)
    return {"final_answer": response.content}


# --- Build the graph ---
def build_graph():
    graph = StateGraph(TripState)
    graph.add_node("researcher", researcher_node)
    graph.add_node("budget_agent", budget_node)
    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "budget_agent")
    graph.add_edge("budget_agent", END)
    return graph.compile()


async def main():
    app = build_graph()
    result = await app.ainvoke(
        {
            "origin": "LHR",
            "destination_city": "Istanbul",
            "destination_airport": "IST",
            "departure_date": "2026-09-15",
            "budget": 500,
        }
    )
    print("\n--- FINAL ANSWER ---")
    print(result["final_answer"])


if __name__ == "__main__":
    asyncio.run(main())
