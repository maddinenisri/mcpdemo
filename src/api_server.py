import os
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_mcp_adapters.client import MultiServerMCPClient, StdioConnection

ERROR_SCHEMA = "Error extracting schema"

# Load environment variables
load_dotenv(override=True)

# MCP client configuration
servers = {
    "local-server": StdioConnection(command="python", args=["src/mcp_server.py"]),
    "figma-server": 
        StdioConnection(
            command="npx",
            args=["-y", "figma-developer-mcp", "--stdio"],
            env={"FIGMA_API_KEY": os.getenv("FIGMA_API_KEY")}
        )
}

# Define lifespan context manager
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    # Startup: Setup MCP client and load tools
    try:
        print("Starting MCP client...")
        fastapi_app.state.mcp_client = MultiServerMCPClient(servers)
        await fastapi_app.state.mcp_client.__aenter__()
        fastapi_app.state.tools = fastapi_app.state.mcp_client.get_tools()
        print(f"MCP client started, loaded {len(fastapi_app.state.tools)} tools")
    except ConnectionError as e:
        print(f"Connection error setting up MCP client: {str(e)}")
        # Perform cleanup
    except ValueError as e:
        print(f"Value error in MCP client setup: {str(e)}")
        # Perform cleanup
    except Exception as e:  # pylint: disable=broad-except
        # We still need a catch-all as a last resort
        print(f"Unexpected error setting up MCP client: {str(e)}")
        if hasattr(fastapi_app.state, "mcp_client") and fastapi_app.state.mcp_client:
            try:
                await fastapi_app.state.mcp_client.__aexit__(None, None, None)
            except Exception as cleanup_error:  # pylint: disable=broad-except
                print(f"Error during cleanup: {cleanup_error}")
    
    yield  # This is where FastAPI runs
    
    # Shutdown: Clean up MCP client
    if hasattr(fastapi_app.state, "mcp_client") and fastapi_app.state.mcp_client:
        try:
            await fastapi_app.state.mcp_client.__aexit__(None, None, None)
            print("MCP client shutdown complete")
        except Exception as e:
            print(f"Error during MCP client shutdown: {str(e)}")
            
# Initialize FastAPI application
app = FastAPI(
    title="MCP Tools API",
    description="API to access MCP tools from multiple servers",
    version="1.0.0",
    lifespan=lifespan,
)

# Initialize state
app.state.mcp_client = None
app.state.tools = []

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ToolSchema(BaseModel):
    """Schema for tool information"""
    name: str
    description: str = ""
    input_schema: Any = Field(default_factory=dict)
    output_schema: Any = Field(default_factory=dict)

class ToolRequest(BaseModel):
    """Request model for invoking a tool"""
    params: Dict[str, Any] = Field(default_factory=dict)

@app.get("/tools", response_model=List[Dict[str, Any]])
async def list_tools():
    """List all available MCP tools"""
    if not app.state.tools:
        raise HTTPException(status_code=503, detail="MCP client not ready or no tools available")
    
    tool_schemas = []
    for tool in app.state.tools:
        try:
            # Extract schema information in a serializable format
            if hasattr(tool, "args_schema"):
                input_schema = str(tool.args_schema)
            elif hasattr(tool.input_schema, "schema"):
                input_schema = tool.input_schema.schema()
            else:
                input_schema = str(tool.input_schema)
            
            if hasattr(tool.output_schema, "schema"):
                output_schema = tool.output_schema.schema()
            else:
                output_schema = str(tool.output_schema)
            
            tool_schemas.append({
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": input_schema,
                "output_schema": output_schema
            })
        except ValueError as e:
            # Handle validation errors
            raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}") from e
        except ConnectionError as e:
            # Handle connection issues
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}") from e
        except Exception as e:  # pylint: disable=broad-except
            # Catch-all for unexpected errors
            raise HTTPException(status_code=500, detail=f"Unexpected error invoking tool: {str(e)}") from e
    
    return tool_schemas

@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool"""
    for tool in app.state.tools:
        if tool.name == tool_name:
            try:
                # Extract schema information
                if hasattr(tool, "args_schema"):
                    input_schema = str(tool.args_schema) 
                elif hasattr(tool.input_schema, "schema"):
                    input_schema = tool.input_schema.schema()
                else:
                    input_schema = str(tool.input_schema)
                
                if hasattr(tool.output_schema, "schema"):
                    output_schema = tool.output_schema.schema()
                else:
                    output_schema = str(tool.output_schema)
                
                return {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": input_schema,
                    "output_schema": output_schema
                }
            except ValueError as e:
                # Handle validation errors
                raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}") from e
            except ConnectionError as e:
                # Handle connection issues
                raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}") from e
            except Exception as e:  # pylint: disable=broad-except
                # Catch-all for unexpected errors
                raise HTTPException(status_code=500, detail=f"Unexpected error invoking tool: {str(e)}") from e

@app.post("/tools/{tool_name}/invoke")
async def invoke_tool(tool_name: str, request: ToolRequest):
    """Invoke a specific tool with parameters"""
    if not app.state.mcp_client:
        raise HTTPException(status_code=503, detail="MCP client not ready")
    
    # Find the requested tool
    selected_tool = None
    for tool in app.state.tools:
        if tool.name == tool_name:
            selected_tool = tool
            break
    
    if not selected_tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    try:
        # Invoke the tool with the provided parameters
        result = await selected_tool.invoke(request.params)
        return {
            "tool": tool_name,
            "result": result
        }
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}") from e
    except ConnectionError as e:
        # Handle connection issues
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}") from e
    except Exception as e:  # pylint: disable=broad-except
        # Catch-all for unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected error invoking tool: {str(e)}") from e

if __name__ == "__main__":
    # Run the API server
    uvicorn.run("api_server:app", host="localhost", port=8001, reload=True)
