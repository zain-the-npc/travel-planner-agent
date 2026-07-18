"""
Quick standalone test - checks if your Geoapify key works.
Run this directly, no MCP involved. If this prints results, your key is good.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GEOAPIFY_API_KEY")
print(f"Loaded key: {KEY[:8]}..." if KEY else "NO KEY FOUND IN .env")

# Step 1: geocode a city
geo_url = "https://api.geoapify.com/v1/geocode/search"
geo_resp = requests.get(geo_url, params={"text": "Istanbul", "apiKey": KEY, "limit": 1}).json()
print("\n--- Geocode response ---")
print(geo_resp)

features = geo_resp.get("features", [])
if not features:
    print("Geocoding failed - check your key or internet connection.")
    exit()

lon, lat = features[0]["geometry"]["coordinates"]
print(f"\nIstanbul coords: lat={lat}, lon={lon}")

# Step 2: search places
places_url = "https://api.geoapify.com/v2/places"
places_resp = requests.get(places_url, params={
    "categories": "tourism.sights",
    "filter": f"circle:{lon},{lat},10000",
    "limit": 5,
    "apiKey": KEY,
}).json()

print("\n--- Places found ---")
for f in places_resp.get("features", []):
    print("-", f["properties"].get("name", "Unknown"))
