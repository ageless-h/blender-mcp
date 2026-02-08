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
import time
from dataclasses import dataclass
from typing import Any

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

from blender_mcp.adapters.mock import MockAdapter
from blender_mcp.adapters.socket import SocketAdapter
from blender_mcp import __version__ as pkg_version
from blender_mcp.schemas.tools import TOOL_DEFINITIONS, get_tool
from blender_mcp.prompts.registry import (
    BLENDER_PROMPTS,
    get_prompt_messages,
)
from blender_mcp.telemetry import telemetry_tool



@dataclass
class MCPServer:
    """MCP protocol server with 26 tools and 10 prompts."""

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

    @telemetry_tool
    def tools_call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool with flat parameters (no payload wrapper)."""
        call_start = time.perf_counter()

        if not name or not isinstance(name, str):
            return {
                "content": [{"type": "text", "text": "Error: 'name' is required and must be a string"}],
                "isError": True,
            }
        if not isinstance(arguments, dict):
            arguments = {}

        # Look up tool definition for internal routing
        tool_def = get_tool(name)
        if tool_def is None:
            return {
                "content": [{"type": "text", "text": f"Error: Unknown tool '{name}'"}],
                "isError": True,
            }

        # Arguments are flat (no payload wrapper) — pass directly as payload
        # For legacy clients sending {"payload": {...}}, unwrap transparently
        if "payload" in arguments and len(arguments) == 1 and isinstance(arguments["payload"], dict):
            payload = arguments["payload"]
        else:
            payload = arguments

        internal_capability = tool_def["internal_capability"]
        logger.info("tools/call %s (capability=%s)", name, internal_capability)

        adapter_mode = os.environ.get("MCP_ADAPTER", "socket").lower()
        if adapter_mode == "mock":
            adapter = MockAdapter()
        else:
            adapter = SocketAdapter(
                host=os.environ.get("MCP_SOCKET_HOST", "127.0.0.1"),
                port=int(os.environ.get("MCP_SOCKET_PORT", "9876")),
                max_retries=int(os.environ.get("MCP_MAX_RETRIES", "3")),
            )

        result = adapter.execute(internal_capability, payload)
        elapsed_ms = (time.perf_counter() - call_start) * 1000.0

        if result.ok:
            logger.info("tools/call %s succeeded in %.0fms", name, elapsed_ms)
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result.result, indent=2),
                }]
            }
        else:
            logger.warning("tools/call %s failed in %.0fms: %s", name, elapsed_ms, result.error)
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {result.error}",
                }],
                "isError": True,
            }

    def prompts_list(self) -> dict[str, Any]:
        """List all available workflow prompts."""
        prompts = []
        for prompt_def in BLENDER_PROMPTS.values():
            prompts.append({
                "name": prompt_def["name"],
                "description": prompt_def.get("description", ""),
                "arguments": prompt_def.get("arguments", []),
            })
        return {"prompts": prompts}

    def prompts_get(self, name: str, arguments: dict[str, str] | None = None) -> dict[str, Any]:
        """Get a specific prompt with generated messages."""
        if not name or not isinstance(name, str):
            return {
                "error": {"code": -32602, "message": "'name' is required and must be a string"},
            }
        result = get_prompt_messages(name, arguments)
        if result is None:
            return {
                "error": {"code": -32602, "message": f"Prompt '{name}' not found"},
            }
        return result

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        """Handle an MCP JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        # Handle notifications (no response expected)
        if method and method.startswith("notifications/"):
            return None

        if method == "tools/list":
            result = self.tools_list()
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            result = self.tools_call(name, arguments)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

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
        pkg_version, adapter_mode, host, port, log_level,
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
