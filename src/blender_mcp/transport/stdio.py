# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from typing import BinaryIO, Iterable

from blender_mcp.transport.base import TransportAdapter


class StdioTransport(TransportAdapter):
    def __init__(
        self, stdin: BinaryIO | None = None, stdout: BinaryIO | None = None
    ) -> None:
        self._stdin = stdin or sys.stdin.buffer
        self._stdout = stdout or sys.stdout.buffer

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None

    def send(self, message: bytes) -> None:
        self._stdout.write(message)
        if not message.endswith(b"\n"):
            self._stdout.write(b"\n")
        self._stdout.flush()

    def receive(self) -> Iterable[bytes]:
        while True:
            line = self._stdin.readline()
            if not line:
                break
            yield line.rstrip(b"\r\n")
