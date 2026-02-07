# -*- coding: utf-8 -*-
"""Socket server for MCP communication with the addon."""
from __future__ import annotations

import json
import logging
import socket
import threading
from typing import Any

from ..capabilities.base import execute_capability

logger = logging.getLogger(__name__)

_server_lock = threading.Lock()
_server_socket: socket.socket | None = None
_server_thread: threading.Thread | None = None
_shutdown_flag = threading.Event()


def is_server_running() -> bool:
    """Check if the socket server is currently running."""
    with _server_lock:
        return _server_socket is not None


def get_server_address() -> tuple[str, int]:
    """Get the server address from addon preferences."""
    try:
        import bpy  # type: ignore
        prefs = bpy.context.preferences.addons["blender_mcp_addon"].preferences
        return prefs.host, prefs.port
    except Exception:
        return "127.0.0.1", 9876


def start_socket_server(host: str | None = None, port: int | None = None) -> dict[str, Any]:
    """Start the socket server for receiving capability requests."""
    global _server_socket, _server_thread

    with _server_lock:
        if _server_socket is not None:
            return {"ok": False, "error": "server_already_running"}

        if host is None or port is None:
            default_host, default_port = get_server_address()
            host = host or default_host
            port = port or default_port

        _shutdown_flag.clear()

        try:
            _server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            _server_socket.bind((host, port))
            _server_socket.listen(5)
            _server_socket.settimeout(1.0)

            _server_thread = threading.Thread(
                target=_server_loop,
                daemon=True,
            )
            _server_thread.start()

            logger.info("Socket server started on %s:%s", host, port)
            return {"ok": True, "host": host, "port": port}
        except Exception as exc:
            logger.error("Failed to start socket server: %s", exc)
            _server_socket = None
            return {"ok": False, "error": str(exc)}


def stop_socket_server() -> dict[str, Any]:
    """Stop the socket server."""
    global _server_socket, _server_thread

    with _server_lock:
        if _server_socket is None:
            return {"ok": False, "error": "server_not_running"}

        _shutdown_flag.set()

        try:
            _server_socket.close()
        except Exception as exc:
            logger.debug("Error closing server socket: %s", exc)

        if _server_thread is not None:
            _server_thread.join(timeout=5.0)
            _server_thread = None

        _server_socket = None
        logger.info("Socket server stopped")
        return {"ok": True}


def _server_loop() -> None:
    """Main server loop accepting connections."""
    global _server_socket

    while not _shutdown_flag.is_set():
        with _server_lock:
            sock = _server_socket
        if sock is None:
            break

        try:
            client_socket, addr = sock.accept()
            client_thread = threading.Thread(
                target=_handle_client,
                args=(client_socket,),
                daemon=True,
            )
            client_thread.start()
        except socket.timeout:
            continue
        except OSError:
            break


def _handle_client(client_socket: socket.socket) -> None:
    """Handle a single client connection."""
    try:
        client_socket.settimeout(30.0)
        data = b""

        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"\n" in data:
                break

        if not data:
            return

        request_str = data.decode("utf-8").strip()
        try:
            request = json.loads(request_str)
        except json.JSONDecodeError:
            response = {
                "ok": False,
                "result": None,
                "error": {"code": "parse_error", "message": "Invalid JSON"},
            }
            client_socket.sendall((json.dumps(response) + "\n").encode("utf-8"))
            return

        response = execute_capability(request)
        client_socket.sendall((json.dumps(response) + "\n").encode("utf-8"))

    except Exception as exc:
        logger.error("Error handling client: %s", exc)
    finally:
        try:
            client_socket.close()
        except Exception as exc:
            logger.debug("Error closing client socket: %s", exc)
