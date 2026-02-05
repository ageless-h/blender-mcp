"""Integration tests against real Blender installations.

These tests execute against actual Blender installations to verify
end-to-end functionality of the MCP socket server and capabilities.

These tests require pytest to run. When pytest is not available,
this module will be skipped during unittest discovery.
"""

from __future__ import annotations

from typing import Any, Generator

# pytest is required for these tests
try:
    import pytest
except ImportError:
    pytest = None  # type: ignore

from ._blender_harness import BlenderProcessHarness
from ._config import load_blender_configs


# Skip the entire module if pytest is not available
if pytest is None:
    import unittest

    class SkipRealBlenderTests(unittest.TestCase):
        """Dummy test case to skip when pytest is not available."""

        @unittest.skip("pytest not available - real Blender tests require pytest")
        def test_pytest_required(self) -> None:
            """Skip all tests when pytest is not available."""

    # Remove from module namespace so unittest doesn't try to run it
    del SkipRealBlenderTests
else:
    def _get_blender_configs() -> list[dict[str, Any]]:
        """Get Blender configurations, excluding tagged as skip.

        Returns:
            List of Blender configuration dictionaries.
        """
        all_configs = load_blender_configs()
        # Filter out configs tagged with 'skip'
        return [c for c in all_configs if "skip" not in c.get("tags", [])]


    def _should_skip_tests() -> bool:
        """Check if real Blender tests should be skipped.

        Returns:
            True if no Blender configurations are available.
        """
        configs = _get_blender_configs()
        return len(configs) == 0


    @pytest.fixture(params=_get_blender_configs(), ids=lambda c: f"blender-{c['version']}")
    def blender_config(request: pytest.FixtureRequest) -> Generator[dict[str, Any], None, None]:
        """Fixture providing Blender configuration for each test.

        This fixture is parametrized to run tests against all configured
        Blender versions.

        Args:
            request: Pytest fixture request.

        Yields:
            Blender configuration dictionary.
        """
        config = request.param
        yield config


    @pytest.fixture
    def blender_harness(blender_config: dict[str, Any]) -> Generator[BlenderProcessHarness, None, None]:
        """Fixture providing a Blender process harness for testing.

        Args:
            blender_config: Blender configuration from the parametrized fixture.

        Yields:
            Started BlenderProcessHarness instance.
        """
        with BlenderProcessHarness(blender_config["path"]) as harness:
            yield harness


    @pytest.mark.skipif(_should_skip_tests(), reason="No Blender configured")
    def test_scene_read(blender_harness: BlenderProcessHarness) -> None:
        """Test scene.read capability against real Blender.

        Verifies that:
        - Blender process starts successfully
        - Socket communication works
        - scene.read capability returns valid data
        - Response includes expected fields (scene_name, object_count, etc.)
        """
        response = blender_harness.send_request({
            "capability": "scene.read",
            "payload": {},
        })

        assert response["ok"], f"scene.read failed: {response.get('error')}"
        assert response["result"] is not None

        result = response["result"]
        assert "scene_name" in result
        assert "object_count" in result
        assert "selected_objects" in result
        assert "active_object" in result

        # object_count should be a non-negative integer
        assert isinstance(result["object_count"], int)
        assert result["object_count"] >= 0

        # selected_objects should be a list
        assert isinstance(result["selected_objects"], list)


    @pytest.mark.skipif(_should_skip_tests(), reason="No Blender configured")
    def test_scene_write(blender_harness: BlenderProcessHarness) -> None:
        """Test scene.write capability against real Blender.

        Verifies that:
        - scene.write can create objects in the scene
        - Cleanup mode works correctly
        - Response includes expected action confirmation
        """
        response = blender_harness.send_request({
            "capability": "scene.write",
            "payload": {
                "name": "TEST_CUBE_INTEGRATION",
                "cleanup": True,
            },
        })

        assert response["ok"], f"scene.write failed: {response.get('error')}"
        assert response["result"] is not None

        result = response["result"]
        assert result["action"] == "create_cube_placeholder"
        assert result["name"] == "TEST_CUBE_INTEGRATION"
        assert result["created"] is True
        assert result["cleanup"] is True


    @pytest.mark.skipif(_should_skip_tests(), reason="No Blender configured")
    def test_scene_write_without_cleanup(blender_harness: BlenderProcessHarness) -> None:
        """Test scene.write without cleanup mode.

        Verifies that:
        - scene.write can create objects without cleanup
        - Object remains in scene after creation
        """
        response = blender_harness.send_request({
            "capability": "scene.write",
            "payload": {
                "name": "TEST_CUBE_NO_CLEANUP",
                "cleanup": False,
            },
        })

        assert response["ok"], f"scene.write failed: {response.get('error')}"
        assert response["result"]["cleanup"] is False

        # Verify object exists by reading scene
        scene_response = blender_harness.send_request({
            "capability": "scene.read",
            "payload": {},
        })
        assert scene_response["ok"]
        # The object count should be > 0 since we didn't clean up
        assert scene_response["result"]["object_count"] > 0


    @pytest.mark.skipif(_should_skip_tests(), reason="No Blender configured")
    def test_unsupported_capability(blender_harness: BlenderProcessHarness) -> None:
        """Test error handling for unsupported capabilities.

        Verifies that:
        - Unsupported capabilities return proper error response
        - Error includes expected code and message
        """
        response = blender_harness.send_request({
            "capability": "unsupported.test",
            "payload": {},
        })

        assert response["ok"] is False
        assert response["error"] is not None
        assert response["error"]["code"] == "unsupported_capability"


    @pytest.mark.skipif(_should_skip_tests(), reason="No Blender configured")
    def test_invalid_request(blender_harness: BlenderProcessHarness) -> None:
        """Test error handling for invalid requests.

        Verifies that:
        - Invalid requests return proper error response
        - Error includes descriptive message
        """
        # Missing capability
        response = blender_harness.send_request({
            "payload": {},
        })

        assert response["ok"] is False
        assert response["error"] is not None
        assert response["error"]["code"] == "invalid_request"


    @pytest.mark.skipif(_should_skip_tests(), reason="No Blender configured")
    def test_multiple_requests_same_harness(blender_harness: BlenderProcessHarness) -> None:
        """Test multiple sequential requests on the same harness.

        Verifies that:
        - Harness can handle multiple requests
        - Each request gets a valid response
        - Blender process remains stable
        """
        # First request
        response1 = blender_harness.send_request({
            "capability": "scene.read",
            "payload": {},
        })
        assert response1["ok"]

        # Second request
        response2 = blender_harness.send_request({
            "capability": "scene.write",
            "payload": {"name": "TEST_MULTI_1", "cleanup": True},
        })
        assert response2["ok"]

        # Third request
        response3 = blender_harness.send_request({
            "capability": "scene.read",
            "payload": {},
        })
        assert response3["ok"]
