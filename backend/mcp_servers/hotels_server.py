"""
MCP server exposing a `search_hotels` tool via StayAPI (Booking.com data).
Self-serve, 50 free requests, no card, no sales call.
"""

import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

STAYAPI_KEY = os.getenv("STAYAPI_KEY")
BASE_URL = "https://api.stayapi.com"
HEADERS = {"x-api-key": STAYAPI_KEY}

mcp = FastMCP("travel-hotels")


def lookup_destination(city: str):
    resp = requests.get(
        f"{BASE_URL}/v1/booking/destinations/lookup",
        headers=HEADERS,
        params={"query": city},
        timeout=10,
    ).json()
    if not resp.get("dest_id"):
        return None, None
    return resp["dest_id"], resp.get("dest_type", "CITY")


@mcp.tool()
def search_hotels(city: str, checkin: str, checkout: str, adults: int = 1) -> str:
    """
    Search for hotels in a city for given check-in/check-out dates.

    Args:
        city: e.g. "Istanbul"
        checkin: YYYY-MM-DD
        checkout: YYYY-MM-DD
        adults: number of guests (default 1)
    """
    if not STAYAPI_KEY:
        return "ERROR: STAYAPI_KEY not set in .env"

    dest_id, dest_type = lookup_destination(city)
    if not dest_id:
        return f"Could not find destination: {city}"

    resp = requests.get(
        f"{BASE_URL}/v1/booking/search",
        headers=HEADERS,
        params={
            "dest_id": dest_id,
            "dest_type": dest_type,
            "checkin": checkin,
            "checkout": checkout,
            "adults": adults,
            "rooms": 1,
        },
        timeout=20,
    )

    if resp.status_code >= 400:
        return f"ERROR {resp.status_code}: {resp.text[:500]}"

    raw = resp.json()
    data = raw.get("data", [])

    # Defensive: handle if 'data' is a dict (e.g. {"hotels": [...]}) instead of a list
    if isinstance(data, dict):
        # try common nested keys
        for key in ("hotels", "results", "items"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            return f"DEBUG - unexpected 'data' shape (dict): {list(data.keys())[:10]}"

    if not isinstance(data, list):
        return f"DEBUG - unexpected 'data' type: {type(data)} -- raw keys: {list(raw.keys())}"

    hotels = data[:5]

    if not hotels:
        return "No hotels found for this destination/dates."

    lines = []
    for h in hotels:
        name = h.get("name", "Unknown hotel")
        stars = h.get("star_rating", "?")

        rating_obj = h.get("rating", {}) or {}
        rating_display = rating_obj.get("display", "N/A")
        rating_score = rating_obj.get("score", "?")

        price_obj = h.get("price", {}) or {}
        price_display = price_obj.get("display", "?")

        lines.append(
            f"- {name} ({stars}-star, {rating_display} {rating_score}/10) — {price_display} for the stay"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
