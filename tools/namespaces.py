"""
Namespace management tools for Kubernetes
"""

from kubernetes import client, config
from kubernetes.client.rest import ApiException


class NamespaceTools:
    """Tools for managing Kubernetes namespaces"""
    
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
    
    async def list_namespaces(self) -> str:
        """List all namespaces"""
        try:
            namespaces = self.v1.list_namespace()
            
            if not namespaces.items:
                return "No namespaces found"
            
            result = "Namespaces:\n\n"
            for ns in namespaces.items:
                result += f"  - {ns.metadata.name}\n"
                result += f"    Status: {ns.status.phase}\n"
                result += f"    Age: {ns.metadata.creation_timestamp}\n"
                
                if ns.metadata.labels:
                    labels = ", ".join([f"{k}={v}" for k, v in ns.metadata.labels.items()])
                    result += f"    Labels: {labels}\n"
                
                result += "\n"
            
            return result
        
        except ApiException as e:
            return f"Error listing namespaces: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def create_namespace(self, name: str, labels: dict = None) -> str:
        """Create a new namespace"""
        try:
            namespace_body = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=name,
                    labels=labels or {}
                )
            )
            
            namespace = self.v1.create_namespace(body=namespace_body)
            return f"Successfully created namespace '{name}'"
        
        except ApiException as e:
            if e.status == 409:
                return f"Namespace '{name}' already exists"
            return f"Error creating namespace: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def delete_namespace(self, name: str) -> str:
        """Delete a namespace"""
        try:
            self.v1.delete_namespace(name=name)
            return f"Successfully initiated deletion of namespace '{name}'"
        
        except ApiException as e:
            if e.status == 404:
                return f"Namespace '{name}' not found"
            return f"Error deleting namespace: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

