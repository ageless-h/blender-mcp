# -*- coding: utf-8 -*-
"""Unit tests for shared utility functions."""
from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import MagicMock, patch, PropertyMock


class TestCreateMeshPrimitive(unittest.TestCase):
    """Tests for create_mesh_primitive()."""

    def _make_mock_bmesh_module(self):
        """Create a mock bmesh module with ops."""
        mock_bmesh = MagicMock()
        mock_bm = MagicMock()
        mock_bmesh.new.return_value = mock_bm
        return mock_bmesh, mock_bm

    def test_cube(self):
        """create_mesh_primitive creates cube geometry."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            create_mesh_primitive(mock_mesh, "cube", {"size": 3.0})

        mock_bmesh.ops.create_cube.assert_called_once_with(mock_bm, size=3.0)
        mock_bm.to_mesh.assert_called_once_with(mock_mesh)
        mock_bm.free.assert_called_once()
        mock_mesh.validate.assert_called_once()
        mock_mesh.update.assert_called_once_with(calc_edges=True, calc_edges_loose=True)

    def test_sphere_with_size_default_radius(self):
        """Sphere uses size/2 as default radius."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            create_mesh_primitive(mock_mesh, "sphere", {"size": 4.0})

        call_kwargs = mock_bmesh.ops.create_uvsphere.call_args
        self.assertEqual(call_kwargs[1]["radius"], 2.0)

    def test_sphere_with_explicit_radius(self):
        """Sphere uses explicit radius when provided."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            create_mesh_primitive(mock_mesh, "sphere", {"size": 4.0, "radius": 1.5})

        call_kwargs = mock_bmesh.ops.create_uvsphere.call_args
        self.assertEqual(call_kwargs[1]["radius"], 1.5)

    def test_cylinder(self):
        """Cylinder creates cone with equal radii."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            create_mesh_primitive(mock_mesh, "cylinder", {"segments": 16, "depth": 3.0, "radius": 0.5})

        call_kwargs = mock_bmesh.ops.create_cone.call_args[1]
        self.assertEqual(call_kwargs["radius1"], 0.5)
        self.assertEqual(call_kwargs["radius2"], 0.5)
        self.assertEqual(call_kwargs["depth"], 3.0)

    def test_cone(self):
        """Cone creates cone with zero top radius."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            create_mesh_primitive(mock_mesh, "cone", {"radius": 1.0})

        call_kwargs = mock_bmesh.ops.create_cone.call_args[1]
        self.assertEqual(call_kwargs["radius1"], 1.0)
        self.assertEqual(call_kwargs["radius2"], 0)

    def test_plane(self):
        """Plane creates a grid."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            create_mesh_primitive(mock_mesh, "plane", {"size": 2.0})

        mock_bmesh.ops.create_grid.assert_called_once()

    def test_icosphere(self):
        """Icosphere creates icosphere geometry."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            create_mesh_primitive(mock_mesh, "icosphere", {"subdivisions": 3, "radius": 2.0})

        call_kwargs = mock_bmesh.ops.create_icosphere.call_args[1]
        self.assertEqual(call_kwargs["subdivisions"], 3)
        self.assertEqual(call_kwargs["radius"], 2.0)

    def test_torus(self):
        """Torus creates torus geometry."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            create_mesh_primitive(mock_mesh, "torus", {
                "major_radius": 2.0, "minor_radius": 0.5,
                "major_segments": 24, "minor_segments": 8,
            })

        call_kwargs = mock_bmesh.ops.create_torus.call_args[1]
        self.assertEqual(call_kwargs["major_radius"], 2.0)
        self.assertEqual(call_kwargs["minor_radius"], 0.5)

    def test_unknown_primitive_raises(self):
        """Unknown primitive type raises ValueError."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            with self.assertRaises(ValueError) as ctx:
                create_mesh_primitive(mock_mesh, "dodecahedron", {})
            self.assertIn("dodecahedron", str(ctx.exception))

        # bmesh must still be freed even on error
        mock_bm.free.assert_called_once()

    def test_bmesh_freed_on_error(self):
        """bmesh is freed even when bmesh.ops raises."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_bmesh.ops.create_cube.side_effect = RuntimeError("boom")
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            with self.assertRaises(RuntimeError):
                create_mesh_primitive(mock_mesh, "cube", {})

        mock_bm.free.assert_called_once()

    def test_case_insensitive(self):
        """Primitive name is case-insensitive."""
        mock_bmesh, mock_bm = self._make_mock_bmesh_module()
        mock_mesh = MagicMock()

        with patch.dict("sys.modules", {"bmesh": mock_bmesh}):
            from blender_mcp_addon.handlers.shared import create_mesh_primitive
            create_mesh_primitive(mock_mesh, "CUBE", {"size": 1.0})

        mock_bmesh.ops.create_cube.assert_called_once()


class TestLinkDataToScene(unittest.TestCase):
    """Tests for link_data_to_scene()."""

    def _setup_bpy_mock(self):
        """Create a mock bpy module."""
        mock_bpy = MagicMock()
        mock_obj = MagicMock()
        mock_bpy.data.objects.new.return_value = mock_obj
        mock_bpy.data.collections = {}
        return mock_bpy, mock_obj

    def test_link_to_scene_collection_default(self):
        """Links to scene collection when no collection specified."""
        mock_bpy, mock_obj = self._setup_bpy_mock()

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import link_data_to_scene
            data_block = MagicMock()
            data_block.name = "MyLight"
            result = link_data_to_scene(data_block, {})

        mock_bpy.data.objects.new.assert_called_once_with("MyLight", data_block)
        mock_bpy.context.scene.collection.objects.link.assert_called_once_with(mock_obj)
        self.assertEqual(result, mock_obj)

    def test_link_with_custom_object_name(self):
        """Uses object_name from params."""
        mock_bpy, mock_obj = self._setup_bpy_mock()

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import link_data_to_scene
            data_block = MagicMock()
            data_block.name = "Data"
            link_data_to_scene(data_block, {"object_name": "CustomName"})

        mock_bpy.data.objects.new.assert_called_once_with("CustomName", data_block)

    def test_link_to_named_collection(self):
        """Links to named collection when it exists."""
        mock_bpy, mock_obj = self._setup_bpy_mock()
        mock_coll = MagicMock()
        mock_bpy.data.collections = {"Lights": mock_coll}

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import link_data_to_scene
            data_block = MagicMock()
            data_block.name = "L"
            link_data_to_scene(data_block, {"collection": "Lights"})

        mock_coll.objects.link.assert_called_once_with(mock_obj)
        mock_bpy.context.scene.collection.objects.link.assert_not_called()

    def test_fallback_when_collection_missing(self):
        """Falls back to scene collection when named collection doesn't exist."""
        mock_bpy, mock_obj = self._setup_bpy_mock()
        mock_bpy.data.collections = {}

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import link_data_to_scene
            data_block = MagicMock()
            data_block.name = "D"
            link_data_to_scene(data_block, {"collection": "NonExistent"})

        mock_bpy.context.scene.collection.objects.link.assert_called_once_with(mock_obj)

    def test_applies_location(self):
        """Sets location from params."""
        mock_bpy, mock_obj = self._setup_bpy_mock()

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import link_data_to_scene
            data_block = MagicMock()
            data_block.name = "D"
            link_data_to_scene(data_block, {"location": [1, 2, 3]})

        self.assertEqual(mock_obj.location, (1, 2, 3))

    def test_applies_rotation(self):
        """Sets rotation_euler from params."""
        mock_bpy, mock_obj = self._setup_bpy_mock()

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import link_data_to_scene
            data_block = MagicMock()
            data_block.name = "D"
            link_data_to_scene(data_block, {"rotation": [0.1, 0.2, 0.3]})

        self.assertEqual(mock_obj.rotation_euler, (0.1, 0.2, 0.3))

    def test_returns_created_object(self):
        """Returns the created object."""
        mock_bpy, mock_obj = self._setup_bpy_mock()

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import link_data_to_scene
            data_block = MagicMock()
            data_block.name = "D"
            result = link_data_to_scene(data_block, {})

        self.assertIs(result, mock_obj)


class TestFindReferencingObjects(unittest.TestCase):
    """Tests for find_referencing_objects()."""

    def _make_mock_obj(self, name: str, obj_type: str, data: Any):
        m = MagicMock()
        m.name = name
        m.type = obj_type
        m.data = data
        return m

    def _make_mock_collection(self, name: str, obj_names: list[str]):
        coll = MagicMock()
        coll.name = name
        coll.objects = {n: True for n in obj_names}
        return coll

    def test_finds_referencing_objects(self):
        """Finds objects whose .data matches the data block."""
        data_block = MagicMock()
        obj1 = self._make_mock_obj("Light.001", "LIGHT", data_block)
        obj2 = self._make_mock_obj("Light.002", "LIGHT", data_block)
        obj3 = self._make_mock_obj("Cube", "MESH", MagicMock())

        coll = self._make_mock_collection("Collection", ["Light.001", "Light.002"])

        mock_bpy = MagicMock()
        mock_bpy.data.objects = [obj1, obj2, obj3]
        mock_bpy.data.collections = [coll]

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import find_referencing_objects
            result = find_referencing_objects(data_block, "LIGHT")

        self.assertEqual(result["objects"], ["Light.001", "Light.002"])
        self.assertEqual(result["collections"], ["Collection"])

    def test_no_references(self):
        """Returns empty lists when no objects reference the data block."""
        data_block = MagicMock()

        mock_bpy = MagicMock()
        mock_bpy.data.objects = []
        mock_bpy.data.collections = []

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import find_referencing_objects
            result = find_referencing_objects(data_block, "LIGHT")

        self.assertEqual(result, {"objects": [], "collections": []})

    def test_collections_deduplicated(self):
        """Collection names appear only once even with multiple objects in same collection."""
        data_block = MagicMock()
        obj1 = self._make_mock_obj("L1", "LIGHT", data_block)
        obj2 = self._make_mock_obj("L2", "LIGHT", data_block)

        coll = self._make_mock_collection("Shared", ["L1", "L2"])

        mock_bpy = MagicMock()
        mock_bpy.data.objects = [obj1, obj2]
        mock_bpy.data.collections = [coll]

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import find_referencing_objects
            result = find_referencing_objects(data_block, "LIGHT")

        self.assertEqual(result["collections"].count("Shared"), 1)

    def test_filters_by_object_type(self):
        """Only returns objects of the specified type."""
        data_block = MagicMock()
        cam_obj = self._make_mock_obj("Cam", "CAMERA", data_block)
        light_obj = self._make_mock_obj("Light", "LIGHT", data_block)

        mock_bpy = MagicMock()
        mock_bpy.data.objects = [cam_obj, light_obj]
        mock_bpy.data.collections = []

        with patch.dict("sys.modules", {"bpy": mock_bpy}):
            from blender_mcp_addon.handlers.shared import find_referencing_objects
            result = find_referencing_objects(data_block, "CAMERA")

        self.assertEqual(result["objects"], ["Cam"])


if __name__ == "__main__":
    unittest.main()
