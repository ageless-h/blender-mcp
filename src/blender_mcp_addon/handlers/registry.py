# -*- coding: utf-8 -*-
"""Handler registry for unified data CRUD operations."""

from __future__ import annotations

from typing import Type, TypeVar

from .base import BaseHandler
from .types import DataType

T = TypeVar("T", bound=BaseHandler)

# Type aliases for parse_type (module-level constant for performance)
_TYPE_ALIASES = {
    "gpencil": "grease_pencil",
    "meta": "metaball",
}


class HandlerRegistry:
    """Registry for data type handlers.

    Provides automatic registration via decorator and dispatch by DataType.

    Usage:
        @HandlerRegistry.register
        class ObjectHandler(BaseHandler):
            data_type = DataType.OBJECT
            ...

        # Later, dispatch to handler:
        handler = HandlerRegistry.get(DataType.OBJECT)
        result = handler.read("Cube", None, {})
    """

    _handlers: dict[DataType, BaseHandler] = {}
    _handler_classes: dict[DataType, Type[BaseHandler]] = {}

    @classmethod
    def register(cls, handler_class: Type[T]) -> Type[T]:
        """Decorator to register a handler class.

        The handler class must have a `data_type` class attribute.

        Args:
            handler_class: The handler class to register

        Returns:
            The same handler class (for decorator chaining)

        Raises:
            ValueError: If handler_class doesn't have data_type attribute
            ValueError: If a handler is already registered for the data type
        """
        if not hasattr(handler_class, "data_type"):
            raise ValueError(f"Handler class {handler_class.__name__} must have a 'data_type' attribute")

        data_type = handler_class.data_type
        if not isinstance(data_type, DataType):
            raise ValueError(
                f"Handler class {handler_class.__name__}.data_type must be a DataType enum, "
                f"got {type(data_type).__name__}"
            )

        if data_type in cls._handler_classes:
            existing = cls._handler_classes[data_type]
            raise ValueError(
                f"Handler already registered for {data_type.value}: {existing.__name__}. "
                f"Cannot register {handler_class.__name__}"
            )

        cls._handler_classes[data_type] = handler_class
        return handler_class

    @classmethod
    def get(cls, data_type: DataType) -> BaseHandler | None:
        """Get the handler instance for a data type.

        Handlers are instantiated lazily on first access.

        Args:
            data_type: The DataType to get handler for

        Returns:
            The handler instance, or None if not registered
        """
        if data_type in cls._handlers:
            return cls._handlers[data_type]

        handler_class = cls._handler_classes.get(data_type)
        if handler_class is None:
            return None

        handler = handler_class()
        cls._handlers[data_type] = handler
        return handler

    @classmethod
    def get_or_error(cls, data_type: DataType) -> BaseHandler:
        """Get the handler instance for a data type, raising if not found.

        Args:
            data_type: The DataType to get handler for

        Returns:
            The handler instance

        Raises:
            KeyError: If no handler is registered for the data type
        """
        handler = cls.get(data_type)
        if handler is None:
            raise KeyError(f"No handler registered for type: {data_type.value}")
        return handler

    @classmethod
    def is_registered(cls, data_type: DataType) -> bool:
        """Check if a handler is registered for a data type.

        Args:
            data_type: The DataType to check

        Returns:
            True if a handler is registered
        """
        return data_type in cls._handler_classes

    @classmethod
    def registered_types(cls) -> list[DataType]:
        """Get all registered data types.

        Returns:
            List of registered DataType values
        """
        return list(cls._handler_classes.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered handlers.

        Primarily for testing purposes.
        """
        cls._handlers.clear()
        cls._handler_classes.clear()

    @classmethod
    def parse_type(cls, type_str: str) -> DataType | None:
        """Parse a type string to DataType enum.

        Args:
            type_str: String representation of the type (e.g., "object", "mesh")

        Returns:
            The DataType enum value, or None if invalid
        """
        normalized = type_str.lower()
        normalized = _TYPE_ALIASES.get(normalized, normalized)
        try:
            return DataType(normalized)
        except ValueError:
            return None
