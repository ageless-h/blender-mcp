# -*- coding: utf-8 -*-
"""Core handlers for camera, light, armature, curve, and world types."""
from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class CameraHandler(BaseHandler):
    """Handler for Blender camera data type (bpy.data.cameras)."""
    
    data_type = DataType.CAMERA
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        camera = bpy.data.cameras.new(name=name)
        
        if "lens" in params:
            camera.lens = params["lens"]
        if "type" in params:
            camera.type = params["type"]
        
        return {"name": camera.name, "type": "camera"}
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        camera = bpy.data.cameras.get(name)
        if camera is None:
            raise KeyError(f"Camera '{name}' not found")
        
        if path:
            value = self._get_nested_attr(camera, path)
            return {"name": name, "path": path, "value": value}
        
        return {
            "name": camera.name,
            "type": camera.type,
            "lens": camera.lens,
            "lens_unit": camera.lens_unit,
            "clip_start": camera.clip_start,
            "clip_end": camera.clip_end,
            "dof_focus_distance": camera.dof.focus_distance if camera.dof else None,
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        camera = bpy.data.cameras.get(name)
        if camera is None:
            raise KeyError(f"Camera '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(camera, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        camera = bpy.data.cameras.get(name)
        if camera is None:
            raise KeyError(f"Camera '{name}' not found")
        bpy.data.cameras.remove(camera)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore
        items = [{"name": c.name, "type": c.type, "lens": c.lens} for c in bpy.data.cameras]
        return {"items": items, "count": len(items)}


@HandlerRegistry.register
class LightHandler(BaseHandler):
    """Handler for Blender light data type (bpy.data.lights)."""
    
    data_type = DataType.LIGHT
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        light_type = params.get("light_type", "POINT")
        light = bpy.data.lights.new(name=name, type=light_type)
        
        if "energy" in params:
            light.energy = params["energy"]
        if "color" in params:
            light.color = tuple(params["color"][:3])
        
        return {"name": light.name, "type": "light", "light_type": light.type}
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        light = bpy.data.lights.get(name)
        if light is None:
            raise KeyError(f"Light '{name}' not found")
        
        if path:
            value = self._get_nested_attr(light, path)
            return {"name": name, "path": path, "value": value}
        
        return {
            "name": light.name,
            "type": light.type,
            "energy": light.energy,
            "color": list(light.color),
            "specular_factor": light.specular_factor,
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        light = bpy.data.lights.get(name)
        if light is None:
            raise KeyError(f"Light '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            if prop_path == "color":
                light.color = tuple(value[:3])
            else:
                self._set_nested_attr(light, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        light = bpy.data.lights.get(name)
        if light is None:
            raise KeyError(f"Light '{name}' not found")
        bpy.data.lights.remove(light)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore
        filter_params = filter_params or {}
        light_type = filter_params.get("light_type")
        
        items = []
        for light in bpy.data.lights:
            if light_type and light.type != light_type.upper():
                continue
            items.append({"name": light.name, "type": light.type, "energy": light.energy})
        return {"items": items, "count": len(items)}


@HandlerRegistry.register
class ArmatureHandler(BaseHandler):
    """Handler for Blender armature data type (bpy.data.armatures)."""
    
    data_type = DataType.ARMATURE
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        armature = bpy.data.armatures.new(name=name)
        return {"name": armature.name, "type": "armature"}
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        armature = bpy.data.armatures.get(name)
        if armature is None:
            raise KeyError(f"Armature '{name}' not found")
        
        if path:
            value = self._get_nested_attr(armature, path)
            return {"name": name, "path": path, "value": value}
        
        bones_info = [{"name": b.name, "head": list(b.head), "tail": list(b.tail)} for b in armature.bones]
        return {
            "name": armature.name,
            "bones": bones_info,
            "bones_count": len(armature.bones),
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        armature = bpy.data.armatures.get(name)
        if armature is None:
            raise KeyError(f"Armature '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(armature, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        armature = bpy.data.armatures.get(name)
        if armature is None:
            raise KeyError(f"Armature '{name}' not found")
        bpy.data.armatures.remove(armature)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore
        items = [{"name": a.name, "bones_count": len(a.bones)} for a in bpy.data.armatures]
        return {"items": items, "count": len(items)}


@HandlerRegistry.register
class CurveHandler(BaseHandler):
    """Handler for Blender curve data type (bpy.data.curves)."""
    
    data_type = DataType.CURVE
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        curve_type = params.get("curve_type", "CURVE")
        curve = bpy.data.curves.new(name=name, type=curve_type)
        
        if "dimensions" in params:
            curve.dimensions = params["dimensions"]
        
        return {"name": curve.name, "type": "curve"}
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        curve = bpy.data.curves.get(name)
        if curve is None:
            raise KeyError(f"Curve '{name}' not found")
        
        if path:
            value = self._get_nested_attr(curve, path)
            return {"name": name, "path": path, "value": value}
        
        return {
            "name": curve.name,
            "dimensions": curve.dimensions,
            "splines_count": len(curve.splines),
            "resolution_u": curve.resolution_u,
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        curve = bpy.data.curves.get(name)
        if curve is None:
            raise KeyError(f"Curve '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(curve, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        curve = bpy.data.curves.get(name)
        if curve is None:
            raise KeyError(f"Curve '{name}' not found")
        bpy.data.curves.remove(curve)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore
        items = [{"name": c.name, "splines_count": len(c.splines)} for c in bpy.data.curves]
        return {"items": items, "count": len(items)}


@HandlerRegistry.register
class WorldHandler(BaseHandler):
    """Handler for Blender world data type (bpy.data.worlds)."""
    
    data_type = DataType.WORLD
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        world = bpy.data.worlds.new(name=name)
        
        if params.get("use_nodes", True):
            world.use_nodes = True
        
        return {"name": world.name, "type": "world"}
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        world = bpy.data.worlds.get(name)
        if world is None:
            raise KeyError(f"World '{name}' not found")
        
        if path:
            value = self._get_nested_attr(world, path)
            return {"name": name, "path": path, "value": value}
        
        result = {
            "name": world.name,
            "use_nodes": world.use_nodes,
        }
        
        if world.use_nodes and world.node_tree:
            bg_node = world.node_tree.nodes.get("Background")
            if bg_node:
                result["background_color"] = list(bg_node.inputs["Color"].default_value)
                result["background_strength"] = bg_node.inputs["Strength"].default_value
        
        return result
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        world = bpy.data.worlds.get(name)
        if world is None:
            raise KeyError(f"World '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            if prop_path == "background_color" and world.use_nodes and world.node_tree:
                bg_node = world.node_tree.nodes.get("Background")
                if bg_node:
                    bg_node.inputs["Color"].default_value = tuple(value)
                    modified.append("background_color")
            elif prop_path == "background_strength" and world.use_nodes and world.node_tree:
                bg_node = world.node_tree.nodes.get("Background")
                if bg_node:
                    bg_node.inputs["Strength"].default_value = value
                    modified.append("background_strength")
            else:
                self._set_nested_attr(world, prop_path, value)
                modified.append(prop_path)
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        world = bpy.data.worlds.get(name)
        if world is None:
            raise KeyError(f"World '{name}' not found")
        bpy.data.worlds.remove(world)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore
        items = [{"name": w.name, "use_nodes": w.use_nodes} for w in bpy.data.worlds]
        return {"items": items, "count": len(items)}
