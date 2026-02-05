# -*- coding: utf-8 -*-
"""Handler system for unified data CRUD operations."""
from __future__ import annotations

from .types import DataType
from .base import BaseHandler
from .registry import HandlerRegistry
from .response import _ok, _error

__all__ = ["DataType", "BaseHandler", "HandlerRegistry", "_ok", "_error"]
