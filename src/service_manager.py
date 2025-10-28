"""
Simple tenant-based service manager for mapping database connections by tenant_id.
"""

from typing import Dict, Optional
from src.vanna_service import VannaService


class ServiceManager:
    """Manages VannaService instances mapped by tenant_id."""
    
    def __init__(self, default_service: Optional[VannaService] = None):
        self._tenant_services: Dict[str, VannaService] = {}
        self._tenant_configs: Dict[str, dict] = {}  # Store tenant configurations
        self._default_service = default_service
    
    def register_tenant(self, tenant_id: str, db_config: dict):
        """Register a tenant with their database configuration."""
        self._tenant_configs[tenant_id] = db_config
        print(f"Registered tenant: {tenant_id}")
    
    def get_service(self, tenant_id: Optional[str] = None) -> VannaService:
        """
        Get VannaService for a tenant. Creates if doesn't exist.
        
        Args:
            tenant_id: Tenant identifier. If None, returns default service.
            
        Returns:
            VannaService instance for the tenant
        """
        if tenant_id is None:
            if self._default_service is None:
                raise RuntimeError("No default service available")
            return self._default_service
        
        # Check if service already exists for this tenant
        if tenant_id not in self._tenant_services:
            # Check if we have config for this tenant
            if tenant_id not in self._tenant_configs:
                raise ValueError(f"No database configuration found for tenant: {tenant_id}")
            
            # Create new service for this tenant
            db_config = self._tenant_configs[tenant_id]
            print(f"Creating VannaService for tenant: {tenant_id}")
            self._tenant_services[tenant_id] = VannaService(database_config=db_config)
        
        return self._tenant_services[tenant_id]
    
    def get_tenant_list(self) -> list:
        """Get list of registered tenant IDs."""
        return list(self._tenant_configs.keys())
    
    def remove_tenant(self, tenant_id: str):
        """Remove a tenant and cleanup their service."""
        if tenant_id in self._tenant_services:
            service = self._tenant_services.pop(tenant_id)
            if hasattr(service, 'close'):
                try:
                    service.close()
                    print(f"Closed service for tenant: {tenant_id}")
                except Exception as e:
                    print(f"Warning: Error closing service for tenant {tenant_id}: {e}")
        
        if tenant_id in self._tenant_configs:
            self._tenant_configs.pop(tenant_id)
            print(f"Removed tenant configuration: {tenant_id}")
    
    def cleanup_all(self):
        """Cleanup all tenant services. Call this on app shutdown."""
        print(f"Cleaning up {len(self._tenant_services)} tenant services...")
        for tenant_id, service in self._tenant_services.items():
            if hasattr(service, 'close'):
                try:
                    service.close()
                    print(f"Closed service for tenant: {tenant_id}")
                except Exception as e:
                    print(f"Warning: Error closing service for tenant {tenant_id}: {e}")
        
        self._tenant_services.clear()
        self._tenant_configs.clear()
    
    def get_stats(self) -> dict:
        """Get statistics about tenant services."""
        return {
            "registered_tenants": len(self._tenant_configs),
            "active_services": len(self._tenant_services),
            "tenant_list": self.get_tenant_list()
        }


# Global service manager instance
service_manager = ServiceManager()