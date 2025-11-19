"""
Node and cluster information tools for Kubernetes
"""

from kubernetes import client, config
from kubernetes.client.rest import ApiException


class NodeTools:
    """Tools for getting node and cluster information"""
    
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
    
    async def list_nodes(self) -> str:
        """List all nodes in the cluster"""
        try:
            nodes = self.v1.list_node()
            
            if not nodes.items:
                return "No nodes found in cluster"
            
            result = "Cluster Nodes:\n\n"
            for node in nodes.items:
                result += f"  - {node.metadata.name}\n"
                
                status_conditions = {c.type: c.status for c in node.status.conditions if c.type in ['Ready', 'MemoryPressure', 'DiskPressure', 'PIDPressure']}
                ready = status_conditions.get('Ready', 'Unknown')
                result += f"    Status: Ready={ready}\n"
                
                if node.status.node_info:
                    result += f"    OS: {node.status.node_info.operating_system}/{node.status.node_info.architecture}\n"
                    result += f"    Kubernetes: {node.status.node_info.kubelet_version}\n"
                    result += f"    Container Runtime: {node.status.node_info.container_runtime_version}\n"
                
                if node.status.allocatable:
                    cpu = node.status.allocatable.get('cpu', 'N/A')
                    memory = node.status.allocatable.get('memory', 'N/A')
                    result += f"    Allocatable: CPU={cpu}, Memory={memory}\n"
                
                if node.metadata.labels:
                    role = node.metadata.labels.get('node-role.kubernetes.io/control-plane') or \
                           node.metadata.labels.get('node-role.kubernetes.io/master') or \
                           'worker'
                    result += f"    Role: {role}\n"
                
                result += f"    Age: {node.metadata.creation_timestamp}\n"
                result += "\n"
            
            return result
        
        except ApiException as e:
            return f"Error listing nodes: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def describe_node(self, node_name: str) -> str:
        """Get detailed information about a node"""
        try:
            node = self.v1.read_node(name=node_name)
            
            result = f"Node: {node.metadata.name}\n"
            result += f"Created: {node.metadata.creation_timestamp}\n\n"
            
            result += "Conditions:\n"
            for condition in node.status.conditions:
                result += f"  {condition.type}: {condition.status} - {condition.reason or 'N/A'}\n"
                if condition.message:
                    result += f"    Message: {condition.message}\n"
            
            result += "\nNode Info:\n"
            if node.status.node_info:
                result += f"  OS: {node.status.node_info.operating_system}\n"
                result += f"  Architecture: {node.status.node_info.architecture}\n"
                result += f"  Kernel: {node.status.node_info.kernel_version}\n"
                result += f"  Kubernetes: {node.status.node_info.kubelet_version}\n"
                result += f"  Container Runtime: {node.status.node_info.container_runtime_version}\n"
            
            result += "\nCapacity:\n"
            if node.status.capacity:
                for key, value in node.status.capacity.items():
                    result += f"  {key}: {value}\n"
            
            result += "\nAllocatable:\n"
            if node.status.allocatable:
                for key, value in node.status.allocatable.items():
                    result += f"  {key}: {value}\n"
            
            if node.metadata.labels:
                result += "\nLabels:\n"
                for key, value in node.metadata.labels.items():
                    result += f"  {key}={value}\n"
            
            return result
        
        except ApiException as e:
            if e.status == 404:
                return f"Node '{node_name}' not found"
            return f"Error describing node: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def list_pods_by_node(self, namespace: str = None) -> str:
        """List all nodes with their pods grouped by node"""
        try:
            nodes = self.v1.list_node()
            
            if namespace:
                pods = self.v1.list_pod_for_all_namespaces()
                pods.items = [p for p in pods.items if p.metadata.namespace == namespace]
            else:
                pods = self.v1.list_pod_for_all_namespaces()
            
            # Grouping pods by node
            pods_by_node = {}
            for pod in pods.items:
                node_name = pod.spec.node_name
                if node_name:
                    if node_name not in pods_by_node:
                        pods_by_node[node_name] = []
                    pods_by_node[node_name].append(pod)
            
            # Nodes with no pods
            for node in nodes.items:
                if node.metadata.name not in pods_by_node:
                    pods_by_node[node.metadata.name] = []
            
            if not pods_by_node:
                return "No nodes or pods found"
            
            scope = f"namespace '{namespace}'" if namespace else "all namespaces"
            result = f"Pods by Node ({scope}):\n\n"
            
            sorted_nodes = sorted(pods_by_node.keys())
            
            for node_name in sorted_nodes:
                node_pods = pods_by_node[node_name]
                
                node = next((n for n in nodes.items if n.metadata.name == node_name), None)
                if node:
                    status_conditions = {c.type: c.status for c in node.status.conditions if c.type == 'Ready'}
                    ready = status_conditions.get('Ready', 'Unknown')
                    result += f"Node: {node_name} (Ready={ready})\n"
                else:
                    result += f"Node: {node_name}\n"
                
                if node_pods:
                    result += f"  Pods ({len(node_pods)}):\n"
                    for pod in node_pods:
                        status = pod.status.phase
                        result += f"    - {pod.metadata.name} ({status}) [ns: {pod.metadata.namespace}]\n"
                else:
                    result += "  Pods: None\n"
                
                result += "\n"
            
            return result
        
        except ApiException as e:
            return f"Error listing pods by node: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    async def cluster_info(self) -> str:
        """Get basic cluster information"""
        try:
            nodes = self.v1.list_node()
            namespaces = self.v1.list_namespace()
            
            # Count nodes by role
            control_plane = 0
            workers = 0
            for node in nodes.items:
                labels = node.metadata.labels or {}
                if 'node-role.kubernetes.io/control-plane' in labels or \
                   'node-role.kubernetes.io/master' in labels:
                    control_plane += 1
                else:
                    workers += 1
            
            result = "Cluster Information:\n\n"
            result += f"Total Nodes: {len(nodes.items)}\n"
            result += f"  Control Plane: {control_plane}\n"
            result += f"  Workers: {workers}\n"
            result += f"Total Namespaces: {len(namespaces.items)}\n"
            
            if nodes.items and nodes.items[0].status.node_info:
                result += f"Kubernetes Version: {nodes.items[0].status.node_info.kubelet_version}\n"
            
            return result
        
        except ApiException as e:
            return f"Error getting cluster info: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

