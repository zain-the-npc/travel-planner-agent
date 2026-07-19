# AI Travel Planner Agent

A multi-agent system that plans real trips — live flights, hotels, and attractions, checked against your budget, converted to any currency. Built with LangGraph, MCP, and GPT-4o-mini.

## How it works

**MCP** = the tools (flight search, hotel search, places, currency — each its own server, no intelligence, just execution).
**LangGraph** = the orchestrator (decides what step runs next, holds shared state).
**GPT-4o-mini** = the brain (decides which tools to call and reasons over the results).

Two nodes, not one giant agent:
- **Researcher** — calls the MCP tools, gathers real flight/hotel/place data
- **Budget agent** — pure reasoning, no tools. Checks the total against your budget, flags overruns

## Stack

`LangGraph` `MCP` `GPT-4o-mini` `FastAPI` `React + TypeScript` `Tailwind` `Framer Motion`

Data: Duffel (flights), StayAPI (hotels), Geoapify (places), Frankfurter (currency)

## Screenshots

![Landing](./screenshots/ss-1.png)
![Form](./screenshots/ss-2.png)
![Results](./screenshots/ss-3.png)
![Budget + currency](./screenshots/ss-4.png)

## Run it

```bash
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env   # add your API keys
py -m uvicorn backend.app.main:app --reload --port 8000

cd frontend && npm install && npm run dev
```
