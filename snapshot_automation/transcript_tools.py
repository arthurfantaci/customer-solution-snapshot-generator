"""LangChain agent system with custom tools for web search and calculations.

This module demonstrates creating a ReAct-style agent using LangChain with:
- Custom tools (web search via Tavily, number multiplication)
- Claude 3.5 Sonnet as the reasoning model
- LangChain's AgentExecutor for tool orchestration

The agent can:
1. Search for company information using Tavily web search API
2. Perform numerical calculations (multiplication example)
3. Chain multiple tool calls together to answer complex queries

Reference: https://python.langchain.com/v0.1/docs/modules/tools/custom_tools/
"""

# Import necessary libraries
import os

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.pydantic_v1 import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import BaseTool


load_dotenv()

# Pydantic models for tool arguments


class SimpleSearchInput(BaseModel):
    """Input schema for simple search tool.

    Attributes:
        query: Search query string to send to Tavily API.
    """

    query: str = Field(description="should be a search query")


class MultiplyNumbersArgs(BaseModel):
    """Input schema for multiply numbers tool.

    Attributes:
        x: First number to multiply.
        y: Second number to multiply.
    """

    x: float = Field(description="First number to multiply")
    y: float = Field(description="Second number to multiply")


# Custom tool with only custom input


class SimpleSearchTool(BaseTool):
    """LangChain tool for web search using Tavily API.

    This tool enables the agent to search the web for information about
    companies, topics, or general queries. It uses Tavily's search API
    which requires a TAVILY_API_KEY environment variable.

    Attributes:
        name: Tool identifier used by the agent ("simple_search").
        description: Natural language description for the LLM to understand
            when to use this tool.
        args_schema: Pydantic model defining the input structure.
    """

    name = "simple_search"
    description = "useful for when you need to answer questions about specific companies or topics"
    args_schema: type[BaseModel] = SimpleSearchInput

    def _run(
        self,
        query: str,
    ) -> str:
        """Execute web search query using Tavily API.

        Args:
            query: Search query string.

        Returns:
            Formatted string with search results from Tavily.

        Example:
            >>> tool = SimpleSearchTool()
            >>> results = tool._run("LangChain latest updates")
            >>> "Search results for:" in results
            True
        """
        from tavily import TavilyClient

        api_key = os.getenv("TAVILY_API_KEY")
        client = TavilyClient(api_key=api_key)
        results = client.search(query=query)
        return f"Search results for: {query}\n\n\n{results}\n"


# Custom tool with custom input and output
class MultiplyNumbersTool(BaseTool):
    """LangChain tool for multiplying two numbers.

    This tool demonstrates a simple calculation capability for the agent.
    It can be used when the LLM needs to perform numerical calculations
    as part of answering a user's query.

    Attributes:
        name: Tool identifier used by the agent ("multiply_numbers").
        description: Natural language description for the LLM to understand
            when to use this tool.
        args_schema: Pydantic model defining the input structure (two floats).
    """

    name = "multiply_numbers"
    description = "useful for multiplying two numbers"
    args_schema: type[BaseModel] = MultiplyNumbersArgs

    def _run(
        self,
        x: float,
        y: float,
    ) -> str:
        """Multiply two numbers and return formatted result.

        Args:
            x: First number to multiply.
            y: Second number to multiply.

        Returns:
            Human-readable string with the multiplication result.

        Example:
            >>> tool = MultiplyNumbersTool()
            >>> result = tool._run(10.0, 20.0)
            >>> "200" in result
            True
        """
        result = x * y
        return f"The product of {x} and {y} is {result}"


# Create tools using the Pydantic subclass approach
tools = [
    SimpleSearchTool(),
    MultiplyNumbersTool(),
]

# Initialize a ChatAnthropic model
llm = ChatAnthropic(model_name="claude-3-5-sonnet-20240620")

# Pull the prompt template from the hub
prompt = hub.pull("hwchase17/openai-tools-agent")

# Create the ReAct agent using the create_tool_calling_agent function
agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

# Create the agent executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)

# Test the agent with sample queries
response = agent_executor.invoke(
    {
        "input": "Search for Artivion. The home page URL for Artivion is https://https://artivion.com/. Provide detailed information about the company. This should include basic details about the company, like 'Company Name', 'Industry' or 'Industries', 'Primary Location', and a 'Company Overview'."
    }
)
print("Response for 'Search for LangChain updates':", response)

# response = agent_executor.invoke({"input": "Multiply 10 and 20"})
# print("Response for 'Multiply 10 and 20':", response)
