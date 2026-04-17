# -*- coding: utf-8 -*-
"""Fake bpy.ops — no-op operator namespace for testing."""

from __future__ import annotations


class _FakeOpNamespace:
    def __getattr__(self, name: str) -> "_FakeOpNamespace":
        return _FakeOpNamespace()

    def __call__(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}


class _FakeRigidbodyOps:
    """Fake rigid body operations."""

    def world_add(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}

    def object_add(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}

    def object_remove(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}


class _FakePtcacheOps:
    """Fake point cache operations."""

    def bake_all(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}

    def free_bake_all(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}


class _FakeConstraintOps:
    """Fake constraint operations."""

    def move_up(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}

    def move_down(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}


class _FakeParticleOps:
    """Fake particle operations."""

    def system_add(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}

    def system_remove(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}


class FakeOps:
    def __init__(self) -> None:
        self.object = _FakeOpNamespace()
        self.mesh = _FakeOpNamespace()
        self.scene = _FakeOpNamespace()
        self.view3d = _FakeOpNamespace()
        self.screen = _FakeOpNamespace()
        self.uv = _FakeOpNamespace()
        self.anim = _FakeOpNamespace()
        self.rigidbody = _FakeRigidbodyOps()
        self.ptcache = _FakePtcacheOps()
        self.constraint = _FakeConstraintOps()
        self.particle = _FakeParticleOps()
