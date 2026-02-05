# -*- coding: utf-8 -*-
"""MCP protocol adapter for Blender MCP server."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any

from blender_mcp.catalog.catalog import CapabilityMeta, capability_to_dict, minimal_capability_set


@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: dict[str, Any]


@dataclass
class MCPServer:
    """Simple MCP protocol server."""

    def tools_list(self) -> dict[str, Any]:
        """List available tools."""
        capabilities = minimal_capability_set()
        tools = []

        for cap in capabilities:
            if cap.name.startswith("data.") or cap.name in ("operator.execute", "info.query"):
                tool = MCPTool(
                    name=cap.name,
                    description=cap.description,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "payload": {
                                "type": "object",
                                "description": f"Parameters for {cap.name}"
                            }
                        },
                        "required": ["payload"]
                    }
                )
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })

        return {"tools": tools}

    def tools_call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool."""
        # Convert MCP tool call to internal capability call
        payload = arguments.get("payload", {})

        # Import here to avoid circular dependency
        from blender_mcp.adapters.socket import SocketAdapter
        import os

        adapter = SocketAdapter(
            host=os.environ.get("MCP_SOCKET_HOST", "127.0.0.1"),
            port=int(os.environ.get("MCP_SOCKET_PORT", "9876"))
        )

        result = adapter.execute(name, payload)

        if result.ok:
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result.result, indent=2)
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {result.error}"
                }],
                "isError": True
            }

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle an MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        if method == "tools/list":
            result = self.tools_list()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            result = self.tools_call(name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }
        elif method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "blender-mcp",
                        "version": "0.1.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }


def run_mcp_server() -> int:
    """Run the MCP server stdio loop."""
    server = MCPServer()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = server.handle_request(request)
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

    return 0


if __name__ == "__main__":
    sys.exit(run_mcp_server())
