"""
YAML operations for Kubernetes resources
"""

import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.utils import create_from_dict


class YamlOpsTools:
    """Tools for YAML-based Kubernetes operations"""
    
    def __init__(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException:
                raise Exception("Could not load Kubernetes configuration")
        
        self.api_client = client.ApiClient()
    
    async def apply(self, yaml_content: str) -> str:
        """Apply Kubernetes resources from YAML using kubectl apply"""
        import tempfile
        import os
        import subprocess
        
        try:
            # Validate YAML syntax first
            try:
                resources = list(yaml.safe_load_all(yaml_content))
                if not resources or all(r is None for r in resources):
                    return "✗ Error: No valid resources found in YAML"
            except yaml.YAMLError as e:
                return f"✗ YAML parsing error: {str(e)}"
            
            # Create temporary file with YAML content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
                tmp_file.write(yaml_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Use kubectl apply to apply the YAML
                result = subprocess.run(
                    ['kubectl', 'apply', '-f', tmp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    return f"✓ Successfully applied YAML:\n\n{result.stdout}"
                else:
                    return f"✗ Error applying YAML:\n\n{result.stderr}"
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
        
        except subprocess.TimeoutExpired:
            return "✗ Error: kubectl apply timed out after 60 seconds"
        except FileNotFoundError:
            return "✗ Error: kubectl command not found. Make sure kubectl is installed and in PATH."
        except Exception as e:
            return f"✗ Unexpected error: {str(e)}"
    
    async def get(self, kind: str, name: str, namespace: str = None) -> str:
        """Get Kubernetes resource as YAML"""
        try:
            # Map kind to API client
            api_map = {
                "Pod": (client.CoreV1Api(), "read_namespaced_pod"),
                "Deployment": (client.AppsV1Api(), "read_namespaced_deployment"),
                "Service": (client.CoreV1Api(), "read_namespaced_service"),
                "ConfigMap": (client.CoreV1Api(), "read_namespaced_config_map"),
                "Secret": (client.CoreV1Api(), "read_namespaced_secret"),
            }
            
            if kind not in api_map:
                return f"Unsupported resource kind: {kind}. Supported: {', '.join(api_map.keys())}"
            
            api_instance, method_name = api_map[kind]
            method = getattr(api_instance, method_name)
            
            if namespace:
                resource = method(name=name, namespace=namespace)
            else:
                # For cluster-scoped resources, we'd need different methods
                return f"Namespace required for {kind} resources"
            
            # Convert to dict and then to YAML
            resource_dict = self.api_client.sanitize_for_serialization(resource)
            yaml_output = yaml.dump(resource_dict, default_flow_style=False, sort_keys=False)
            
            return f"YAML for {kind}/{name}:\n\n{yaml_output}"
        
        except ApiException as e:
            if e.status == 404:
                return f"Resource {kind}/{name} not found in namespace '{namespace}'"
            return f"Error getting resource: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

