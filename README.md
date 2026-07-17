# AI Travel Planner Agent

Multi-agent system that builds a full trip itinerary (flights, hotels, day-by-day plan, budget) from a single prompt like:
"Plan a 5-day trip to Istanbul in September, budget $800."

## Architecture
- **Planner agent** — breaks the request into subtasks, orchestrates other agents
- **Research agent** — pulls flight/hotel/places data via MCP tools
- **Itinerary agent** — builds day-by-day plan
- **Budget agent** — checks totals against budget, flags overruns

Built with LangGraph (orchestration) + MCP (tool access) + FastAPI (backend) + Postgres (trip history).

## Status
🚧 Week 1: MCP servers for external data (flights/hotels/places)

## Setup
```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
cp .env.example .env       # fill in your API keys
```

## Roadmap
- [ ] Week 1 — MCP servers (places, flights/hotels)
- [ ] Week 2 — LangGraph multi-agent loop (planner + research agent)
- [ ] Week 3 — Budget agent + itinerary formatting
- [ ] Week 4 — Frontend + live agent reasoning trace
- [ ] Week 5 — Deploy (Vercel + Railway), polish, demo video
