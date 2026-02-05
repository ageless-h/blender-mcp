# -*- coding: utf-8 -*-
"""Base handler abstract class for unified data CRUD operations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .types import DataType


class BaseHandler(ABC):
    """Abstract base class for data type handlers.
    
    Each handler implements CRUD operations for a specific DataType.
    Handlers are registered with the HandlerRegistry using the @register decorator.
    
    Subclasses must:
    - Set the `data_type` class attribute to the handled DataType
    - Implement create(), read(), write(), delete(), list_items() methods
    """
    
    data_type: DataType
    
    @abstractmethod
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new data block.
        
        Args:
            name: Name for the new data block
            params: Creation parameters specific to the data type
            
        Returns:
            Dict with 'name', 'type', and creation details
        """
        ...
    
    @abstractmethod
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read properties from a data block.
        
        Args:
            name: Name of the data block to read
            path: Optional dot-separated property path to read specific property
            params: Read parameters (e.g., format for images)
            
        Returns:
            Dict with requested properties
        """
        ...
    
    @abstractmethod
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to a data block.
        
        Args:
            name: Name of the data block to modify
            properties: Dict of property paths to values
            params: Write parameters
            
        Returns:
            Dict with 'modified' list of changed properties
        """
        ...
    
    @abstractmethod
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a data block.
        
        Args:
            name: Name of the data block to delete
            params: Deletion parameters
            
        Returns:
            Dict with 'deleted' name
        """
        ...
    
    @abstractmethod
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all data blocks of this type.
        
        Args:
            filter_params: Optional filter criteria
            
        Returns:
            Dict with 'items' list of data block info
        """
        ...
    
    def link(
        self,
        source_name: str,
        target_type: DataType,
        target_name: str,
        unlink: bool = False,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Link or unlink this data block to/from a target.
        
        Default implementation returns an error. Override in handlers
        that support linking (e.g., ObjectHandler, MaterialHandler).
        
        Args:
            source_name: Name of this data block
            target_type: Type of the target data block
            target_name: Name of the target data block
            unlink: If True, unlink instead of link
            params: Additional parameters
            
        Returns:
            Dict with 'action' ('link' or 'unlink') and result
        """
        return {
            "error": f"Link operation not supported for type {self.data_type.value}"
        }
    
    def get_collection(self) -> Any:
        """Get the bpy.data collection for this handler's data type.
        
        Returns:
            The bpy.data.<collection> for this type, or None for pseudo-types
        """
        try:
            import bpy  # type: ignore
        except ImportError:
            return None
        
        from .types import get_collection_name, is_pseudo_type
        
        if is_pseudo_type(self.data_type):
            return None
        
        collection_name = get_collection_name(self.data_type)
        if collection_name is None:
            return None
        
        return getattr(bpy.data, collection_name, None)
    
    def get_item(self, name: str) -> Any:
        """Get a data block by name from the collection.
        
        Args:
            name: Name of the data block
            
        Returns:
            The data block, or None if not found
        """
        collection = self.get_collection()
        if collection is None:
            return None
        return collection.get(name)
    
    def _get_nested_attr(self, obj: Any, path: str) -> Any:
        """Get a nested attribute using dot-separated path.
        
        Args:
            obj: The root object
            path: Dot-separated attribute path (e.g., "location.x")
            
        Returns:
            The attribute value
            
        Raises:
            AttributeError: If path is invalid
        """
        current = obj
        for part in path.split("."):
            if hasattr(current, part):
                current = getattr(current, part)
            elif hasattr(current, "__getitem__"):
                try:
                    current = current[part]
                except (KeyError, IndexError, TypeError):
                    current = current[int(part)]
            else:
                raise AttributeError(f"Cannot access '{part}' on {type(current).__name__}")
        return current
    
    def _set_nested_attr(self, obj: Any, path: str, value: Any) -> None:
        """Set a nested attribute using dot-separated path.
        
        Args:
            obj: The root object
            path: Dot-separated attribute path (e.g., "location.x")
            value: The value to set
            
        Raises:
            AttributeError: If path is invalid
        """
        parts = path.split(".")
        current = obj
        for part in parts[:-1]:
            if hasattr(current, part):
                current = getattr(current, part)
            elif hasattr(current, "__getitem__"):
                try:
                    current = current[part]
                except (KeyError, IndexError, TypeError):
                    current = current[int(part)]
            else:
                raise AttributeError(f"Cannot access '{part}' on {type(current).__name__}")
        
        final_attr = parts[-1]
        if hasattr(current, final_attr):
            setattr(current, final_attr, value)
        elif hasattr(current, "__setitem__"):
            try:
                current[final_attr] = value
            except (KeyError, IndexError, TypeError):
                current[int(final_attr)] = value
        else:
            raise AttributeError(f"Cannot set '{final_attr}' on {type(current).__name__}")
