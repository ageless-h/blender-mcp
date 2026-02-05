# Unified Data CRUD

## Purpose
TBD.

## Requirements

### Requirement: data.create tool
The system SHALL provide a `data.create` tool that creates new Blender data blocks of any supported type.

#### Scenario: Create object with mesh
- **WHEN** `data.create` is called with `type="object"`, `name="Cube"`, `params={"mesh_name": "CubeMesh"}`
- **THEN** system creates a new object named "Cube" with associated mesh data
- **AND** returns `{"name": "Cube", "type": "object", "success": true}`

#### Scenario: Create material with nodes
- **WHEN** `data.create` is called with `type="material"`, `name="RedMaterial"`, `params={"use_nodes": true}`
- **THEN** system creates a new material with node tree enabled
- **AND** returns the created material name

#### Scenario: Create geometry node tree
- **WHEN** `data.create` is called with `type="node_tree"`, `name="MyGeoNodes"`, `params={"type": "GeometryNodeTree"}`
- **THEN** system creates a new geometry node group
- **AND** returns the created node tree name

### Requirement: data.read tool
The system SHALL provide a `data.read` tool that reads properties from any Blender data block.

#### Scenario: Read object properties
- **WHEN** `data.read` is called with `type="object"`, `name="Cube"`
- **THEN** system returns object properties including name, location, rotation, scale, and type

#### Scenario: Read specific property path
- **WHEN** `data.read` is called with `type="object"`, `name="Cube"`, `path="location"`
- **THEN** system returns only the location property value

#### Scenario: Read image as base64
- **WHEN** `data.read` is called with `type="image"`, `name="Render Result"`, `params={"format": "base64"}`
- **THEN** system returns image data encoded as base64 string
- **AND** includes width, height, and format metadata

#### Scenario: Read evaluated mesh data
- **WHEN** `data.read` is called with `type="mesh"`, `name="Cube"`, `params={"evaluated": true}`
- **THEN** system returns mesh data with all modifiers applied

#### Scenario: Read context state
- **WHEN** `data.read` is called with `type="context"`
- **THEN** system returns current mode, active_object, selected_objects, scene, and workspace

### Requirement: data.write tool
The system SHALL provide a `data.write` tool that modifies properties of any Blender data block.

#### Scenario: Write object location
- **WHEN** `data.write` is called with `type="object"`, `name="Cube"`, `properties={"location": [1, 2, 3]}`
- **THEN** system updates the object's location to [1, 2, 3]
- **AND** returns `{"success": true, "modified": ["location"]}`

#### Scenario: Write nested property
- **WHEN** `data.write` is called with `type="material"`, `name="Material"`, `properties={"node_tree.nodes.Principled BSDF.inputs.Base Color.default_value": [1, 0, 0, 1]}`
- **THEN** system updates the nested property value

#### Scenario: Write context mode
- **WHEN** `data.write` is called with `type="context"`, `properties={"mode": "EDIT"}`
- **THEN** system switches to Edit mode for the active object

#### Scenario: Write context selection
- **WHEN** `data.write` is called with `type="context"`, `properties={"active_object": "Sphere", "selected_objects": ["Sphere", "Cube"]}`
- **THEN** system updates active object and selection state

### Requirement: data.delete tool
The system SHALL provide a `data.delete` tool that removes Blender data blocks.

#### Scenario: Delete object
- **WHEN** `data.delete` is called with `type="object"`, `name="Cube"`
- **THEN** system removes the object from the scene and data
- **AND** returns `{"success": true, "deleted": "Cube"}`

#### Scenario: Delete non-existent data
- **WHEN** `data.delete` is called with a name that does not exist
- **THEN** system returns an error indicating the data block was not found

### Requirement: data.list tool
The system SHALL provide a `data.list` tool that lists all data blocks of a specified type.

#### Scenario: List all objects
- **WHEN** `data.list` is called with `type="object"`
- **THEN** system returns a list of all objects with their names and basic info

#### Scenario: List with filter
- **WHEN** `data.list` is called with `type="object"`, `filter={"object_type": "MESH"}`
- **THEN** system returns only mesh-type objects

#### Scenario: List node trees by type
- **WHEN** `data.list` is called with `type="node_tree"`, `filter={"tree_type": "GeometryNodeTree"}`
- **THEN** system returns only geometry node groups

### Requirement: data.link tool
The system SHALL provide a `data.link` tool that manages relationships between data blocks.

#### Scenario: Link object to collection
- **WHEN** `data.link` is called with `source={"type": "object", "name": "Cube"}`, `target={"type": "collection", "name": "MyCollection"}`
- **THEN** system adds the object to the collection
- **AND** returns `{"success": true, "action": "link"}`

#### Scenario: Unlink object from collection
- **WHEN** `data.link` is called with `source={"type": "object", "name": "Cube"}`, `target={"type": "collection", "name": "MyCollection"}`, `unlink=true`
- **THEN** system removes the object from the collection
- **AND** returns `{"success": true, "action": "unlink"}`

#### Scenario: Link material to object
- **WHEN** `data.link` is called with `source={"type": "material", "name": "RedMaterial"}`, `target={"type": "object", "name": "Cube"}`
- **THEN** system assigns the material to the object
