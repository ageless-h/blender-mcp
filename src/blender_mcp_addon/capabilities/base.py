# -*- coding: utf-8 -*-
"""Base capability dispatcher and helpers.

Routes blender.* capabilities through a four-tier handler architecture:
- Perception: 11 read-only tools
- Declarative: 3 node/animation/sequencer editors
- Imperative: 9 object/material/modifier/etc managers
- Fallback: 3 operator/script/import_export handlers
"""

from __future__ import annotations

import time
from typing import Any, Callable

from ..handlers import data as _data_handlers  # noqa: F401 - Import to register handlers
from ..handlers.response import _error
from .declarative import DECLARATIVE_HANDLERS
from .fallback import FALLBACK_HANDLERS
from .imperative import IMPERATIVE_HANDLERS
from .perception import PERCEPTION_HANDLERS

# ---------------------------------------------------------------
# Capability dispatch registry
# ---------------------------------------------------------------

_CAPABILITY_HANDLERS: dict[str, Callable[[dict[str, Any], float], dict[str, Any]]] = {
    **PERCEPTION_HANDLERS,
    **DECLARATIVE_HANDLERS,
    **IMPERATIVE_HANDLERS,
    **FALLBACK_HANDLERS,
}


def _dispatch_new_capability(capability: str, payload: dict[str, Any], started: float) -> dict[str, Any]:
    """Dispatch blender.* capabilities via four-tier handler registry.

    Handlers are organized by layer: Perception, Declarative, Imperative, Fallback.
    Each handler is imported lazily if it requires bpy access.
    """
    handler = _CAPABILITY_HANDLERS.get(capability)
    if handler is not None:
        return handler(payload, started)
    return _error(
        code="unsupported_capability",
        message=f"capability '{capability}' not found in handler registry",
        data={"capability": capability},
        started=started,
    )


_WRITE_CAPABILITIES = frozenset(
    {
        "blender.edit_nodes",
        "blender.edit_animation",
        "blender.edit_sequencer",
        "blender.create_object",
        "blender.modify_object",
        "blender.manage_material",
        "blender.manage_modifier",
        "blender.manage_collection",
        "blender.manage_uv",
        "blender.manage_constraints",
        "blender.manage_physics",
        "blender.setup_scene",
        "blender.execute_operator",
        "blender.execute_script",
        "blender.import_export",
    }
)


def _push_undo_step(capability: str) -> None:
    """Push an undo step so Ctrl+Z can revert the MCP operation."""
    try:
        import bpy  # type: ignore

        bpy.ops.ed.undo_push(message=f"MCP: {capability}")
    except (AttributeError, RuntimeError):
        pass


def execute_capability(request: dict[str, Any]) -> dict[str, Any]:
    """Execute a capability request and return the result.

    Supports internal capabilities (data.*, operator.execute, info.query,
    script.execute) and new blender.* capabilities from the 26-tool architecture.

    Write capabilities are wrapped with an undo-push so that every MCP
    mutation can be reverted with Ctrl+Z in Blender.
    """
    started = time.perf_counter()
    try:
        if not isinstance(request, dict):
            return _error(
                code="invalid_request",
                message="request must be a dict",
                data={"type": type(request).__name__},
                started=started,
            )

        capability = request.get("capability")
        if not isinstance(capability, str) or not capability.strip():
            return _error(
                code="invalid_request",
                message="missing or invalid 'capability'",
                data={"capability": capability},
                started=started,
            )

        payload = request.get("payload", {})
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            return _error(
                code="invalid_request",
                message="'payload' must be a dict",
                data={"type": type(payload).__name__},
                started=started,
            )

        if capability.startswith("blender."):
            if capability in _WRITE_CAPABILITIES:
                _push_undo_step(capability)
            return _dispatch_new_capability(capability, payload, started)

        return _error(
            code="unsupported_capability",
            message="capability is not supported by this addon",
            data={"capability": capability},
            started=started,
        )
    except Exception as exc:  # noqa: BLE001 — top-level fallback for all capability handlers
        import traceback

        tb = traceback.format_exc()
        return _error(
            code="addon_exception",
            message=f"unhandled: {type(exc).__name__}: {exc}",
            data={"traceback": tb},
            started=started,
        )
