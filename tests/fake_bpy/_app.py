# -*- coding: utf-8 -*-
"""Fake bpy.app — simulated Blender application info for testing."""

from __future__ import annotations


class FakeApp:
    def __init__(self, version: tuple[int, ...] = (4, 2, 0)) -> None:
        self._version = version

    @property
    def version(self) -> tuple[int, ...]:
        return self._version

    @property
    def version_string(self) -> str:
        return ".".join(str(v) for v in self._version)

    @property
    def version_file(self) -> str:
        major, minor = self._version[:2]
        return f"{major}.{minor}"
