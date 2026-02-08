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
    def test_get_scene(blender_harness: BlenderProcessHarness) -> None:
        """Test blender.get_scene capability against real Blender.

        Verifies that:
        - Blender process starts successfully
        - Socket communication works
        - blender.get_scene capability returns valid data
        - Response includes expected fields
        """
        response = blender_harness.send_request({
            "capability": "blender.get_scene",
            "payload": {"include": ["stats", "render", "timeline"]},
        })

        assert response["ok"], f"blender.get_scene failed: {response.get('error')}"
        assert response["result"] is not None


    @pytest.mark.skipif(_should_skip_tests(), reason="No Blender configured")
    def test_create_object(blender_harness: BlenderProcessHarness) -> None:
        """Test blender.create_object capability against real Blender.

        Verifies that:
        - blender.create_object can create objects in the scene
        - Response includes expected result
        """
        response = blender_harness.send_request({
            "capability": "blender.create_object",
            "payload": {
                "name": "TEST_CUBE_INTEGRATION",
                "object_type": "MESH",
                "primitive": "cube",
            },
        })

        assert response["ok"], f"blender.create_object failed: {response.get('error')}"
        assert response["result"] is not None


    @pytest.mark.skipif(_should_skip_tests(), reason="No Blender configured")
    def test_create_then_get_objects(blender_harness: BlenderProcessHarness) -> None:
        """Test create then list objects workflow.

        Verifies that:
        - Objects can be created and then listed
        - Object appears in the scene
        """
        create_response = blender_harness.send_request({
            "capability": "blender.create_object",
            "payload": {
                "name": "TEST_CUBE_LIST",
                "object_type": "MESH",
                "primitive": "cube",
            },
        })
        assert create_response["ok"], f"create failed: {create_response.get('error')}"

        # Verify object exists by listing objects
        list_response = blender_harness.send_request({
            "capability": "blender.get_objects",
            "payload": {},
        })
        assert list_response["ok"]


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
            "capability": "blender.get_scene",
            "payload": {},
        })
        assert response1["ok"]

        # Second request
        response2 = blender_harness.send_request({
            "capability": "blender.create_object",
            "payload": {"name": "TEST_MULTI_1", "object_type": "MESH"},
        })
        assert response2["ok"]

        # Third request
        response3 = blender_harness.send_request({
            "capability": "blender.get_objects",
            "payload": {},
        })
        assert response3["ok"]
