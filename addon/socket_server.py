# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import socket
import threading
from typing import Any

from addon.entrypoint import execute_capability


_server_socket: socket.socket | None = None
_server_thread: threading.Thread | None = None
_shutdown_flag = threading.Event()


def start_socket_server(host: str = "127.0.0.1", port: int = 9876) -> dict[str, Any]:
    """Start the socket server for receiving capability requests."""
    global _server_socket, _server_thread

    if _server_socket is not None:
        return {"ok": False, "error": "server_already_running"}

    _shutdown_flag.clear()

    try:
        _server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _server_socket.bind((host, port))
        _server_socket.listen(1)
        _server_socket.settimeout(1.0)

        _server_thread = threading.Thread(
            target=_server_loop,
            daemon=True,
        )
        _server_thread.start()

        return {"ok": True, "host": host, "port": port}
    except Exception as exc:
        _server_socket = None
        return {"ok": False, "error": str(exc)}


def stop_socket_server() -> dict[str, Any]:
    """Stop the socket server."""
    global _server_socket, _server_thread

    if _server_socket is None:
        return {"ok": False, "error": "server_not_running"}

    _shutdown_flag.set()

    try:
        _server_socket.close()
    except Exception:
        pass

    if _server_thread is not None:
        _server_thread.join(timeout=5.0)
        _server_thread = None

    _server_socket = None
    return {"ok": True}


def _server_loop() -> None:
    """Main server loop accepting connections."""
    global _server_socket

    while not _shutdown_flag.is_set():
        if _server_socket is None:
            break

        try:
            client_socket, _ = _server_socket.accept()
            _handle_client(client_socket)
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

    except Exception:
        pass
    finally:
        try:
            client_socket.close()
        except Exception:
            pass
