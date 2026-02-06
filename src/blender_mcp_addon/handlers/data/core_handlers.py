# -*- coding: utf-8 -*-
"""Core handlers for camera, light, armature, curve, and world types."""
from __future__ import annotations

from typing import Any, Iterable

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
        
        # Parameters
        if "lens" in params:
            camera.lens = params["lens"]
        if "type" in params:
            camera.type = params["type"]
        if "clip_start" in params:
            camera.clip_start = params["clip_start"]
        if "clip_end" in params:
            camera.clip_end = params["clip_end"]
        if "sensor_width" in params:
            camera.sensor_width = params["sensor_width"]
        if "sensor_height" in params:
            camera.sensor_height = params["sensor_height"]
        if "dof_focus_distance" in params:
            camera.dof.focus_distance = params["dof_focus_distance"]
        if "shift_x" in params:
            camera.shift_x = params["shift_x"]
        if "shift_y" in params:
            camera.shift_y = params["shift_y"]
        
        # Optional convenience: create and link an object using this camera data
        if params.get("link_object", True):
            obj_name = params.get("object_name", name)
            cam_obj = bpy.data.objects.new(obj_name, camera)
            collection_name = params.get("collection")
            if collection_name and collection_name in bpy.data.collections:
                bpy.data.collections[collection_name].objects.link(cam_obj)
            else:
                bpy.context.scene.collection.objects.link(cam_obj)
            if "location" in params:
                cam_obj.location = tuple(params["location"])
            if "rotation" in params:
                cam_obj.rotation_euler = tuple(params["rotation"])
        
        return {
            "name": camera.name,
            "type": "camera",
            "lens": camera.lens,
            "clip_start": camera.clip_start,
            "clip_end": camera.clip_end,
        }
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        camera = bpy.data.cameras.get(name)
        if camera is None:
            raise KeyError(f"Camera '{name}' not found")
        
        if path:
            value = self._get_nested_attr(camera, path)
            return {"name": name, "path": path, "value": value}
        
        objects = [
            obj.name for obj in bpy.data.objects
            if obj.type == "CAMERA" and obj.data == camera
        ]
        collections = []
        if objects:
            for coll in bpy.data.collections:
                if any(obj_name in coll.objects for obj_name in objects):
                    collections.append(coll.name)
        
        return {
            "name": camera.name,
            "type": camera.type,
            "lens": camera.lens,
            "lens_unit": camera.lens_unit,
            "clip_start": camera.clip_start,
            "clip_end": camera.clip_end,
            "sensor_width": camera.sensor_width,
            "sensor_height": camera.sensor_height,
            "dof_focus_distance": camera.dof.focus_distance if camera.dof else None,
            "shift_x": camera.shift_x,
            "shift_y": camera.shift_y,
            "objects": objects,
            "collections": collections,
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
        
        # Parameters
        if "energy" in params:
            light.energy = params["energy"]
        if "color" in params:
            light.color = tuple(params["color"][:3])
        
        if params.get("link_object", True):
            obj_name = params.get("object_name", name)
            light_obj = bpy.data.objects.new(obj_name, light)
            collection_name = params.get("collection")
            if collection_name and collection_name in bpy.data.collections:
                bpy.data.collections[collection_name].objects.link(light_obj)
            else:
                bpy.context.scene.collection.objects.link(light_obj)
            if "location" in params:
                light_obj.location = tuple(params["location"])
            if "rotation" in params:
                light_obj.rotation_euler = tuple(params["rotation"])
        
        return {
            "name": light.name,
            "type": "light",
            "light_type": light.type,
            "energy": light.energy,
            "color": list(light.color),
        }
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        light = bpy.data.lights.get(name)
        if light is None:
            raise KeyError(f"Light '{name}' not found")
        
        if path:
            value = self._get_nested_attr(light, path)
            return {"name": name, "path": path, "value": value}
        
        objects = [
            obj.name for obj in bpy.data.objects
            if obj.type == "LIGHT" and obj.data == light
        ]
        collections = []
        if objects:
            for coll in bpy.data.collections:
                if any(obj_name in coll.objects for obj_name in objects):
                    collections.append(coll.name)
        
        return {
            "name": light.name,
            "type": light.type,
            "energy": light.energy,
            "color": list(light.color),
            "specular_factor": light.specular_factor,
            "objects": objects,
            "collections": collections,
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
        from mathutils import Vector  # type: ignore
        
        curve_type = params.get("curve_type") or "CURVE"
        spline_type_default = params.get("spline_type") or params.get("type") or "BEZIER"
        curve = bpy.data.curves.new(name=name, type=curve_type)
        
        if "dimensions" in params:
            curve.dimensions = params["dimensions"]
        if "resolution_u" in params:
            curve.resolution_u = params["resolution_u"]
        
        splines_data = params.get("splines", [])
        for spline_data in splines_data:
            spline_type = spline_data.get("type", spline_type_default)
            spline = curve.splines.new(type=spline_type)
            spline.use_cyclic_u = spline_data.get("use_cyclic_u", False)
            spline.resolution_u = spline_data.get("resolution_u", curve.resolution_u)
            
            if spline_type == "BEZIER":
                points = spline_data.get("bezier_points", [])
                spline.bezier_points.add(max(len(points) - 1, 0))
                for idx, point_data in enumerate(points):
                    if idx >= len(spline.bezier_points):
                        break
                    point = spline.bezier_points[idx]
                    if "co" in point_data:
                        point.co = Vector(point_data["co"])
                    if "handle_left" in point_data:
                        point.handle_left = Vector(point_data["handle_left"])
                    if "handle_right" in point_data:
                        point.handle_right = Vector(point_data["handle_right"])
                    point.handle_left_type = point_data.get("handle_left_type", point.handle_left_type)
                    point.handle_right_type = point_data.get("handle_right_type", point.handle_right_type)
            else:
                points = spline_data.get("points", [])
                spline.points.add(max(len(points) - 1, 0))
                for idx, point_data in enumerate(points):
                    if idx >= len(spline.points):
                        break
                    point = spline.points[idx]
                    if isinstance(point_data, Iterable):
                        co = list(point_data)
                        if len(co) == 3:
                            co.append(1.0)
                        point.co = co
                    elif isinstance(point_data, dict) and "co" in point_data:
                        co = list(point_data["co"])
                        if len(co) == 3:
                            co.append(point_data.get("w", 1.0))
                        point.co = co
        
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
class FontHandler(BaseHandler):
    """Handler for text/font curve data blocks (bpy.data.curves type FONT)."""
    
    data_type = DataType.FONT
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        
        font_curve = bpy.data.curves.new(name=name, type="FONT")
        if "body" in params:
            font_curve.body = params["body"]
        if "extrude" in params:
            font_curve.extrude = params["extrude"]
        if "bevel_depth" in params:
            font_curve.bevel_depth = params["bevel_depth"]
        if "size" in params:
            font_curve.size = params["size"]
        
        return {"name": font_curve.name, "type": "font"}
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        font_curve = bpy.data.curves.get(name)
        if font_curve is None or font_curve.type != "FONT":
            raise KeyError(f"Font '{name}' not found")
        
        if path:
            value = self._get_nested_attr(font_curve, path)
            return {"name": name, "path": path, "value": value}
        
        return {
            "name": font_curve.name,
            "body": font_curve.body,
            "extrude": font_curve.extrude,
            "bevel_depth": font_curve.bevel_depth,
            "size": font_curve.size,
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        font_curve = bpy.data.curves.get(name)
        if font_curve is None or font_curve.type != "FONT":
            raise KeyError(f"Font '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(font_curve, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        font_curve = bpy.data.curves.get(name)
        if font_curve is None or font_curve.type != "FONT":
            raise KeyError(f"Font '{name}' not found")
        bpy.data.curves.remove(font_curve)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore
        items = [
            {"name": c.name, "body": c.body}
            for c in bpy.data.curves
            if c.type == "FONT"
        ]
        return {"items": items, "count": len(items)}


@HandlerRegistry.register
class TextHandler(BaseHandler):
    """Handler for legacy text data type mapping to Blender FONT curves."""
    
    data_type = DataType.TEXT
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        
        font_curve = bpy.data.curves.new(name=name, type="FONT")
        if "body" in params:
            font_curve.body = params["body"]
        if "extrude" in params:
            font_curve.extrude = params["extrude"]
        if "bevel_depth" in params:
            font_curve.bevel_depth = params["bevel_depth"]
        if "size" in params:
            font_curve.size = params["size"]
        
        return {"name": font_curve.name, "type": "text"}
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        font_curve = bpy.data.curves.get(name)
        if font_curve is None or font_curve.type != "FONT":
            raise KeyError(f"Text '{name}' not found")
        
        if path:
            value = self._get_nested_attr(font_curve, path)
            return {"name": name, "path": path, "value": value}
        
        return {
            "name": font_curve.name,
            "body": font_curve.body,
            "extrude": font_curve.extrude,
            "bevel_depth": font_curve.bevel_depth,
            "size": font_curve.size,
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        font_curve = bpy.data.curves.get(name)
        if font_curve is None or font_curve.type != "FONT":
            raise KeyError(f"Text '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(font_curve, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        font_curve = bpy.data.curves.get(name)
        if font_curve is None or font_curve.type != "FONT":
            raise KeyError(f"Text '{name}' not found")
        bpy.data.curves.remove(font_curve)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore
        items = [
            {"name": c.name, "body": c.body}
            for c in bpy.data.curves
            if c.type == "FONT"
        ]
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


@HandlerRegistry.register
class MetaBallHandler(BaseHandler):
    """Handler for Blender metaball data type (bpy.data.metaballs)."""
    
    data_type = DataType.METABALL
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        meta = bpy.data.metaballs.new(name=name)
        elements = params.get("elements", [])
        for element in elements:
            el = meta.elements.new(type=element.get("type", "BALL"))
            if "co" in element:
                el.co = element["co"]
            if "radius" in element:
                el.radius = element["radius"]
            if "size_x" in element:
                el.size_x = element["size_x"]
            if "size_y" in element:
                el.size_y = element["size_y"]
            if "size_z" in element:
                el.size_z = element["size_z"]
        return {"name": meta.name, "type": "metaball", "elements": len(meta.elements)}
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        meta = bpy.data.metaballs.get(name)
        if meta is None:
            raise KeyError(f"Metaball '{name}' not found")
        
        if path:
            value = self._get_nested_attr(meta, path)
            return {"name": name, "path": path, "value": value}
        
        return {
            "name": meta.name,
            "elements": len(meta.elements),
            "resolution": meta.resolution,
            "render_resolution": meta.render_resolution,
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        meta = bpy.data.metaballs.get(name)
        if meta is None:
            raise KeyError(f"Metaball '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(meta, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        meta = bpy.data.metaballs.get(name)
        if meta is None:
            raise KeyError(f"Metaball '{name}' not found")
        bpy.data.metaballs.remove(meta)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore
        items = [{"name": m.name, "elements": len(m.elements)} for m in bpy.data.metaballs]
        return {"items": items, "count": len(items)}


@HandlerRegistry.register
class GreasePencilHandler(BaseHandler):
    """Handler for grease pencil data type (bpy.data.grease_pencils)."""
    
    data_type = DataType.GREASE_PENCIL
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        gp = bpy.data.grease_pencils.new(name=name)
        
        if "layers" in params:
            self._create_layers(gp, params["layers"])
        
        layers_count = len(gp.layers)
        frames_total = sum(len(layer.frames) for layer in gp.layers)
        strokes_total = sum(len(frame.strokes) for layer in gp.layers for frame in layer.frames)
        
        return {
            "name": gp.name,
            "type": "grease_pencil",
            "layers_count": layers_count,
            "frames_total": frames_total,
            "strokes_total": strokes_total,
        }
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        gp = bpy.data.grease_pencils.get(name)
        if gp is None:
            raise KeyError(f"Grease Pencil '{name}' not found")
        
        if path:
            value = self._get_nested_attr(gp, path)
            return {"name": name, "path": path, "value": value}
        
        layers = [{"name": l.name, "frames": len(l.frames)} for l in gp.layers]
        return {
            "name": gp.name,
            "layers": layers,
            "layers_count": len(gp.layers),
            "frames_total": sum(len(layer.frames) for layer in gp.layers),
            "strokes_total": sum(len(frame.strokes) for layer in gp.layers for frame in layer.frames),
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        gp = bpy.data.grease_pencils.get(name)
        if gp is None:
            raise KeyError(f"Grease Pencil '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(gp, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore
        gp = bpy.data.grease_pencils.get(name)
        if gp is None:
            raise KeyError(f"Grease Pencil '{name}' not found")
        bpy.data.grease_pencils.remove(gp)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore
        items = [{"name": g.name, "layers": len(g.layers)} for g in bpy.data.grease_pencils]
        return {"items": items, "count": len(items)}

    def _create_layers(self, gpencil, layers_data):
        import bpy  # type: ignore

        for layer_data in layers_data:
            layer = gpencil.layers.new(layer_data.get("name", "Layer"))

            for frame_data in layer_data.get("frames", []):
                frame_number = frame_data.get("frame_number", 1)
                frame = layer.frames.new(frame_number)

                for stroke_data in frame_data.get("strokes", []):
                    stroke = frame.strokes.new()
                    stroke.line_width = stroke_data.get("line_width", 1.0)

                    for point_data in stroke_data.get("points", []):
                        point = stroke.points.new()
                        point.co = point_data["co"]
                        point.strength = point_data.get("strength", 1.0)
                        point.pressure = point_data.get("pressure", 0.5)
