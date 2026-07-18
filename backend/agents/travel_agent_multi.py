"""
Multi-agent LangGraph: researcher node (3 MCP tools) + budget node.

  researcher   -> calls MCP tools (flights, places, hotels), gathers raw data
  budget_agent -> pure LLM reasoning: checks total cost (flight + hotel + food)
                  against user's budget, flags overruns, suggests cuts

Run:
    py backend/agents/travel_agent_multi.py
"""

import asyncio
import os
from datetime import datetime, timedelta
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
HOTELS_SERVER = os.path.join(THIS_DIR, "..", "mcp_servers", "hotels_server.py")


class TripState(TypedDict):
    origin: str
    destination_city: str
    destination_airport: str
    departure_date: str
    budget: float
    research_output: str
    final_answer: str
    total_cost_usd: float


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
_research_agent = None


async def get_research_agent():
    global _research_agent
    if _research_agent is None:
        client = MultiServerMCPClient(
            {
                "places": {"command": "py", "args": [PLACES_SERVER], "transport": "stdio"},
                "flights": {"command": "py", "args": [FLIGHTS_SERVER], "transport": "stdio"},
                "hotels": {"command": "py", "args": [HOTELS_SERVER], "transport": "stdio"},
            }
        )
        tools = await client.get_tools()
        _research_agent = create_react_agent(llm, tools)
    return _research_agent


def compute_checkout(departure_date: str, nights: int = 4) -> str:
    d = datetime.strptime(departure_date, "%Y-%m-%d")
    return (d + timedelta(days=nights)).strftime("%Y-%m-%d")


async def researcher_node(state: TripState) -> dict:
    agent = await get_research_agent()
    checkout_date = compute_checkout(state["departure_date"])

    prompt = (
        f"Find flight options from {state['origin']} to {state['destination_airport']} "
        f"on {state['departure_date']}. "
        f"Find hotel options in {state['destination_city']} checking in "
        f"{state['departure_date']} and checking out {checkout_date}. "
        f"Find 4 attractions in {state['destination_city']}. "
        f"List raw prices and names clearly for all three."
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    return {"research_output": result["messages"][-1].content}


async def budget_node(state: TripState) -> dict:
    prompt = (
        f"The user's total budget is ${state['budget']}.\n\n"
        f"Here is the research data (flights + hotels + attractions):\n{state['research_output']}\n\n"
        "Task: Pick the cheapest sensible flight AND the cheapest sensible hotel, "
        "add ~$40/day for food+local transport over a 4-day trip, and check if the "
        "total (flight + hotel + food/transport) fits the budget. "
        "If it doesn't fit, say what to cut or suggest cheaper options. "
        "Respond with a clear final itinerary + full budget breakdown, formatted with headers. "
        "On the VERY LAST LINE of your response, output exactly this format with no extra text: "
        "TOTAL_USD: <number>  (just the final total cost in USD as a plain number, no $ sign, no commas)"
    )
    response = await llm.ainvoke(prompt)
    content = response.content

    # Extract the structured total from the last line, then strip it from the displayed text
    total_usd = 0.0
    lines = content.strip().split("\n")
    if lines and lines[-1].strip().startswith("TOTAL_USD:"):
        try:
            total_usd = float(lines[-1].split("TOTAL_USD:")[1].strip())
        except ValueError:
            total_usd = 0.0
        content = "\n".join(lines[:-1]).strip()
    else:
        # Fallback: LLM didn't follow the format - grab the largest $ amount mentioned
        import re
        amounts = re.findall(r"\$?(\d+(?:,\d{3})*(?:\.\d{1,2})?)\s*(?:USD)?", content)
        cleaned = [float(a.replace(",", "")) for a in amounts if a]
        total_usd = max(cleaned) if cleaned else 0.0

    return {"final_answer": content, "total_cost_usd": total_usd}


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
            "budget": 800,
        }
    )
    print("\n--- FINAL ANSWER ---")
    print(result["final_answer"])


if __name__ == "__main__":
    asyncio.run(main())
