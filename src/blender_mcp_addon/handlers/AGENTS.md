# handlers — Blender Tool Handler System

Runs inside Blender. 37 handlers across 29 files, each implementing CRUD for a specific `DataType`. All registered via `@HandlerRegistry.register` decorator.

## STRUCTURE

```
registry.py            # HandlerRegistry — decorator + lazy instantiation + parse_type()
types.py               # DataType enum (40+) + DATA_TYPE_TO_COLLECTION + PSEUDO_TYPES + ATTACHED_TYPES
base.py                # BaseHandler ABC + GenericCollectionHandler (shared CRUD, 333 lines)
response.py            # _ok(), _error(), not_found_error(), invalid_params_error(), etc.
error_codes.py         # Error code constants + DEFAULT_SUGGESTIONS
shared.py              # Shared handler utilities
context_utils.py       # bpy context helpers
response_schema.py     # Response schema validation
utils/property_parser.py  # Value coercion (string → bpy type)
data/                  # 30 handlers: object, mesh, material, image, modifier, etc.
nodes/                 # reader.py + editor.py (shader/compositor/geonode trees)
animation/             # reader.py + editor.py + __init__.py (iter_fcurves helper)
sequencer/editor.py    # VSE operations
constraints/handler.py # Constraint CRUD + move_up/move_down
physics/handler.py     # Rigid body, cloth, fluid, particle, force field
uv/handler.py          # UV mapping: unwrap, smart_project, seam marking
scene/config.py        # Scene setup: render, timeline, world
importexport/handler.py # FBX/OBJ/glTF/USD import/export
info/query.py          # Scene info + statistics (559 lines)
operator/executor.py   # Generic bpy.ops execution
script/executor.py     # Arbitrary Python in Blender
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Add handler for new bpy type | `data/<type>_handler.py` | Inherit `GenericCollectionHandler` |
| Register new data type | `types.py` | Add to `DataType` enum + `DATA_TYPE_TO_COLLECTION` |
| Fix response format | `response.py` | `_ok(result=..., started=t)` or `_error(...)` |
| Version-specific compat | `animation/__init__.py` | `iter_fcurves()` helper (not `action.fcurves`) |
| Property coercion | `utils/property_parser.py` | String → bpy value conversion |
| Dispatch a handler | `registry.py` | `HandlerRegistry.get(DataType.XXX)` |

## ANTI-PATTERNS (THIS PROJECT)

- **Never** compute `bpy.data` collection name from `bl_rna.identifier.lower()+"s"` → use `DATA_TYPE_TO_COLLECTION`
- **Never** access `action.fcurves` directly → `iter_fcurves(action)` from `animation/__init__.py`
- **Never** skip `obj.data is not None` check (Empty objects crash)
- **Never** mutate original images → copy first, clean up in `finally`
- **Never** use dict arg for context overrides → `temp_override()` (Blender 4.2+)
- **Never** set `hide_render` on visibility toggle → only `hide_viewport`
- **Never** access `bpy.data.curves` without `_curves_available()` guard (Blender 5.0+ only)
- Fractional FPS → use `fps_base=1000`
- All writes → `_push_undo_step()` for Ctrl+Z

## ADDING A NEW HANDLER

1. Add `DataType.YOUR_TYPE = "your_type"` to `types.py` enum
2. Add `DataType.YOUR_TYPE: "collection_name"` to `DATA_TYPE_TO_COLLECTION`
3. Create `data/your_type_handler.py` with `@HandlerRegistry.register` decorator
4. Inherit `GenericCollectionHandler` (most cases) or `BaseHandler`
5. Set `data_type = DataType.YOUR_TYPE` class attribute
6. Implement `create()`, `read()`, `write()`, `delete()`, `list_items()`
7. All returns: `_ok(result=..., started=t)` or `_error(code=..., message=..., started=t)`
8. Add test in `tests/addon/test_your_type_handler.py`
