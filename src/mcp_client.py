import asyncio
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load environment variables
load_dotenv(override=True)

# Example usage of the MCP client with LangChain
async def main():
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, max_tokens=2000)
    async with MultiServerMCPClient(
        {
            "local-server": {
                "command": "python",
                "args": ["src/mcp_server.py"],  # Adjust the path to your server
                "transport": "stdio",
            },
            "figma-server": {
                "command": "npx",
                "args": ["-y", "figma-developer-mcp", "--stdio"],
                "env": {
                    "FIGMA_API_KEY": "XXXXXXXXXX",  # Replace with your actual Figma API key
                },
                "transport": "stdio",
            },
        }
    ) as client:
        print("MCP client started")
        # Load available tools
        tools = client.get_tools()
        print("Available tools:", tools)
        agent = create_react_agent(model, client.get_tools())
        # Define the prompt template
        # message = "Analyze the sentiment of this text: 'I love programming!' and get me the summary of sale details."
        
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
        print(response['messages'][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
