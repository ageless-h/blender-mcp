# Blender MCP Advanced Test Suite

> Prerequisites: Default scene with Camera, Cube, Light. Blender 5.1+ with MCP addon enabled.

---

## Test 1: Complete PBR Material Pipeline

Create a multi-layered PBR material with procedural textures, normal mapping, and assign to multiple objects.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `create_object` Sphere "MatSphere" at [0,0,0] | Object created |
| 2 | `create_object` Cylinder "MatCylinder" at [3,0,0] | Object created |
| 3 | `manage_material` create "Advanced_PBR" base_color [0.2,0.2,0.2,1] metallic 0.9 roughness 0.15 | Material created |
| 4 | `edit_nodes` add ShaderNodeTexNoise "NoiseScale5" at [-800,200] | Node added |
| 5 | `edit_nodes` set_value NoiseScale5 Scale=10, Detail=12 | Values set |
| 6 | `edit_nodes` add ShaderNodeTexVoronoi "VoronoiCracks" at [-800,-100] | Node added |
| 7 | `edit_nodes` add ShaderNodeBump "CrackBump" at [-400,100] Strength=1.0 | Node added |
| 8 | `edit_nodes` add ShaderNodeMix "ColorMix" at [-400,-200] Factor=0.6 | Node added |
| 9 | `edit_nodes` connect NoiseScale5.Color → ColorMix.A, VoronoiCracks.Color → ColorMix.B | 2 links |
| 10 | `edit_nodes` connect ColorMix.Result → ShaderNodeBsdfPrincipled.Base Color, CrackBump.Normal → ShaderNodeBsdfPrincipled.Normal | 2 links |
| 11 | `edit_nodes` connect NoiseScale5.Fac → CrackBump.Height | Link created |
| 12 | `manage_material` assign "Advanced_PBR" to "MatSphere" | Assigned |
| 13 | `manage_material` assign "Advanced_PBR" to "MatCylinder" | Assigned |
| 14 | `get_node_tree` verify 7 nodes, 6+ links | Correct topology |

---

## Test 2: Multi-Object Modifier Stack

Build a complex modifier pipeline on multiple objects with different modifier types.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `create_object` cube "StackCube" at [0,0,0] size=1 | Created |
| 2 | `manage_modifier` add SUBSURF "SubD" on StackCube | Modifier added |
| 3 | `manage_modifier` configure SubD levels=3 | Configured |
| 4 | `manage_modifier` add BEVEL "Bevel1" on StackCube | Modifier added |
| 5 | `manage_modifier` configure Bevel1 width=0.05 segments=3 | Configured |
| 6 | `manage_modifier` add SOLIDIFY "Shell" on StackCube | Modifier added |
| 7 | `manage_modifier` configure Shell thickness=0.02 | Configured |
| 8 | `manage_modifier` add MIRROR "MirrorX" on StackCube | Modifier added |
| 9 | `create_object` sphere "StackSphere" at [4,0,0] | Created |
| 10 | `manage_modifier` add SUBSURF "Smooth" on StackSphere levels=4 | Added & configured |
| 11 | `manage_modifier` add SHRINKWRAP "Wrap" on StackSphere | Added |
| 12 | `get_object_data` verify StackCube has 4 modifiers, StackSphere has 2 | Correct counts |

---

## Test 3: Character Armature with Constraints

Create a basic character armature with bone parenting and IK constraints.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `create_object` ARMATURE "CharRig" at [0,0,0] | Created |
| 2 | `execute_operator` armature.bone_primitive_add name="Hips" | Bone added |
| 3 | `execute_operator` armature.bone_primitive_add name="Spine" | Bone added |
| 4 | `execute_operator` armature.bone_primitive_add name="Head" | Bone added |
| 5 | `execute_operator` armature.bone_primitive_add name="Arm_L" | Bone added |
| 6 | `execute_operator` armature.bone_primitive_add name="Arm_R" | Bone added |
| 7 | `execute_operator` armature.bone_primitive_add name="Leg_L" | Bone added |
| 8 | `execute_operator` armature.bone_primitive_add name="Leg_R" | Bone added |
| 9 | `get_armature_data` verify 7 bones | Correct |
| 10 | `manage_constraints` add TRACK_TO on Arm_L target CharRig | Constraint added |
| 11 | `manage_constraints` add TRACK_TO on Arm_R target CharRig | Constraint added |
| 12 | `get_object_data` verify Arm_L and Arm_R have constraints | Correct |

---

## Test 4: Full Animation Sequence

Create a bouncing ball animation with location, scale, and rotation keyframes across the timeline.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `create_object` sphere "BounceBall" at [0,0,5] radius=0.5 | Created |
| 2 | `edit_animation` insert_keyframe BounceBall location at frame=1 | Keyframe inserted |
| 3 | `modify_object` BounceBall location=[0,0,0] | Modified |
| 4 | `edit_animation` insert_keyframe BounceBall location at frame=15 | Keyframe inserted |
| 5 | `modify_object` BounceBall location=[0,0,3] | Modified |
| 6 | `edit_animation` insert_keyframe BounceBall location at frame=30 | Keyframe inserted |
| 7 | `modify_object` BounceBall location=[0,0,0] scale=[1.2,1.2,0.8] (squash) | Modified |
| 8 | `edit_animation` insert_keyframe BounceBall location+scale at frame=32 | 2 keyframes |
| 9 | `modify_object` BounceBall scale=[1,1,1] rotation=[0,0,0] | Reset |
| 10 | `edit_animation` insert_keyframe BounceBall rotation at frame=60 value=π | Keyframe inserted |
| 11 | `modify_object` BounceBall location=[2,0,5] | Modified |
| 12 | `edit_animation` insert_keyframe BounceBall location at frame=90 | Keyframe inserted |
| 13 | `get_object_data` verify BounceBall has animation data | Animated |

---

## Test 5: Geometry Nodes Procedural Generation

Build a procedural scattering system with geometry nodes.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `create_object` plane "ScatterGround" at [0,0,0] size=10 | Created |
| 2 | `create_object` icosphere "ScatterInstance" at [0,0,5] | Created |
| 3 | `execute_operator` object.modifier_add type=NODES on ScatterGround | GeoNodes added |
| 4 | `edit_nodes` GEOMETRY/MODIFIER: add GeometryNodeDistributePointsOnFaces "DistPts" | Added |
| 5 | `edit_nodes` add GeometryNodeInstanceOnPoints "InstancePts" | Added |
| 6 | `edit_nodes` add GeometryNodeObjectInfo "ObjInfo" | Added |
| 7 | `edit_nodes` add GeometryNodeRealizeInstances "Realize" | Added |
| 8 | `edit_nodes` set_value DistPts Density=50 | Set |
| 9 | `edit_nodes` connect NodeGroupInput.Geometry → DistPts.Mesh | Connected |
| 10 | `edit_nodes` connect DistPts.Points → InstancePts.Points | Connected |
| 11 | `edit_nodes` connect ObjInfo.Object → InstancePts.Instance | Connected |
| 12 | `edit_nodes` connect InstancePts.Instances → Realize.Geometry | Connected |
| 13 | `edit_nodes` connect Realize.Geometry → NodeGroupOutput.Geometry | Connected |
| 14 | `get_object_data` verify modifier exists and node_tree has 6+ nodes | Correct |

---

## Test 6: Rigid Body Physics Simulation

Set up a complete domino-like chain with active and passive rigid bodies.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `create_object` plane "Floor" at [0,0,-0.5] size=20 | Created |
| 2 | `manage_physics` add RIGID_BODY_PASSIVE on Floor | Physics added |
| 3 | `manage_physics` configure Floor restitution=0.5 | Configured |
| 4 | `create_object` cube "Domino_01" at [0,0,0] size=0.3 | Created |
| 5 | `modify_object` Domino_01 scale=[0.3,1,2] | Scaled |
| 6 | `manage_physics` add RIGID_BODY on Domino_01 mass=0.5 | Active RB |
| 7 | `create_object` cube "Domino_02" at [0,1.2,0] size=0.3 | Created |
| 8 | `modify_object` Domino_02 scale=[0.3,1,2] | Scaled |
| 9 | `manage_physics` add RIGID_BODY on Domino_02 mass=0.5 | Active RB |
| 10 | `create_object` cube "Domino_03" at [0,2.4,0] size=0.3 | Created |
| 11 | `modify_object` Domino_03 scale=[0.3,1,2] | Scaled |
| 12 | `manage_physics` add RIGID_BODY on Domino_03 mass=0.5 | Active RB |
| 13 | `create_object` sphere "Boulder" at [0,-2,2] radius=0.5 | Created |
| 14 | `manage_physics` add RIGID_BODY on Boulder mass=5 | Heavy RB |
| 15 | `get_object_data` verify 5 objects have physics | Correct |

---

## Test 7: Multi-Material Assignment & UV Workflow

Create objects, unwrap UVs, create multiple materials, and assign to different faces.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `create_object` cube "MultiMatCube" at [0,0,0] size=2 | Created |
| 2 | `manage_uv` smart_project on MultiMatCube angle_limit=60 | UV unwrapped |
| 3 | `manage_uv` pack_islands on MultiMatCube margin=0.02 | Islands packed |
| 4 | `manage_material` create "RedMat" base_color=[1,0,0,1] | Created |
| 5 | `manage_material` create "BlueMat" base_color=[0,0,1,1] | Created |
| 6 | `manage_material` create "GreenMat" base_color=[0,1,0,1] | Created |
| 7 | `manage_material` assign "RedMat" to MultiMatCube slot=0 | Assigned |
| 8 | `manage_material` assign "BlueMat" to MultiMatCube (creates slot 1) | Assigned |
| 9 | `manage_material` assign "GreenMat" to MultiMatCube (creates slot 2) | Assigned |
| 10 | `get_object_data` verify 3 material slots | Correct |
| 11 | `manage_uv` add_uv_map "UVMap_Second" on MultiMatCube | Second UV added |
| 12 | `get_object_data` verify 2 UV maps | Correct |

---

## Test 8: Render Pipeline Configuration

Configure a complete render pipeline with Cycles, denoising, film settings, and world environment.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `setup_scene` engine=CYCLES samples=256 resolution=3840x2160 | Configured |
| 2 | `setup_scene` fps=24 frame_range=[1,120] film_transparent=true | Configured |
| 3 | `setup_scene` denoising=true background_color=[0.05,0.05,0.1,1] | Configured |
| 4 | `create_object` camera "RenderCam" at [8,-8,5] | Created |
| 5 | `modify_object` RenderCam rotation=[1.1,0,0.785] | Rotated to face origin |
| 6 | `create_object` LIGHT "KeyLight" type=SUN energy=3 color=[1,0.95,0.9] at [5,5,10] | Created |
| 7 | `create_object` LIGHT "FillLight" type=AREA energy=200 color=[0.6,0.7,1] at [-3,-2,3] | Created |
| 8 | `manage_material` create "Chrome" base_color=[0.8,0.8,0.8,1] metallic=1 roughness=0.05 | Created |
| 9 | `manage_material` assign Chrome to Cube | Assigned |
| 10 | `get_scene` verify CYCLES engine, 3840x2160 resolution, 256 samples | Correct |
| 11 | `get_objects` verify RenderCam, KeyLight, FillLight exist | Correct |

---

## Test 9: Collection Organization & Scene Management

Organize a complex scene with collections, visibility, and parenting.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `manage_collection` create "Environment" | Created |
| 2 | `manage_collection` create "Characters" | Created |
| 3 | `manage_collection` create "Lights" color_tag=COLOR_03 | Created with color |
| 4 | `manage_collection` create "Physics_Objects" | Created |
| 5 | `manage_collection` link_object Camera → Environment | Linked |
| 6 | `manage_collection` link_object RedPointLight → Lights | Linked |
| 7 | `manage_collection` link_object BlueSpotLight → Lights | Linked |
| 8 | `manage_collection` link_object GreenAreaLight → Lights | Linked |
| 9 | `manage_collection` link_object PhysicsBall → Physics_Objects | Linked |
| 10 | `manage_collection` link_object GroundPlane → Physics_Objects | Linked |
| 11 | `manage_collection` set_visibility "Lights" hide_render=false | Visible in render |
| 12 | `get_collections` verify 4+ collections with correct object counts | Correct |

---

## Test 10: Complex Shader Network with Multiple Outputs

Build a shader network with multiple material outputs, displacement, and vertex color mixing.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | `manage_material` create "ComplexShader" metallic=0.5 roughness=0.4 | Created |
| 2 | `edit_nodes` add ShaderNodeTexNoise "DispNoise" at [-800,0] Scale=15 | Added |
| 3 | `edit_nodes` add ShaderNodeTexVoronoi "VoronoiColor" at [-800,300] | Added |
| 4 | `edit_nodes` add ShaderNodeMix "BlendColors" at [-400,300] Factor=0.4 | Added |
| 5 | `edit_nodes` add ShaderNodeBump "DisplacementBump" at [-400,0] Strength=0.3 | Added |
| 6 | `edit_nodes` add ShaderNodeBsdfGlossy "GlossyCoat" at [0,300] | Added |
| 7 | `edit_nodes` add ShaderNodeBsdfDiffuse "DiffuseBase" at [0,100] | Added |
| 8 | `edit_nodes` add ShaderNodeMixShader "MixShaders" at [200,200] Factor=0.7 | Added |
| 9 | `edit_nodes` connect VoronoiColor.Color → BlendColors.A | Connected |
| 10 | `edit_nodes` connect BlendColors.Result → DiffuseBase.Color, GlossyCoat.Color | 2 links |
| 11 | `edit_nodes` connect DiffuseBase.BSDF → MixShaders[1], GlossyCoat.BSDF → MixShaders[2] | 2 links |
| 12 | `edit_nodes` connect MixShaders.Shader → ShaderNodeOutputMaterial.Surface | Connected |
| 13 | `edit_nodes` connect DispNoise.Fac → DisplacementBump.Height | Connected |
| 14 | `get_node_tree` verify 9+ nodes, 7+ links | Correct |

---

## Known Limitations (expected failures)

These operations are known to fail due to Blender 5.1 timer context API restrictions:

- **VSE strip creation**: `edit_sequencer` add_strip → `operation_failed`
- **Compositor node editing**: `edit_nodes` COMPOSITOR context → `operation_failed` / `addon_exception`
- **Torus primitive**: `create_object` primitive=torus → `operation_failed`
- **Bone positioning/parenting**: Requires `execute_script` which is disabled in current config
