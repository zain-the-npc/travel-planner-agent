"""
FastAPI backend - wraps the multi-agent LangGraph (researcher + budget)
as a web API.

Run (from project ROOT folder):
    py -m uvicorn backend.app.main:app --reload --port 8000
"""

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Allow importing from backend/agents/
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agents"))
from travel_agent_multi import build_graph  # noqa: E402

app = FastAPI(title="Travel Planner Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


class TripRequest(BaseModel):
    origin: str
    destination_city: str
    destination_airport: str
    departure_date: str
    budget: float


@app.post("/plan-trip")
async def plan_trip(req: TripRequest):
    graph = get_graph()
    result = await graph.ainvoke(
        {
            "origin": req.origin,
            "destination_city": req.destination_city,
            "destination_airport": req.destination_airport,
            "departure_date": req.departure_date,
            "budget": req.budget,
        }
    )
    return {"answer": result["final_answer"]}


@app.get("/health")
async def health():
    return {"status": "ok"}
