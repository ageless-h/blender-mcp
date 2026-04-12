# -*- coding: utf-8 -*-
"""Tests for the 9 imperative write layer tools."""

from __future__ import annotations

import json
import os
import unittest

os.environ["MCP_ADAPTER"] = "mock"

from blender_mcp.mcp_protocol import MCPServer


class _ToolTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = MCPServer()

    def _call(self, name, args=None):
        return self.server.tools_call(name, args or {})

    def _ok(self, result):
        self.assertIn("content", result)
        self.assertNotIn("isError", result)
        self.assertEqual(result["content"][0]["type"], "text")
        return json.loads(result["content"][0]["text"])


class TestCreateObject(_ToolTestBase):
    def test_mesh_cube(self):
        self._ok(
            self._call("blender_create_object", {"name": "C", "object_type": "MESH", "primitive": "cube", "size": 2.0})
        )

    def test_mesh_sphere(self):
        self._ok(
            self._call(
                "blender_create_object", {"name": "S", "object_type": "MESH", "primitive": "sphere", "segments": 32}
            )
        )

    def test_light(self):
        self._ok(
            self._call(
                "blender_create_object",
                {"name": "L", "object_type": "LIGHT", "light_type": "POINT", "energy": 1000, "color": [1, 0.9, 0.8]},
            )
        )

    def test_camera(self):
        self._ok(
            self._call(
                "blender_create_object", {"name": "Cam", "object_type": "CAMERA", "lens": 50, "set_active_camera": True}
            )
        )

    def test_curve(self):
        self._ok(self._call("blender_create_object", {"name": "Cv", "object_type": "CURVE", "curve_type": "BEZIER"}))

    def test_empty(self):
        self._ok(self._call("blender_create_object", {"name": "E", "object_type": "EMPTY"}))

    def test_text(self):
        self._ok(
            self._call("blender_create_object", {"name": "T", "object_type": "TEXT", "body": "Hi", "extrude": 0.1})
        )

    def test_with_transform(self):
        self._ok(
            self._call(
                "blender_create_object",
                {"name": "X", "location": [1, 2, 3], "rotation": [0, 0, 1.57], "scale": [2, 2, 2]},
            )
        )

    def test_in_collection(self):
        self._ok(self._call("blender_create_object", {"name": "P", "primitive": "plane", "collection": "MyCol"}))

    def test_name_only(self):
        self._ok(self._call("blender_create_object", {"name": "Min"}))


class TestModifyObject(_ToolTestBase):
    def test_location(self):
        self._ok(self._call("blender_modify_object", {"name": "Cube", "location": [1, 2, 3]}))

    def test_rotation(self):
        self._ok(self._call("blender_modify_object", {"name": "Cube", "rotation": [0, 0, 1.57]}))

    def test_scale(self):
        self._ok(self._call("blender_modify_object", {"name": "Cube", "scale": [2, 2, 2]}))

    def test_visibility(self):
        self._ok(self._call("blender_modify_object", {"name": "Cube", "visible": False, "hide_render": True}))

    def test_parent(self):
        self._ok(self._call("blender_modify_object", {"name": "Cube", "parent": "Empty"}))

    def test_rename(self):
        self._ok(self._call("blender_modify_object", {"name": "Cube", "new_name": "Renamed"}))

    def test_origin(self):
        self._ok(self._call("blender_modify_object", {"name": "Cube", "origin": "GEOMETRY"}))

    def test_delete(self):
        self._ok(self._call("blender_modify_object", {"name": "Cube", "delete": True}))

    def test_selection(self):
        self._ok(self._call("blender_modify_object", {"name": "Cube", "active": True, "selected": True}))


class TestManageMaterial(_ToolTestBase):
    def test_create(self):
        self._ok(
            self._call(
                "blender_manage_material",
                {"action": "create", "name": "M", "base_color": [0.8, 0.1, 0.1, 1], "metallic": 1.0},
            )
        )

    def test_edit(self):
        self._ok(self._call("blender_manage_material", {"action": "edit", "name": "M", "roughness": 0.5}))

    def test_assign(self):
        self._ok(
            self._call("blender_manage_material", {"action": "assign", "name": "M", "object_name": "Cube", "slot": 0})
        )

    def test_unassign(self):
        self._ok(self._call("blender_manage_material", {"action": "unassign", "name": "M", "object_name": "Cube"}))

    def test_duplicate(self):
        self._ok(self._call("blender_manage_material", {"action": "duplicate", "name": "M"}))

    def test_delete(self):
        self._ok(self._call("blender_manage_material", {"action": "delete", "name": "M"}))

    def test_emission(self):
        self._ok(
            self._call(
                "blender_manage_material",
                {"action": "create", "name": "G", "emission_color": [1, 1, 0, 1], "emission_strength": 5},
            )
        )


class TestManageModifier(_ToolTestBase):
    def test_add_subsurf(self):
        self._ok(
            self._call(
                "blender_manage_modifier",
                {
                    "action": "add",
                    "object_name": "Cube",
                    "modifier_name": "Sub",
                    "modifier_type": "SUBSURF",
                    "settings": {"levels": 2},
                },
            )
        )

    def test_configure(self):
        self._ok(
            self._call(
                "blender_manage_modifier",
                {"action": "configure", "object_name": "Cube", "modifier_name": "Sub", "settings": {"levels": 3}},
            )
        )

    def test_apply(self):
        self._ok(
            self._call("blender_manage_modifier", {"action": "apply", "object_name": "Cube", "modifier_name": "Sub"})
        )

    def test_remove(self):
        self._ok(
            self._call("blender_manage_modifier", {"action": "remove", "object_name": "Cube", "modifier_name": "Sub"})
        )

    def test_move(self):
        self._ok(
            self._call(
                "blender_manage_modifier", {"action": "move_up", "object_name": "Cube", "modifier_name": "Mirror"}
            )
        )


class TestManageCollection(_ToolTestBase):
    def test_create(self):
        self._ok(self._call("blender_manage_collection", {"action": "create", "collection_name": "Props"}))

    def test_delete(self):
        self._ok(self._call("blender_manage_collection", {"action": "delete", "collection_name": "Props"}))

    def test_link(self):
        self._ok(
            self._call(
                "blender_manage_collection",
                {"action": "link_object", "collection_name": "Props", "object_name": "Cube"},
            )
        )

    def test_unlink(self):
        self._ok(
            self._call(
                "blender_manage_collection",
                {"action": "unlink_object", "collection_name": "Props", "object_name": "Cube"},
            )
        )

    def test_visibility(self):
        self._ok(
            self._call(
                "blender_manage_collection",
                {"action": "set_visibility", "collection_name": "Props", "hide_viewport": True},
            )
        )

    def test_parent(self):
        self._ok(
            self._call(
                "blender_manage_collection",
                {"action": "set_parent", "collection_name": "Props", "parent": "Scene Collection"},
            )
        )

    def test_color_tag(self):
        self._ok(
            self._call(
                "blender_manage_collection", {"action": "create", "collection_name": "T", "color_tag": "COLOR_01"}
            )
        )


class TestManageUV(_ToolTestBase):
    def test_smart_project(self):
        self._ok(
            self._call("blender_manage_uv", {"action": "smart_project", "object_name": "Cube", "angle_limit": 66.0})
        )

    def test_unwrap(self):
        self._ok(self._call("blender_manage_uv", {"action": "unwrap", "object_name": "Cube"}))

    def test_mark_seam(self):
        self._ok(
            self._call(
                "blender_manage_uv", {"action": "mark_seam", "object_name": "Cube", "selection_mode": "SHARP_EDGES"}
            )
        )

    def test_add_uv_map(self):
        self._ok(self._call("blender_manage_uv", {"action": "add_uv_map", "object_name": "Cube", "uv_map_name": "UV2"}))

    def test_remove_uv_map(self):
        self._ok(
            self._call("blender_manage_uv", {"action": "remove_uv_map", "object_name": "Cube", "uv_map_name": "UV2"})
        )

    def test_pack_islands(self):
        self._ok(self._call("blender_manage_uv", {"action": "pack_islands", "object_name": "Cube"}))


class TestManageConstraints(_ToolTestBase):
    def test_add(self):
        self._ok(
            self._call(
                "blender_manage_constraints",
                {"action": "add", "target_name": "Cube", "constraint_name": "TT", "constraint_type": "TRACK_TO"},
            )
        )

    def test_configure(self):
        self._ok(
            self._call(
                "blender_manage_constraints",
                {"action": "configure", "target_name": "Cube", "constraint_name": "TT", "settings": {"influence": 0.5}},
            )
        )

    def test_remove(self):
        self._ok(
            self._call(
                "blender_manage_constraints", {"action": "remove", "target_name": "Cube", "constraint_name": "TT"}
            )
        )

    def test_bone(self):
        self._ok(
            self._call(
                "blender_manage_constraints",
                {"action": "add", "target_type": "BONE", "target_name": "Arm/Hand", "constraint_type": "IK"},
            )
        )

    def test_enable_disable(self):
        self._ok(
            self._call(
                "blender_manage_constraints", {"action": "enable", "target_name": "Cube", "constraint_name": "TT"}
            )
        )
        self._ok(
            self._call(
                "blender_manage_constraints", {"action": "disable", "target_name": "Cube", "constraint_name": "TT"}
            )
        )


class TestManagePhysics(_ToolTestBase):
    def test_add_rigid(self):
        self._ok(
            self._call("blender_manage_physics", {"action": "add", "object_name": "Cube", "physics_type": "RIGID_BODY"})
        )

    def test_configure(self):
        self._ok(
            self._call(
                "blender_manage_physics", {"action": "configure", "object_name": "Cube", "settings": {"mass": 5.0}}
            )
        )

    def test_remove(self):
        self._ok(
            self._call(
                "blender_manage_physics", {"action": "remove", "object_name": "Cube", "physics_type": "RIGID_BODY"}
            )
        )

    def test_bake(self):
        self._ok(
            self._call(
                "blender_manage_physics", {"action": "bake", "object_name": "Cube", "frame_start": 1, "frame_end": 250}
            )
        )

    def test_force_field(self):
        self._ok(
            self._call(
                "blender_manage_physics",
                {"action": "add", "object_name": "E", "physics_type": "FORCE_FIELD", "force_field_type": "WIND"},
            )
        )


class TestSetupScene(_ToolTestBase):
    def test_engine(self):
        self._ok(self._call("blender_setup_scene", {"engine": "CYCLES", "samples": 128}))

    def test_resolution(self):
        self._ok(self._call("blender_setup_scene", {"resolution_x": 1920, "resolution_y": 1080}))

    def test_output(self):
        self._ok(self._call("blender_setup_scene", {"output_format": "PNG", "output_path": "/tmp/render"}))

    def test_timeline(self):
        self._ok(self._call("blender_setup_scene", {"fps": 24, "frame_start": 1, "frame_end": 250}))

    def test_world(self):
        self._ok(
            self._call("blender_setup_scene", {"background_color": [0.05, 0.05, 0.05, 1], "background_strength": 1.0})
        )

    def test_denoising(self):
        self._ok(self._call("blender_setup_scene", {"denoising": True, "denoiser": "OPENIMAGEDENOISE"}))

    def test_empty_params(self):
        self._ok(self._call("blender_setup_scene"))


if __name__ == "__main__":
    unittest.main()
