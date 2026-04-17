# -*- coding: utf-8 -*-
"""Unified response format helpers for handler operations."""

from __future__ import annotations

import functools
import time
from typing import Any

from .error_codes import ErrorCode


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

    Args:
        code: Error code string or ErrorCode enum value
        message: Human-readable error message
        started: The start time from time.perf_counter()
        data: Optional additional data about the error
        suggestion: Optional suggestion for how to resolve the error

    If *suggestion* is not provided, looks up a default suggestion from
    ``error_codes.DEFAULT_SUGGESTIONS`` using *code*.
    """
    from .error_codes import DEFAULT_SUGGESTIONS, ErrorCode

    code_str = code.value if isinstance(code, ErrorCode) else code
    resolved_suggestion = suggestion if suggestion is not None else DEFAULT_SUGGESTIONS.get(code_str)

    err: dict[str, Any] = {"code": code_str, "message": message, "data": data}
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
    return _error(
        code=ErrorCode.BPY_UNAVAILABLE,
        message="bpy is not available; this entrypoint must run inside Blender",
        started=started,
    )


def not_found_error(
    data_type: str,
    name: str,
    started: float,
) -> dict[str, Any]:
    return _error(
        code=ErrorCode.NOT_FOUND,
        message=f"{data_type} '{name}' not found",
        data={"type": data_type, "name": name},
        started=started,
    )


def invalid_params_error(
    message: str,
    started: float,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _error(
        code=ErrorCode.INVALID_PARAMS,
        message=message,
        data=data,
        started=started,
    )


def operation_failed_error(
    operation: str,
    exc: Exception,
    started: float,
) -> dict[str, Any]:
    exc_message = str(exc)
    if len(exc_message) > 500:
        exc_message = exc_message[:500] + "..."
    return _error(
        code=ErrorCode.OPERATION_FAILED,
        message=f"{operation} failed: {exc_message}",
        data={"exception_type": type(exc).__name__},
        started=started,
    )


def unsupported_type_error(
    data_type: str,
    started: float,
) -> dict[str, Any]:
    return _error(
        code=ErrorCode.UNSUPPORTED_TYPE,
        message=f"No handler registered for type: {data_type}",
        data={"type": data_type},
        started=started,
    )
