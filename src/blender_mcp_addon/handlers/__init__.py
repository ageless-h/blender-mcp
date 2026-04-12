# -*- coding: utf-8 -*-
"""Handler system for unified data CRUD operations."""
from __future__ import annotations

from .base import BaseHandler, GenericCollectionHandler
from .registry import HandlerRegistry
from .response import _error, _ok
from .types import DataType

__all__ = ["DataType", "BaseHandler", "GenericCollectionHandler", "HandlerRegistry", "_ok", "_error"]
