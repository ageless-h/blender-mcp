# -*- coding: utf-8 -*-
"""Base capability dispatcher and helpers."""
from __future__ import annotations

import time
from typing import Any

from .scene import scene_read, scene_write


def execute_capability(request: dict[str, Any]) -> dict[str, Any]:
    """Execute a capability request and return the result."""
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

        if capability == "scene.read":
            return scene_read(payload, started=started)
        if capability == "scene.write":
            return scene_write(payload, started=started)

        return _error(
            code="unsupported_capability",
            message="capability is not supported by this addon",
            data={"capability": capability},
            started=started,
        )
    except Exception as exc:
        return _error(
            code="addon_exception",
            message="unhandled addon exception",
            data={"type": type(exc).__name__},
            started=started,
        )


def _ok(*, result: dict[str, Any], started: float) -> dict[str, Any]:
    """Create a successful response."""
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
    """Create an error response."""
    return {
        "ok": False,
        "result": None,
        "error": {"code": code, "message": message, "data": data},
        "timing_ms": (time.perf_counter() - started) * 1000.0,
    }
