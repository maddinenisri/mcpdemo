import asyncio
import os
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient, StdioConnection

# Load environment variables
load_dotenv(override=True)

servers = {
    "local-server": StdioConnection(command="python", args=["src/mcp_server.py"]),
    "figma-server": 
        StdioConnection(
            command="npx",
            args=["-y", "figma-developer-mcp", "--stdio"],
            env={"FIGMA_API_KEY": os.getenv("FIGMA_API_KEY")}
        )
}

FIGMA_API_KEY = os.getenv("FIGMA_API_KEY")
# Example usage of the MCP client with LangChain
async def main():
    """
    Example usage of the MCP client with LangChain
    """
    # Initialize the model
    # Note: You can use any model compatible with LangChain
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, max_tokens=2000)
    
    # Initialize the MCP client with multiple servers
    async with MultiServerMCPClient(servers) as client:
        print("MCP client started")
        # Load available tools
        tools = client.get_tools()
        # Print available tools
        for tool in tools:
            print(f"tool {tool.name}({tool.input_schema}) -> {tool.output_schema}")
        agent = create_react_agent(model, client.get_tools())
        
        inputs = {
            "messages": [
                SystemMessage(
                    content="""
                    You are a helpful assistant. Use the tools provided to answer the user's questions. 
                    Determine which tool to use based on the user's request and identify correct input parameters.
                    ## Guidelines:
                    1. Use the tools to perform specific tasks.
                    2. If the task requires multiple tools, use them sequentially.
                    3. Combine results if necessary.
                    4. If the task is ambiguous, ask clarifying questions.
                    5. Provide clear and concise responses.
                    ## Tools:
                    You can use the following tools:
                    {tools}
                    """
                ), 
                HumanMessage(content="Analyze the sentiment of this text: 'I love programming!' and get me the summary of sale details from sales database."),
                # HumanMessage(content="Fetch figma JSON document and return as is using mcp server tool from Figma URL: ..")
            ]}
        response = await agent.ainvoke(input=inputs)
        return response

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result['messages'][-1].content)
