# -*- coding: utf-8 -*-
"""Tests for plugin contract validation."""

from __future__ import annotations

import unittest

from blender_mcp.adapters.plugin_contract import PluginContract, validate_contract


class TestPluginContract(unittest.TestCase):
    def test_plugin_contract_creation(self):
        contract = PluginContract(version="0.1.0", entrypoints=["execute", "query"])
        self.assertEqual(contract.version, "0.1.0")
        self.assertEqual(contract.entrypoints, ["execute", "query"])

    def test_plugin_contract_empty_entrypoints(self):
        contract = PluginContract(version="1.0.0", entrypoints=[])
        self.assertEqual(contract.entrypoints, [])


class TestValidateContract(unittest.TestCase):
    def test_validate_all_required_present(self):
        contract = PluginContract(
            version="0.1.0",
            entrypoints=["execute", "query", "shutdown"],
        )
        self.assertTrue(validate_contract(contract, ["execute", "query"]))

    def test_validate_missing_required(self):
        contract = PluginContract(version="0.1.0", entrypoints=["execute"])
        self.assertFalse(validate_contract(contract, ["execute", "query"]))

    def test_validate_empty_version(self):
        contract = PluginContract(version="", entrypoints=["execute"])
        self.assertFalse(validate_contract(contract, ["execute"]))

    def test_validate_no_required_entrypoints(self):
        contract = PluginContract(version="0.1.0", entrypoints=[])
        self.assertTrue(validate_contract(contract, []))

    def test_validate_exact_match(self):
        contract = PluginContract(version="0.1.0", entrypoints=["execute", "query"])
        self.assertTrue(validate_contract(contract, ["execute", "query"]))

    def test_validate_extra_entrypoints(self):
        contract = PluginContract(
            version="0.1.0",
            entrypoints=["execute", "query", "extra"],
        )
        self.assertTrue(validate_contract(contract, ["execute", "query"]))


if __name__ == "__main__":
    unittest.main()
