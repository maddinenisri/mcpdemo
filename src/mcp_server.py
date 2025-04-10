from mcp.server.fastmcp import FastMCP
from typing import Annotated

mcp = FastMCP("ExampleServer")

@mcp.tool()
def text_analysis(
    text: Annotated[str, "Text to analyze"],
    operation: Annotated[str, "Analysis type (sentiment, summary)"]
) -> str:
    """Perform text analysis operations"""
    print(f"Analyzing text: {text} with operation: {operation}")
    if operation == "sentiment":
        return "Positive"  # Replace with actual analysis logic
    elif operation == "summary":
        return "Summary placeholder"
    return "Invalid operation"

@mcp.tool()
def data_query(
    query: Annotated[str, "Natural language query"],
    source: Annotated[str, "Data source identifier"]
) -> dict:
    """Query structured data sources"""
    print(f"Querying data: {query} from source: {source}")
    return {"result": {"product": "MacBook", "comments": "Product is exceeded our expectation"}, "source": source}

if __name__ == "__main__":
    mcp.run(transport="sse")
