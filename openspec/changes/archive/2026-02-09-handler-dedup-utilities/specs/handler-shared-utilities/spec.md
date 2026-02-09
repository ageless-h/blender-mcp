## ADDED Requirements

### Requirement: create_mesh_primitive utility function
The handler system SHALL provide a `create_mesh_primitive(mesh, primitive, params)` function that creates bmesh primitive geometry on a given mesh data block. The function SHALL support cube, sphere, cylinder, cone, plane, icosphere, and torus primitives. All handler code that creates bmesh primitives SHALL use this single function.

#### Scenario: Create cube primitive
- **WHEN** `create_mesh_primitive(mesh, "cube", {"size": 2.0})` is called
- **THEN** the mesh contains cube geometry with the specified size
- **AND** the mesh is validated and updated with edge calculation

#### Scenario: Create sphere primitive with segments
- **WHEN** `create_mesh_primitive(mesh, "sphere", {"segments": 32, "ring_count": 16, "radius": 1.0})` is called
- **THEN** the mesh contains UV sphere geometry with the specified parameters

#### Scenario: Create cylinder primitive
- **WHEN** `create_mesh_primitive(mesh, "cylinder", {"segments": 32, "depth": 2.0, "radius": 1.0})` is called
- **THEN** the mesh contains cylinder geometry (capped cone with equal radii)

#### Scenario: Create cone primitive
- **WHEN** `create_mesh_primitive(mesh, "cone", {"segments": 32, "depth": 2.0, "radius": 1.0})` is called
- **THEN** the mesh contains cone geometry (capped cone with top radius 0)

#### Scenario: Create plane primitive
- **WHEN** `create_mesh_primitive(mesh, "plane", {"size": 2.0})` is called
- **THEN** the mesh contains a single-quad grid

#### Scenario: Create icosphere primitive
- **WHEN** `create_mesh_primitive(mesh, "icosphere", {"subdivisions": 2, "radius": 1.0})` is called
- **THEN** the mesh contains icosphere geometry with the specified subdivisions

#### Scenario: Create torus primitive
- **WHEN** `create_mesh_primitive(mesh, "torus", {"major_radius": 1.0, "minor_radius": 0.25, "major_segments": 48, "minor_segments": 12})` is called
- **THEN** the mesh contains torus geometry with the specified parameters

#### Scenario: Unknown primitive raises ValueError
- **WHEN** `create_mesh_primitive(mesh, "unknown_shape", {})` is called
- **THEN** the function raises `ValueError` with a message containing the primitive name

#### Scenario: Size parameter provides defaults for radius
- **WHEN** `create_mesh_primitive(mesh, "sphere", {"size": 2.0})` is called without explicit radius
- **THEN** the function uses `size / 2` as the default radius

#### Scenario: bmesh is freed after use
- **WHEN** `create_mesh_primitive(mesh, "cube", {})` completes (success or failure)
- **THEN** the internal bmesh object is freed and not leaked

### Requirement: link_data_to_scene utility function
The handler system SHALL provide a `link_data_to_scene(data_block, params)` function that creates a Blender object from a data block and links it to the scene. The function SHALL handle object naming, collection placement, location, and rotation from the params dict. All handler `create()` methods that link data blocks to scene objects SHALL use this single function.

#### Scenario: Link data block to default scene collection
- **WHEN** `link_data_to_scene(light_data, {"object_name": "MyLight"})` is called without a collection param
- **THEN** a new object named "MyLight" is created with the light data and linked to `bpy.context.scene.collection`

#### Scenario: Link data block to named collection
- **WHEN** `link_data_to_scene(camera_data, {"collection": "Cameras"})` is called and the collection "Cameras" exists
- **THEN** the new object is linked to `bpy.data.collections["Cameras"]` instead of the scene collection

#### Scenario: Fallback to scene collection when named collection not found
- **WHEN** `link_data_to_scene(data, {"collection": "NonExistent"})` is called and the collection does not exist
- **THEN** the new object is linked to `bpy.context.scene.collection`

#### Scenario: Apply location from params
- **WHEN** `link_data_to_scene(data, {"location": [1, 2, 3]})` is called
- **THEN** the created object's location is set to `(1, 2, 3)`

#### Scenario: Apply rotation from params
- **WHEN** `link_data_to_scene(data, {"rotation": [0.1, 0.2, 0.3]})` is called
- **THEN** the created object's `rotation_euler` is set to `(0.1, 0.2, 0.3)`

#### Scenario: Default object name from data block
- **WHEN** `link_data_to_scene(data_block, {})` is called without "object_name" in params
- **THEN** the created object uses `data_block.name` as its name

#### Scenario: Return the created object
- **WHEN** `link_data_to_scene(data, params)` is called
- **THEN** the function returns the created `bpy.types.Object` instance

### Requirement: find_referencing_objects utility function
The handler system SHALL provide a `find_referencing_objects(data_block, object_type)` function that scans `bpy.data.objects` to find all objects of the given type whose `.data` attribute references the provided data block. It SHALL also collect the collection names those objects belong to. All handler read methods that perform this scan SHALL use this single function.

#### Scenario: Find objects referencing a light data block
- **WHEN** `find_referencing_objects(point_light, "LIGHT")` is called and two objects use that light data
- **THEN** the function returns `{"objects": ["Light.001", "Light.002"], "collections": ["Collection"]}`

#### Scenario: Find objects referencing a camera data block
- **WHEN** `find_referencing_objects(camera_data, "CAMERA")` is called and one object uses that camera
- **THEN** the function returns `{"objects": ["Camera"], "collections": [...]}`

#### Scenario: No objects reference the data block
- **WHEN** `find_referencing_objects(orphan_light, "LIGHT")` is called and no objects use that data
- **THEN** the function returns `{"objects": [], "collections": []}`

#### Scenario: Collections are deduplicated
- **WHEN** `find_referencing_objects(data, "LIGHT")` is called and two referencing objects are in the same collection
- **THEN** the collection name appears only once in the returned collections list
