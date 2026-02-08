# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_mcp.adapters.types import AdapterResult
from blender_mcp.catalog.catalog import minimal_capability_set
from blender_mcp.core.types import Request

from ._harness import build_integration_harness


class TestWorkflowScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = build_integration_harness()
        self.server = self.harness.server

    def test_allowed_capability_executes(self) -> None:
        request = Request(
            capability="blender.get_scene", payload={}, scopes=["info:read"]
        )
        response = self.server.handle_request(request)
        self.assertTrue(response.ok)

    def test_capability_discovery_returns_catalog(self) -> None:
        request = Request(capability="capabilities.list", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertTrue(response.ok)
        names = {cap["name"] for cap in response.result["capabilities"]}
        expected = {cap.name for cap in minimal_capability_set()}
        self.assertEqual(names, expected)

    def test_disallowed_capability_rejected(self) -> None:
        request = Request(capability="nonexistent.delete", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "capability_not_allowed")

    def test_missing_scope_rejected(self) -> None:
        request = Request(capability="blender.get_object_data", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "missing_scope")

    def test_rate_limit_rejected(self) -> None:
        request = Request(
            capability="blender.get_object_data", payload={}, scopes=["data:read"]
        )
        self.assertTrue(self.server.handle_request(request).ok)
        self.assertTrue(self.server.handle_request(request).ok)
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "rate_limited")

    def test_rate_limit_window_reset(self) -> None:
        self.harness.rate_limiter.window_seconds = 0.0
        request = Request(
            capability="blender.get_object_data", payload={}, scopes=["data:read"]
        )
        self.assertTrue(self.server.handle_request(request).ok)
        self.assertTrue(self.server.handle_request(request).ok)


class TestAdapterDispatch(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = build_integration_harness()
        self.server = self.harness.server
        self.adapter = self.harness.adapter

    def test_adapter_result_returned_in_response(self) -> None:
        expected_result = {"scene_name": "TestScene", "object_count": 5}
        self.adapter.set_response(
            "blender.get_scene",
            AdapterResult(ok=True, result=expected_result),
        )
        request = Request(
            capability="blender.get_scene", payload={}, scopes=["info:read"]
        )
        response = self.server.handle_request(request)
        self.assertTrue(response.ok)
        self.assertEqual(response.result, expected_result)

    def test_adapter_error_returned_in_response(self) -> None:
        self.adapter.set_response(
            "blender.get_scene",
            AdapterResult(ok=False, error="bpy_unavailable"),
        )
        request = Request(
            capability="blender.get_scene", payload={}, scopes=["info:read"]
        )
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "bpy_unavailable")

    def test_security_checks_before_adapter_dispatch(self) -> None:
        self.adapter.set_response(
            "blender.get_scene",
            AdapterResult(ok=True, result={"should_not_reach": True}),
        )
        request = Request(
            capability="blender.get_scene", payload={}, scopes=[]
        )
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "missing_scope")

    def test_end_to_end_scene_read_with_simulated_data(self) -> None:
        simulated_scene = {
            "scene_name": "Scene",
            "object_count": 3,
            "selected_objects": ["Cube", "Camera"],
            "active_object": "Cube",
        }
        self.adapter.set_response(
            "blender.get_scene",
            AdapterResult(ok=True, result=simulated_scene),
        )
        request = Request(
            capability="blender.get_scene", payload={}, scopes=["info:read"]
        )
        response = self.server.handle_request(request)
        self.assertTrue(response.ok)
        self.assertEqual(response.result["scene_name"], "Scene")
        self.assertEqual(response.result["object_count"], 3)
        self.assertIn("Cube", response.result["selected_objects"])


if __name__ == "__main__":
    unittest.main()
