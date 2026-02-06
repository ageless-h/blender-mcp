# -*- coding: utf-8 -*-
"""Base capability dispatcher and helpers."""
from __future__ import annotations

import time
from typing import Any

from .scene import scene_read, scene_write

from ..handlers.data.dispatcher import (
    data_create,
    data_delete,
    data_link,
    data_list,
    data_read,
    data_write,
)
from ..handlers.info import info_query
from ..handlers.operator import operator_execute
from ..handlers.response import _error
from ..handlers.script import script_execute

from ..handlers import data as _data_handlers  # noqa: F401 - Import to register handlers


def execute_capability(request: dict[str, Any]) -> dict[str, Any]:
    """Execute a capability request and return the result.
    
    Supports both legacy capabilities (scene.read, scene.write) and
    new unified tools (data.*, operator.execute, info.query, script.execute).
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

        # New unified tools
        if capability == "data.create":
            return data_create(payload, started=started)
        if capability == "data.read":
            return data_read(payload, started=started)
        if capability == "data.write":
            return data_write(payload, started=started)
        if capability == "data.delete":
            return data_delete(payload, started=started)
        if capability == "data.list":
            return data_list(payload, started=started)
        if capability == "data.link":
            return data_link(payload, started=started)
        if capability == "operator.execute":
            return operator_execute(payload, started=started)
        if capability == "info.query":
            return info_query(payload, started=started)
        if capability == "script.execute":
            return script_execute(payload, started=started)

        # Legacy capabilities (deprecated, will be removed in future)
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
            data={"type": type(exc).__name__, "message": str(exc)},
            started=started,
        )
