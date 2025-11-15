"""
Event monitoring tools for Kubernetes
"""

from kubernetes import client, config
from kubernetes.client.rest import ApiException


class EventTools:
    """Tools for monitoring Kubernetes events"""
    
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
    
    async def list_events(self, namespace: str = None, limit: int = 50) -> str:
        """List events in a namespace or cluster-wide"""
        try:
            if namespace:
                events = self.v1.list_namespaced_event(namespace=namespace, limit=limit)
                scope = f"namespace '{namespace}'"
            else:
                events = self.v1.list_event_for_all_namespaces(limit=limit)
                scope = "all namespaces"
            
            if not events.items:
                return f"No events found in {scope}"
            
            # Sort by timestamp (newest first)
            sorted_events = sorted(
                events.items,
                key=lambda e: e.first_timestamp or e.event_time or e.metadata.creation_timestamp,
                reverse=True
            )
            
            result = f"Recent events in {scope} (showing {len(sorted_events)}):\n\n"
            
            for event in sorted_events[:limit]:
                timestamp = event.first_timestamp or event.event_time or event.metadata.creation_timestamp
                result += f"[{timestamp}] {event.type} - {event.reason}\n"
                result += f"  Object: {event.involved_object.kind}/{event.involved_object.name}\n"
                result += f"  Namespace: {event.involved_object.namespace}\n"
                if event.message:
                    result += f"  Message: {event.message}\n"
                result += "\n"
            
            return result
        
        except ApiException as e:
            return f"Error listing events: {e.reason} - {e.body}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

