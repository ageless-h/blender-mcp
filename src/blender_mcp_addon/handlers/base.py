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


class GenericCollectionHandler(BaseHandler):
    """Concrete base class providing default CRUD for simple bpy.data collection handlers.

    Subclasses MUST:
    - Set the ``data_type`` class attribute
    - Implement ``create()``
    - Override ``_read_summary(item)``

    Subclasses MAY override:
    - ``_list_fields(item)`` — fields returned per item in ``list_items()``
    - ``_filter_item(item, filter_params)`` — filter items in ``list_items()``
    - ``_custom_write(item, prop_path, value)`` — handle special properties in ``write()``
    - ``_type_label()`` — human-readable name for error messages
    - ``write()`` / ``delete()`` / ``list_items()`` — for non-standard logic
    """

    # ── Override hooks ────────────────────────────────────────────

    def _read_summary(self, item: Any) -> dict[str, Any]:
        """Return the dict of fields for a full read (no path).

        Subclasses MUST override this method.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must override _read_summary()"
        )

    def _list_fields(self, item: Any) -> dict[str, Any]:
        """Return the dict of fields for each item in ``list_items()``.

        Default returns ``{"name": item.name}``.  Override to add fields.
        """
        return {"name": item.name}

    def _filter_item(self, item: Any, filter_params: dict[str, Any]) -> bool:
        """Return whether *item* should be included in ``list_items()``.

        Default returns ``True`` (include all).  Override to implement
        type-specific filtering (e.g., by light_type or texture type).
        """
        return True

    def _custom_write(self, item: Any, prop_path: str, value: Any) -> bool:
        """Handle a special property write, returning ``True`` if handled.

        Called by ``write()`` for each property before falling back to
        ``_set_nested_attr()``.  If this method returns ``True``, the
        property is considered written and ``_set_nested_attr()`` is skipped.

        Default returns ``False`` (all properties fall through).
        """
        return False

    def _type_label(self) -> str:
        """Human-readable type name used in error messages.

        Default capitalises ``data_type.value``.
        """
        return self.data_type.value.replace("_", " ").capitalize()

    # ── Default CRUD implementations ─────────────────────────────

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read properties from a data block.

        If *path* is given, delegates to ``_get_nested_attr``.
        Otherwise returns ``_read_summary(item)``.
        """
        item = self.get_item(name)
        if item is None:
            raise KeyError(f"{self._type_label()} '{name}' not found")

        if path:
            value = self._get_nested_attr(item, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "path": path, "value": value}

        return self._read_summary(item)

    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to a data block using ``_set_nested_attr``."""
        item = self.get_item(name)
        if item is None:
            raise KeyError(f"{self._type_label()} '{name}' not found")

        modified: list[str] = []
        for prop_path, value in properties.items():
            if not self._custom_write(item, prop_path, value):
                self._set_nested_attr(item, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a data block from the bpy.data collection."""
        item = self.get_item(name)
        if item is None:
            raise KeyError(f"{self._type_label()} '{name}' not found")

        collection = self.get_collection()
        collection.remove(item)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all data blocks, using ``_list_fields`` per item."""
        collection = self.get_collection()
        if collection is None:
            return {"items": [], "count": 0}

        filter_params = filter_params or {}
        items = [
            self._list_fields(item)
            for item in collection
            if self._filter_item(item, filter_params)
        ]
        return {"items": items, "count": len(items)}
