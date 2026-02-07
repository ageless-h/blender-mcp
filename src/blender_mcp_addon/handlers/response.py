# -*- coding: utf-8 -*-
"""Unified response format helpers for handler operations."""
from __future__ import annotations

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
) -> dict[str, Any]:
    """Create an error response.
    
    Args:
        code: Error code (e.g., "not_found", "invalid_params")
        message: Human-readable error message
        started: The start time from time.perf_counter()
        data: Optional additional error data
        
    Returns:
        Standard error response dict with ok=False
    """
    return {
        "ok": False,
        "result": None,
        "error": {"code": code, "message": message, "data": data},
        "timing_ms": (time.perf_counter() - started) * 1000.0,
    }


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
    )
