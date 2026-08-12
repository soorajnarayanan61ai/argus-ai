"""
Dynamic Plugin & Module Manager for ARGUS AI Platform.
Discovers and registers pluggable modules implementing BaseModule without changing existing core code.
"""
from typing import Dict, List, Type
from modules.base_module import BaseModule
from core.logger import logger
from core.exceptions import PluginException


class PluginManager:
    """Singleton Plugin Discovery & Registry Engine."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginManager, cls).__new__(cls)
            cls._instance._modules: Dict[str, BaseModule] = {}
            cls._instance._initialized = False
        return cls._instance

    def register_module(self, module_instance: BaseModule) -> None:
        """Register a module instance into the platform registry."""
        if not isinstance(module_instance, BaseModule):
            raise PluginException(f"Module {type(module_instance)} must inherit from BaseModule.")

        mod_id = module_instance.module_id
        if mod_id in self._modules:
            logger.warning(f"Module '{mod_id}' is being re-registered.")

        module_instance.initialize()
        self._modules[mod_id] = module_instance
        logger.info(f"Registered Pluggable Module: [{mod_id}] '{module_instance.name}' (Order: {module_instance.order})")

    def get_module(self, module_id: str) -> BaseModule:
        """Get registered module instance by ID."""
        if module_id not in self._modules:
            raise PluginException(f"Module '{module_id}' is not registered.")
        return self._modules[module_id]

    def list_modules(self) -> List[BaseModule]:
        """Return registered modules ordered by display order."""
        return sorted(self._modules.values(), key=lambda m: m.order)

    def get_module_menu(self) -> List[dict]:
        """Return navigation menu items for sidebar rendering."""
        return [
            {
                "id": m.module_id,
                "name": m.name,
                "icon": m.icon,
                "category": m.category,
            }
            for m in self.list_modules()
        ]


# Singleton instance
plugin_manager = PluginManager()
