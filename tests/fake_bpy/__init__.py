# -*- coding: utf-8 -*-
"""Fake bpy module for testing without a real Blender installation.

Usage:
    import fake_bpy
    fake_bpy.install()                              # Replace real bpy with fake
    fake_bpy.reset()                                 # Clear all fake data
    fake_bpy.data.objects.new("Cube", ...)           # Create test data
    fake_bpy.uninstall()                              # Restore real bpy

Or as a context manager:
    with fake_bpy.fake_bpy_context():
        ...
"""

from __future__ import annotations

import sys
from types import ModuleType

from . import _app as app_mod
from . import _context as context_mod
from . import _data as data_mod
from . import _ops as ops_mod
from . import _types as types_mod

_ORIG_BPY = None
_INSTALLED = False


def install(version: tuple[int, ...] = (4, 2, 0)) -> None:
    """Install fake bpy into sys.modules, replacing any real bpy."""
    global _ORIG_BPY, _INSTALLED

    _ORIG_BPY = sys.modules.get("bpy", None)

    fake = ModuleType("bpy")
    fake.data = data_mod.FakeData(blender_version=version)
    fake.context = context_mod.FakeContext()
    fake.ops = ops_mod.FakeOps()
    fake.app = app_mod.FakeApp(version=version)
    fake.types = types_mod

    sys.modules["bpy"] = fake
    _INSTALLED = True


def uninstall() -> None:
    """Restore the original bpy module (or remove fake if none existed)."""
    global _ORIG_BPY, _INSTALLED

    if _ORIG_BPY is not None:
        sys.modules["bpy"] = _ORIG_BPY
    else:
        sys.modules.pop("bpy", None)
    _ORIG_BPY = None
    _INSTALLED = False


def reset(version: tuple[int, ...] = (4, 2, 0)) -> None:
    """Reset all fake data to empty state. Only valid while installed."""
    if not _INSTALLED:
        raise RuntimeError("fake_bpy not installed — call install() first")

    bpy = sys.modules["bpy"]
    bpy.data = data_mod.FakeData(blender_version=version)
    bpy.context = context_mod.FakeContext()
    bpy.ops = ops_mod.FakeOps()
    bpy.app = app_mod.FakeApp(version=version)


class _FakeBpyContextManager:
    def __init__(self, version: tuple[int, ...] = (4, 2, 0)):
        self._version = version

    def __enter__(self):
        install(self._version)
        return sys.modules["bpy"]

    def __exit__(self, *args):
        uninstall()


def fake_bpy_context(version: tuple[int, ...] = (4, 2, 0)):
    return _FakeBpyContextManager(version)
