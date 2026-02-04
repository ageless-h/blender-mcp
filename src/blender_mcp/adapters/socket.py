# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import socket
import time
from typing import Any, Dict

from blender_mcp.adapters.types import AdapterResult


class SocketAdapter:
    """Adapter that communicates with Blender addon over TCP socket."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9876,
        timeout: float = 30.0,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def execute(self, capability: str, payload: Dict[str, Any]) -> AdapterResult:
        """Execute a capability via socket connection to Blender addon."""
        started = time.perf_counter()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))

                request = json.dumps({"capability": capability, "payload": payload})
                sock.sendall((request + "\n").encode("utf-8"))

                response_data = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    if b"\n" in response_data:
                        break

                elapsed_ms = (time.perf_counter() - started) * 1000.0

                if not response_data:
                    return AdapterResult(
                        ok=False,
                        error="adapter_empty_response",
                        timing_ms=elapsed_ms,
                    )

                response = json.loads(response_data.decode("utf-8").strip())
                return AdapterResult(
                    ok=response.get("ok", False),
                    result=response.get("result"),
                    error=response.get("error", {}).get("code") if response.get("error") else None,
                    timing_ms=elapsed_ms,
                )

        except socket.timeout:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            return AdapterResult(
                ok=False,
                error="adapter_timeout",
                timing_ms=elapsed_ms,
            )
        except (socket.error, ConnectionRefusedError, OSError):
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            return AdapterResult(
                ok=False,
                error="adapter_unavailable",
                timing_ms=elapsed_ms,
            )
        except json.JSONDecodeError:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            return AdapterResult(
                ok=False,
                error="adapter_invalid_response",
                timing_ms=elapsed_ms,
            )
