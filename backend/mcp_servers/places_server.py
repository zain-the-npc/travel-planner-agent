"""
MCP server exposing a `search_places` tool backed by Google Places API.
This is your Week 1 starting file. Run it, connect it to Claude Desktop
or your own LangGraph agent later, and confirm it works before moving on.

Setup:
    pip install mcp requests python-dotenv
    Set GOOGLE_PLACES_API_KEY in your .env

Run:
    python places_server.py
"""

import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

mcp = FastMCP("travel-places")


@mcp.tool()
def search_places(query: str, location_bias: str = "") -> str:
    """
    Search for places (attractions, restaurants, hotels) matching a query.

    Args:
        query: e.g. "top attractions in Istanbul" or "budget hotels near Sultanahmet"
        location_bias: optional city/region to bias results, e.g. "Istanbul, Turkey"

    Returns:
        A formatted string list of place names, ratings, and addresses.
    """
    if not GOOGLE_PLACES_API_KEY:
        return "ERROR: GOOGLE_PLACES_API_KEY not set in .env"

    full_query = f"{query} {location_bias}".strip()
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": full_query, "key": GOOGLE_PLACES_API_KEY}

    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()

    if data.get("status") != "OK":
        return f"No results or API error: {data.get('status')}"

    results = data.get("results", [])[:8]
    lines = []
    for place in results:
        name = place.get("name", "Unknown")
        rating = place.get("rating", "N/A")
        address = place.get("formatted_address", "")
        lines.append(f"- {name} (rating: {rating}) — {address}")

    return "\n".join(lines) if lines else "No places found."


if __name__ == "__main__":
    mcp.run()
