"""
MCP server exposing a `search_flights` tool backed by Duffel API (test mode).

Setup:
    pip install mcp requests python-dotenv
    Set DUFFEL_API_KEY in your .env (the duffel_test_... token)

Run (for direct testing via Inspector):
    npx @modelcontextprotocol/inspector py backend/mcp_servers/flights_server.py
"""

import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

DUFFEL_API_KEY = os.getenv("DUFFEL_API_KEY")
BASE_URL = "https://api.duffel.com"

HEADERS = {
    "Authorization": f"Bearer {DUFFEL_API_KEY}",
    "Duffel-Version": "v2",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

mcp = FastMCP("travel-flights")


@mcp.tool()
def search_flights(origin: str, destination: str, departure_date: str, adults: int = 1) -> str:
    """
    Search for flight offers between two airports on a given date.

    Args:
        origin: 3-letter IATA airport code, e.g. "IST" (Istanbul)
        destination: 3-letter IATA airport code, e.g. "LHR" (London Heathrow)
        departure_date: date in YYYY-MM-DD format
        adults: number of adult passengers (default 1)

    Returns:
        A formatted string list of flight offers with airline, price, and duration.
    """
    if not DUFFEL_API_KEY:
        return "ERROR: DUFFEL_API_KEY not set in .env"

    # Step 1: create an offer request
    payload = {
        "data": {
            "slices": [
                {"origin": origin, "destination": destination, "departure_date": departure_date}
            ],
            "passengers": [{"type": "adult"} for _ in range(adults)],
            "cabin_class": "economy",
        }
    }

    resp = requests.post(
        f"{BASE_URL}/air/offer_requests",
        headers=HEADERS,
        params={"return_offers": "true"},
        json=payload,
        timeout=20,
    )

    if resp.status_code >= 400:
        return f"ERROR {resp.status_code}: {resp.text[:500]}"

    data = resp.json().get("data", {})
    offers = data.get("offers", [])[:5]

    if not offers:
        return "No flight offers found for this route/date."

    lines = []
    for offer in offers:
        airline = offer.get("owner", {}).get("name", "Unknown airline")
        price = offer.get("total_amount", "?")
        currency = offer.get("total_currency", "")
        slices = offer.get("slices", [])
        duration = slices[0].get("duration", "N/A") if slices else "N/A"
        lines.append(f"- {airline}: {price} {currency} (duration: {duration})")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
