# Real-Blender Integration Test Plan

> 分支: `test/integration-all`
> 更新日期: 2026-04-12
> 前置: 329 单元测试全部通过
> 验证特性: Error Suggestion (#155), Watchdog (#152), Screenshot Compress (#151), Property Parser (#153), Blender 5.0 Animation (#154)

---

## Test A — 建模 + 材质 + Shader Pipeline (26 步)

**验证特性**: Property Parser, Error Suggestion, Screenshot Compress

| # | 操作 | 预期结果 | 验证点 |
|---|------|----------|--------|
| 1 | `get_scene` | 返回默认场景 (Cube, Light, Camera) | 基础连通 |
| 2 | `create_object` name="Torus" type=MESH primitive=torus | Torus 出现在场景中 | create_object |
| 3 | `create_object` name="Sphere" type=MESH primitive=sphere | Sphere 出现 | create_object |
| 4 | `modify_object` name="Torus" location=[2, 0, 0] | Torus 移动到 x=2 | Property Parser: Vector3 |
| 5 | `modify_object` name="Torus" scale=[1.5, 1.5, 1.5] | Torus 放大 1.5x | Property Parser: Vector3 |
| 6 | `modify_object` name="Sphere" location=[-2, 0, 1] rotation=[0.785, 0, 0] | Sphere 移动并旋转 | Property Parser: 多参数 |
| 7 | `manage_material` action=create name="RedMetal" base_color=[1, 0, 0, 1] metallic=0.9 roughness=0.2 | 材质创建成功 | Property Parser: Color4 |
| 8 | `manage_material` action=assign name="RedMetal" object_name="Torus" | Torus 变红 | 材质分配 |
| 9 | `manage_material` action=create name="GlassBlue" base_color=[0.1, 0.3, 0.9, 0.5] alpha=0.3 | 半透明蓝材质 | Property Parser: alpha |
| 10 | `manage_material` action=assign name="GlassBlue" object_name="Sphere" | Sphere 变蓝半透明 | 材质分配 |
| 11 | `get_node_tree` tree_type=SHADER context=OBJECT target="RedMetal" | 返回 Principled BSDF + Material Output | 节点树读取 |
| 12 | `edit_nodes` tree_type=SHADER context=OBJECT target="RedMetal" operations=[{action: add_node, type: "ShaderNodeNoiseTexture", name: "Noise", location: [-300, 300]}] | Noise 节点添加 | 节点编辑 |
| 13 | `edit_nodes` operations=[{action: connect, from_node: "Noise", from_socket: "Fac", to_node: "Principled BSDF", to_socket: "Roughness"}] | Noise → Roughness 连线 | 节点连接 |
| 14 | `edit_nodes` operations=[{action: set_value, node: "Noise", input: "Scale", value: 5.0}] | Noise Scale=5 | Property Parser: float |
| 15 | `manage_modifier` action=add object_name="Torus" modifier_type=SUBSURF | Subsurf modifier 添加 | Modifier |
| 16 | `manage_modifier` action=configure object_name="Torus" modifier_name="Subdivision" settings={levels: 2} | levels=2 | Property Parser: int |
| 17 | `manage_modifier` action=add object_name="Torus" modifier_type=BEVEL | Bevel 添加 | Modifier |
| 18 | `manage_modifier` action=configure object_name="Torus" modifier_name="Bevel" settings={segments: 4, width: 0.05} | Bevel 参数设置 | Property Parser: multi |
| 19 | `get_object_data` name="Torus" include=[mesh_stats, modifiers, materials] | 返回正确的 mesh 数据和 modifier 列表 | 数据读取 |
| 20 | `capture_viewport` shading=MATERIAL format=JPEG | 返回 JPEG base64, 体积 < 100KB | **Screenshot Compress** |
| 21 | `capture_viewport` shading=RENDERED format=PNG | 返回 PNG base64, 完整尺寸 | PNG 回退 |
| 22 | `modify_object` name="NonExistent" location=[0,0,0] | 错误 + suggestion 提示正确对象名 | **Error Suggestion** |
| 23 | `edit_nodes` tree_type=SHADER context=OBJECT target="RedMetal" operations=[{action: set_value, node: "Noise", input: "Scale", value: "very_high"}] | 错误 + suggestion 提示类型要求 | **Error Suggestion + Property Parser** |
| 24 | `manage_material` action=create name="" | 错误 + suggestion 非空名称 | **Error Suggestion** |
| 25 | `create_object` name="Plane" type=MESH primitive=plane location=[0, 0, -2] scale=[10, 10, 1] | 地面平面 | 建模 |
| 26 | `get_scene` include=[stats] | 返回 5 个对象 (Cube, Torus, Sphere, Light, Camera + Plane) | 最终状态 |

---

## Test B — 动画 Pipeline + Blender 5.0 兼容 (24 步)

**验证特性**: Blender 5.0 Animation (#154), Property Parser

| # | 操作 | 预期结果 | 验证点 |
|---|------|----------|--------|
| 1 | `get_scene` | 默认场景 | 基础连通 |
| 2 | `setup_scene` engine=CYCLES samples=128 resolution_x=1920 resolution_y=1080 | 渲染设置更新 | 场景配置 |
| 3 | `create_object` name="Cube" type=MESH primitive=cube location=[0, 0, 1] | Cube 创建 | 建模 |
| 4 | `create_object` name="Camera2" type=CAMERA location=[5, -5, 5] rotation=[1.1, 0, 0.785] lens=50 | 相机创建 | Property Parser |
| 5 | `modify_object` name="Camera2" set_active_camera=true | 激活相机 | 相机设置 |
| 6 | `create_object` name="KeyLight" type=LIGHT light_type=SUN location=[3, -2, 5] color=[1, 0.95, 0.8] energy=2 | 太阳光 | Property Parser: Color3 |
| 7 | `edit_animation` action=insert_keyframe object_name="Cube" data_path="location" frame=1 index=-1 | 关键帧插入 frame 1 | 动画 |
| 8 | `modify_object` name="Cube" location=[3, 0, 1] | Cube 移动 | 变换 |
| 9 | `edit_animation` action=insert_keyframe object_name="Cube" data_path="location" frame=30 | 关键帧 frame 30 | 动画 |
| 10 | `modify_object` name="Cube" location=[-3, 0, 3] | Cube 移动+升高 | 变换 |
| 11 | `edit_animation` action=insert_keyframe object_name="Cube" data_path="location" frame=60 | 关键帧 frame 60 | 动画 |
| 12 | `edit_animation` action=insert_keyframe object_name="Cube" data_path="rotation_euler" frame=1 | 旋转关键帧 | 动画 |
| 13 | `modify_object` name="Cube" rotation=[0, 0, 3.14] | Cube 旋转 | 变换 |
| 14 | `edit_animation` action=insert_keyframe object_name="Cube" data_path="rotation_euler" frame=60 | 旋转关键帧 frame 60 | 动画 |
| 15 | `edit_animation` action=insert_keyframe object_name="Cube" data_path="scale" frame=1 | 缩放关键帧 | 动画 |
| 16 | `modify_object` name="Cube" scale=[2, 2, 2] | Cube 放大 | 变换 |
| 17 | `edit_animation` action=insert_keyframe object_name="Cube" data_path="scale" frame=60 | 缩放关键帧 | 动画 |
| 18 | `get_animation_data` target="Cube" include=[keyframes, fcurves] | 返回 location/rotation/scale 的 fcurves | **_iter_fcurves 兼容** |
| 19 | `edit_animation` action=modify_keyframe object_name="Cube" data_path="location" frame=30 index=0 value=5 | 修改单个关键帧值 | 关键帧编辑 |
| 20 | `get_animation_data` target="Cube" include=[keyframes] | 确认 frame 30 X 值为 5 | 数据验证 |
| 21 | `setup_scene` frame_start=1 frame_end=60 fps=24 | 时间线设置 | 场景配置 |
| 22 | `edit_animation` action=set_frame frame=30 | 跳到 frame 30 | 帧控制 |
| 23 | `capture_viewport` shading=MATERIAL | frame 30 的截图 | 截图 |
| 24 | `get_animation_data` target="Cube" include=[fcurves] frame_range=[1, 60] | 仅返回 1-60 帧的 fcurve 数据 | 范围过滤 |

---

## Test C — 错误恢复 + 约束 + 物理 (22 步)

**验证特性**: Error Suggestion (#155), Property Parser

| # | 操作 | 预期结果 | 验证点 |
|---|------|----------|--------|
| 1 | `get_scene` | 默认场景 | 连通 |
| 2 | `create_object` name="Target" type=MESH primitive=sphere location=[0, 0, 3] | 目标球体 | 建模 |
| 3 | `create_object` name="Follower" type=MESH primitive=cube location=[3, 0, 0] | 跟随立方体 | 建模 |
| 4 | `manage_constraints` action=add target_name="Follower" constraint_type=TRACK_TO | Track To 约束添加 | 约束 |
| 5 | `manage_constraints` action=configure target_name="Follower" constraint_name="Track To" settings={target: "Target", track_axis: "TRACK_NEGATIVE_Z", up_axis: "UP_Y"} | Follower 跟踪 Target | Property Parser: enum strings |
| 6 | `manage_constraints` action=add target_name="Follower" constraint_type=COPY_LOCATION | Copy Location 添加 | 约束 |
| 7 | `manage_constraints` action=configure target_name="Follower" constraint_name="Copy Location" settings={target: "Target", use_offset: true} | 位置偏移跟随 | Property Parser: bool |
| 8 | `get_object_data` name="Follower" include=[constraints] | 2 个约束可见 | 约束验证 |
| 9 | `manage_constraints` action=disable target_name="Follower" constraint_name="Track To" | Track To 禁用但保留 | 约束控制 |
| 10 | `manage_constraints` action=enable target_name="Follower" constraint_name="Track To" | Track To 重新启用 | 约束控制 |
| 11 | `manage_physics` action=add object_name="Target" physics_type=RIGID_BODY settings={mass: 1.0} | 刚体添加 | Property Parser: float |
| 12 | `manage_physics` action=add object_name="Follower" physics_type=RIGID_BODY settings={mass: 0.5} | 刚体添加 | 物理 |
| 13 | `create_object` name="Ground" type=MESH primitive=plane location=[0, 0, -2] scale=[20, 20, 1] | 地面 | 建模 |
| 14 | `manage_physics` action=add object_name="Ground" physics_type=RIGID_BODY_PASSIVE | 被动刚体 | 物理 |
| 15 | `manage_physics` action=configure object_name="Target" settings={restitution: 0.8, friction: 0.3} | 弹性设置 | Property Parser: multi-float |
| 16 | `modify_object` name="XXX_invisible_XXX" location=[0,0,0] | **错误 + suggestion**: "检查对象名称是否存在" | **Error Suggestion** |
| 17 | `manage_constraints` action=add target_name="Ghost" constraint_type=IK | **错误 + suggestion**: "确保 target_name 是存在的对象" | **Error Suggestion** |
| 18 | `manage_physics` action=add object_name="NoOne" physics_type=CLOTH | **错误 + suggestion**: "对象不存在" | **Error Suggestion** |
| 19 | `edit_animation` action=insert_keyframe object_name="Missing" data_path="location" frame=1 | **错误 + suggestion**: "对象不存在或无动画数据" | **Error Suggestion** |
| 20 | `get_node_tree` tree_type=SHADER context=OBJECT target="FakeMat" | **错误 + suggestion**: "材质不存在" | **Error Suggestion** |
| 21 | `manage_material` action=assign name="NoMat" object_name="Target" | **错误 + suggestion**: "材质不存在，先 create" | **Error Suggestion** |
| 22 | `capture_viewport` shading=SOLID | 截图确认场景状态 | 截图 |

---

## Test D — Collection + Scene + Render + Screenshot (23 步)

**验证特性**: Screenshot Compress (#151), Error Suggestion (#155)

| # | 操作 | 预期结果 | 验证点 |
|---|------|----------|--------|
| 1 | `get_collections` | 返回 Scene Collection 根集合 | 基础 |
| 2 | `manage_collection` action=create collection_name="Props" | Props 集合创建 | Collection |
| 3 | `manage_collection` action=create collection_name="Lights" | Lights 集合创建 | Collection |
| 4 | `manage_collection` action=create collection_name="Cameras" | Cameras 集合创建 | Collection |
| 5 | `create_object` name="Chair" type=MESH primitive=cube location=[1, 0, 0] scale=[0.5, 0.5, 1] collection="Props" | 椅子在 Props 中 | Collection link |
| 6 | `create_object` name="Table" type=MESH primitive=cube location=[0, 0, 0.5] scale=[1.5, 1, 0.05] collection="Props" | 桌子在 Props 中 | Collection link |
| 7 | `create_object` name="Sun" type=LIGHT light_type=SUN location=[0, 0, 5] collection="Lights" energy=3 color=[1, 0.9, 0.7] | 太阳光在 Lights | Collection link |
| 8 | `create_object` name="Fill" type=LIGHT light_type=AREA location=[-3, 0, 3] collection="Lights" energy=100 | 补光在 Lights | Collection link |
| 9 | `create_object` name="Cam" type=CAMERA location=[4, -3, 2] rotation=[1.2, 0, 0.8] collection="Cameras" lens=85 | 相机在 Cameras | Collection link |
| 10 | `modify_object` name="Cam" active=true | 激活相机 | 相机 |
| 11 | `get_collections` depth=3 | 显示 Scene Collection → Props/Lights/Cameras + 对象 | 层级验证 |
| 12 | `manage_material` action=create name="Wood" base_color=[0.4, 0.25, 0.1, 1] roughness=0.8 | 木头材质 | 材质 |
| 13 | `manage_material` action=assign name="Wood" object_name="Chair" | 椅子变木色 | 材质分配 |
| 14 | `manage_material` action=assign name="Wood" object_name="Table" | 桌子变木色 | 材质分配 |
| 15 | `setup_scene` engine=CYCLES samples=64 resolution_x=1280 resolution_y=720 fps=24 | 渲染配置 | 场景设置 |
| 16 | `capture_viewport` shading=MATERIAL format=JPEG | **JPEG 缩略图, < 100KB** | **Screenshot Compress** |
| 17 | `capture_viewport` shading=RENDERED format=JPEG | **JPEG 渲染截图** | **Screenshot Compress** |
| 18 | `capture_viewport` shading=SOLID format=PNG | **PNG 全尺寸** | PNG 模式 |
| 19 | `manage_collection` action=set_visibility collection_name="Lights" hide_viewport=true | Lights 隐藏 | Collection 可见性 |
| 20 | `capture_viewport` shading=MATERIAL format=JPEG | 灯光隐藏后的截图 | 状态验证 |
| 21 | `manage_collection` action=set_visibility collection_name="Lights" hide_viewport=false | Lights 恢复 | Collection 可见性 |
| 22 | `manage_collection` action=delete collection_name="Cameras" | Cameras 集合删除 (Cam 也删除) | Collection 删除 |
| 23 | `get_scene` include=[stats] | 确认对象数减少 | 最终状态 |

---

## Test E — Property Parser 压力测试 (21 步)

**验证特性**: Property Parser (#153)

| # | 操作 | 预期结果 | 验证点 |
|---|------|----------|--------|
| 1 | `create_object` name="TestBox" type=MESH primitive=cube | 基础立方体 | 创建 |
| 2 | `modify_object` name="TestBox" location=[1.5, -2.3, 0.7] | float 精确传递 | Vector3 float |
| 3 | `modify_object` name="TestBox" rotation=[1.5708, 0, 3.14159] | 弧度精确传递 | Vector3 radians |
| 4 | `modify_object` name="TestBox" scale=[0.01, 100, 0.5] | 极端缩放值 | Vector3 extreme |
| 5 | `manage_material` action=create name="TestMat" base_color=[0.8, 0.2, 0.1, 1] | RGBA 1.0 范围 | Color4 |
| 6 | `manage_material` action=edit name="TestMat" metallic=1.0 roughness=0.0 | 极端 PBR 值 | float 0/1 |
| 7 | `manage_material` action=edit name="TestMat" alpha=0.0 | 完全透明 | alpha 0 |
| 8 | `manage_material` action=edit name="TestMat" alpha=1.0 | 完全不透明 | alpha 1 |
| 9 | `manage_material` action=assign name="TestMat" object_name="TestBox" | 材质分配 | 基础 |
| 10 | `get_node_tree` tree_type=SHADER context=OBJECT target="TestMat" depth=full | 完整节点树 | 节点读取 |
| 11 | `edit_nodes` operations=[{action: set_value, node: "Principled BSDF", input: "Base Color", value: "#ff5500"}] | hex 颜色解析为 RGB | **Property Parser: hex** |
| 12 | `edit_nodes` operations=[{action: set_value, node: "Principled BSDF", input: "Metallic", value: "0.75"}] | 字符串数字解析 | **Property Parser: string→float** |
| 13 | `edit_nodes` operations=[{action: set_value, node: "Principled BSDF", input: "Roughness", value: "true"}] | bool 不应用到 roughness，错误或忽略 | **Property Parser: type guard** |
| 14 | `manage_modifier` action=add object_name="TestBox" modifier_type=ARRAY | Array 添加 | Modifier |
| 15 | `manage_modifier` action=configure object_name="TestBox" modifier_name="Array" settings={count: 3, relative_offset_displace: [1.0, 0, 0]} | 数组参数 | **Property Parser: mixed types** |
| 16 | `manage_modifier` action=add object_name="TestBox" modifier_type=MIRROR | Mirror 添加 | Modifier |
| 17 | `manage_modifier` action=configure object_name="TestBox" modifier_name="Mirror" settings={use_bisect_axis: [true, false, false]} | Mirror 轴设置 | **Property Parser: bool list** |
| 18 | `create_object` name="Light2" type=LIGHT light_type=SPOT location=[0, 0, 5] energy=500 color="#3366ff" | hex 颜色灯光 | **Property Parser: hex in create** |
| 19 | `manage_constraints` action=add target_name="TestBox" constraint_type=LIMIT_LOCATION | 限制位置约束 | 约束 |
| 20 | `manage_constraints` action=configure target_name="TestBox" constraint_name="Limit Location" settings={use_min_x: true, min_x: -5, use_max_x: true, max_x: 5} | 混合 bool + float | **Property Parser: mixed** |
| 21 | `get_object_data` name="TestBox" include=[mesh_stats, modifiers, materials, constraints] | 完整数据验证 | 最终状态 |

---

## 测试顺序

1. **Test A** (建模+材质+Shader) → 验证基础功能 + Error Suggestion + Screenshot + Property Parser
2. **Test B** (动画) → 验证关键帧 + Blender 5.0 `_iter_fcurves` 兼容
3. **Test C** (错误恢复) → 重点验证 Error Suggestion 在各种错误场景下的表现
4. **Test D** (Collection+Render) → 验证 Screenshot Compress 多种格式/模式
5. **Test E** (Property Parser 压力) → 验证 hex/bool/string/float/Vector3/Color 各种类型转换

每完成一个测试，记录通过/失败步骤，交给用户手动检查后再继续下一个。
