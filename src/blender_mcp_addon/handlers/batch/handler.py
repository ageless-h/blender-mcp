# -*- coding: utf-8 -*-
"""Batch operation handler — execute multiple operations in a single request."""

from __future__ import annotations

import logging
from typing import Any

from ..error_codes import ErrorCode
from ..response import _error, _ok, bpy_unavailable_error, check_bpy_available

logger = logging.getLogger(__name__)

_ALLOWED_TOOLS = frozenset(
    {
        "blender_create_object",
        "blender_modify_object",
        "blender_manage_material",
        "blender_manage_modifier",
        "blender_manage_collection",
        "blender_manage_uv",
        "blender_manage_constraints",
        "blender_manage_physics",
        "blender_setup_scene",
        "blender_edit_mesh",
        "blender_edit_nodes",
        "blender_edit_animation",
        "blender_edit_sequencer",
    }
)


def batch_execute(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute multiple operations in a single batch request.

    Args:
        payload: Batch parameters:
            - operations: List of operations to execute, each with:
                - tool: Tool name (e.g., "blender_create_object")
                - params: Tool parameters
            - stop_on_error: If True, stop on first error (default: True)
            - continue_on_error: If True, continue even on errors (default: False)

    Returns:
        Dict with batch result info including individual operation results
    """
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    operations = payload.get("operations", [])
    if not operations:
        return _error(code=ErrorCode.INVALID_PARAMS, message="operations is required", started=started)

    stop_on_error = payload.get("stop_on_error", True)
    continue_on_error = payload.get("continue_on_error", False)
    if continue_on_error:
        stop_on_error = False

    results = []
    success_count = 0
    error_count = 0

    for i, op in enumerate(operations):
        tool_name = op.get("tool", "")
        params = op.get("params", {})

        if not tool_name:
            error_count += 1
            results.append({"index": i, "ok": False, "error": "tool name is required"})
            if stop_on_error:
                break
            continue

        if tool_name not in _ALLOWED_TOOLS:
            error_count += 1
            results.append({"index": i, "ok": False, "error": f"tool '{tool_name}' not allowed in batch"})
            if stop_on_error:
                break
            continue

        try:
            result = _execute_single_tool(bpy, tool_name, params)
            if result.get("ok", False):
                success_count += 1
                results.append({"index": i, "ok": True, "result": result.get("result")})
            else:
                error_count += 1
                results.append(
                    {"index": i, "ok": False, "error": result.get("error", {}).get("message", "Unknown error")}
                )
                if stop_on_error:
                    break
        except Exception as exc:
            error_count += 1
            results.append({"index": i, "ok": False, "error": str(exc)})
            if stop_on_error:
                break

    return _ok(
        result={
            "total": len(operations),
            "executed": len(results),
            "success_count": success_count,
            "error_count": error_count,
            "results": results,
        },
        started=started,
    )


def _execute_single_tool(bpy: Any, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
    import time

    from ...capabilities.declarative import DECLARATIVE_HANDLERS
    from ...capabilities.imperative import IMPERATIVE_HANDLERS

    started = time.perf_counter()

    internal_cap = tool_name.replace("blender_", "blender.")

    if internal_cap in IMPERATIVE_HANDLERS:
        return IMPERATIVE_HANDLERS[internal_cap](params, started)

    if internal_cap in DECLARATIVE_HANDLERS:
        return DECLARATIVE_HANDLERS[internal_cap](params, started)

    return {"ok": False, "error": {"message": f"Tool '{tool_name}' handler not found"}}
