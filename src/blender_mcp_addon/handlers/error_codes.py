# -*- coding: utf-8 -*-
"""Unified error code definitions for all handler responses.

Every error response produced by _error() SHOULD use one of these codes.
This module serves as a single source of truth so that:
  - Client code can match on stable, documented strings.
  - New handlers stay consistent without inventing ad-hoc codes.
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    """All error codes used across blender_mcp_addon handlers.

    Categories:
      Environment  - runtime prerequisites not met
      Validation   - caller supplied bad input
      Lookup       - requested entity does not exist
      Execution    - operation started but failed
      Security     - action blocked by policy
    """

    # ── Environment ──────────────────────────────────────────────
    BPY_UNAVAILABLE = "bpy_unavailable"
    """bpy module not importable (not running inside Blender)."""

    # ── Validation ───────────────────────────────────────────────
    INVALID_PARAMS = "invalid_params"
    """Required parameter missing, wrong type, or out of range."""

    INVALID_OPERATOR = "invalid_operator"
    """Operator id does not resolve to a valid bpy.ops entry."""

    INVALID_REQUEST = "invalid_request"
    """Top-level request envelope is malformed."""

    UNSUPPORTED_TYPE = "unsupported_type"
    """No handler registered for the given data type."""

    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    """Capability name not recognised by the dispatch layer."""

    # ── Lookup ───────────────────────────────────────────────────
    NOT_FOUND = "not_found"
    """Named data-block, object, bone, strip, etc. does not exist."""

    # ── Execution ────────────────────────────────────────────────
    OPERATION_FAILED = "operation_failed"
    """Generic handler/operation failure (wraps exception)."""

    OPERATOR_ERROR = "operator_error"
    """bpy.ops.* returned an error or raised RuntimeError."""

    EXECUTION_ERROR = "execution_error"
    """Script execution produced a Python exception."""

    EXECUTION_TIMEOUT = "execution_timeout"
    """Script execution exceeded the allowed time limit."""

    LINK_FAILED = "link_failed"
    """data.link / collection link operation could not complete."""

    ADDON_EXCEPTION = "addon_exception"
    """Unhandled exception inside the addon layer."""

    # ── Security ─────────────────────────────────────────────────
    SCRIPT_DISABLED = "script_disabled"
    """blender_execute_script is disabled by admin policy."""

    CONSENT_REQUIRED = "consent_required"
    """Operation requires explicit user consent before proceeding."""


# ── Default suggestions for each error code ─────────────────────────
# These are automatically appended to error responses when the error
# code matches.  Callers can override by passing an explicit suggestion.

DEFAULT_SUGGESTIONS: dict[str, str] = {
    # Environment
    ErrorCode.BPY_UNAVAILABLE: "Ensure Blender is running with the MCP addon enabled.",
    # Validation
    ErrorCode.INVALID_PARAMS: "Check the tool description for required parameters and their types.",
    ErrorCode.INVALID_OPERATOR: "Use blender_execute_script to run custom Python instead, or verify the operator ID.",
    ErrorCode.INVALID_REQUEST: "Check the request format matches the MCP tool inputSchema.",
    ErrorCode.UNSUPPORTED_TYPE: "Use blender_get_objects to inspect the scene, then check available data types.",
    ErrorCode.UNSUPPORTED_CAPABILITY: "Use blender_get_scene to see what tools are available.",
    # Lookup
    ErrorCode.NOT_FOUND: "Use blender_get_objects or blender_get_collections to list available items first.",
    # Execution
    ErrorCode.OPERATION_FAILED: "Try blender_execute_script as a fallback, or check object mode and state.",
    ErrorCode.OPERATOR_ERROR: "The object may be in the wrong mode. Try switching mode first.",
    ErrorCode.EXECUTION_ERROR: "Check the Python traceback for details. Simplify the script.",
    ErrorCode.EXECUTION_TIMEOUT: "The script ran too long. Break it into smaller operations.",
    ErrorCode.LINK_FAILED: "Verify both source and target exist before linking.",
    ErrorCode.ADDON_EXCEPTION: "This is an internal error. Check the Blender system console for details.",
    # Security
    ErrorCode.SCRIPT_DISABLED: "Set MCP_ENABLE_SCRIPT_EXECUTE=true in environment variables to enable.",
    ErrorCode.CONSENT_REQUIRED: "This operation needs user approval in the Blender addon UI.",
}
