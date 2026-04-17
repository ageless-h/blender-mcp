# -*- coding: utf-8 -*-
"""Tests for audit logging."""

from __future__ import annotations

import os
import tempfile
import unittest

from blender_mcp.security.audit import AuditEvent, JsonFileAuditLogger, MemoryAuditLogger


class TestAuditEvent(unittest.TestCase):
    def test_fields(self):
        e = AuditEvent(capability="test", ok=True, error=None)
        self.assertEqual(e.capability, "test")
        self.assertTrue(e.ok)
        self.assertIsNone(e.error)
        self.assertIsInstance(e.timestamp, str)

    def test_frozen(self):
        e = AuditEvent(capability="x", ok=False)
        with self.assertRaises(AttributeError):
            e.capability = "y"


class TestMemoryAuditLogger(unittest.TestCase):
    def test_record_and_list(self):
        logger = MemoryAuditLogger()
        ev = AuditEvent(capability="a", ok=True)
        logger.record(ev)
        self.assertEqual(len(logger.events), 1)
        self.assertEqual(logger.events[0], ev)

    def test_export_json(self):
        logger = MemoryAuditLogger()
        logger.record(AuditEvent(capability="b", ok=True))
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            logger.export_json(path)
            self.assertTrue(os.path.getsize(path) > 0)
        finally:
            os.unlink(path)


class TestJsonFileAuditLogger(unittest.TestCase):
    def test_record_appends(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            logger = JsonFileAuditLogger(path)
            logger.record(AuditEvent(capability="c", ok=True))
            logger.record(AuditEvent(capability="d", ok=False))
            logger.flush()
            with open(path) as fh:
                lines = fh.readlines()
            self.assertEqual(len(lines), 2)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
