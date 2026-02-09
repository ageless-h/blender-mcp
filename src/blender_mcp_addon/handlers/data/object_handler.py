# -*- coding: utf-8 -*-
"""Object handler for unified CRUD operations."""
from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry
from ..shared import create_mesh_primitive as _create_mesh_primitive_shared


@HandlerRegistry.register
class ObjectHandler(BaseHandler):
    """Handler for Blender object data type (bpy.data.objects)."""
    
    data_type = DataType.OBJECT
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new object.
        
        Args:
            name: Name for the new object
            params: Creation parameters:
                - mesh_name: Name for associated mesh (creates empty mesh if not found)
                - object_type: Type of object data (MESH, EMPTY, CAMERA, LIGHT, etc.)
                - data_name: Name of existing data block to use
                
        Returns:
            Dict with created object info
        """
        import bpy  # type: ignore
        
        object_type = params.get("object_type", "MESH").upper()
        # Map TEXT → FONT for Blender compatibility
        if object_type == "TEXT":
            object_type = "FONT"
        data_name = params.get("data_name")
        mesh_name = params.get("mesh_name")
        
        obj_data = None
        
        if object_type == "MESH":
            if data_name and data_name in bpy.data.meshes:
                obj_data = bpy.data.meshes[data_name]
            elif mesh_name:
                if mesh_name in bpy.data.meshes:
                    obj_data = bpy.data.meshes[mesh_name]
                else:
                    obj_data = bpy.data.meshes.new(name=mesh_name)
            else:
                obj_data = bpy.data.meshes.new(name=f"{name}_mesh")
            
            # Create primitive geometry via bmesh if requested
            primitive = params.get("primitive")
            if primitive and obj_data:
                self._create_mesh_primitive(obj_data, primitive, params)
        elif object_type == "CAMERA":
            if data_name and data_name in bpy.data.cameras:
                obj_data = bpy.data.cameras[data_name]
            else:
                obj_data = bpy.data.cameras.new(name=data_name or f"{name}_camera")
            if "lens" in params:
                obj_data.lens = params["lens"]
            if "clip_start" in params:
                obj_data.clip_start = params["clip_start"]
            if "clip_end" in params:
                obj_data.clip_end = params["clip_end"]
        elif object_type == "LIGHT":
            light_type = params.get("light_type", "POINT")
            if data_name and data_name in bpy.data.lights:
                obj_data = bpy.data.lights[data_name]
            else:
                obj_data = bpy.data.lights.new(name=data_name or f"{name}_light", type=light_type)
            if "energy" in params:
                obj_data.energy = params["energy"]
            if "color" in params:
                obj_data.color = tuple(params["color"][:3])
        elif object_type == "EMPTY":
            obj_data = None
        elif object_type == "ARMATURE":
            if data_name and data_name in bpy.data.armatures:
                obj_data = bpy.data.armatures[data_name]
            else:
                obj_data = bpy.data.armatures.new(name=data_name or f"{name}_armature")
        elif object_type == "CURVE":
            curve_type = params.get("curve_type", "CURVE")
            if data_name and data_name in bpy.data.curves:
                obj_data = bpy.data.curves[data_name]
            else:
                obj_data = bpy.data.curves.new(name=data_name or f"{name}_curve", type=curve_type)
        elif object_type == "FONT":
            if data_name and data_name in bpy.data.curves:
                obj_data = bpy.data.curves[data_name]
            else:
                obj_data = bpy.data.curves.new(name=data_name or f"{name}_text", type="FONT")
            body = params.get("body")
            if body is not None:
                obj_data.body = body
            if "extrude" in params:
                obj_data.extrude = params["extrude"]
            if "bevel_depth" in params:
                obj_data.bevel_depth = params["bevel_depth"]
            if "size" in params:
                obj_data.size = params["size"]
        elif object_type == "META":
            if data_name and data_name in bpy.data.metaballs:
                obj_data = bpy.data.metaballs[data_name]
            else:
                obj_data = bpy.data.metaballs.new(name=data_name or f"{name}_meta")
        elif object_type in {"GPENCIL", "GREASE_PENCIL"}:
            if data_name and data_name in bpy.data.grease_pencils:
                obj_data = bpy.data.grease_pencils[data_name]
            else:
                obj_data = bpy.data.grease_pencils.new(name=data_name or f"{name}_gpencil")
        else:
            # default fallback to mesh
            if data_name and data_name in bpy.data.meshes:
                obj_data = bpy.data.meshes[data_name]
            else:
                obj_data = bpy.data.meshes.new(name=f"{name}_mesh")
        
        obj = bpy.data.objects.new(name=name, object_data=obj_data)
        
        collection_name = params.get("collection")
        if collection_name and collection_name in bpy.data.collections:
            bpy.data.collections[collection_name].objects.link(obj)
        else:
            bpy.context.scene.collection.objects.link(obj)
        
        location = params.get("location")
        if location:
            obj.location = tuple(location)
        
        rotation = params.get("rotation")
        if rotation:
            obj.rotation_euler = tuple(rotation)
        
        scale = params.get("scale")
        if scale:
            obj.scale = tuple(scale)
        
        return {
            "name": obj.name,
            "type": "object",
            "object_type": obj.type,
            "data_name": obj_data.name if obj_data else None,
        }
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read object properties.
        
        Args:
            name: Name of the object
            path: Optional property path to read specific property
            params: Read parameters:
                - include: list of sections to return. Valid values:
                  summary, mesh_stats, modifiers, materials, constraints,
                  physics, animation, custom_properties, vertex_groups,
                  shape_keys, uv_maps, particle_systems
                  
        Returns:
            Dict with object properties
        """
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise KeyError(f"Object '{name}' not found")
        
        if path:
            value = self._get_nested_attr(obj, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "path": path, "value": value}
        
        include = params.get("include", ["summary"])
        result: dict[str, Any] = {"name": obj.name, "type": obj.type}
        
        if "summary" in include:
            data_info = None
            if obj.data:
                data_info = {"name": obj.data.name, "type": type(obj.data).__name__}
            result["summary"] = {
                "location": list(obj.location),
                "rotation_euler": list(obj.rotation_euler),
                "scale": list(obj.scale),
                "visible": obj.visible_get(),
                "selected": obj.select_get(),
                "data": data_info,
                "parent": obj.parent.name if obj.parent else None,
                "children": [c.name for c in obj.children],
            }
        
        if "mesh_stats" in include and obj.type == "MESH" and obj.data:
            mesh = obj.data
            result["mesh_stats"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
                "loops": len(mesh.loops),
                "has_custom_normals": mesh.has_custom_normals,
                "materials_count": len(mesh.materials),
            }
        
        if "modifiers" in include:
            mods = []
            for m in obj.modifiers:
                mod_info: dict[str, Any] = {"name": m.name, "type": m.type, "show_viewport": m.show_viewport, "show_render": m.show_render}
                mods.append(mod_info)
            result["modifiers"] = mods
        
        if "materials" in include:
            result["materials"] = [
                {"slot_index": i, "name": slot.material.name if slot.material else None, "link": slot.link}
                for i, slot in enumerate(obj.material_slots)
            ]
        
        if "constraints" in include:
            result["constraints"] = [
                {"name": c.name, "type": c.type, "enabled": not c.mute}
                for c in obj.constraints
            ]
        
        if "physics" in include:
            physics = {}
            for mod in obj.modifiers:
                if mod.type in {"PARTICLE_SYSTEM", "CLOTH", "SOFT_BODY", "FLUID", "COLLISION", "DYNAMIC_PAINT"}:
                    physics[mod.name] = {"type": mod.type}
            if hasattr(obj, "rigid_body") and obj.rigid_body:
                physics["rigid_body"] = {"type": obj.rigid_body.type, "mass": obj.rigid_body.mass, "enabled": obj.rigid_body.enabled}
            result["physics"] = physics
        
        if "animation" in include:
            anim: dict[str, Any] = {"has_action": False}
            if obj.animation_data:
                ad = obj.animation_data
                anim["has_action"] = ad.action is not None
                if ad.action:
                    anim["action_name"] = ad.action.name
                    anim["fcurves_count"] = len(ad.action.fcurves)
                anim["nla_tracks_count"] = len(ad.nla_tracks)
                anim["drivers_count"] = len(ad.drivers)
            result["animation"] = anim
        
        if "custom_properties" in include:
            result["custom_properties"] = {k: v for k, v in obj.items() if k != "_RNA_UI" and not k.startswith("_")}
        
        if "vertex_groups" in include:
            result["vertex_groups"] = [{"index": vg.index, "name": vg.name, "lock_weight": vg.lock_weight} for vg in obj.vertex_groups]
        
        if "shape_keys" in include and obj.data and hasattr(obj.data, "shape_keys") and obj.data.shape_keys:
            sk = obj.data.shape_keys
            result["shape_keys"] = {
                "reference_key": sk.reference_key.name if sk.reference_key else None,
                "keys": [{"name": k.name, "value": k.value, "mute": k.mute} for k in sk.key_blocks],
            }
        
        if "uv_maps" in include and obj.type == "MESH" and obj.data:
            result["uv_maps"] = [{"name": uv.name, "active": uv.active} for uv in obj.data.uv_layers]
        
        if "particle_systems" in include:
            result["particle_systems"] = [
                {"name": ps.name, "type": ps.settings.type if ps.settings else None, "count": ps.settings.count if ps.settings else 0}
                for ps in obj.particle_systems
            ]
        
        return result
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to an object.
        
        Args:
            name: Name of the object
            properties: Dict of property paths to values
            params: Write parameters
            
        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise KeyError(f"Object '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            if prop_path == "location":
                obj.location = tuple(value)
            elif prop_path == "rotation_euler":
                obj.rotation_euler = tuple(value)
            elif prop_path == "scale":
                obj.scale = tuple(value)
            elif prop_path == "visible":
                obj.hide_viewport = not value
                obj.hide_render = not value
            elif prop_path == "selected":
                obj.select_set(value)
            elif prop_path == "active":
                if value:
                    bpy.context.view_layer.objects.active = obj
            elif prop_path == "parent":
                if value:
                    parent_obj = bpy.data.objects.get(value)
                    if parent_obj:
                        obj.parent = parent_obj
                else:
                    obj.parent = None
            else:
                self._set_nested_attr(obj, prop_path, value)
            modified.append(prop_path)
        
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete an object.
        
        Args:
            name: Name of the object to delete
            params: Deletion parameters:
                - delete_data: Also delete associated data block (default: False)
                
        Returns:
            Dict with deleted object name
        """
        import bpy  # type: ignore
        
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise KeyError(f"Object '{name}' not found")
        
        delete_data = params.get("delete_data", False)
        obj_data = obj.data
        
        bpy.data.objects.remove(obj, do_unlink=True)
        
        if delete_data and obj_data:
            collection = getattr(bpy.data, type(obj_data).bl_rna.identifier.lower() + "s", None)
            if collection and obj_data.name in collection:
                collection.remove(obj_data)
        
        return {"deleted": name, "data_deleted": delete_data and obj_data is not None}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all objects.
        
        Args:
            filter_params: Optional filter criteria:
                - object_type: Filter by object type (MESH, CAMERA, etc.)
                - selected: Filter by selection state
                - visible: Filter by visibility
                - name_pattern: Glob pattern to filter by name
                - collection: Filter by collection name
                
        Returns:
            Dict with items list
        """
        import bpy  # type: ignore
        import fnmatch
        
        filter_params = filter_params or {}
        object_type = filter_params.get("object_type")
        selected_only = filter_params.get("selected")
        visible_only = filter_params.get("visible")
        name_pattern = filter_params.get("name_pattern")
        collection_name = filter_params.get("collection")
        
        collection_objects = None
        if collection_name:
            col = bpy.data.collections.get(collection_name)
            if col:
                collection_objects = {obj.name for obj in col.objects}
            else:
                return {"items": [], "count": 0}
        
        items = []
        for obj in bpy.data.objects:
            if object_type and obj.type != object_type.upper():
                continue
            if selected_only is not None and obj.select_get() != selected_only:
                continue
            if visible_only is not None and obj.visible_get() != visible_only:
                continue
            if name_pattern and not fnmatch.fnmatch(obj.name, name_pattern):
                continue
            if collection_objects is not None and obj.name not in collection_objects:
                continue
            
            items.append({
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "selected": obj.select_get(),
                "visible": obj.visible_get(),
            })
        
        return {"items": items, "count": len(items)}
    
    def link(
        self,
        source_name: str,
        target_type: DataType,
        target_name: str,
        unlink: bool = False,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Link or unlink object to/from a collection.
        
        Args:
            source_name: Name of the object
            target_type: Must be COLLECTION
            target_name: Name of the collection
            unlink: If True, unlink instead of link
            params: Additional parameters
            
        Returns:
            Dict with action result
        """
        import bpy  # type: ignore
        
        if target_type != DataType.COLLECTION:
            return {"error": f"Objects can only be linked to collections, not {target_type.value}"}
        
        obj = bpy.data.objects.get(source_name)
        if obj is None:
            raise KeyError(f"Object '{source_name}' not found")
        
        collection = bpy.data.collections.get(target_name)
        if collection is None:
            raise KeyError(f"Collection '{target_name}' not found")
        
        if unlink:
            if obj.name in collection.objects:
                collection.objects.unlink(obj)
                return {"action": "unlink", "object": source_name, "collection": target_name}
            return {"action": "unlink", "skipped": True, "reason": "Object not in collection"}
        else:
            if obj.name not in collection.objects:
                collection.objects.link(obj)
                return {"action": "link", "object": source_name, "collection": target_name}
            return {"action": "link", "skipped": True, "reason": "Object already in collection"}

    @staticmethod
    def _create_mesh_primitive(mesh, primitive: str, params: dict[str, Any]) -> None:
        """Create primitive geometry on a mesh data block using bmesh."""
        _create_mesh_primitive_shared(mesh, primitive, params)
