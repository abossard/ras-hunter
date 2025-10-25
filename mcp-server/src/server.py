"""
MCP Server for Ras's Deep Treasure.

Wraps the backend API endpoints as MCP tools for AI agent access.
Constitution: Explicit tool definitions with clear error handling.
"""

import asyncio
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Backend API URL from environment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Create MCP server instance
app = Server("ras-hunter")

# HTTP client for backend API calls
http_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    """Get or create HTTP client."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=30.0)
    return http_client


async def close_client() -> None:
    """Close HTTP client."""
    global http_client
    if http_client:
        await http_client.aclose()
        http_client = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available MCP tools.

    Returns:
        List of tool definitions for AI agents.
    """
    return [
        Tool(
            name="health_check",
            description="Check if the Ras's Deep Treasure backend API is healthy and responding",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_api_info",
            description="Get information about the Ras's Deep Treasure API including available endpoints",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Execute an MCP tool.

    Args:
        name: Tool name to execute.
        arguments: Tool arguments.

    Returns:
        Tool execution results as text content.

    Raises:
        ValueError: If tool name is unknown.
    """
    client = await get_client()

    try:
        if name == "health_check":
            response = await client.get("/api/health")
            response.raise_for_status()
            data = response.json()
            return [
                TextContent(
                    type="text",
                    text=f"Backend API is healthy. Status: {data.get('status', 'unknown')}",
                )
            ]

        elif name == "get_api_info":
            response = await client.get("/")
            response.raise_for_status()
            data = response.json()
            return [
                TextContent(
                    type="text",
                    text=f"API Information:\n{data.get('message', 'Unknown')}\n"
                    f"Documentation: {BACKEND_URL}{data.get('docs', '/docs')}\n"
                    f"Health Check: {BACKEND_URL}{data.get('health', '/api/health')}",
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except httpx.HTTPError as e:
        return [
            TextContent(
                type="text",
                text=f"Error calling backend API: {type(e).__name__}: {str(e)}",
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Unexpected error: {type(e).__name__}: {str(e)}",
            )
        ]


async def main() -> None:
    """Run the MCP server."""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
    finally:
        await close_client()


if __name__ == "__main__":
    asyncio.run(main())
