# -*- coding: utf-8 -*-
"""Capability catalog test utilities.

Moved from src/blender_mcp/catalog/ as it was only used by tests.
"""

from __future__ import annotations

from .catalog import (
    CapabilityCatalog,
    CapabilityMeta,
    capability_availability,
    capability_scope_map,
    capability_to_dict,
    minimal_capability_set,
    new_tool_scope_map,
)

__all__ = [
    "CapabilityCatalog",
    "CapabilityMeta",
    "capability_availability",
    "capability_scope_map",
    "capability_to_dict",
    "minimal_capability_set",
    "new_tool_scope_map",
]
