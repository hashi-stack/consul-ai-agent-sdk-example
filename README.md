# consul-ai-agent-sdk-example
The AI agent and MCP server based on hashi-stack/consul-ai-agent-sdk.
The example creates 3 agents and 1 MCP server.

# Setup Instructions
```bash
# Environment setup
python3 -m venv .venv
source .venv/bin/activate
pip install .

# Running the agents
uv run python3 -m agents.orchestrator_agent.entry --host localhost --port 10000
uv run python3 -m agents.weather_agent --host localhost --port 10001
uv run python3 -m agents.travel_agent --host localhost --port 10002
uv run python3 -m mcps.curr.server --host localhost --port 10003

# Running the Client CLI
uv run python3 -m app.cmd.cmd --agent http://localhost:10000
```
