"""
LangGraph agent that connects to your two MCP servers (places, flights)
and uses GPT to reason about which tool to call and when.

Setup:
    pip install -r requirements.txt
    Make sure .env has OPENAI_API_KEY, GEOAPIFY_API_KEY, DUFFEL_API_KEY

Run:
    py backend/agents/travel_agent.py
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

# Paths to your two MCP servers (adjust if your folder structure differs)
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PLACES_SERVER = os.path.join(THIS_DIR, "..", "mcp_servers", "places_server.py")
FLIGHTS_SERVER = os.path.join(THIS_DIR, "..", "mcp_servers", "flights_server.py")


async def main():
    # 1. Connect to both MCP servers - this launches them as subprocesses
    #    and exposes their tools (search_places, search_flights) to LangChain
    client = MultiServerMCPClient(
        {
            "places": {
                "command": "py",
                "args": [PLACES_SERVER],
                "transport": "stdio",
            },
            "flights": {
                "command": "py",
                "args": [FLIGHTS_SERVER],
                "transport": "stdio",
            },
        }
    )

    tools = await client.get_tools()
    print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")

    # 2. Set up the brain - GPT-4o-mini is cheap and good enough for this
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 3. Build a ReAct agent - LangGraph's prebuilt loop:
    #    LLM thinks -> picks a tool -> executes -> feeds result back -> repeats
    agent = create_react_agent(llm, tools)

    # 4. Give it a real trip-planning request
    user_request = (
        "Plan a short trip idea for Istanbul. I'm flying from London (LHR) "
        "on 2026-09-15. Tell me 3 flight options and 3 attractions to visit."
    )

    result = await agent.ainvoke({"messages": [{"role": "user", "content": user_request}]})

    # 5. Print the final answer (last message in the conversation)
    final_message = result["messages"][-1]
    print("\n--- AGENT RESPONSE ---")
    print(final_message.content)


if __name__ == "__main__":
    asyncio.run(main())
