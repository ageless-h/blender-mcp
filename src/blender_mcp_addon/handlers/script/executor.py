# -*- coding: utf-8 -*-
"""Script execution with security controls."""

from __future__ import annotations

import io
import sys
import threading
import time
import traceback
from typing import Any

from ..response import (
    _ok,
    _error,
    check_bpy_available,
    bpy_unavailable_error,
    invalid_params_error,
)

_script_config: dict[str, Any] = {
    "enabled": False,
    "default_timeout": 30,
    "require_consent": False,
    "audit_log_enabled": True,
}

_audit_log: list[dict[str, Any]] = []


def configure_script_execution(
    enabled: bool | None = None,
    default_timeout: int | None = None,
    require_consent: bool | None = None,
    audit_log_enabled: bool | None = None,
) -> None:
    """Configure script execution settings.

    Args:
        enabled: Enable/disable script.execute
        default_timeout: Default execution timeout in seconds
        require_consent: Require user consent before execution
        audit_log_enabled: Enable audit logging
    """
    if enabled is not None:
        _script_config["enabled"] = enabled
    if default_timeout is not None:
        _script_config["default_timeout"] = default_timeout
    if require_consent is not None:
        _script_config["require_consent"] = require_consent
    if audit_log_enabled is not None:
        _script_config["audit_log_enabled"] = audit_log_enabled


def is_script_execution_enabled() -> bool:
    """Check if script execution is enabled."""
    return _script_config["enabled"]


def get_audit_log(limit: int = 100) -> list[dict[str, Any]]:
    """Get recent audit log entries.

    Args:
        limit: Maximum number of entries to return

    Returns:
        List of audit log entries
    """
    return list(_audit_log[-limit:])


def clear_audit_log() -> None:
    """Clear the audit log."""
    _audit_log.clear()


def _log_execution(code: str, success: bool, result: Any, error: str | None, duration_ms: float) -> None:
    """Log script execution to audit log."""
    if not _script_config["audit_log_enabled"]:
        return

    entry = {
        "timestamp": time.time(),
        "code_preview": code[:200] + "..." if len(code) > 200 else code,
        "code_length": len(code),
        "success": success,
        "result_type": type(result).__name__ if result is not None else None,
        "error": error,
        "duration_ms": duration_ms,
    }
    _audit_log.append(entry)

    if len(_audit_log) > 1000:
        _audit_log[:] = _audit_log[-500:]


def script_execute(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute arbitrary Python code in Blender environment.

    Args:
        payload: Execution parameters:
            - code: Python code to execute
            - timeout: Execution timeout in seconds (default: 30)
        started: Start time for timing

    Returns:
        Response dict with execution result
    """
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    if not _script_config["enabled"]:
        return _error(
            code="script_disabled",
            message="script.execute is disabled. Enable it in security configuration to use this tool.",
            data={"config_key": "script_execute.enabled"},
            started=started,
        )

    if _script_config["require_consent"]:
        consent_granted = payload.get("consent_granted", False)
        if not consent_granted:
            return _error(
                code="consent_required",
                message="User consent is required before executing scripts. Set 'consent_granted: true' to proceed.",
                data={"warning": "This will execute arbitrary Python code in your Blender session."},
                started=started,
            )

    code = payload.get("code")
    if not code:
        return invalid_params_error("'code' parameter is required", started)

    if not isinstance(code, str):
        return invalid_params_error("'code' must be a string", started)

    raw_timeout = payload.get("timeout", _script_config["default_timeout"])
    if not isinstance(raw_timeout, (int, float)) or raw_timeout <= 0:
        raw_timeout = _script_config["default_timeout"]
    timeout = int(min(raw_timeout, 300))  # cap at 5 minutes

    exec_start = time.perf_counter()

    try:
        result = _execute_with_timeout(code, timeout, bpy)
        exec_duration = (time.perf_counter() - exec_start) * 1000.0

        _log_execution(code, True, result.get("return_value"), None, exec_duration)

        return _ok(
            result={
                "success": True,
                "return_value": result.get("return_value"),
                "output": result.get("output", ""),
                "execution_time_ms": exec_duration,
            },
            started=started,
        )
    except TimeoutError:
        exec_duration = (time.perf_counter() - exec_start) * 1000.0
        error_msg = f"Execution timeout after {timeout} seconds"
        _log_execution(code, False, None, error_msg, exec_duration)

        return _error(
            code="execution_timeout",
            message=error_msg,
            data={"timeout": timeout},
            started=started,
        )
    except Exception as exc:
        exec_duration = (time.perf_counter() - exec_start) * 1000.0
        error_msg = str(exc)
        tb = traceback.format_exc()
        _log_execution(code, False, None, error_msg, exec_duration)

        return _error(
            code="execution_error",
            message=f"Script execution failed: {error_msg}",
            data={"traceback": tb},
            started=started,
        )


def _execute_with_timeout(code: str, timeout: int, bpy: Any) -> dict[str, Any]:
    """Execute code with timeout control.

    Args:
        code: Python code to execute
        timeout: Timeout in seconds
        bpy: The bpy module

    Returns:
        Dict with return_value and output

    Raises:
        TimeoutError: If execution exceeds timeout
        Exception: If execution fails
    """
    result_container: dict[str, Any] = {
        "return_value": None,
        "output": "",
        "error": None,
    }

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    exec_globals = {
        "bpy": bpy,
        "__builtins__": __builtins__,
        "__name__": "__main__",
    }

    try:
        import bmesh

        exec_globals["bmesh"] = bmesh
    except ImportError:
        pass

    try:
        import mathutils

        exec_globals["mathutils"] = mathutils
    except ImportError:
        pass

    def execute_code():
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            try:
                compiled = compile(code, "<script>", "eval")
                result_container["return_value"] = eval(compiled, exec_globals)
            except SyntaxError:
                exec(code, exec_globals)
                if "_result" in exec_globals:
                    result_container["return_value"] = exec_globals["_result"]

            result_container["output"] = stdout_capture.getvalue() + stderr_capture.getvalue()
        except Exception as e:
            result_container["error"] = e
            result_container["output"] = stdout_capture.getvalue() + stderr_capture.getvalue()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    thread = threading.Thread(target=execute_code)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        raise TimeoutError(f"Script execution timed out after {timeout} seconds")

    if result_container["error"]:
        raise result_container["error"]

    return_value = result_container["return_value"]
    if return_value is not None:
        try:
            if hasattr(return_value, "__iter__") and not isinstance(return_value, (str, dict)):
                return_value = list(return_value)
            elif hasattr(return_value, "name"):
                return_value = f"<{type(return_value).__name__}: {return_value.name}>"
            elif not isinstance(return_value, (bool, int, float, str, list, dict, type(None))):
                return_value = str(return_value)
        except (TypeError, ValueError):
            return_value = str(return_value)

    return {
        "return_value": return_value,
        "output": result_container["output"],
    }
