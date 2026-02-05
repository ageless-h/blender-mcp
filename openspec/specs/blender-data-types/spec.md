# Blender Data Types

## Purpose
TBD.

## Requirements

### Requirement: DataType enumeration
The system SHALL define a DataType enumeration that maps to all supported Blender data block types.

#### Scenario: Core object types supported
- **WHEN** system initializes
- **THEN** DataType includes: object, mesh, curve, surface, metaball, armature, lattice

#### Scenario: Appearance types supported
- **WHEN** system initializes
- **THEN** DataType includes: material, texture, image, world, linestyle

#### Scenario: Light and camera types supported
- **WHEN** system initializes
- **THEN** DataType includes: camera, light, probe

#### Scenario: Node system types supported
- **WHEN** system initializes
- **THEN** DataType includes: node_tree (supporting ShaderNodeTree, GeometryNodeTree, CompositorNodeTree)

#### Scenario: Organization types supported
- **WHEN** system initializes
- **THEN** DataType includes: collection, scene, workspace

#### Scenario: Animation types supported
- **WHEN** system initializes
- **THEN** DataType includes: action

#### Scenario: 2D animation types supported
- **WHEN** system initializes
- **THEN** DataType includes: grease_pencil

#### Scenario: Audio/video types supported
- **WHEN** system initializes
- **THEN** DataType includes: sound, speaker, movieclip, mask

#### Scenario: Physics types supported
- **WHEN** system initializes
- **THEN** DataType includes: particle

#### Scenario: Special geometry types supported
- **WHEN** system initializes
- **THEN** DataType includes: volume, pointcloud, hair_curves

#### Scenario: Tool types supported
- **WHEN** system initializes
- **THEN** DataType includes: brush, palette, paintcurve, text, font

#### Scenario: External data types supported
- **WHEN** system initializes
- **THEN** DataType includes: library, cache_file

### Requirement: Pseudo-types for context access
The system SHALL support pseudo-types that map to non-data-block entities.

#### Scenario: Context pseudo-type
- **WHEN** `type="context"` is used with data.read or data.write
- **THEN** system accesses bpy.context state instead of bpy.data

#### Scenario: Preferences pseudo-type
- **WHEN** `type="preferences"` is used with data.read or data.write
- **THEN** system accesses bpy.context.preferences

### Requirement: Attached types with parent reference
The system SHALL support attached types that require a parent object reference.

#### Scenario: Modifier type with parent
- **WHEN** `type="modifier"` is used with `params={"object": "Cube"}`
- **THEN** system accesses Cube's modifiers collection

#### Scenario: Constraint type with parent
- **WHEN** `type="constraint"` is used with `params={"object": "Armature"}`
- **THEN** system accesses the object's constraints collection

#### Scenario: Driver type with parent
- **WHEN** `type="driver"` is used with appropriate parent reference
- **THEN** system accesses the animation_data.drivers collection

#### Scenario: NLA track type with parent
- **WHEN** `type="nla_track"` is used with `params={"object": "Character"}`
- **THEN** system accesses the object's animation_data.nla_tracks

### Requirement: Type to bpy.data mapping
The system SHALL map each DataType to the corresponding bpy.data collection.

#### Scenario: Object type mapping
- **WHEN** `type="object"` is used
- **THEN** system accesses `bpy.data.objects`

#### Scenario: Mesh type mapping
- **WHEN** `type="mesh"` is used
- **THEN** system accesses `bpy.data.meshes`

#### Scenario: Material type mapping
- **WHEN** `type="material"` is used
- **THEN** system accesses `bpy.data.materials`

#### Scenario: Node tree type mapping
- **WHEN** `type="node_tree"` is used
- **THEN** system accesses `bpy.data.node_groups`

### Requirement: Handler registry pattern
The system SHALL use a Handler registry pattern where each DataType has a corresponding Handler class.

#### Scenario: Handler registration
- **WHEN** a Handler class is decorated with @HandlerRegistry.register
- **THEN** system automatically registers the handler for its data_type

#### Scenario: Handler dispatch
- **WHEN** a data.* tool is called with a specific type
- **THEN** system dispatches to the registered handler for that type

#### Scenario: Unknown type error
- **WHEN** a data.* tool is called with an unsupported type
- **THEN** system returns error indicating no handler registered for the type
