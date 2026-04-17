# -*- coding: utf-8 -*-
"""Fake bmesh module for testing mesh operations."""

from __future__ import annotations

from typing import Any


class FakeBMVert:
    def __init__(self) -> None:
        self.co = [0.0, 0.0, 0.0]
        self.normal = [0.0, 0.0, 1.0]
        self.link_edges: list[Any] = []
        self.link_faces: list[Any] = []
        self.hide = False
        self.index = -1
        self.select = False
        self.tag = False


class FakeBMEdge:
    def __init__(self) -> None:
        self.verts: list[FakeBMVert] = []
        self.link_faces: list[Any] = []
        self.hide = False
        self.index = -1
        self.select = False
        self.smooth = False
        self.tag = False


class FakeBMFace:
    def __init__(self) -> None:
        self.verts: list[FakeBMVert] = []
        self.edges: list[FakeBMEdge] = []
        self.loops: list[Any] = []
        self.normal = [0.0, 0.0, 1.0]
        self.material_index = 0
        self.hide = False
        self.index = -1
        self.select = False
        self.smooth = False
        self.tag = False


class FakeBMeshOps:
    def __init__(self, bm: "FakeBMesh") -> None:
        self._bm = bm

    def create_cube(self, **kwargs) -> dict:
        return {"verts": []}

    def create_sphere(self, **kwargs) -> dict:
        return {"verts": []}

    def create_icosphere(self, bm, subdivisions=2, radius=1.0, **kwargs) -> dict:
        return {"verts": []}

    def create_cylinder(self, **kwargs) -> dict:
        return {"verts": []}

    def create_cone(self, **kwargs) -> dict:
        return {"verts": []}

    def create_grid(self, bm, x_segments=1, y_segments=1, size=1.0, **kwargs) -> dict:
        return {"verts": []}

    def create_torus(
        self, bm, major_segments=48, minor_segments=12, major_radius=1.0, minor_radius=0.25, **kwargs
    ) -> dict:
        return {"verts": []}

    def transform(self, bm, matrix, **kwargs) -> None:
        pass

    def triangulate(self, bm, **kwargs) -> dict:
        return {"faces": []}


class FakeBMesh:
    def __init__(self) -> None:
        self.verts: list[FakeBMVert] = []
        self.edges: list[FakeBMEdge] = []
        self.faces: list[FakeBMFace] = []
        self.loops: list[Any] = []
        self.ops = FakeBMeshOps(self)
        self.select_mode = {"VERT"}

    def new(self) -> "FakeBMesh":
        return FakeBMesh()

    def from_mesh(self, mesh: Any) -> None:
        pass

    def to_mesh(self, mesh: Any) -> None:
        pass

    def free(self) -> None:
        pass

    def clear(self) -> None:
        self.verts.clear()
        self.edges.clear()
        self.faces.clear()

    def validate(self) -> bool:
        return True


def new() -> FakeBMesh:
    return FakeBMesh()
