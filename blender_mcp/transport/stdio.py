# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Iterable, List

from blender_mcp.transport.base import TransportAdapter


class StdioTransport(TransportAdapter):
    def __init__(self) -> None:
        self._buffer: List[bytes] = []

    def start(self) -> None:
        return None

    def stop(self) -> None:
        self._buffer.clear()

    def send(self, message: bytes) -> None:
        self._buffer.append(message)

    def receive(self) -> Iterable[bytes]:
        while self._buffer:
            yield self._buffer.pop(0)
