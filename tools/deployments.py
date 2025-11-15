"""
Deployment management tools for Kubernetes
"""

from kubernetes import client, config
from kubernetes.client.rest import ApiException


class DeploymentTools:
    """Tools for managing Kubernetes deployments"""
    
    def __init__(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException:
                raise Exception("Could not load Kubernetes configuration")
        
        self.apps_v1 = client.AppsV1Api()
    
    async def list_deployments(self, namespace: str = "default") -> str:
        """List deployments in a namespace"""
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)
            
            if not deployments.items:
                return f"No deployments found in namespace '{namespace}'"
            
            result = f"Deployments in namespace '{namespace}':\n\n"
            for deployment in deployments.items:
                replicas = deployment.spec.replicas or 0
                ready = deployment.status.ready_replicas or 0
                available = deployment.status.available_replicas or 0
                
                result += f"  - {deployment.metadata.name}\n"
                result += f"    Replicas: {ready}/{replicas} ready, {available} available\n"
                result += f"    Age: {deployment.metadata.creation_timestamp}\n"
                result += f"    Strategy: {deployment.spec.strategy.type if deployment.spec.strategy else 'RollingUpdate'}\n"
                result += "\n"
            
            return result
        
        except ApiException as e:
            return f"Error listing deployments: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def scale(self, deployment_name: str, replicas: int, namespace: str = "default") -> str:
        """Scale a deployment"""
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Update replica count
            deployment.spec.replicas = replicas
            
            # Apply update
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            return f"Successfully scaled deployment '{deployment_name}' to {replicas} replicas in namespace '{namespace}'"
        
        except ApiException as e:
            if e.status == 404:
                return f"Deployment '{deployment_name}' not found in namespace '{namespace}'"
            return f"Error scaling deployment: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def restart(self, deployment_name: str, namespace: str = "default") -> str:
        """Restart a deployment by rolling restart"""
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Add annotation to trigger rolling restart
            if deployment.spec.template.metadata.annotations is None:
                deployment.spec.template.metadata.annotations = {}
            
            import time
            deployment.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Apply update
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            return f"Successfully triggered rolling restart for deployment '{deployment_name}' in namespace '{namespace}'"
        
        except ApiException as e:
            if e.status == 404:
                return f"Deployment '{deployment_name}' not found in namespace '{namespace}'"
            return f"Error restarting deployment: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

