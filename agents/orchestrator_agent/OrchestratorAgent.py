from google.adk.agents import LlmAgent

from utilities.consul_agent import ConsulEnabledAIAgent


class OrchestratorAgent(ConsulEnabledAIAgent):

    def build_agent(self) -> LlmAgent:
        """
        Construct the Gemini-based LlmAgent with tools
        """
        tools = [
            self._list_agents,
            self._agent_skills,
            self._delegate_task,
            self._tell_time
        ]
        # MCP tools are added as MCPToolset instances
        for tool_set in self._remote_mcp_tools.values():
            # Add each MCPToolset to the agent's tools
            tools.append(tool_set)

        ai_agent = LlmAgent(
            model="gemini-1.5-flash-latest",
            name="orchestrator_agent",
            description="Delegates user queries to child A2A agents based on intent.",
            instruction=self._root_instruction,
            tools=tools
        )

        return ai_agent
