"""
Service management tools for Kubernetes
"""

from kubernetes import client, config
from kubernetes.client.rest import ApiException


class ServiceTools:
    """Tools for managing Kubernetes services"""
    
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
    
    async def list_services(self, namespace: str = "default") -> str:
        """List services in a namespace"""
        try:
            services = self.v1.list_namespaced_service(namespace=namespace)
            
            if not services.items:
                return f"No services found in namespace '{namespace}'"
            
            result = f"Services in namespace '{namespace}':\n\n"
            for service in services.items:
                result += f"  - {service.metadata.name}\n"
                result += f"    Type: {service.spec.type}\n"
                
                if service.spec.cluster_ip:
                    result += f"    Cluster IP: {service.spec.cluster_ip}\n"
                
                if service.spec.ports:
                    ports = ", ".join([f"{p.port}:{p.target_port}/{p.protocol}" for p in service.spec.ports])
                    result += f"    Ports: {ports}\n"
                
                if service.status.load_balancer and service.status.load_balancer.ingress:
                    ingress = service.status.load_balancer.ingress[0]
                    ip = ingress.ip or ingress.hostname or "N/A"
                    result += f"    External IP: {ip}\n"
                
                result += f"    Age: {service.metadata.creation_timestamp}\n"
                result += "\n"
            
            return result
        
        except ApiException as e:
            return f"Error listing services: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def describe(self, service_name: str, namespace: str = "default") -> str:
        """Get detailed information about a service"""
        try:
            service = self.v1.read_namespaced_service(name=service_name, namespace=namespace)
            
            result = f"Service: {service.metadata.name}\n"
            result += f"Namespace: {service.metadata.namespace}\n"
            result += f"Type: {service.spec.type}\n"
            result += f"Cluster IP: {service.spec.cluster_ip}\n"
            result += f"Created: {service.metadata.creation_timestamp}\n\n"
            
            result += "Ports:\n"
            if service.spec.ports:
                for port in service.spec.ports:
                    result += f"  - Port: {port.port}\n"
                    result += f"    Target Port: {port.target_port}\n"
                    result += f"    Protocol: {port.protocol}\n"
                    if port.node_port:
                        result += f"    Node Port: {port.node_port}\n"
            else:
                result += "  None\n"
            
            result += "\nSelector:\n"
            if service.spec.selector:
                for key, value in service.spec.selector.items():
                    result += f"  {key}={value}\n"
            else:
                result += "  None\n"
            
            if service.status.load_balancer and service.status.load_balancer.ingress:
                result += "\nLoad Balancer Ingress:\n"
                for ingress in service.status.load_balancer.ingress:
                    if ingress.ip:
                        result += f"  IP: {ingress.ip}\n"
                    if ingress.hostname:
                        result += f"  Hostname: {ingress.hostname}\n"
            
            return result
        
        except ApiException as e:
            if e.status == 404:
                return f"Service '{service_name}' not found in namespace '{namespace}'"
            return f"Error describing service: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

