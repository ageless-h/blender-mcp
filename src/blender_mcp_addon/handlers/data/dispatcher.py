# -*- coding: utf-8 -*-
"""Dispatcher for data.* tool operations."""

from __future__ import annotations

import logging
import unicodedata
from typing import Any

from ..error_codes import ErrorCode
from ..registry import HandlerRegistry
from ..response import (
    _error,
    _ok,
    bpy_unavailable_error,
    check_bpy_available,
    invalid_params_error,
    not_found_error,
    operation_failed_error,
    unsupported_type_error,
)

logger = logging.getLogger(__name__)


def _resolve_handler(payload: dict[str, Any], started: float) -> tuple[Any, str, dict[str, Any] | None]:
    """Common preamble: check bpy, parse type, look up handler.

    Returns:
        (handler, type_str, error_response_or_None)
    """
    available, _ = check_bpy_available()
    if not available:
        return None, "", bpy_unavailable_error(started)

    type_str = payload.get("type", "")
    if not type_str:
        return None, "", invalid_params_error("'type' parameter is required", started)

    data_type = HandlerRegistry.parse_type(type_str)
    if data_type is None:
        return None, type_str, unsupported_type_error(type_str, started)

    handler = HandlerRegistry.get(data_type)
    if handler is None:
        return None, type_str, unsupported_type_error(type_str, started)

    return handler, type_str, None


def data_create(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute data.create operation."""
    handler, type_str, err = _resolve_handler(payload, started)
    if err is not None:
        return err

    name = payload.get("name")
    if not name:
        return invalid_params_error("'name' parameter is required", started)

    # Backward compatibility: earlier drafts used "data" to pass creation params.
    params = payload.get("params") if payload.get("params") is not None else payload.get("data", {})
    if params is None:
        params = {}

    try:
        result = handler.create(unicodedata.normalize("NFC", name), params)
        return _ok(result=result, started=started)
    except (AttributeError, KeyError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("data.create", exc, started)


def data_read(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute data.read operation."""
    handler, type_str, err = _resolve_handler(payload, started)
    if err is not None:
        return err

    name = payload.get("name", "")
    if name:
        name = unicodedata.normalize("NFC", name)
    path = payload.get("path")
    params = payload.get("params", {})

    try:
        result = handler.read(name, path, params)
        return _ok(result=result, started=started)
    except KeyError:
        return not_found_error(type_str, name, started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("data.read", exc, started)


def data_write(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute data.write operation."""
    handler, type_str, err = _resolve_handler(payload, started)
    if err is not None:
        return err

    name = payload.get("name", "")
    if name:
        name = unicodedata.normalize("NFC", name)
    properties = payload.get("properties", {})
    params = payload.get("params", {})

    if not properties:
        return invalid_params_error("'properties' parameter is required", started)

    try:
        result = handler.write(name, properties, params)
        result["success"] = True
        return _ok(result=result, started=started)
    except KeyError:
        return not_found_error(type_str, name, started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("data.write", exc, started)


def data_delete(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute data.delete operation."""
    handler, type_str, err = _resolve_handler(payload, started)
    if err is not None:
        return err

    name = payload.get("name")
    if not name:
        return invalid_params_error("'name' parameter is required", started)

    name = unicodedata.normalize("NFC", name)
    params = payload.get("params", {})

    try:
        result = handler.delete(name, params)
        result["success"] = True
        return _ok(result=result, started=started)
    except KeyError:
        return not_found_error(type_str, name, started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("data.delete", exc, started)


def data_list(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute data.list operation."""
    handler, type_str, err = _resolve_handler(payload, started)
    if err is not None:
        return err

    filter_params = payload.get("filter", {})

    try:
        result = handler.list_items(filter_params)
        return _ok(result=result, started=started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("data.list", exc, started)


def data_link(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute data.link operation.

    Links or unlinks data blocks. The source is linked to the target.

    Payload:
        source: {"type": str, "name": str} - The data block to link
        target: {"type": str, "name": str} - The target to link to
        unlink: bool - If True, unlink instead of link (default: False)
        params: dict - Additional parameters for the link operation
    """
    available, _ = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    source = payload.get("source")
    if not source or not isinstance(source, dict):
        return invalid_params_error("'source' parameter is required and must be a dict", started)

    target = payload.get("target")
    if not target or not isinstance(target, dict):
        return invalid_params_error("'target' parameter is required and must be a dict", started)

    source_type_str = source.get("type")
    source_name = source.get("name")
    if not source_type_str or not source_name:
        return invalid_params_error("source must have 'type' and 'name'", started)

    source_name = unicodedata.normalize("NFC", source_name)

    target_type_str = target.get("type")
    target_name = target.get("name")
    if not target_type_str or not target_name:
        return invalid_params_error("target must have 'type' and 'name'", started)

    target_name = unicodedata.normalize("NFC", target_name)

    source_type = HandlerRegistry.parse_type(source_type_str)
    if source_type is None:
        return unsupported_type_error(source_type_str, started)

    target_type = HandlerRegistry.parse_type(target_type_str)
    if target_type is None:
        return unsupported_type_error(target_type_str, started)

    handler = HandlerRegistry.get(source_type)
    if handler is None:
        return unsupported_type_error(source_type_str, started)

    unlink = payload.get("unlink", False)
    params = payload.get("params", {})

    try:
        result = handler.link(source_name, target_type, target_name, unlink, params)
        if "error" in result:
            return _error(
                code=ErrorCode.LINK_FAILED,
                message=result["error"],
                started=started,
            )
        result["success"] = True
        return _ok(result=result, started=started)
    except KeyError as exc:
        return _error(
            code=ErrorCode.NOT_FOUND,
            message=str(exc),
            started=started,
        )
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("data.link", exc, started)
