# -*- coding: utf-8 -*-
"""MCP protocol adapter for Blender MCP server.

Implements the MCP JSON-RPC protocol with:
- 26 tools with flat parameters, hand-written schemas, and annotations
- 10 prompts (7 workflow + 3 strategy) for LLM guidance
"""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Configure logging level from MCP_LOG_LEVEL environment variable."""
    level_name = os.environ.get("MCP_LOG_LEVEL", "WARNING").upper()
    level = getattr(logging, level_name, logging.WARNING)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )


_PRETTY_JSON = os.environ.get("MCP_PRETTY_JSON", "").lower() in ("1", "true", "yes")


from blender_mcp.adapters.mock import MockAdapter
from blender_mcp.adapters.socket import SocketAdapter
from blender_mcp import __version__ as pkg_version
from blender_mcp.schemas.tools import TOOL_DEFINITIONS, get_tool
from blender_mcp.prompts.registry import (
    BLENDER_PROMPTS,
    get_prompt_messages,
)
from blender_mcp.security.allowlist import Allowlist
from blender_mcp.security.audit import (
    AuditEvent,
    JsonFileAuditLogger,
    MemoryAuditLogger,
)
from blender_mcp.security.guardrails import Guardrails
from blender_mcp.security.rate_limit import RateLimiter
from blender_mcp.telemetry import telemetry_tool


@dataclass
class MCPServer:
    """MCP protocol server with 26 tools, 10 prompts, and security pipeline.

    Security checks run in order on every tools/call:
      1. Allowlist  — is this capability permitted?
      2. Guardrails — payload size / depth / blocked-list
      3. Rate limit — per-capability sliding window
      4. Audit log  — record every call and outcome

    Progress notifications:
      The server supports MCP progress notifications via the notifications/progress
      method. Clients can include a progressToken in the _meta field of their
      request, and the server will send progress updates during long-running
      operations.
    """

    _notification_callback: Any = None
    _notification_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _last_progress_time: dict[str | int, float] = field(default_factory=dict, repr=False)
    _progress_rate_limit_ms: float = 100.0
    _progress_message_max_chars: int = 1000
    _max_active_tokens: int = 100

    def __post_init__(self) -> None:
        # Adapter — created once, reused for all requests
        adapter_mode = os.environ.get("MCP_ADAPTER", "socket").lower()
        if adapter_mode == "mock":
            self._adapter = MockAdapter()
        else:
            self._adapter = SocketAdapter(
                host=os.environ.get("MCP_SOCKET_HOST", "127.0.0.1"),
                port=int(os.environ.get("MCP_SOCKET_PORT", "9876")),
                timeout=float(os.environ.get("MCP_SOCKET_TIMEOUT", "300.0")),
                max_retries=int(os.environ.get("MCP_MAX_RETRIES", "3")),
            )

        # Security modules — all configurable via environment variables
        audit_path = os.environ.get("MCP_AUDIT_LOG")
        self._audit = JsonFileAuditLogger(audit_path) if audit_path else MemoryAuditLogger()
        self._allowlist = Allowlist(audit_logger=self._audit)
        if os.environ.get("MCP_ENABLE_SCRIPT_EXECUTE", "").lower() in (
            "1",
            "true",
            "yes",
        ):
            self._allowlist.enable_script_execute()
        self._guardrails = Guardrails.from_env()

        # Rate limits: env var format "capability=limit,capability=limit"
        rate_cfg: dict[str, int] = {}
        raw_limits = os.environ.get("MCP_RATE_LIMITS", "")
        for pair in raw_limits.split(","):
            pair = pair.strip()
            if "=" in pair:
                cap, lim = pair.split("=", 1)
                try:
                    rate_cfg[cap.strip()] = int(lim.strip())
                except ValueError:
                    pass
        window = float(os.environ.get("MCP_RATE_WINDOW_SECONDS", "60"))
        self._rate_limiter = RateLimiter(rate_cfg, window_seconds=window)
        self._active_progress_tokens: dict[str | int, dict[str, Any]] = {}

    def _send_notification(self, notification: dict[str, Any]) -> None:
        """Send a JSON-RPC notification to the client.

        Thread-safe: uses a lock to prevent interleaved output.
        For stdio transport, this writes to stdout.
        For SSE/HTTP transport, this would use the callback.
        """
        with self._notification_lock:
            if self._notification_callback is not None:
                self._notification_callback(notification)
            else:
                print(json.dumps(notification, ensure_ascii=False))
                sys.stdout.flush()

    def send_progress(
        self,
        progress_token: str | int,
        progress: float,
        total: float | None = None,
        message: str | None = None,
    ) -> bool:
        """Send a progress notification to the client.

        Args:
            progress_token: The token from the client's request _meta field
            progress: Current progress value (must be non-decreasing)
            total: Optional total value for progress calculation
            message: Optional human-readable progress message

        Returns:
            True if notification was sent, False if rate-limited or token not active
        """
        if progress_token not in self._active_progress_tokens:
            return False

        now = time.time()
        last_time = self._last_progress_time.get(progress_token, 0.0)
        if (now - last_time) * 1000 < self._progress_rate_limit_ms:
            return False

        if message is not None and len(message) > self._progress_message_max_chars:
            message = message[: self._progress_message_max_chars - 3] + "..."

        self._last_progress_time[progress_token] = now

        params: dict[str, Any] = {
            "progressToken": progress_token,
            "progress": progress,
        }
        if total is not None:
            params["total"] = total
        if message is not None:
            params["message"] = message

        self._send_notification(
            {
                "jsonrpc": "2.0",
                "method": "notifications/progress",
                "params": params,
            }
        )
        return True

    def tools_list(self) -> dict[str, Any]:
        """List all 26 available tools with full schemas and annotations."""
        tools = []
        for tool_def in TOOL_DEFINITIONS:
            tool_entry: dict[str, Any] = {
                "name": tool_def["name"],
                "description": tool_def["description"],
                "inputSchema": tool_def["inputSchema"],
            }
            if "annotations" in tool_def:
                tool_entry["annotations"] = tool_def["annotations"]
            tools.append(tool_entry)
        return {"tools": tools}

    def _validate_schema(self, arguments: dict[str, Any], schema: dict[str, Any]) -> str | None:
        """Lightweight schema validation (zero dependencies).

        Returns error message if validation fails, None if OK.
        """
        if not schema:
            return None

        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for req in required:
            if req not in arguments:
                return f"Missing required parameter: '{req}'"

        for key, value in arguments.items():
            if key not in properties:
                continue

            prop_schema = properties[key]
            prop_type = prop_schema.get("type")

            if prop_type == "string":
                if not isinstance(value, str):
                    return f"Parameter '{key}' must be a string"
                if "enum" in prop_schema and value not in prop_schema["enum"]:
                    allowed = ", ".join(repr(e) for e in prop_schema["enum"])
                    return f"Parameter '{key}' must be one of: {allowed}"
            elif prop_type == "number":
                if not isinstance(value, (int, float)):
                    return f"Parameter '{key}' must be a number"
            elif prop_type == "integer":
                if not isinstance(value, int) or isinstance(value, bool):
                    return f"Parameter '{key}' must be an integer"
            elif prop_type == "boolean":
                if not isinstance(value, bool):
                    return f"Parameter '{key}' must be a boolean"
            elif prop_type == "array":
                if not isinstance(value, list):
                    return f"Parameter '{key}' must be an array"

        return None

    @telemetry_tool
    def tools_call(
        self,
        name: str,
        arguments: dict[str, Any],
        progress_token: str | int | None = None,
    ) -> dict[str, Any]:
        """Call a tool with flat parameters.

        Args:
            name: Tool name (e.g., 'blender_get_objects')
            arguments: Tool arguments as a flat dict
            progress_token: Optional token for progress notifications
        """
        call_start = time.perf_counter()

        if not name or not isinstance(name, str):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: 'name' is required and must be a string",
                    }
                ],
                "isError": True,
            }
        if not isinstance(arguments, dict):
            arguments = {}

        tool_def = get_tool(name)
        if tool_def is None:
            return {
                "content": [{"type": "text", "text": f"Error: Unknown tool '{name}'"}],
                "isError": True,
            }

        schema_validation_error = self._validate_schema(arguments, tool_def.get("inputSchema", {}))
        if schema_validation_error:
            return {
                "content": [{"type": "text", "text": f"Error: {schema_validation_error}"}],
                "isError": True,
            }

        payload = arguments

        internal_capability = tool_def["internal_capability"]
        logger.info("tools/call %s (capability=%s)", name, internal_capability)

        # ── Security check chain ──────────────────────────────
        # 1. Allowlist
        if not self._allowlist.is_allowed(internal_capability):
            logger.warning("tools/call %s BLOCKED by allowlist", name)
            self._audit.record(
                AuditEvent(
                    capability=internal_capability,
                    ok=False,
                    error="capability_not_allowed",
                )
            )
            return {
                "content": [{"type": "text", "text": f"Error: tool '{name}' is not allowed"}],
                "isError": True,
            }

        # 2. Guardrails (payload size / depth / blocked-list)
        if not self._guardrails.allow(internal_capability, payload):
            logger.warning("tools/call %s BLOCKED by guardrails", name)
            self._audit.record(
                AuditEvent(
                    capability=internal_capability,
                    ok=False,
                    error="guardrails_blocked",
                )
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: request blocked by guardrails (payload too large or nested)",
                    }
                ],
                "isError": True,
            }

        # 3. Rate limit
        if not self._rate_limiter.allow(internal_capability):
            logger.warning("tools/call %s BLOCKED by rate limiter", name)
            self._audit.record(
                AuditEvent(
                    capability=internal_capability,
                    ok=False,
                    error="rate_limited",
                )
            )
            return {
                "content": [{"type": "text", "text": f"Error: rate limit exceeded for '{name}'"}],
                "isError": True,
            }
        # ── End security checks ───────────────────────────────

        progress_callback: Callable[[float, float | None, str | None], None] | None = None
        if progress_token is not None:

            def progress_callback(progress: float, total: float | None, message: str | None) -> None:
                self.send_progress(progress_token, progress, total, message)

        result = self._adapter.execute(internal_capability, payload, progress_callback)
        elapsed_ms = (time.perf_counter() - call_start) * 1000.0

        if result.ok:
            logger.info("tools/call %s succeeded in %.0fms", name, elapsed_ms)
            self._audit.record(
                AuditEvent(
                    capability=internal_capability,
                    ok=True,
                    data={"elapsed_ms": round(elapsed_ms)},
                )
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result.result, indent=2 if _PRETTY_JSON else None),
                    }
                ]
            }
        else:
            logger.warning("tools/call %s failed in %.0fms: %s", name, elapsed_ms, result.error)
            self._audit.record(
                AuditEvent(
                    capability=internal_capability,
                    ok=False,
                    error=result.error,
                    data={"elapsed_ms": round(elapsed_ms)},
                )
            )
            error_detail = result.error_message or result.error or "unknown"
            error_text = f"Error: {error_detail}"
            if result.error_suggestion:
                error_text += f"\nSuggestion: {result.error_suggestion}"
            return {
                "content": [
                    {
                        "type": "text",
                        "text": error_text,
                    }
                ],
                "isError": True,
            }

    def prompts_list(self) -> dict[str, Any]:
        """List all available workflow prompts."""
        prompts = []
        for prompt_def in BLENDER_PROMPTS.values():
            prompts.append(
                {
                    "name": prompt_def["name"],
                    "description": prompt_def.get("description", ""),
                    "arguments": prompt_def.get("arguments", []),
                }
            )
        return {"prompts": prompts}

    def prompts_get(self, name: str, arguments: dict[str, str] | None = None) -> dict[str, Any]:
        """Get a specific prompt with generated messages."""
        if not name or not isinstance(name, str):
            return {
                "error": {
                    "code": -32602,
                    "message": "'name' is required and must be a string",
                },
            }
        result = get_prompt_messages(name, arguments)
        if result is None:
            return {
                "error": {"code": -32602, "message": f"Prompt '{name}' not found"},
            }
        return result

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        """Handle an MCP JSON-RPC request.

        Supports progress notifications: clients can include a progressToken
        in the _meta field, which will be used for progress updates during
        long-running operations.
        """
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        # Handle notifications (no response expected)
        if method and method.startswith("notifications/"):
            if method == "notifications/cancelled":
                token = params.get("requestId")
                if token in self._active_progress_tokens:
                    del self._active_progress_tokens[token]
                    self._last_progress_time.pop(token, None)
                    logger.info("Request %s cancelled by client", token)
            return None

        if method == "tools/list":
            result = self.tools_list()
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})

            meta = params.get("_meta", {})
            progress_token = meta.get("progressToken")

            if progress_token is not None:
                if len(self._active_progress_tokens) >= self._max_active_tokens:
                    logger.warning("Max progress tokens reached, rejecting new token")
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32604, "message": "Too many concurrent operations"},
                    }
                self._active_progress_tokens[progress_token] = {
                    "tool": name,
                    "started": time.time(),
                }

            try:
                result = self.tools_call(name, arguments, progress_token=progress_token)
                return {"jsonrpc": "2.0", "id": req_id, "result": result}
            finally:
                if progress_token is not None:
                    self._active_progress_tokens.pop(progress_token, None)
                    self._last_progress_time.pop(progress_token, None)

        elif method == "prompts/list":
            result = self.prompts_list()
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        elif method == "prompts/get":
            name = params.get("name", "")
            arguments = params.get("arguments")
            result = self.prompts_get(name, arguments)
            if "error" in result:
                return {"jsonrpc": "2.0", "id": req_id, "error": result["error"]}
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        elif method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "blender-mcp",
                        "version": pkg_version,
                    },
                    "capabilities": {
                        "tools": {},
                        "prompts": {"listChanged": False},
                    },
                },
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": "Method not found"},
            }


def run_mcp_server() -> int:
    """Run the MCP server stdio loop."""
    _configure_logging()

    adapter_mode = os.environ.get("MCP_ADAPTER", "socket").lower()
    host = os.environ.get("MCP_SOCKET_HOST", "127.0.0.1")
    port = os.environ.get("MCP_SOCKET_PORT", "9876")
    log_level = os.environ.get("MCP_LOG_LEVEL", "WARNING")
    logger.info(
        "Blender MCP server v%s starting (adapter=%s, host=%s, port=%s, log_level=%s)",
        pkg_version,
        adapter_mode,
        host,
        port,
        log_level,
    )

    server = MCPServer()

    for line in sys.stdin:
        request: dict[str, Any] = {}
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = server.handle_request(request)
            # Only send response for requests, not for notifications
            if response is not None:
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as exc:
            logger.error("Internal error processing request: %s", exc)
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if request else None,
                "error": {"code": -32603, "message": "Internal error"},
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

    return 0


if __name__ == "__main__":
    sys.exit(run_mcp_server())
