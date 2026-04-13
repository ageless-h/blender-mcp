# -*- coding: utf-8 -*-
"""End-to-end tests for all 26 MCP tools against a real Blender instance.

Run via:
    BLENDER_EXECUTABLE=/Applications/Blender.app/Contents/MacOS/Blender \
        uv run python -m unittest tests.integration.real_blender.test_all_26_tools -v
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from ._blender_harness import BlenderProcessHarness, find_free_port

_LAUNCH_SCRIPT = Path(__file__).parent.parent.parent.parent / "src" / "blender_mcp_addon" / "server" / "_launch.py"

_TEST_OBJECTS = ["T_Cube", "T_Sphere", "T_Light", "T_Camera", "T_Armature"]


def _has_blender() -> bool:
    return bool(os.environ.get("BLENDER_EXECUTABLE"))


@unittest.skipUnless(_has_blender(), "BLENDER_EXECUTABLE not set")
class TestAll26Tools(unittest.TestCase):
    harness: BlenderProcessHarness  # type: ignore[assignment]

    @classmethod
    def setUpClass(cls) -> None:
        blender_path = os.environ["BLENDER_EXECUTABLE"]
        port = find_free_port()
        cls.harness = BlenderProcessHarness(blender_path, port=port)
        cls.harness._server_script = _LAUNCH_SCRIPT
        if not cls.harness.start():
            raise RuntimeError("Failed to start Blender process")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.harness.stop()

    def _req(self, capability: str, payload: dict | None = None) -> dict:
        return self.harness.send_request(
            {
                "capability": capability,
                "payload": payload or {},
            }
        )

    def _assert_ok(self, r: dict) -> dict:
        self.assertTrue(r["ok"], f"{r.get('error')}")
        self.assertIn("result", r)
        return r["result"]

    # ----------------------------------------------------------------
    # 1. Connection
    # ----------------------------------------------------------------

    def test_01_get_scene(self) -> None:
        result = self._assert_ok(
            self._req(
                "blender.get_scene",
                {
                    "include": ["stats", "render", "timeline", "version"],
                },
            )
        )
        self.assertIn("stats", result)

    # ----------------------------------------------------------------
    # 2. Perception (read default scene)
    # ----------------------------------------------------------------

    def test_02_get_objects(self) -> None:
        result = self._assert_ok(self._req("blender.get_objects"))
        items = result.get("items", result) if isinstance(result, dict) else result
        names = [o["name"] for o in items]
        self.assertIn("Camera", names)
        self.assertIn("Cube", names)
        self.assertIn("Light", names)

    def test_03_get_object_data_default(self) -> None:
        result = self._assert_ok(
            self._req(
                "blender.get_object_data",
                {
                    "name": "Cube",
                    "include": ["summary", "mesh_stats"],
                },
            )
        )
        self.assertIn("name", result)

    def test_04_get_selection(self) -> None:
        self._assert_ok(self._req("blender.get_selection"))

    def test_05_get_materials(self) -> None:
        self._assert_ok(self._req("blender.get_materials"))

    def test_06_get_collections(self) -> None:
        result = self._assert_ok(self._req("blender.get_collections"))
        self.assertIsInstance(result, (list, dict))

    def test_07_get_images(self) -> None:
        self._assert_ok(self._req("blender.get_images"))

    # ----------------------------------------------------------------
    # 3. Create objects
    # ----------------------------------------------------------------

    def test_08_create_object_cube(self) -> None:
        self._assert_ok(
            self._req(
                "blender.create_object",
                {
                    "name": "T_Cube",
                    "object_type": "MESH",
                    "primitive": "cube",
                    "location": [1, 0, 0],
                },
            )
        )

    def test_09_create_object_sphere(self) -> None:
        self._assert_ok(
            self._req(
                "blender.create_object",
                {
                    "name": "T_Sphere",
                    "object_type": "MESH",
                    "primitive": "sphere",
                    "segments": 16,
                    "location": [2, 0, 0],
                },
            )
        )

    def test_10_create_object_light(self) -> None:
        self._assert_ok(
            self._req(
                "blender.create_object",
                {
                    "name": "T_Light",
                    "object_type": "LIGHT",
                    "light_type": "POINT",
                    "energy": 500,
                    "color": [0.9, 0.9, 1.0],
                    "location": [3, 0, 2],
                },
            )
        )

    def test_11_create_object_camera(self) -> None:
        self._assert_ok(
            self._req(
                "blender.create_object",
                {
                    "name": "T_Camera",
                    "object_type": "CAMERA",
                    "lens": 50,
                    "location": [0, -5, 2],
                },
            )
        )

    def test_12_create_object_armature(self) -> None:
        self._assert_ok(
            self._req(
                "blender.create_object",
                {
                    "name": "T_Armature",
                    "object_type": "ARMATURE",
                    "location": [0, 0, 0],
                },
            )
        )

    # ----------------------------------------------------------------
    # 4. Read created objects
    # ----------------------------------------------------------------

    def test_13_get_object_data_full(self) -> None:
        result = self._assert_ok(
            self._req(
                "blender.get_object_data",
                {
                    "name": "T_Cube",
                    "include": [
                        "summary",
                        "mesh_stats",
                        "modifiers",
                        "materials",
                        "constraints",
                        "custom_properties",
                        "vertex_groups",
                        "shape_keys",
                        "uv_maps",
                        "particle_systems",
                    ],
                },
            )
        )
        self.assertEqual(result["name"], "T_Cube")

    def test_14_get_armature_data(self) -> None:
        self._assert_ok(
            self._req(
                "blender.get_armature_data",
                {
                    "armature_name": "T_Armature",
                    "include": ["hierarchy", "poses"],
                },
            )
        )

    # ----------------------------------------------------------------
    # 5. Modify
    # ----------------------------------------------------------------

    def test_15_modify_object(self) -> None:
        self._assert_ok(
            self._req(
                "blender.modify_object",
                {
                    "name": "T_Cube",
                    "location": [5, 5, 5],
                    "rotation": [0, 0, 0.785],
                    "scale": [1.5, 1.5, 1.5],
                },
            )
        )

    def test_16_manage_material_create(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_material",
                {
                    "action": "create",
                    "name": "T_Mat",
                    "base_color": [0.8, 0.2, 0.2, 1.0],
                    "metallic": 0.5,
                    "roughness": 0.3,
                },
            )
        )

    def test_17_manage_material_assign(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_material",
                {
                    "action": "assign",
                    "name": "T_Mat",
                    "object_name": "T_Cube",
                },
            )
        )

    def test_18_manage_modifier_add(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_modifier",
                {
                    "action": "add",
                    "object_name": "T_Cube",
                    "modifier_name": "SubD",
                    "modifier_type": "SUBSURF",
                    "settings": {"levels": 2},
                },
            )
        )

    def test_19_manage_collection(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_collection",
                {
                    "action": "create",
                    "collection_name": "T_Collection",
                    "color_tag": "COLOR_01",
                },
            )
        )
        self._assert_ok(
            self._req(
                "blender.manage_collection",
                {
                    "action": "link_object",
                    "collection_name": "T_Collection",
                    "object_name": "T_Sphere",
                },
            )
        )

    def test_20_manage_constraints(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_constraints",
                {
                    "action": "add",
                    "target_name": "T_Sphere",
                    "constraint_type": "TRACK_TO",
                    "settings": {"target": "T_Cube"},
                },
            )
        )

    # ----------------------------------------------------------------
    # 6. Node editing
    # ----------------------------------------------------------------

    def test_21_get_node_tree(self) -> None:
        result = self._assert_ok(
            self._req(
                "blender.get_node_tree",
                {
                    "tree_type": "SHADER",
                    "context": "OBJECT",
                    "target": "T_Mat",
                    "depth": "full",
                },
            )
        )
        self.assertIn("nodes", result)

    def test_22_edit_nodes(self) -> None:
        self._assert_ok(
            self._req(
                "blender.edit_nodes",
                {
                    "tree_type": "SHADER",
                    "context": "OBJECT",
                    "target": "T_Mat",
                    "operations": [
                        {
                            "action": "add_node",
                            "type": "ShaderNodeTexNoise",
                            "name": "T_NoiseNode",
                            "location": [-400, 200],
                        },
                        {
                            "action": "set_property",
                            "node": "T_NoiseNode",
                            "property": "noise_dimensions",
                            "value": "3D",
                        },
                    ],
                },
            )
        )

    # ----------------------------------------------------------------
    # 7. Animation
    # ----------------------------------------------------------------

    def test_23_edit_animation(self) -> None:
        self._assert_ok(
            self._req(
                "blender.edit_animation",
                {
                    "action": "insert_keyframe",
                    "object_name": "T_Cube",
                    "data_path": "location",
                    "index": 0,
                    "frame": 1,
                    "value": 5.0,
                },
            )
        )
        self._assert_ok(
            self._req(
                "blender.edit_animation",
                {
                    "action": "insert_keyframe",
                    "object_name": "T_Cube",
                    "data_path": "location",
                    "index": 0,
                    "frame": 24,
                    "value": 10.0,
                },
            )
        )

    def test_24_get_animation_data(self) -> None:
        self._assert_ok(
            self._req(
                "blender.get_animation_data",
                {
                    "target": "T_Cube",
                    "include": ["keyframes"],
                },
            )
        )

    # ----------------------------------------------------------------
    # 8. Scene
    # ----------------------------------------------------------------

    def test_25_setup_scene(self) -> None:
        self._assert_ok(
            self._req(
                "blender.setup_scene",
                {
                    "frame_start": 1,
                    "frame_end": 120,
                    "fps": 30,
                },
            )
        )

    # ----------------------------------------------------------------
    # 9. UV
    # ----------------------------------------------------------------

    def test_26_manage_uv(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_uv",
                {
                    "action": "smart_project",
                    "object_name": "T_Cube",
                    "angle_limit": 66,
                    "island_margin": 0.02,
                },
            )
        )

    # ----------------------------------------------------------------
    # 10. VSE
    # ----------------------------------------------------------------

    def test_27_edit_sequencer(self) -> None:
        r = self._req(
            "blender.edit_sequencer",
            {
                "action": "add_strip",
                "strip_type": "COLOR",
                "channel": 1,
                "frame_start": 1,
                "frame_end": 30,
                "color": [1, 0, 0],
            },
        )
        self.assertTrue(r["ok"], f"edit_sequencer failed: {r.get('error')}")

    # ----------------------------------------------------------------
    # 11. Physics
    # ----------------------------------------------------------------

    def test_28_manage_physics(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_physics",
                {
                    "action": "add",
                    "object_name": "T_Cube",
                    "physics_type": "RIGID_BODY",
                    "settings": {"mass": 1.0},
                },
            )
        )

    # ----------------------------------------------------------------
    # 12. Fallback
    # ----------------------------------------------------------------

    def test_29_execute_operator(self) -> None:
        self._assert_ok(
            self._req(
                "blender.execute_operator",
                {
                    "operator": "object.select_all",
                    "params": {"action": "DESELECT"},
                },
            )
        )

    def test_30_execute_script(self) -> None:
        r = self._req(
            "blender.execute_script",
            {
                "code": "import bpy; _mcp_print(len(bpy.data.objects))",
            },
        )
        if r["ok"]:
            self.assertIn("result", r)
        else:
            self.assertIn("script_disabled", str(r.get("error", "")))

    def test_31_import_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "t_export.stl")
            self._assert_ok(
                self._req(
                    "blender.import_export",
                    {
                        "action": "export",
                        "format": "STL",
                        "filepath": filepath,
                    },
                )
            )
            self.assertTrue(os.path.exists(filepath), "Exported STL file not found")

    # ----------------------------------------------------------------
    # 13. Viewport
    # ----------------------------------------------------------------

    def test_32_capture_viewport(self) -> None:
        r = self._req("blender.capture_viewport", {"shading": "SOLID"})
        if r["ok"]:
            self.assertIn("result", r)

    # ----------------------------------------------------------------
    # 14. Cleanup
    # ----------------------------------------------------------------

    def test_33_cleanup_delete_test_objects(self) -> None:
        for name in _TEST_OBJECTS:
            r = self._req("blender.modify_object", {"name": name, "delete": True})
            self.assertTrue(r["ok"], f"Failed to delete {name}: {r.get('error')}")

    def test_34_cleanup_collection(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_collection",
                {
                    "action": "delete",
                    "collection_name": "T_Collection",
                },
            )
        )

    def test_35_cleanup_material(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_material",
                {
                    "action": "delete",
                    "name": "T_Mat",
                },
            )
        )


if __name__ == "__main__":
    unittest.main()
