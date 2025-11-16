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

from tools.pods import PodTools
from tools.deployments import DeploymentTools
from tools.yaml_ops import YamlOpsTools
from tools.events import EventTools
from tools.services import ServiceTools
from tools.configmaps_secrets import ConfigMapSecretTools
from tools.namespaces import NamespaceTools
from tools.nodes import NodeTools
from tools.jobs import JobTools

# Initialize MCP server
app = Server("k8s-mcp-server")

# Initialize tool modules
pod_tools = PodTools()
deployment_tools = DeploymentTools()
yaml_tools = YamlOpsTools()
event_tools = EventTools()
service_tools = ServiceTools()
configmap_secret_tools = ConfigMapSecretTools()
namespace_tools = NamespaceTools()
node_tools = NodeTools()
job_tools = JobTools()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    tools = []
    
    # Pod tools
    tools.extend([
        Tool(
            name="list_pods",
            description="List all pods in a namespace or cluster-wide",
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
            name="get_pod_logs",
            description="Get logs from a pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "pod_name": {
                        "type": "string",
                        "description": "Name of the pod"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (defaults to 'default')"
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Number of lines to tail (default: 100)"
                    }
                },
                "required": ["pod_name"]
            }
        ),
        Tool(
            name="describe_pod",
            description="Get detailed information about a pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "pod_name": {
                        "type": "string",
                        "description": "Name of the pod"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (defaults to 'default')"
                    }
                },
                "required": ["pod_name"]
            }
        ),
    ])
    
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
    
    # YAML operations
    tools.extend([
        Tool(
            name="apply_yaml",
            description="Apply Kubernetes resources from YAML",
            inputSchema={
                "type": "object",
                "properties": {
                    "yaml_content": {
                        "type": "string",
                        "description": "YAML content to apply"
                    }
                },
                "required": ["yaml_content"]
            }
        ),
        Tool(
            name="get_yaml",
            description="Get Kubernetes resource as YAML",
            inputSchema={
                "type": "object",
                "properties": {
                    "kind": {
                        "type": "string",
                        "description": "Resource kind (e.g., Pod, Deployment, Service)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Resource name"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (optional)"
                    }
                },
                "required": ["kind", "name"]
            }
        ),
    ])
    
    # Event tools
    tools.extend([
        Tool(
            name="list_events",
            description="List events in a namespace or cluster-wide",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of events to return (default: 50)"
                    }
                }
            }
        ),
    ])
    
    # Service tools
    tools.extend([
        Tool(
            name="list_services",
            description="List all services in a namespace",
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
            name="describe_service",
            description="Get detailed information about a service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (defaults to 'default')"
                    }
                },
                "required": ["service_name"]
            }
        ),
    ])
    
    # ConfigMap and Secret tools
    tools.extend([
        Tool(
            name="list_configmaps",
            description="List all ConfigMaps in a namespace",
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
            name="get_configmap",
            description="Get ConfigMap data",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the ConfigMap"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (defaults to 'default')"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="list_secrets",
            description="List all Secrets in a namespace",
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
            name="get_secret",
            description="Get Secret data (optionally decoded)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the Secret"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (defaults to 'default')"
                    },
                    "decode": {
                        "type": "boolean",
                        "description": "Whether to decode base64 values (default: true)"
                    }
                },
                "required": ["name"]
            }
        ),
    ])
    
    # Namespace tools
    tools.extend([
        Tool(
            name="list_namespaces",
            description="List all namespaces in the cluster",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="create_namespace",
            description="Create a new namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the namespace"
                    },
                    "labels": {
                        "type": "object",
                        "description": "Labels to apply to the namespace (optional)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="delete_namespace",
            description="Delete a namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the namespace"
                    }
                },
                "required": ["name"]
            }
        ),
    ])
    
    # Node and cluster tools
    tools.extend([
        Tool(
            name="list_nodes",
            description="List all nodes in the cluster",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="describe_node",
            description="Get detailed information about a node",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_name": {
                        "type": "string",
                        "description": "Name of the node"
                    }
                },
                "required": ["node_name"]
            }
        ),
        Tool(
            name="cluster_info",
            description="Get basic cluster information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_pods_by_node",
            description="List all nodes with their pods grouped by node",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (optional, filters pods by namespace)"
                    }
                }
            }
        ),
    ])
    
    # Job tools
    tools.extend([
        Tool(
            name="list_jobs",
            description="List all jobs in a namespace",
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
            name="describe_job",
            description="Get detailed information about a job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_name": {
                        "type": "string",
                        "description": "Name of the job"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (defaults to 'default')"
                    }
                },
                "required": ["job_name"]
            }
        ),
        Tool(
            name="list_cronjobs",
            description="List all CronJobs in a namespace",
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
            name="delete_job",
            description="Delete a job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_name": {
                        "type": "string",
                        "description": "Name of the job"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace name (defaults to 'default')"
                    }
                },
                "required": ["job_name"]
            }
        ),
    ])
    
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls"""
    try:
        # Pod operations
        if name == "list_pods":
            namespace = arguments.get("namespace", "default")
            result = await pod_tools.list_pods(namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_pod_logs":
            pod_name = arguments["pod_name"]
            namespace = arguments.get("namespace", "default")
            tail = arguments.get("tail", 100)
            result = await pod_tools.get_logs(pod_name, namespace, tail)
            return [TextContent(type="text", text=result)]
        
        elif name == "describe_pod":
            pod_name = arguments["pod_name"]
            namespace = arguments.get("namespace", "default")
            result = await pod_tools.describe(pod_name, namespace)
            return [TextContent(type="text", text=result)]
        
        # Deployment operations
        elif name == "list_deployments":
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
        
        # YAML operations
        elif name == "apply_yaml":
            yaml_content = arguments["yaml_content"]
            result = await yaml_tools.apply(yaml_content)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_yaml":
            kind = arguments["kind"]
            name = arguments["name"]
            namespace = arguments.get("namespace")
            result = await yaml_tools.get(kind, name, namespace)
            return [TextContent(type="text", text=result)]
        
        # Event operations
        elif name == "list_events":
            namespace = arguments.get("namespace")
            limit = arguments.get("limit", 50)
            result = await event_tools.list_events(namespace, limit)
            return [TextContent(type="text", text=result)]
        
        # Service operations
        elif name == "list_services":
            namespace = arguments.get("namespace", "default")
            result = await service_tools.list_services(namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "describe_service":
            service_name = arguments["service_name"]
            namespace = arguments.get("namespace", "default")
            result = await service_tools.describe(service_name, namespace)
            return [TextContent(type="text", text=result)]
        
        # ConfigMap and Secret operations
        elif name == "list_configmaps":
            namespace = arguments.get("namespace", "default")
            result = await configmap_secret_tools.list_configmaps(namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_configmap":
            name = arguments["name"]
            namespace = arguments.get("namespace", "default")
            result = await configmap_secret_tools.get_configmap(name, namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "list_secrets":
            namespace = arguments.get("namespace", "default")
            result = await configmap_secret_tools.list_secrets(namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_secret":
            name = arguments["name"]
            namespace = arguments.get("namespace", "default")
            decode = arguments.get("decode", True)
            result = await configmap_secret_tools.get_secret(name, namespace, decode)
            return [TextContent(type="text", text=result)]
        
        # Namespace operations
        elif name == "list_namespaces":
            result = await namespace_tools.list_namespaces()
            return [TextContent(type="text", text=result)]
        
        elif name == "create_namespace":
            name = arguments["name"]
            labels = arguments.get("labels")
            result = await namespace_tools.create_namespace(name, labels)
            return [TextContent(type="text", text=result)]
        
        elif name == "delete_namespace":
            name = arguments["name"]
            result = await namespace_tools.delete_namespace(name)
            return [TextContent(type="text", text=result)]
        
        # Node and cluster operations
        elif name == "list_nodes":
            result = await node_tools.list_nodes()
            return [TextContent(type="text", text=result)]
        
        elif name == "describe_node":
            node_name = arguments["node_name"]
            result = await node_tools.describe_node(node_name)
            return [TextContent(type="text", text=result)]
        
        elif name == "cluster_info":
            result = await node_tools.cluster_info()
            return [TextContent(type="text", text=result)]
        
        elif name == "list_pods_by_node":
            namespace = arguments.get("namespace")
            result = await node_tools.list_pods_by_node(namespace)
            return [TextContent(type="text", text=result)]
        
        # Job operations
        elif name == "list_jobs":
            namespace = arguments.get("namespace", "default")
            result = await job_tools.list_jobs(namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "describe_job":
            job_name = arguments["job_name"]
            namespace = arguments.get("namespace", "default")
            result = await job_tools.describe_job(job_name, namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "list_cronjobs":
            namespace = arguments.get("namespace", "default")
            result = await job_tools.list_cronjobs(namespace)
            return [TextContent(type="text", text=result)]
        
        elif name == "delete_job":
            job_name = arguments["job_name"]
            namespace = arguments.get("namespace", "default")
            result = await job_tools.delete_job(job_name, namespace)
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
