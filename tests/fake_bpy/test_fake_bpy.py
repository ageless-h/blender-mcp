# -*- coding: utf-8 -*-
"""Tests for the fake_bpy module."""

from __future__ import annotations

import sys
import unittest


class TestFakeBpyInstall(unittest.TestCase):
    def tearDown(self):
        if "bpy" in sys.modules and hasattr(sys.modules["bpy"], "data"):
            from fake_bpy import uninstall

            uninstall()

    def test_install_creates_fake_bpy(self):
        from fake_bpy import install

        install()
        import bpy

        self.assertIsNotNone(bpy.data)
        self.assertIsNotNone(bpy.context)
        self.assertIsNotNone(bpy.ops)
        self.assertIsNotNone(bpy.app)

    def test_install_with_version(self):
        from fake_bpy import install, uninstall

        install(version=(5, 0, 0))
        import bpy

        self.assertEqual(bpy.app.version, (5, 0, 0))
        self.assertEqual(bpy.app.version_string, "5.0.0")
        uninstall()

    def test_install_enables_curves_new_for_50(self):
        from fake_bpy import install, uninstall

        install(version=(5, 0, 0))
        import bpy

        self.assertTrue(hasattr(bpy.data, "curves_new"))
        uninstall()

    def test_install_no_curves_new_for_42(self):
        from fake_bpy import install, uninstall

        install(version=(4, 2, 0))
        import bpy

        self.assertFalse(hasattr(bpy.data, "curves_new"))
        uninstall()

    def test_uninstall_restores_original(self):
        from fake_bpy import install, uninstall

        original = sys.modules.get("bpy")
        install()
        fake_bpy = sys.modules["bpy"]
        self.assertIsNot(fake_bpy, original)
        uninstall()
        self.assertEqual(sys.modules.get("bpy"), original)

    def test_context_manager(self):
        from fake_bpy import fake_bpy_context

        with fake_bpy_context(version=(4, 5, 0)) as bpy:
            self.assertEqual(bpy.app.version, (4, 5, 0))
            self.assertEqual(len(bpy.data.objects), 0)


class TestFakeDataCollections(unittest.TestCase):
    def setUp(self):
        from fake_bpy import install

        install()

    def tearDown(self):
        from fake_bpy import uninstall

        uninstall()

    def test_create_and_get_object(self):
        import bpy

        obj = bpy.data.objects.new("Cube")
        self.assertEqual(obj.name, "Cube")
        self.assertEqual(bpy.data.objects.get("Cube"), obj)

    def test_remove_object(self):
        import bpy

        obj = bpy.data.objects.new("Cube")
        self.assertIn("Cube", bpy.data.objects)
        bpy.data.objects.remove(obj)
        self.assertIsNone(bpy.data.objects.get("Cube"))

    def test_collection_len(self):
        import bpy

        self.assertEqual(len(bpy.data.objects), 0)
        bpy.data.objects.new("A")
        bpy.data.objects.new("B")
        self.assertEqual(len(bpy.data.objects), 2)

    def test_iteration(self):
        import bpy

        bpy.data.objects.new("A")
        bpy.data.objects.new("B")
        names = [obj.name for obj in bpy.data.objects]
        self.assertEqual(sorted(names), ["A", "B"])

    def test_reset_clears_data(self):
        import bpy

        from fake_bpy import reset

        bpy.data.objects.new("Cube")
        self.assertEqual(len(bpy.data.objects), 1)
        reset()
        self.assertEqual(len(bpy.data.objects), 0)

    def test_data_block_kwargs(self):
        import bpy

        obj = bpy.data.objects.new("Light", location=(1, 2, 3))
        self.assertEqual(obj.name, "Light")
        self.assertEqual(obj.location, (1, 2, 3))


class TestFakeContext(unittest.TestCase):
    def setUp(self):
        from fake_bpy import install

        install()

    def tearDown(self):
        from fake_bpy import uninstall

        uninstall()

    def test_default_context(self):
        import bpy

        self.assertIsNone(bpy.context.scene)
        self.assertEqual(bpy.context.mode, "OBJECT")

    def test_temp_override(self):
        import bpy

        with bpy.context.temp_override(scene="mock_scene"):
            pass


class TestFakeApp(unittest.TestCase):
    def setUp(self):
        from fake_bpy import install

        install()

    def tearDown(self):
        from fake_bpy import uninstall

        uninstall()

    def test_version_properties(self):
        import bpy

        self.assertEqual(bpy.app.version, (4, 2, 0))
        self.assertEqual(bpy.app.version_string, "4.2.0")


if __name__ == "__main__":
    unittest.main()
