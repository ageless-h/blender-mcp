# -*- coding: utf-8 -*-
"""Unit tests for script executor — security controls, timeout, audit log."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


class TestScriptConfig(unittest.TestCase):
    def test_default_config(self):
        from blender_mcp_addon.handlers.script.executor import (
            _script_config,
            is_script_execution_enabled,
        )

        self.assertFalse(is_script_execution_enabled())
        self.assertEqual(_script_config["default_timeout"], 30)

    def test_configure_enable(self):
        from blender_mcp_addon.handlers.script.executor import (
            configure_script_execution,
            is_script_execution_enabled,
        )

        configure_script_execution(enabled=True)
        self.assertTrue(is_script_execution_enabled())
        configure_script_execution(enabled=False)

    def test_configure_timeout(self):
        from blender_mcp_addon.handlers.script.executor import (
            _script_config,
            configure_script_execution,
        )

        configure_script_execution(default_timeout=60)
        self.assertEqual(_script_config["default_timeout"], 60)
        configure_script_execution(default_timeout=30)


class TestAuditLog(unittest.TestCase):
    def test_get_audit_log(self):
        from blender_mcp_addon.handlers.script.executor import (
            clear_audit_log,
            get_audit_log,
        )

        clear_audit_log()
        log = get_audit_log()
        self.assertIsInstance(log, list)

    def test_clear_audit_log(self):
        from blender_mcp_addon.handlers.script.executor import (
            clear_audit_log,
            get_audit_log,
        )

        clear_audit_log()
        self.assertEqual(len(get_audit_log()), 0)

    def test_get_audit_log_with_limit(self):
        from blender_mcp_addon.handlers.script.executor import (
            clear_audit_log,
            get_audit_log,
        )

        clear_audit_log()
        log = get_audit_log(limit=10)
        self.assertIsInstance(log, list)


class TestScriptExecuteValidation(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.script.executor.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.script.executor import script_execute

        result = script_execute({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.script.executor.check_bpy_available")
    def test_script_disabled(self, mock_check):
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.script.executor import (
            configure_script_execution,
            script_execute,
        )

        configure_script_execution(enabled=False)
        result = script_execute({"code": "1+1"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "script_disabled")

    @patch("blender_mcp_addon.handlers.script.executor.check_bpy_available")
    def test_missing_code(self, mock_check):
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.script.executor import (
            configure_script_execution,
            script_execute,
        )

        configure_script_execution(enabled=True, require_consent=False)
        result = script_execute({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("code", result["error"]["message"])
        configure_script_execution(enabled=False)

    @patch("blender_mcp_addon.handlers.script.executor.check_bpy_available")
    def test_non_string_code(self, mock_check):
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.script.executor import (
            configure_script_execution,
            script_execute,
        )

        configure_script_execution(enabled=True, require_consent=False)
        result = script_execute({"code": 123}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("string", result["error"]["message"])
        configure_script_execution(enabled=False)


class TestScriptExecuteConsent(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.script.executor.check_bpy_available")
    def test_consent_required(self, mock_check):
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.script.executor import (
            configure_script_execution,
            script_execute,
        )

        configure_script_execution(enabled=True, require_consent=True)
        result = script_execute({"code": "1+1"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "consent_required")

    @patch("blender_mcp_addon.handlers.script.executor.check_bpy_available")
    def test_consent_granted(self, mock_check):
        bpy = MagicMock()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.script.executor import (
            clear_audit_log,
            configure_script_execution,
            script_execute,
        )

        configure_script_execution(enabled=True, require_consent=True, audit_log_enabled=True)
        clear_audit_log()
        result = script_execute({"code": "1+1", "consent_granted": True}, started=_started())
        self.assertTrue(result["ok"])
        configure_script_execution(enabled=False, require_consent=False)


if __name__ == "__main__":
    unittest.main()
