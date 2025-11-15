#!/usr/bin/env python3
"""
MCP Server for Kubernetes Operations
Provides tools for interacting with Kubernetes clusters via MCP protocol
"""

import asyncio
import sys
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from tools.deployments import DeploymentTools

# Initialize MCP server
app = Server("k8s-mcp-server")

# Initialize tool modules
deployment_tools = DeploymentTools()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    tools = []
    
    # Deployment tools
    tools.extend([
        Tool(
            name="list_deployments",
            description="List all deployments in a namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (optional, defaults to 'default')"
                    }
                }
            }
        ),
        Tool(
            name="scale_deployment",
            description="Scale a deployment to a specific number of replicas",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {
                        "type": "string",
                        "description": "Name of the deployment"
                    },
                    "replicas": {
                        "type": "integer",
                        "description": "Number of replicas"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (defaults to 'default')"
                    }
                },
                "required": ["deployment_name", "replicas"]
            }
        ),
        Tool(
            name="restart_deployment",
            description="Restart a deployment by rolling out restart",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {
                        "type": "string",
                        "description": "Name of the deployment"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (defaults to 'default')"
                    }
                },
                "required": ["deployment_name"]
            }
        ),
    ])
    
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls"""
    try:
        # Deployment operations
        if name == "list_deployments":
            namespace = arguments.get("namespace", "default")
            result = await deployment_tools.list_deployments(namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "scale_deployment":
            deployment_name = arguments["deployment_name"]
            replicas = arguments["replicas"]
            namespace = arguments.get("namespace", "default")
            result = await deployment_tools.scale(deployment_name, replicas, namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "restart_deployment":
            deployment_name = arguments["deployment_name"]
            namespace = arguments.get("namespace", "default")
            result = await deployment_tools.restart(deployment_name, namespace)
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
