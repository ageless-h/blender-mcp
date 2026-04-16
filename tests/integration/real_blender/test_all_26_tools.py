# -*- coding: utf-8 -*-
"""End-to-end tests for all 26 MCP tools against a real Blender instance.

Run via:
    BLENDER_EXECUTABLE=/Applications/Blender.app/Contents/MacOS/Blender \
        uv run python -m unittest tests.integration.real_blender.test_all_26_tools -v
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from ._blender_harness import BlenderProcessHarness, find_free_port

_LAUNCH_SCRIPT = Path(__file__).parent.parent.parent.parent / "src" / "blender_mcp_addon" / "server" / "_launch.py"

_TEST_OBJECTS = ["T_Cube", "T_Sphere", "T_Light", "T_Camera", "T_Armature", "T_Empty", "T_Curve", "T_Text"]


def _has_blender() -> bool:
    return bool(os.environ.get("BLENDER_EXECUTABLE"))


def _detect_blender_version(exe_path: str) -> tuple[int, ...]:
    result = subprocess.run(
        [exe_path, "--version"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    for line in result.stdout.strip().split("\n"):
        if line.startswith("Blender "):
            parts = line.split()[1].split(".")
            return tuple(int(p) for p in parts[:3])
    return (0, 0, 0)


@unittest.skipUnless(_has_blender(), "BLENDER_EXECUTABLE not set")
class TestAll26Tools(unittest.TestCase):
    harness: BlenderProcessHarness  # type: ignore[assignment]
    blender_version: tuple[int, ...] = (0, 0, 0)
    _failed_prerequisites: set[str] = set()

    @classmethod
    def setUpClass(cls) -> None:
        blender_path = os.environ["BLENDER_EXECUTABLE"]
        cls.blender_version = _detect_blender_version(blender_path)
        port = find_free_port()
        cls.harness = BlenderProcessHarness(blender_path, port=port)
        cls.harness._server_script = _LAUNCH_SCRIPT
        if not cls.harness.start():
            raise RuntimeError("Failed to start Blender process")
        cls._failed_prerequisites = set()

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
        if not r.get("ok"):
            self._print_blender_diag()
        self.assertTrue(r["ok"], f"{r.get('error')}")
        self.assertIn("result", r)
        return r["result"]

    def _print_blender_diag(self) -> None:
        try:
            diag = self.harness.send_request(
                {
                    "capability": "blender.execute_script",
                    "payload": {
                        "code": (
                            "import bpy\n"
                            "text = bpy.data.texts.get('__mcp_diag__')\n"
                            "_mcp_print(text.as_string() if text else 'no __mcp_diag__ text block')"
                        )
                    },
                }
            )
            if diag.get("ok"):
                output = diag.get("result", {}).get("output", "")
                if output:
                    print(f"\n[Blender diag]\n{output}")
        except Exception:
            pass

    def _require(self, *objects: str) -> None:
        missing = [o for o in objects if o in self.__class__._failed_prerequisites]
        if missing:
            self.skipTest(f"Skipped: prerequisite object(s) failed to create: {', '.join(missing)}")

    def _mark_failed(self, *objects: str) -> None:
        self.__class__._failed_prerequisites.update(objects)

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
        r = self._req(
            "blender.create_object",
            {
                "name": "T_Cube",
                "object_type": "MESH",
                "primitive": "cube",
                "location": [1, 0, 0],
            },
        )
        if not r.get("ok"):
            self._mark_failed("T_Cube")
        self._assert_ok(r)

    def test_09_create_object_sphere(self) -> None:
        r = self._req(
            "blender.create_object",
            {
                "name": "T_Sphere",
                "object_type": "MESH",
                "primitive": "sphere",
                "segments": 16,
                "location": [2, 0, 0],
            },
        )
        if not r.get("ok"):
            self._mark_failed("T_Sphere")
        self._assert_ok(r)

    def test_10_create_object_light(self) -> None:
        r = self._req(
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
        if not r.get("ok"):
            self._mark_failed("T_Light")
        self._assert_ok(r)

    def test_11_create_object_camera(self) -> None:
        r = self._req(
            "blender.create_object",
            {
                "name": "T_Camera",
                "object_type": "CAMERA",
                "lens": 50,
                "location": [0, -5, 2],
            },
        )
        if not r.get("ok"):
            self._mark_failed("T_Camera")
        self._assert_ok(r)

    def test_12_create_object_armature(self) -> None:
        r = self._req(
            "blender.create_object",
            {
                "name": "T_Armature",
                "object_type": "ARMATURE",
                "location": [0, 0, 0],
            },
        )
        if not r.get("ok"):
            self._mark_failed("T_Armature")
        self._assert_ok(r)

    # ----------------------------------------------------------------
    # 4. Read created objects
    # ----------------------------------------------------------------

    def test_13_get_object_data_full(self) -> None:
        self._require("T_Cube")
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
        self._require("T_Armature")
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
        self._require("T_Cube")
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

    def test_15b_modify_object_visibility(self) -> None:
        self._require("T_Sphere")
        self._assert_ok(
            self._req(
                "blender.modify_object",
                {"name": "T_Sphere", "visible": False},
            )
        )
        self._assert_ok(
            self._req(
                "blender.modify_object",
                {"name": "T_Sphere", "visible": True},
            )
        )

    def test_15c_modify_object_rename(self) -> None:
        self._require("T_Empty")
        self._assert_ok(
            self._req(
                "blender.modify_object",
                {"name": "T_Empty", "new_name": "T_Empty_Renamed"},
            )
        )
        self._assert_ok(
            self._req(
                "blender.modify_object",
                {"name": "T_Empty_Renamed", "new_name": "T_Empty"},
            )
        )

    def test_16_manage_material_create(self) -> None:
        self._require("T_Cube")
        r = self._req(
            "blender.manage_material",
            {
                "action": "create",
                "name": "T_Mat",
                "base_color": [0.8, 0.2, 0.2, 1.0],
                "metallic": 0.5,
                "roughness": 0.3,
            },
        )
        if not r.get("ok"):
            self._mark_failed("T_Mat")
        self._assert_ok(r)

    def test_16b_manage_material_edit(self) -> None:
        self._require("T_Mat")
        self._assert_ok(
            self._req(
                "blender.manage_material",
                {
                    "action": "edit",
                    "name": "T_Mat",
                    "roughness": 0.7,
                    "metallic": 0.2,
                },
            )
        )

    def test_17_manage_material_assign(self) -> None:
        self._require("T_Cube", "T_Mat")
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

    def test_08b_create_object_empty(self) -> None:
        r = self._req(
            "blender.create_object",
            {
                "name": "T_Empty",
                "object_type": "EMPTY",
                "location": [4, 0, 0],
            },
        )
        if not r.get("ok"):
            self._mark_failed("T_Empty")
        self._assert_ok(r)

    def test_08c_create_object_curve(self) -> None:
        r = self._req(
            "blender.create_object",
            {
                "name": "T_Curve",
                "object_type": "CURVE",
                "location": [5, 0, 0],
            },
        )
        if not r.get("ok"):
            self._mark_failed("T_Curve")
        self._assert_ok(r)

    def test_08d_create_object_text(self) -> None:
        r = self._req(
            "blender.create_object",
            {
                "name": "T_Text",
                "object_type": "TEXT",
                "location": [6, 0, 0],
            },
        )
        if not r.get("ok"):
            self._mark_failed("T_Text")
        self._assert_ok(r)

    def test_18_manage_modifier_add(self) -> None:
        self._require("T_Cube")
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

    def test_18b_manage_modifier_configure(self) -> None:
        self._require("T_Cube")
        self._assert_ok(
            self._req(
                "blender.manage_modifier",
                {
                    "action": "configure",
                    "object_name": "T_Cube",
                    "modifier_name": "SubD",
                    "settings": {"levels": 3},
                },
            )
        )

    def test_18c_manage_modifier_remove(self) -> None:
        self._require("T_Cube")
        self._assert_ok(
            self._req(
                "blender.manage_modifier",
                {
                    "action": "remove",
                    "object_name": "T_Cube",
                    "modifier_name": "SubD",
                },
            )
        )

    def test_18d_manage_modifier_move_and_apply(self) -> None:
        self._require("T_Cube")
        for name, typ in [("SubD_A", "SUBSURF"), ("Bevel_B", "BEVEL")]:
            self._assert_ok(
                self._req(
                    "blender.manage_modifier",
                    {
                        "action": "add",
                        "object_name": "T_Cube",
                        "modifier_name": name,
                        "modifier_type": typ,
                        "settings": {},
                    },
                )
            )
        self._assert_ok(
            self._req(
                "blender.manage_modifier",
                {
                    "action": "move_up",
                    "object_name": "T_Cube",
                    "modifier_name": "Bevel_B",
                },
            )
        )
        self._assert_ok(
            self._req(
                "blender.manage_modifier",
                {
                    "action": "move_down",
                    "object_name": "T_Cube",
                    "modifier_name": "Bevel_B",
                },
            )
        )
        for name in ["SubD_A", "Bevel_B"]:
            self._req(
                "blender.manage_modifier",
                {"action": "remove", "object_name": "T_Cube", "modifier_name": name},
            )

    def test_19_manage_collection(self) -> None:
        self._require("T_Sphere")
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

    def test_19b_manage_collection_visibility(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_collection",
                {
                    "action": "set_visibility",
                    "collection_name": "T_Collection",
                    "hide_viewport": False,
                    "hide_render": False,
                },
            )
        )

    def test_19c_manage_collection_unlink_object(self) -> None:
        self._require("T_Sphere")
        self._assert_ok(
            self._req(
                "blender.manage_collection",
                {
                    "action": "unlink_object",
                    "collection_name": "T_Collection",
                    "object_name": "T_Sphere",
                },
            )
        )

    def test_20_manage_constraints(self) -> None:
        self._require("T_Sphere", "T_Cube")
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

    def test_20b_manage_constraints_configure(self) -> None:
        self._require("T_Sphere", "T_Cube")
        self._assert_ok(
            self._req(
                "blender.manage_constraints",
                {
                    "action": "configure",
                    "target_name": "T_Sphere",
                    "constraint_name": "Track To",
                    "settings": {"target": "T_Cube"},
                },
            )
        )

    def test_20c_manage_constraints_enable_disable(self) -> None:
        self._require("T_Sphere")
        self._assert_ok(
            self._req(
                "blender.manage_constraints",
                {
                    "action": "disable",
                    "target_name": "T_Sphere",
                    "constraint_name": "Track To",
                },
            )
        )
        self._assert_ok(
            self._req(
                "blender.manage_constraints",
                {
                    "action": "enable",
                    "target_name": "T_Sphere",
                    "constraint_name": "Track To",
                },
            )
        )

    def test_20d_manage_constraints_remove(self) -> None:
        self._require("T_Sphere")
        self._assert_ok(
            self._req(
                "blender.manage_constraints",
                {
                    "action": "remove",
                    "target_name": "T_Sphere",
                    "constraint_name": "Track To",
                },
            )
        )

    # ----------------------------------------------------------------
    # 6. Node editing
    # ----------------------------------------------------------------

    def test_21_get_node_tree(self) -> None:
        self._require("T_Mat")
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
        self._require("T_Mat")
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

    def test_22b_edit_nodes_connect(self) -> None:
        self._require("T_Mat")
        self._assert_ok(
            self._req(
                "blender.edit_nodes",
                {
                    "tree_type": "SHADER",
                    "context": "OBJECT",
                    "target": "T_Mat",
                    "operations": [
                        {
                            "action": "connect",
                            "from_node": "T_NoiseNode",
                            "from_socket": "Color",
                            "to_node": "Principled BSDF",
                            "to_socket": "Base Color",
                        }
                    ],
                },
            )
        )

    def test_22c_edit_nodes_disconnect(self) -> None:
        self._require("T_Mat")
        self._assert_ok(
            self._req(
                "blender.edit_nodes",
                {
                    "tree_type": "SHADER",
                    "context": "OBJECT",
                    "target": "T_Mat",
                    "operations": [
                        {
                            "action": "disconnect",
                            "node": "Principled BSDF",
                            "input": "Base Color",
                        }
                    ],
                },
            )
        )

    def test_22d_edit_nodes_remove_node(self) -> None:
        self._require("T_Mat")
        self._assert_ok(
            self._req(
                "blender.edit_nodes",
                {
                    "tree_type": "SHADER",
                    "context": "OBJECT",
                    "target": "T_Mat",
                    "operations": [
                        {
                            "action": "remove_node",
                            "node": "T_NoiseNode",
                        }
                    ],
                },
            )
        )

    # ----------------------------------------------------------------
    # 7. Animation
    # ----------------------------------------------------------------

    def test_23_edit_animation(self) -> None:
        self._require("T_Cube")
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

    def test_23b_edit_animation_delete_keyframe(self) -> None:
        self._require("T_Cube")
        self._assert_ok(
            self._req(
                "blender.edit_animation",
                {
                    "action": "delete_keyframe",
                    "object_name": "T_Cube",
                    "data_path": "location",
                    "index": 0,
                    "frame": 24,
                },
            )
        )

    def test_23c_edit_animation_set_frame_range(self) -> None:
        self._assert_ok(
            self._req(
                "blender.edit_animation",
                {
                    "action": "set_frame_range",
                    "frame_start": 1,
                    "frame_end": 250,
                },
            )
        )

    def test_23d_edit_animation_set_frame(self) -> None:
        self._assert_ok(
            self._req(
                "blender.edit_animation",
                {
                    "action": "set_frame",
                    "frame": 12,
                },
            )
        )

    def test_23e_edit_animation_modify_keyframe(self) -> None:
        self._require("T_Cube")
        self._assert_ok(
            self._req(
                "blender.edit_animation",
                {
                    "action": "modify_keyframe",
                    "object_name": "T_Cube",
                    "data_path": "location",
                    "index": 0,
                    "frame": 1,
                    "value": 7.0,
                    "interpolation": "LINEAR",
                },
            )
        )

    def test_24_get_animation_data(self) -> None:
        self._require("T_Cube")
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
        self._require("T_Cube")
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

    def test_27b_edit_sequencer_modify_strip(self) -> None:
        r = self._req(
            "blender.edit_sequencer",
            {
                "action": "modify_strip",
                "strip_name": "Color",
                "settings": {"blend_alpha": 0.8},
            },
        )
        self.assertTrue(r["ok"], f"edit_sequencer modify_strip failed: {r.get('error')}")

    def test_27c_edit_sequencer_delete_strip(self) -> None:
        r = self._req(
            "blender.edit_sequencer",
            {
                "action": "delete_strip",
                "strip_name": "Color",
            },
        )
        self.assertTrue(r["ok"], f"edit_sequencer delete_strip failed: {r.get('error')}")

    def test_27d_edit_sequencer_add_effect(self) -> None:
        r = self._req(
            "blender.edit_sequencer",
            {
                "action": "add_strip",
                "strip_type": "ADJUSTMENT",
                "channel": 3,
                "frame_start": 1,
                "frame_end": 50,
            },
        )
        self.assertTrue(r["ok"], f"edit_sequencer add ADJUSTMENT strip failed: {r.get('error')}")

    def test_27e_edit_sequencer_move_strip(self) -> None:
        r = self._req(
            "blender.edit_sequencer",
            {
                "action": "move_strip",
                "strip_name": "Adjustment",
                "frame_start": 5,
            },
        )
        self.assertTrue(r["ok"], f"edit_sequencer move_strip failed: {r.get('error')}")

    def test_27f_edit_sequencer_add_transition(self) -> None:
        if self.blender_version >= (5, 1):
            self.skipTest("VSE strip creation broken in Blender 5.1 timer context")
        for strip_name, ch, fs, fe, color in [
            ("TCol_A", 1, 1, 30, [0, 1, 0]),
            ("TCol_B", 1, 20, 50, [0, 0, 1]),
        ]:
            r = self._req(
                "blender.edit_sequencer",
                {
                    "action": "add_strip",
                    "strip_type": "COLOR",
                    "channel": ch,
                    "frame_start": fs,
                    "frame_end": fe,
                    "color": color,
                },
            )
            self.assertTrue(r["ok"], f"add_strip {strip_name} failed: {r.get('error')}")
        r = self._req(
            "blender.edit_sequencer",
            {
                "action": "add_transition",
                "transition_type": "CROSS",
                "channel": 2,
                "strip1_name": "Color",
                "strip2_name": "Color.001",
                "frame_start": 20,
                "transition_duration": 10,
            },
        )
        self.assertTrue(r["ok"], f"edit_sequencer add_transition failed: {r.get('error')}")

    # ----------------------------------------------------------------
    # 11. Physics
    # ----------------------------------------------------------------

    def test_28_manage_physics(self) -> None:
        self._require("T_Cube")
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

    def test_28b_manage_physics_configure(self) -> None:
        self._require("T_Cube")
        self._assert_ok(
            self._req(
                "blender.manage_physics",
                {
                    "action": "configure",
                    "object_name": "T_Cube",
                    "physics_type": "RIGID_BODY",
                    "settings": {"mass": 2.5},
                },
            )
        )

    def test_28c_manage_physics_remove(self) -> None:
        self._require("T_Cube")
        self._assert_ok(
            self._req(
                "blender.manage_physics",
                {
                    "action": "remove",
                    "object_name": "T_Cube",
                    "physics_type": "RIGID_BODY",
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

    def test_31b_import_export_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = os.path.join(tmpdir, "t_roundtrip.stl")
            self._assert_ok(
                self._req(
                    "blender.import_export",
                    {
                        "action": "export",
                        "format": "STL",
                        "filepath": export_path,
                    },
                )
            )
            self.assertTrue(os.path.exists(export_path), "Export file missing before import test")
            self._assert_ok(
                self._req(
                    "blender.import_export",
                    {
                        "action": "import",
                        "format": "STL",
                        "filepath": export_path,
                    },
                )
            )

    # ----------------------------------------------------------------
    # 13. Viewport
    # ----------------------------------------------------------------

    def test_32_capture_viewport(self) -> None:
        r = self._req("blender.capture_viewport", {"shading": "SOLID"})
        if r["ok"]:
            self.assertIn("result", r)

    # ----------------------------------------------------------------
    # 13b. Version-specific tests (Blender 5.0+)
    # ----------------------------------------------------------------

    def test_33_layered_animation_blender_50(self) -> None:
        self._require("T_Cube")
        if self.blender_version < (5, 0):
            self.skipTest(
                f"Layered animation requires Blender 5.0+, got {'.'.join(str(v) for v in self.blender_version)}"
            )

        result = self._assert_ok(
            self._req(
                "blender.get_animation_data",
                {"target": "T_Cube", "include": ["fcurves"]},
            )
        )
        self.assertIn("fcurves", result)

    # ----------------------------------------------------------------
    # 13c. Version-boundary API assertions
    # ----------------------------------------------------------------

    def test_33b_version_render_engine_name(self) -> None:
        result = self._assert_ok(self._req("blender.get_scene", {"include": ["render"]}))
        engine = result.get("render", {}).get("engine", "")
        if self.blender_version >= (5, 0):
            self.assertNotEqual(
                engine,
                "BLENDER_EEVEE_NEXT",
                f"Blender {self.blender_version}: engine should be BLENDER_EEVEE on 5.x, got {engine!r}",
            )
        else:
            self.assertNotEqual(
                engine,
                "BLENDER_EEVEE",
                f"Blender {self.blender_version}: engine should be BLENDER_EEVEE_NEXT on 4.x, got {engine!r}",
            )

    def test_33c_version_vse_strips_api(self) -> None:
        r = self._req(
            "blender.edit_sequencer",
            {
                "action": "add_strip",
                "strip_type": "COLOR",
                "channel": 2,
                "frame_start": 50,
                "frame_end": 80,
                "color": [0, 1, 0],
            },
        )
        self.assertTrue(
            r["ok"],
            f"VSE add_strip failed on Blender {self.blender_version}: {r.get('error')}",
        )

    # ----------------------------------------------------------------
    # 14. Cleanup
    # ----------------------------------------------------------------

    def test_34_cleanup_delete_test_objects(self) -> None:
        for name in _TEST_OBJECTS:
            r = self._req("blender.modify_object", {"name": name, "delete": True})
            self.assertTrue(r["ok"], f"Failed to delete {name}: {r.get('error')}")

    def test_35_cleanup_collection(self) -> None:
        self._assert_ok(
            self._req(
                "blender.manage_collection",
                {
                    "action": "delete",
                    "collection_name": "T_Collection",
                },
            )
        )

    def test_36_cleanup_material(self) -> None:
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
