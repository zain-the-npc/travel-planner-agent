"""
MCP server exposing a `convert_currency` tool via Frankfurter API (ECB rates).
No API key needed - completely free, no signup.

Run (for testing via Inspector):
    npx @modelcontextprotocol/inspector py backend/mcp_servers/currency_server.py
"""

import requests
from mcp.server.fastmcp import FastMCP

BASE_URL = "https://api.frankfurter.dev/v2"

mcp = FastMCP("travel-currency")


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert an amount from one currency to another using live ECB rates.

    Args:
        amount: the amount to convert, e.g. 500
        from_currency: 3-letter currency code, e.g. "USD"
        to_currency: 3-letter currency code, e.g. "EUR"

    Returns:
        A formatted string with the converted amount and rate used.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    resp = requests.get(
        f"{BASE_URL}/rates",
        params={"base": from_currency, "quotes": to_currency},
        timeout=10,
    )

    if resp.status_code >= 400:
        return f"ERROR {resp.status_code}: {resp.text[:300]}"

    data = resp.json()
    rate = data.get("rates", {}).get(to_currency)

    if rate is None:
        return f"Could not find rate for {from_currency} -> {to_currency}"

    converted = amount * rate
    return f"{amount} {from_currency} = {converted:.2f} {to_currency} (rate: {rate}, as of {data.get('date')})"


if __name__ == "__main__":
    mcp.run()
