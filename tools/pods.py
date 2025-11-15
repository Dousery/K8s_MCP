"""
Pod management tools for Kubernetes
"""

import asyncio
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class PodTools:
    """Tools for managing Kubernetes pods"""
    
    def __init__(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException:
                raise Exception("Could not load Kubernetes configuration")
        
        self.v1 = client.CoreV1Api()
    
    async def list_pods(self, namespace: str = "default") -> str:
        """List pods in a namespace"""
        try:
            if namespace:
                pods = self.v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.v1.list_pod_for_all_namespaces()
            
            if not pods.items:
                return f"No pods found in namespace '{namespace}'"
            
            result = f"Pods in namespace '{namespace}':\n\n"
            for pod in pods.items:
                status = pod.status.phase
                result += f"  - {pod.metadata.name} ({status})\n"
                result += f"    Namespace: {pod.metadata.namespace}\n"
                result += f"    Node: {pod.spec.node_name or 'N/A'}\n"
                if pod.status.container_statuses:
                    for container in pod.status.container_statuses:
                        result += f"    Container: {container.name} - Ready: {container.ready}\n"
                result += "\n"
            
            return result
        
        except ApiException as e:
            return f"Error listing pods: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def get_logs(self, pod_name: str, namespace: str = "default", tail: int = 100) -> str:
        """Get logs from a pod"""
        try:
            logs = self.v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=tail
            )
            return f"Logs from pod '{pod_name}' in namespace '{namespace}':\n\n{logs}"
        
        except ApiException as e:
            if e.status == 404:
                return f"Pod '{pod_name}' not found in namespace '{namespace}'"
            return f"Error getting logs: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def describe(self, pod_name: str, namespace: str = "default") -> str:
        """Get detailed information about a pod"""
        try:
            pod = self.v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            
            result = f"Pod: {pod.metadata.name}\n"
            result += f"Namespace: {pod.metadata.namespace}\n"
            result += f"Status: {pod.status.phase}\n"
            result += f"Node: {pod.spec.node_name or 'N/A'}\n"
            result += f"Created: {pod.metadata.creation_timestamp}\n\n"
            
            result += "Containers:\n"
            for container in pod.spec.containers:
                result += f"  - {container.name}\n"
                result += f"    Image: {container.image}\n"
                if container.resources:
                    if container.resources.requests:
                        result += f"    Requests: {container.resources.requests}\n"
                    if container.resources.limits:
                        result += f"    Limits: {container.resources.limits}\n"
            
            result += "\nContainer Statuses:\n"
            if pod.status.container_statuses:
                for status in pod.status.container_statuses:
                    result += f"  - {status.name}: Ready={status.ready}, Restarts={status.restart_count}\n"
                    if status.state:
                        if status.state.running:
                            result += f"    State: Running (started: {status.state.running.started_at})\n"
                        elif status.state.waiting:
                            result += f"    State: Waiting - {status.state.waiting.reason}\n"
                        elif status.state.terminated:
                            result += f"    State: Terminated - {status.state.terminated.reason}\n"
            
            return result
        
        except ApiException as e:
            if e.status == 404:
                return f"Pod '{pod_name}' not found in namespace '{namespace}'"
            return f"Error describing pod: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

