import uuid

from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import ToolContext

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
            instruction=self.root_instruction,
            tools=tools
        )

        return ai_agent

    def root_instruction(self, context: ReadonlyContext) -> str:
        """
                System prompt function: returns detailed instruction text for the LLM,
                including which tools it can use and a list of child agents with detailed skills.
                """
        agent_list = "\n".join(f"- {name}" for name in self.connectors)

        # Build a detailed list of agents with their skills, descriptions, tags, instructions, and examples
        agent_skills_list = []
        for name, skills in self.skills.items():
            if not skills:
                agent_skills_list.append(f"- {name}: No specific skills defined")
                continue
            skill_details = []
            for skill in skills:
                skill_name = getattr(skill, 'name', getattr(skill, 'id', str(skill)))
                skill_desc = getattr(skill, 'description', 'No description provided.')
                skill_tags = getattr(skill, 'tags', [])
                skill_instruction = getattr(skill, 'instruction', None)
                skill_example = getattr(skill, 'examples', None)
                tags_str = f" [tags: {', '.join(skill_tags)}]" if skill_tags else ""
                instruction_str = f"\n      Instruction: {skill_instruction}" if skill_instruction else ""
                example_str = f"\n      Example: {skill_example}" if skill_example else ""
                skill_details.append(f"  • {skill_name}:{tags_str}\n    Description: {skill_desc}{instruction_str}{example_str}")
            agent_skills_list.append(f"- {name}:\n" + "\n".join(skill_details))
        agent_skills = "\n".join(agent_skills_list)
        #
        # # Build the list of available tools from the current instance
        # agent_tools_list = []
        # i = 1
        # for tool in self._agent.tools:
        #     if callable(tool):
        #         agent_tools_list.append(f"{i}) {tool.__name__}: {tool.__doc__.strip() if tool.__doc__ else 'No description provided'}\n")
        #         i += 1
        # # for i, mcp_toolset in enumerate(self._remote_mcp_tools.values(), start=i):
        #     # Add MCPToolset tools to the list
        #     if hasattr(mcp_toolset, 'get_tools'):
        #         # tools = await mcp_toolset.get_tools()
        #         # Await the async get_tools() call and get the result
        #         import asyncio
        #         if asyncio.iscoroutinefunction(mcp_toolset.get_tools):
        #             tools = asyncio.run(mcp_toolset.get_tools())
        #         else:
        #             tools = mcp_toolset.get_tools()
        #         for tool in tools:
        #             agent_tools_list.append(f"{i}) {tool.name}: {tool.description or 'No description provided'}\n")

        # agent_tools_list.append(f"{i}) MCPToolset: Provides access to MCP server APIs.\n")

        return (
            "You are an orchestrator agent that routes user queries to specialized child agents.\n\n"
            # "Available tools:\n" + "".join(agent_tools_list) + "\n\n"
            "IMPORTANT GUIDELINES:\n"
            "- If required split the user query into multiple queries curated for each agent. Also do not hesitate to pipe the response of one query into the next task.\n"
            "- Always break down the user query into a chain of thoughts and sub-tasks.\n"
            "- Use pipe_agents() when you need to process a query through multiple agents in sequence, where each agent builds on the previous one's output\n"
            "- If a query requires multiple steps or skills, select and sequence multiple agents as needed.\n"
            "- For complex queries, execute tasks in sequence by invoking the right agent for each sub-task.\n"
            "- Always analyze the user query to determine the best agent(s) to handle it.\n"
            "- If unsure which agent to use, check their skills first.\n"
            "- When a task fails or cannot be completed, always provide a detailed explanation of:\n"
            "- Be specific about missing capabilities - don't just say 'I can't do that', explain exactly what\n"
            "  additional agent, skill, or tool would be needed to complete the task successfully.\n"
            "- Respond directly only for simple greetings or clarification questions.\n\n"
            "Available agents:\n" + agent_list + "\n\n"
            "Agent skills (with descriptions, tags, instructions, and examples):\n" + agent_skills
        )

    # Tool to list all registered child agents
    def _list_agents(self) -> list[str]:
        """
        Tool function: returns the list of child-agent names currently registered.
        Called by the LLM when it wants to discover available agents.
        """
        return list(self.connectors.keys())

    # Tool to delegate a task to a specific child agent
    async def _delegate_task(
            self,
            agent_name: str,
            message: str,
            tool_context: ToolContext
    ) -> str:
        """
        Tool function: forwards the `message` to the specified child agent
        (via its AgentConnector), waits for the response, and returns the
        text of the last reply.
        """
        # Validate agent_name exists
        if agent_name not in self.connectors:
            raise ValueError(f"Unknown agent: {agent_name}")
        connector = self.connectors[agent_name]

        # Ensure session_id persists across tool calls via tool_context.state
        state = tool_context.state
        if "session_id" not in state:
            state["session_id"] = str(uuid.uuid4())
        session_id = state["session_id"]

        # Delegate task asynchronously and await Task result
        child_task = await connector.send_task(message, session_id)

        # Extract text from the last history entry if available
        if child_task.history and len(child_task.history) > 1:
            return child_task.history[-1].parts[0].text
        return ""

    # Tool to get the skills of a specific agent
    def _agent_skills(
            self,
            agent_name: str
    ) -> list:
        """
        Tool function: returns the list of skills available for the specified agent.
        Called by the LLM when it needs to determine which agent has the right capabilities
        for handling a user query.

        Args:
            agent_name: Name of the agent to get skills for

        Returns:
            List of skill objects for the specified agent
        """
        # Validate agent_name exists
        if agent_name not in self.skills:
            raise ValueError(f"Unknown agent: {agent_name}")

        return self.skills[agent_name]

    # Tool to tell the current date and time
    def _tell_time(self) -> str:
        """
        Tool function: returns the current date and time as a string.
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
