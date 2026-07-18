"""
MCP server exposing a `search_places` tool backed by Geoapify Places API.
No credit card needed - free tier gives 3000 requests/day.

Setup:
    pip install mcp requests python-dotenv
    Get free key at geoapify.com, set GEOAPIFY_API_KEY in your .env

Run:
    python places_server.py
"""

import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

mcp = FastMCP("travel-places")


def geocode_city(city: str):
    """Turn a city name into lat/lon using Geoapify geocoding."""
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": city, "apiKey": GEOAPIFY_API_KEY, "limit": 1}
    resp = requests.get(url, params=params, timeout=10).json()
    features = resp.get("features", [])
    if not features:
        return None
    lon, lat = features[0]["geometry"]["coordinates"]
    return lat, lon


@mcp.tool()
def search_places(city: str, category: str = "tourism.sights") -> str:
    """
    Search for places (attractions, restaurants, hotels) in a city.

    Args:
        city: e.g. "Istanbul, Turkey"
        category: Geoapify category, common ones:
            tourism.sights (attractions), catering.restaurant (food),
            accommodation.hotel (hotels)

    Returns:
        A formatted string list of place names and addresses.
    """
    if not GEOAPIFY_API_KEY:
        return "ERROR: GEOAPIFY_API_KEY not set in .env"

    coords = geocode_city(city)
    if not coords:
        return f"Could not find location: {city}"
    lat, lon = coords

    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": category,
        "filter": f"circle:{lon},{lat},10000",  # 10km radius
        "limit": 10,
        "apiKey": GEOAPIFY_API_KEY,
    }
    resp = requests.get(url, params=params, timeout=10).json()
    features = resp.get("features", [])

    if not features:
        return "No places found."

    lines = []
    for f in features:
        props = f.get("properties", {})
        name = props.get("name", "Unknown")
        address = props.get("formatted", "")
        lines.append(f"- {name} — {address}")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()