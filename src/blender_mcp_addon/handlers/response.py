# -*- coding: utf-8 -*-
"""Unified response format helpers for handler operations."""

from __future__ import annotations

import functools
import time
from typing import Any


def _ok(*, result: dict[str, Any], started: float) -> dict[str, Any]:
    """Create a successful response.

    Args:
        result: The result data to include
        started: The start time from time.perf_counter()

    Returns:
        Standard success response dict with ok=True
    """
    return {
        "ok": True,
        "result": result,
        "error": None,
        "timing_ms": (time.perf_counter() - started) * 1000.0,
    }


def _error(
    *,
    code: str,
    message: str,
    started: float,
    data: dict[str, Any] | None = None,
    suggestion: str | None = None,
) -> dict[str, Any]:
    """Create an error response.

    If *suggestion* is not provided, looks up a default suggestion from
    ``error_codes.DEFAULT_SUGGESTIONS`` using *code*.
    """
    from .error_codes import DEFAULT_SUGGESTIONS

    resolved_suggestion = suggestion if suggestion is not None else DEFAULT_SUGGESTIONS.get(code)

    err: dict[str, Any] = {"code": code, "message": message, "data": data}
    if resolved_suggestion is not None:
        err["suggestion"] = resolved_suggestion

    return {
        "ok": False,
        "result": None,
        "error": err,
        "timing_ms": (time.perf_counter() - started) * 1000.0,
    }


@functools.lru_cache(maxsize=1)
def check_bpy_available() -> tuple[bool, Any]:
    """Check if bpy is available and return it.

    Returns:
        Tuple of (is_available, bpy_module_or_None)
    """
    try:
        import bpy  # type: ignore

        return True, bpy
    except ImportError:
        return False, None


def bpy_unavailable_error(started: float) -> dict[str, Any]:
    """Create a standard error for when bpy is not available.

    Args:
        started: The start time from time.perf_counter()

    Returns:
        Error response indicating bpy is unavailable
    """
    return _error(
        code="bpy_unavailable",
        message="bpy is not available; this entrypoint must run inside Blender",
        started=started,
        suggestion="Ensure Blender is running with the MCP addon enabled.",
    )


def not_found_error(
    data_type: str,
    name: str,
    started: float,
) -> dict[str, Any]:
    """Create a standard error for when a data block is not found.

    Args:
        data_type: The type of data block
        name: The name that was not found
        started: The start time from time.perf_counter()

    Returns:
        Error response indicating the data was not found
    """
    return _error(
        code="not_found",
        message=f"{data_type} '{name}' not found",
        data={"type": data_type, "name": name},
        started=started,
        suggestion=f"Use blender_get_objects to list available {data_type}s, then retry with an exact name.",
    )


def invalid_params_error(
    message: str,
    started: float,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standard error for invalid parameters.

    Args:
        message: Description of the parameter error
        started: The start time from time.perf_counter()
        data: Optional additional data about the error

    Returns:
        Error response indicating invalid parameters
    """
    return _error(
        code="invalid_params",
        message=message,
        data=data,
        started=started,
    )


def operation_failed_error(
    operation: str,
    exc: Exception,
    started: float,
) -> dict[str, Any]:
    """Create a standard error for a failed operation.

    Args:
        operation: The operation that failed (e.g., "data.read")
        exc: The exception that was raised
        started: The start time from time.perf_counter()

    Returns:
        Error response indicating the operation failed
    """
    exc_message = str(exc)
    # Truncate overly long error messages to prevent info leakage
    if len(exc_message) > 500:
        exc_message = exc_message[:500] + "..."
    return _error(
        code="operation_failed",
        message=f"{operation} failed: {exc_message}",
        data={"exception_type": type(exc).__name__},
        started=started,
        suggestion=f"Try blender_execute_script as a fallback for {operation}, or check object mode/state.",
    )


def unsupported_type_error(
    data_type: str,
    started: float,
) -> dict[str, Any]:
    """Create a standard error for unsupported data type.

    Args:
        data_type: The unsupported type string
        started: The start time from time.perf_counter()

    Returns:
        Error response indicating the type is not supported
    """
    return _error(
        code="unsupported_type",
        message=f"No handler registered for type: {data_type}",
        data={"type": data_type},
        started=started,
        suggestion="Use blender_get_scene to inspect available data types and their names.",
    )
