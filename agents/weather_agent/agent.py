# =============================================================================
# agents/weather_agent/agent.py
# =============================================================================
# 🎯 Purpose:
# This file defines a WeatherAgent that provides weather information for multiple locations.
# It uses Google's ADK (Agent Development Kit) and Gemini model to respond with weather data.
# =============================================================================


# -----------------------------------------------------------------------------
# 📦 Built-in & External Library Imports
# -----------------------------------------------------------------------------

# 🧠 Gemini-based AI agent provided by Google's ADK
from google.adk.agents.llm_agent import LlmAgent


from google.adk.tools import FunctionTool

# 🔐 Load environment variables (like API keys) from a `.env` file
from dotenv import load_dotenv

from agents.weather_agent.tools.weather_tool import WeatherTool
from utilities.consul_agent import ConsulEnabledAIAgent

load_dotenv()  # Load variables like GOOGLE_API_KEY into the system


# This allows you to keep sensitive data out of your code.


# -----------------------------------------------------------------------------
# ��️ WeatherAgent: AI agent that provides weather information for multiple locations
# -----------------------------------------------------------------------------

class WeatherAgent(ConsulEnabledAIAgent):

    def build_agent(self) -> LlmAgent:
        """
        ⚙️ Creates and configures a Gemini agent with weather capabilities.

        Returns:
            LlmAgent: A configured agent object from Google's ADK
        """
        # Manually adding the WeatherTool to the agent's tools
        tools = [
            FunctionTool(WeatherTool(name="WeatherTool", description="Gets the realtime weather for one or more locations").get_weather)
        ]

        # Automatically add MCP tools as they are registered in Consul and Intentions are defined
        for tool_set in self._remote_mcp_tools.values():
            tools.append(tool_set)

        return LlmAgent(
            model="gemini-1.5-flash-latest",  # Gemini model version
            name="weather_agent",  # Name of the agent
            description="Provides weather information for multiple locations",  # Description for metadata
            instruction="You are a helpful weather assistant. When asked about weather, extract the 'locations' parameter as a list (even for a single location), then use the 'WeatherTool' to provide weather information. When multiple locations are requested, organize your response clearly with headings for each location. Be friendly and informative. If user asks for locations with specific weather conditions, first get weather for several cities in that region, then recommend ones that match the criteria.",
            # System prompt
            tools=tools,
        )