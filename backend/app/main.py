"""
FastAPI backend - wraps the multi-agent LangGraph (researcher + budget)
as a web API, plus a standalone currency conversion endpoint.

Run (from project ROOT folder):
    py -m uvicorn backend.app.main:app --reload --port 8000
"""

import sys
import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    return {"answer": result["final_answer"], "total_cost_usd": result["total_cost_usd"]}


class ConvertRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


@app.post("/convert-currency")
async def convert_currency(req: ConvertRequest):
    """
    Direct currency conversion - NOT routed through the LangGraph agent.
    Called only when the user clicks the convert button on the results screen.
    Uses the same Frankfurter API logic as the currency_server MCP tool,
    called directly here to avoid subprocess overhead for a simple button click.
    """
    from_curr = req.from_currency.upper()
    to_curr = req.to_currency.upper()

    resp = requests.get(
        f"https://api.frankfurter.dev/v2/rate/{from_curr}/{to_curr}",
        timeout=10,
    )

    if resp.status_code >= 400:
        return {"error": f"API error {resp.status_code}"}

    data = resp.json()
    rate = data.get("rate")

    if rate is None:
        return {"error": f"Could not find rate for {from_curr} -> {to_curr}"}

    converted = req.amount * rate
    return {
        "converted_amount": round(converted, 2),
        "rate": rate,
        "from_currency": from_curr,
        "to_currency": to_curr,
        "date": data.get("date"),
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
