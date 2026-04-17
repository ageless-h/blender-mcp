# -*- coding: utf-8 -*-
"""Core handlers for camera, light, armature, curve, and world types."""

from __future__ import annotations

from typing import Any, Iterable

from ..base import BaseHandler, GenericCollectionHandler
from ..registry import HandlerRegistry
from ..shared import find_referencing_objects, link_data_to_scene
from ..types import DataType


@HandlerRegistry.register
class CameraHandler(GenericCollectionHandler):
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
            link_data_to_scene(camera, params)

        return {
            "name": camera.name,
            "type": "camera",
            "lens": camera.lens,
            "clip_start": camera.clip_start,
            "clip_end": camera.clip_end,
        }

    def _read_summary(self, item: Any) -> dict[str, Any]:
        refs = find_referencing_objects(item, "CAMERA")

        return {
            "name": item.name,
            "type": item.type,
            "lens": item.lens,
            "lens_unit": item.lens_unit,
            "clip_start": item.clip_start,
            "clip_end": item.clip_end,
            "sensor_width": item.sensor_width,
            "sensor_height": item.sensor_height,
            "dof_focus_distance": item.dof.focus_distance if item.dof else None,
            "shift_x": item.shift_x,
            "shift_y": item.shift_y,
            "objects": refs["objects"],
            "collections": refs["collections"],
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "type": item.type, "lens": item.lens}


@HandlerRegistry.register
class LightHandler(GenericCollectionHandler):
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
            link_data_to_scene(light, params)

        return {
            "name": light.name,
            "type": "light",
            "light_type": light.type,
            "energy": light.energy,
            "color": list(light.color),
        }

    def _read_summary(self, item: Any) -> dict[str, Any]:
        refs = find_referencing_objects(item, "LIGHT")

        return {
            "name": item.name,
            "type": item.type,
            "energy": item.energy,
            "color": list(item.color),
            "specular_factor": item.specular_factor,
            "objects": refs["objects"],
            "collections": refs["collections"],
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "type": item.type, "energy": item.energy}

    def _filter_item(self, item: Any, filter_params: dict[str, Any]) -> bool:
        light_type = filter_params.get("light_type")
        if light_type and item.type != light_type.upper():
            return False
        return True

    def _custom_write(self, item: Any, prop_path: str, value: Any) -> bool:
        if prop_path == "color":
            item.color = tuple(value[:3])
            return True
        return False


@HandlerRegistry.register
class ArmatureHandler(GenericCollectionHandler):
    """Handler for Blender armature data type (bpy.data.armatures)."""

    data_type = DataType.ARMATURE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore

        armature = bpy.data.armatures.new(name=name)
        return {"name": armature.name, "type": "armature"}

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import fnmatch

        import bpy  # type: ignore

        armature = bpy.data.armatures.get(name)
        if armature is None:
            obj = bpy.data.objects.get(name)
            if obj is not None and obj.type == "ARMATURE":
                armature = obj.data
            else:
                raise KeyError(f"Armature '{name}' not found")

        if path:
            value = self._get_nested_attr(armature, path)
            return {"name": name, "path": path, "value": value}

        include = params.get("include", ["hierarchy"])
        bone_filter = params.get("bone_filter")

        def _match(n: str) -> bool:
            return not bone_filter or fnmatch.fnmatch(n, bone_filter)

        result: dict[str, Any] = {"name": armature.name, "bones_count": len(armature.bones)}

        if "hierarchy" in include:
            result["hierarchy"] = [
                {
                    "name": b.name,
                    "head": list(b.head),
                    "tail": list(b.tail),
                    "length": b.length,
                    "parent": b.parent.name if b.parent else None,
                    "children": [c.name for c in b.children],
                    "connected": b.use_connect,
                }
                for b in armature.bones
                if _match(b.name)
            ]

        arm_obj = None
        if any(s in include for s in ("poses", "constraints", "bone_groups", "ik_chains")):
            for obj in bpy.data.objects:
                if obj.type == "ARMATURE" and obj.data == armature:
                    arm_obj = obj
                    break

        if "poses" in include and arm_obj and arm_obj.pose:
            result["poses"] = [
                {
                    "name": pb.name,
                    "location": list(pb.location),
                    "rotation_quaternion": list(pb.rotation_quaternion),
                    "scale": list(pb.scale),
                    "rotation_mode": pb.rotation_mode,
                }
                for pb in arm_obj.pose.bones
                if _match(pb.name)
            ]

        if "constraints" in include and arm_obj and arm_obj.pose:
            cons = []
            for pb in arm_obj.pose.bones:
                if not _match(pb.name):
                    continue
                for c in pb.constraints:
                    cons.append(
                        {
                            "bone": pb.name,
                            "name": c.name,
                            "type": c.type,
                            "enabled": not c.mute,
                            "influence": c.influence,
                        }
                    )
            result["constraints"] = cons

        if "bone_groups" in include and arm_obj and arm_obj.pose:
            if hasattr(arm_obj.pose, "bone_groups"):
                result["bone_groups"] = [
                    {"name": bg.name, "color_set": bg.color_set} for bg in arm_obj.pose.bone_groups
                ]
            else:
                result["bone_groups"] = []

        if "ik_chains" in include and arm_obj and arm_obj.pose:
            chains = []
            for pb in arm_obj.pose.bones:
                if not _match(pb.name):
                    continue
                for c in pb.constraints:
                    if c.type == "IK":
                        chains.append(
                            {
                                "bone": pb.name,
                                "target": c.target.name if c.target else None,
                                "subtarget": c.subtarget,
                                "chain_count": c.chain_count,
                            }
                        )
            result["ik_chains"] = chains

        return result

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "bones_count": len(item.bones)}

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "bones_count": len(item.bones)}


@HandlerRegistry.register
class CurveHandler(GenericCollectionHandler):
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

        result = {"name": curve.name, "type": "curve", "splines_count": len(curve.splines)}

        if params.get("link_object", False):
            obj = link_data_to_scene(curve, params)
            result["object_name"] = obj.name

        return result

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {
            "name": item.name,
            "dimensions": item.dimensions,
            "splines_count": len(item.splines),
            "resolution_u": item.resolution_u,
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "splines_count": len(item.splines)}


class _FontCurveHandler(BaseHandler):
    """Shared implementation for FONT curve handlers (FontHandler & TextHandler).

    Both DataType.FONT and DataType.TEXT operate on bpy.data.curves
    filtered by type == "FONT".  Only the data_type and type label differ.
    """

    def _type_label(self) -> str:
        return self.data_type.value.capitalize()

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

        result = {"name": font_curve.name, "type": self.data_type.value}

        if params.get("link_object", False):
            obj = link_data_to_scene(font_curve, params)
            result["object_name"] = obj.name

        return result

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore

        font_curve = bpy.data.curves.get(name)
        if font_curve is None or font_curve.type != "FONT":
            raise KeyError(f"{self._type_label()} '{name}' not found")

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
            raise KeyError(f"{self._type_label()} '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(font_curve, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore

        font_curve = bpy.data.curves.get(name)
        if font_curve is None or font_curve.type != "FONT":
            raise KeyError(f"{self._type_label()} '{name}' not found")
        bpy.data.curves.remove(font_curve)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        import bpy  # type: ignore

        items = [{"name": c.name, "body": c.body} for c in bpy.data.curves if c.type == "FONT"]
        return {"items": items, "count": len(items)}


@HandlerRegistry.register
class FontHandler(_FontCurveHandler):
    """Handler for font curve data blocks (bpy.data.curves type FONT)."""

    data_type = DataType.FONT


@HandlerRegistry.register
class TextHandler(_FontCurveHandler):
    """Handler for text data type mapping to Blender FONT curves."""

    data_type = DataType.TEXT


@HandlerRegistry.register
class WorldHandler(GenericCollectionHandler):
    """Handler for Blender world data type (bpy.data.worlds)."""

    data_type = DataType.WORLD

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore

        world = bpy.data.worlds.new(name=name)

        if params.get("use_nodes", True):
            world.use_nodes = True

        return {"name": world.name, "type": "world"}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": item.name,
            "use_nodes": item.use_nodes,
        }

        if item.use_nodes and item.node_tree:
            bg_node = item.node_tree.nodes.get("Background")
            if bg_node:
                result["background_color"] = list(bg_node.inputs["Color"].default_value)
                result["background_strength"] = bg_node.inputs["Strength"].default_value

        return result

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "use_nodes": item.use_nodes}

    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import bpy  # type: ignore

        world = bpy.data.worlds.get(name)
        if world is None:
            raise KeyError(f"World '{name}' not found")

        modified = []
        # Look up Background node once instead of twice
        bg_node = None
        if world.use_nodes and world.node_tree:
            bg_node = world.node_tree.nodes.get("Background")

        for prop_path, value in properties.items():
            if prop_path == "background_color" and bg_node:
                bg_node.inputs["Color"].default_value = tuple(value)
                modified.append("background_color")
            elif prop_path == "background_strength" and bg_node:
                bg_node.inputs["Strength"].default_value = value
                modified.append("background_strength")
            else:
                self._set_nested_attr(world, prop_path, value)
                modified.append(prop_path)
        return {"name": name, "modified": modified}


@HandlerRegistry.register
class MetaBallHandler(GenericCollectionHandler):
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
        result = {"name": meta.name, "type": "metaball", "elements": len(meta.elements)}

        if params.get("link_object", False):
            obj = link_data_to_scene(meta, params)
            result["object_name"] = obj.name

        return result

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {
            "name": item.name,
            "elements": len(item.elements),
            "resolution": item.resolution,
            "render_resolution": item.render_resolution,
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "elements": len(item.elements)}


@HandlerRegistry.register
class GreasePencilHandler(GenericCollectionHandler):
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

        result = {
            "name": gp.name,
            "type": "grease_pencil",
            "layers_count": layers_count,
            "frames_total": frames_total,
            "strokes_total": strokes_total,
        }

        if params.get("link_object", False):
            obj = link_data_to_scene(gp, params)
            result["object_name"] = obj.name

        return result

    def _read_summary(self, item: Any) -> dict[str, Any]:
        layers = [{"name": l.name, "frames": len(l.frames)} for l in item.layers]
        return {
            "name": item.name,
            "layers": layers,
            "layers_count": len(item.layers),
            "frames_total": sum(len(layer.frames) for layer in item.layers),
            "strokes_total": sum(len(frame.strokes) for layer in item.layers for frame in layer.frames),
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "layers": len(item.layers)}

    def _create_layers(self, gpencil, layers_data):
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
