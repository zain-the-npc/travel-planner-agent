"""
FastAPI backend - wraps the LangGraph travel agent as a web API.

Run:
    py -m uvicorn backend.app.main:app --reload --port 8000
    (run this from the project ROOT folder, not inside backend/)
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

app = FastAPI(title="Travel Planner Agent API")

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PLACES_SERVER = os.path.join(THIS_DIR, "..", "mcp_servers", "places_server.py")
FLIGHTS_SERVER = os.path.join(THIS_DIR, "..", "mcp_servers", "flights_server.py")

# Built once, reused across requests
_agent = None


async def get_agent():
    global _agent
    if _agent is None:
        client = MultiServerMCPClient(
            {
                "places": {"command": "py", "args": [PLACES_SERVER], "transport": "stdio"},
                "flights": {"command": "py", "args": [FLIGHTS_SERVER], "transport": "stdio"},
            }
        )
        tools = await client.get_tools()
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        _agent = create_react_agent(llm, tools)
    return _agent


class TripRequest(BaseModel):
    origin: str          # e.g. "LHR"
    destination_city: str  # e.g. "Istanbul"
    destination_airport: str  # e.g. "IST"
    departure_date: str  # e.g. "2026-09-15"


@app.post("/plan-trip")
async def plan_trip(req: TripRequest):
    agent = await get_agent()

    prompt = (
        f"Plan a short trip to {req.destination_city}. "
        f"I'm flying from {req.origin} to {req.destination_airport} "
        f"on {req.departure_date}. Give me 3 flight options with prices, "
        f"and 4 attractions to visit. Format clearly with headers."
    )

    result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    answer = result["messages"][-1].content
    return {"answer": answer}


@app.get("/health")
async def health():
    return {"status": "ok"}
