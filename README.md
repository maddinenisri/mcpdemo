# MCP Demo Project Documentation

## 1. Project Overview

This project demonstrates the interaction between an MCP (Model Context Protocol) client and server using Langchain. It provides a sample implementation of text analysis and data querying functionalities using the MCP architecture.

## 2. Installation

This project uses Poetry for dependency management. To install the project and its dependencies:

1. Ensure you have Poetry installed on your system.
2. Clone the repository.
3. Navigate to the project directory.
4. Run `poetry install` to install the dependencies.

## 3. Project Structure

```
mcpdemo/
├── src/
│   ├── mcp_client.py
│   └── mcp_server.py
├── .env
├── .gitignore
├── poetry.lock
├── pyproject.toml
└── README.md
```

## 4. Dependencies

The project requires Python 3.13 and uses the following main dependencies:

- python-dotenv: For loading environment variables
- openai: For interacting with OpenAI's API
- langchain and related packages: For building language model applications
- fastapi: For building the API
- uvicorn: ASGI server for FastAPI
- asyncio: For asynchronous programming
- mcp: For implementing the Model Context Protocol

Dev dependencies include pytest, flake8, and reportlab.

## 5. MCP Client (mcp_client.py)

The MCP client is responsible for interacting with the MCP servers and executing the language model tasks. Key features include:

- Uses the MultiServerMCPClient to connect to multiple MCP servers (local and Figma).
- Creates a ReAct agent using ChatOpenAI model and available tools.
- Demonstrates how to send a request to analyze text sentiment and query sales data.

### Main Components:

- `main()` function: Sets up the MCP client, loads tools, creates the agent, and processes a sample request.
- MultiServerMCPClient: Connects to both a local server and a Figma server.
- ChatOpenAI model: Used for natural language processing tasks.
- ReAct agent: Combines the language model with the available tools for task execution.

## 6. MCP Server (mcp_server.py)

The MCP server implements two main tools:

1. `text_analysis`: Performs sentiment analysis or summarization on given text.
2. `data_query`: Queries structured data sources based on natural language input.

The server uses FastMCP to create and run the MCP server with these tools.

### Main Components:

- FastMCP: Creates the MCP server instance.
- `text_analysis` function: Analyzes text for sentiment or generates summaries.
- `data_query` function: Queries data sources based on natural language input.

## 7. Usage

To run the project:

1. Set up the required environment variables in the `.env` file, including the `FIGMA_API_KEY`.
2. In a separate terminal, run the MCP server:
   ```
   python src/mcp_server.py
   ```
3. In a separate terminal, run the MCP client:
   ```
   python src/mcp_client.py
   ```

The client will send a sample request to analyze the sentiment of the text "I love programming!" and query sales data. The server will process these requests and return the results.

## 8. Configuration

The project uses a `pyproject.toml` file for configuration and dependency management. Key configurations include:

- Project metadata (name, version, description, authors, license)
- Python version requirement (^3.13)
- Dependencies and their versions
- Development dependencies

## 9. References

- [Langchain MCP Server](https://apidog.com/blog/langchain-mcp-server/)
- [MCP Server tools and resources](https://www.youtube.com/watch?v=-WogqfxWBbM)

This documentation provides an overview of the MCP Demo project, its structure, and how to use it. For more detailed information about specific components or functionalities, refer to the inline comments in the source code files.
