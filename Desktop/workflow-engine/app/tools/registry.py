"""
Tool Registry - Simple function registry for workflow tools
"""
from typing import Callable, Dict, Any
import inspect


class ToolRegistry:
    """Registry for workflow tools"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._descriptions: Dict[str, str] = {}
    
    def register(self, name: str, func: Callable, description: str = ""):
        """Register a tool"""
        self._tools[name] = func
        self._descriptions[name] = description or inspect.getdoc(func) or ""
        
    def get(self, name: str) -> Callable:
        """Get a tool by name"""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def has(self, name: str) -> bool:
        """Check if tool exists"""
        return name in self._tools
    
    def list_tools(self) -> Dict[str, str]:
        """List all registered tools with descriptions"""
        return {
            name: self._descriptions[name]
            for name in self._tools.keys()
        }
    
    def call(self, name: str, *args, **kwargs) -> Any:
        """Call a tool by name"""
        tool = self.get(name)
        return tool(*args, **kwargs)


# Global registry instance
registry = ToolRegistry()


# Decorator for easy registration
def tool(name: str = None, description: str = ""):
    """Decorator to register a function as a tool"""
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        registry.register(tool_name, func, description)
        return func
    return decorator