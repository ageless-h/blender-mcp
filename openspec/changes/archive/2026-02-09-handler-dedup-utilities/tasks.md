## 1. Shared Utility Functions

- [x] 1.1 Create `src/blender_mcp_addon/handlers/shared.py` with `create_mesh_primitive(mesh, primitive, params)` — extract from `MeshHandler.create()` bmesh dispatch logic, add try/finally for `bm.free()`
- [x] 1.2 Add `link_data_to_scene(data_block, params)` to `shared.py` — extract from `CameraHandler.create()` object-linking boilerplate (object naming, collection placement, location, rotation)
- [x] 1.3 Add `find_referencing_objects(data_block, object_type)` to `shared.py` — extract from `CameraHandler._read_summary()` the scan-objects-and-collections logic
- [x] 1.4 Write unit tests for all 3 utility functions in `tests/addon/test_shared_utilities.py`

## 2. GenericCollectionHandler Hooks

- [x] 2.1 Add `_filter_item(self, item, filter_params) -> bool` method to `GenericCollectionHandler` in `base.py` with default returning `True`
- [x] 2.2 Update `GenericCollectionHandler.list_items()` to call `_filter_item()` for each item, skipping items where it returns `False`
- [x] 2.3 Add `_custom_write(self, item, prop_path, value) -> bool` method to `GenericCollectionHandler` in `base.py` with default returning `False`
- [x] 2.4 Update `GenericCollectionHandler.write()` to call `_custom_write()` before `_set_nested_attr()`, skipping `_set_nested_attr` when `_custom_write()` returns `True`
- [x] 2.5 Write unit tests for both hooks in `tests/addon/test_generic_handler.py` — verify default behavior unchanged, verify hook override works
- [x] 2.6 Run full test suite to confirm no regressions from hook additions

## 3. Replace Duplicated Utility Code

- [x] 3.1 Replace `MeshHandler.create()` bmesh primitive block with call to `create_mesh_primitive()`
- [x] 3.2 Replace `ObjectHandler._create_mesh_primitive()` with call to `create_mesh_primitive()` (or remove the method and call shared function directly)
- [x] 3.3 Replace object-linking boilerplate in `CameraHandler.create()` with call to `link_data_to_scene()`
- [x] 3.4 Replace object-linking boilerplate in `LightHandler.create()` with call to `link_data_to_scene()`
- [x] 3.5 Replace object-linking boilerplate in `CurveHandler.create()` with call to `link_data_to_scene()`
- [x] 3.6 Replace object-linking boilerplate in `MetaBallHandler.create()` with call to `link_data_to_scene()`
- [x] 3.7 Replace object-linking boilerplate in `GreasePencilHandler.create()` with call to `link_data_to_scene()`
- [x] 3.8 Replace object-linking boilerplate in `_FontCurveHandler.create()` with call to `link_data_to_scene()`
- [x] 3.9 Replace object-linking boilerplate in `MeshHandler.create()` with call to `link_data_to_scene()`
- [x] 3.10 Replace referencing-objects scan in `CameraHandler._read_summary()` with call to `find_referencing_objects()`
- [x] 3.11 Replace referencing-objects scan in `LightHandler.read()` with call to `find_referencing_objects()`
- [x] 3.12 Run full test suite to confirm no regressions from utility replacements

## 4. Migrate Handlers to GenericCollectionHandler

- [x] 4.1 Migrate `LightHandler` from `BaseHandler` to `GenericCollectionHandler` — keep `create()`, add `_read_summary()`, `_list_fields()`, `_filter_item()`, `_custom_write()` for color handling
- [x] 4.2 Migrate `TextureHandler` from `BaseHandler` to `GenericCollectionHandler` — keep `create()`, add `_read_summary()`, `_list_fields()`, `_filter_item()` for type filtering
- [x] 4.3 Migrate `WorldHandler` from `BaseHandler` to `GenericCollectionHandler` — keep `create()`, add `_read_summary()`, `_list_fields()`, override `write()` for node-tree-backed properties (too complex for `_custom_write()` alone)
- [x] 4.4 Migrate `SceneHandler` from `BaseHandler` to `GenericCollectionHandler` — keep `create()`, add `_read_summary()`, `_list_fields()`, `_custom_write()` for camera/world reference properties, override `delete()` for the "cannot delete only scene" guard
- [x] 4.5 Run full test suite to confirm no regressions from handler migrations

## 5. Verification

- [x] 5.1 Run `uv run python -m unittest discover -s tests -p "test_*.py"` — all tests pass (390 passed, 6 skipped)
- [x] 5.2 Import chain verified — all shared utilities and migrated handlers import cleanly
- [x] 5.3 Verified all migrated handlers inherit from correct base classes (GenericCollectionHandler)
