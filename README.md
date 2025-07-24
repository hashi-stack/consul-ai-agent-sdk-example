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

# Example Usage
```bash
(.venv) ~/git/consul-ai-agent-sdk-example git:[main]
python3 -m app.cmd.cmd --agent http://13.203.43.193:10002
🔗 A2AClient initialized with URL: http://13.203.43.193:10002

What do you want to send to the agent? (type ':q' or 'quit' to exit): How is the weather in Paris?

📤 Sending JSON-RPC request:
{
  "jsonrpc": "2.0",
  "id": "b37cc6e324914bfc90707670b4c378bc",
  "method": "tasks/send",
  "params": {
    "id": "6820ad6ee8cc4297bc53ed218e52f569",
    "sessionId": "2587f6c0bf264bcf91d247104201b0ec",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "How is the weather in Paris?"
        }
      ]
    },
    "historyLength": null,
    "metadata": null
  }
}

Agent says: The weather in Paris is currently light rain with a temperature of 20.2°C (68.4°F), 78% humidity, and a 6.9 mph wind blowing from the North.


What do you want to send to the agent? (type ':q' or 'quit' to exit): What is exchange rate between USD and INR?

📤 Sending JSON-RPC request:
{
  "jsonrpc": "2.0",
  "id": "2f8c834596864484a0b09a637a563f7c",
  "method": "tasks/send",
  "params": {
    "id": "0dcf3bc6c894458aa3f7458224b7e286",
    "sessionId": "2587f6c0bf264bcf91d247104201b0ec",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "What is exchange rate between USD and INR?"
        }
      ]
    },
    "historyLength": null,
    "metadata": null
  }
}

Agent says: The current exchange rate is 1 USD to 86.39 INR.  This is based on data from July 24, 2025.  Keep in mind that exchange rates constantly change.
```
