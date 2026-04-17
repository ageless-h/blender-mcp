# MCP Stability Test Loop - Core Systems

## Mission

通过真实工作流持续测试 blender-mcp 的核心系统稳定性。重点关注节点系统（着色器/几何/合成）、修改器栈、物理模拟、粒子系统、约束系统和动画时间轴。

**核心原则**: 深度测试每个子系统的完整操作链，不是浅层调用。

---

## 核心测试系统

| 系统 | 工具 | 复杂度 |
|------|------|--------|
| 着色器节点 | `blender_get_node_tree`, `blender_edit_nodes` | 高 |
| 几何节点 | `blender_get_node_tree`, `blender_edit_nodes`, `blender_manage_modifier` | 高 |
| 合成节点 | `blender_get_node_tree`, `blender_edit_nodes` | 中 |
| 修改器栈 | `blender_manage_modifier`, `blender_get_object_data` | 高 |
| 时间轴/动画 | `blender_edit_animation`, `blender_get_animation_data` | 高 |
| 物理系统 | `blender_manage_physics` | 中 |
| 粒子系统 | `blender_manage_physics`, `blender_get_object_data` | 中 |
| 约束系统 | `blender_manage_constraints` | 中 |
| 材质系统 | `blender_manage_material`, `blender_get_materials` | 中 |
| 数据系统 | `blender_get_object_data`, `blender_get_images`, `blender_get_armature_data` | 中 |

---

## 场景 1: 着色器节点深度测试

**目标**: 创建复杂的程序化材质，测试节点系统的所有操作

### 工作流

```
Phase 1: 读取默认节点树
├── blender_get_node_tree(tree_type=SHADER, context=OBJECT, target=Material)
├── 记录节点数量和连接
└── 分析默认节点结构

Phase 2: 构建噪声纹理材质
├── 添加 Noise Texture 节点
├── 添加 Color Ramp 节点
├── 添加 Mix Color 节点
├── 添加 Bump 节点
├── 连接: Noise → Color Ramp → Mix Color → BSDF Base Color
├── 连接: Noise → Bump → BSDF Normal
└── 设置各节点参数

Phase 3: 添加程序化颜色变化
├── 添加 Voronoi Texture 节点
├── 添加 HSV 节点
├── 连接: Voronoi → HSV → Mix Color (第二个输入)
└── 设置混合模式

Phase 4: 添加自发光层
├── 添加 Light Path 节点
├── 添加 Emission 节点
├── 添加 Add Shader 节点
├── 连接: BSDF → Add Shader → Material Output
└── 设置条件性发光

Phase 5: 验证和修改
├── 读取完整节点树 (depth=full)
├── 验证所有节点存在
├── 验证所有连接正确
├── 修改随机参数值
└── 再次读取验证

Phase 6: 边缘情况测试
├── 尝试连接不兼容的 socket
├── 删除中间节点
├── 创建孤立节点
├── 设置超出范围的值
└── 尝试删除不存在的节点
```

### 测试点

| 操作 | 预期结果 | 边缘情况 |
|------|---------|---------|
| 添加节点 | 返回节点名称 | 无效节点类型 |
| 删除节点 | 成功删除，连接断开 | 删除不存在的节点 |
| 连接节点 | 连接建立 | 类型不兼容 |
| 断开连接 | 连接移除 | 不存在的连接 |
| 设置值 | 值更新 | 类型错误 |
| 设置属性 | 属性更新 | 无效属性名 |

### 错误场景

```python
# 场景 1.1: 连接不兼容的 socket
blender_edit_nodes(
    operations=[{
        "action": "connect",
        "from_node": "Noise Texture",
        "from_socket": "Color",  # RGBA
        "to_node": "Bump",
        "to_socket": "Strength"  # Float
    }]
)
# 预期: 错误 - 类型不匹配

# 场景 1.2: 创建循环连接
# A → B → C → A (在某些节点类型中可能允许)
blender_edit_nodes(
    operations=[
        {"action": "connect", "from_node": "A", "from_socket": "Out", "to_node": "B", "to_socket": "In"},
        {"action": "connect", "from_node": "B", "from_socket": "Out", "to_node": "C", "to_socket": "In"},
        {"action": "connect", "from_node": "C", "from_socket": "Out", "to_node": "A", "to_socket": "In"}
    ]
)
# 预期: 错误或 Blender 自动处理

# 场景 1.3: 设置数组值类型错误
blender_edit_nodes(
    operations=[{
        "action": "set_value",
        "node": "Noise Texture",
        "input": "Scale",
        "value": "not_a_number"  # 字符串
    }]
)
# 预期: 错误 - 类型错误

# 场景 1.4: 删除后被引用的节点
blender_edit_nodes(
    operations=[
        {"action": "remove_node", "name": "Noise Texture"},  # 被 Color Ramp 引用
        {"action": "get_node_tree", ...}  # 检查状态
    ]
)
# 预期: 连接自动断开
```

---

## 场景 2: 几何节点程序化建模

**目标**: 使用几何节点创建程序化模型，测试几何节点特有的操作

### 工作流

```
Phase 1: 创建几何节点修改器
├── blender_create_object(name="GeoNodeTarget", object_type=MESH, primitive=plane)
├── blender_manage_modifier(action=add, modifier_type=NODES)
└── 记录修改器名称

Phase 2: 构建基础几何节点树
├── blender_get_node_tree(tree_type=GEOMETRY, context=MODIFIER, target="GeoNodeTarget/GeometryNodes")
├── 添加 Subdivision Surface 节点
├── 添加 Set Position 节点
├── 添加 Noise Texture 节点 (输入)
├── 连接: Input Geometry → Subdivision → Set Position → Output
└── 设置细分级别

Phase 3: 添加实例化系统
├── 添加 Distribute Points on Faces 节点
├── 添加 Instance on Points 节点
├── 添加 Object Info 节点 (引用实例对象)
├── 连接实例化链
└── 设置分布参数

Phase 4: 添加属性系统
├── 添加 Store Named Attribute 节点
├── 添加 Random Value 节点
├── 添加 Scale Elements 节点
├── 创建随机缩放效果
└── 验证属性传递

Phase 5: 测试节点组
├── 创建节点组 (如果支持)
├── 在组内添加节点
├── 连接组输入输出
└── 验证组内节点操作

Phase 6: 实时更新测试
├── 修改参数值
├── 验证视口更新
├── 批量修改多个参数
└── 验证性能
```

### 测试点

| 操作 | 测试内容 |
|------|---------|
| 几何节点修改器 | 创建、配置、连接节点树 |
| 节点属性 | 域选择、数据类型 |
| 实例化 | 对象引用、变换 |
| 属性传递 | 命名、类型、范围 |

### 边缘情况

```python
# 场景 2.1: 几何节点引用不存在的对象
blender_edit_nodes(
    operations=[{
        "action": "set_value",
        "node": "Object Info",
        "input": "Object",
        "value": "NonExistentObject"  # 不存在
    }]
)
# 预期: 错误或自动创建引用

# 场景 2.2: 几何节点循环依赖
# 节点树引用自身输出
# 预期: 错误 - 检测到循环

# 场景 2.3: 大量实例化 (性能测试)
# 创建 10000 个实例
# 测试响应时间
```

---

## 场景 3: 合成节点后期处理

**目标**: 设置完整的合成管线

### 工作流

```
Phase 1: 读取默认合成节点树
├── blender_get_node_tree(tree_type=COMPOSITOR, context=SCENE)
└── 分析默认结构

Phase 2: 构建基础合成链
├── 添加 Glare 节点
├── 添加 Color Balance 节点
├── 添加 Lens Distortion 节点
├── 连接: Render Layers → Glare → Color Balance → Lens Distortion → Composite
└── 设置各节点参数

Phase 3: 添加多通道输出
├── 添加 File Output 节点
├── 添加 Separate RGBA 节点
├── 连接深度通道输出
└── 配置文件路径

Phase 4: 验证和渲染
├── 读取完整节点树
├── 验证所有连接
├── 执行测试渲染
└── 检查输出文件
```

---

## 场景 4: 修改器栈完整测试

**目标**: 测试修改器的完整生命周期和依赖关系

### 工作流

```
Phase 1: 创建测试对象
├── blender_create_object(name="ModTest", object_type=MESH, primitive=cube)
└── 记录初始状态

Phase 2: 构建修改器栈
├── 添加 Subdivision Surface (levels=2)
├── 添加 Mirror (X axis)
├── 添加 Bevel (segments=3)
├── 添加 Solidify (thickness=0.1)
├── 添加 Array (count=5, offset=2)
└── 验证修改器顺序

Phase 3: 配置修改器
├── 配置 Mirror: 勾选 Y, Z 轴
├── 配置 Bevel: 设置宽度
├── 配置 Array: 设置相对偏移
└── 读取修改器数据验证

Phase 4: 测试修改器操作
├── 移动修改器顺序 (move_up, move_down)
├── 应用修改器 (apply)
├── 配置已应用的修改器 (预期失败)
└── 验证几何变化

Phase 5: 边缘情况
├── 在 Empty 上添加修改器
├── 添加不支持的修改器类型
├── 配置不存在的参数
├── 应用后再次应用
└── 删除不存在的修改器

Phase 6: 性能测试
├── 添加 20 个修改器
├── 配置每个修改器
├── 验证响应时间
└── 检查内存使用
```

### 修改器类型全覆盖

```python
MODIFIER_TYPES = [
    # 修改类
    "SUBSURF", "MIRROR", "ARRAY", "BOOLEAN", "SOLIDIFY", "BEVEL",
    "DECIMATE", "REMESH", "SKIN", "WIREFRAME", "SCREW",
    # 变形类
    "SHRINKWRAP", "SIMPLE_DEFORM", "CAST", "SMOOTH",
    "LAPLACIANSMOOTH", "CORRECTIVE_SMOOTH", "WARP", "WAVE",
    # 仿真类
    "CLOTH", "COLLISION",
    # 骨骼类
    "ARMATURE", "MESH_DEFORM", "HOOK", "SURFACE_DEFORM",
    # 数据类
    "DATA_TRANSFER", "NORMAL_EDIT", "WEIGHTED_NORMAL",
    "UV_PROJECT", "UV_WARP",
    # 节点类
    "NODES"  # 几何节点
]

# 每种类型至少测试一次:
# 1. 添加
# 2. 配置基本参数
# 3. 验证存在
# 4. 删除
```

### 修改器依赖测试

```python
# 场景 4.1: 修改器顺序影响
# Subdivision → Bevel vs Bevel → Subdivision
# 结果应该不同

# 场景 4.2: 修改器应用顺序
# 先应用 Bevel 再应用 Subdivision
# 等于 Subdivision 后应用 Bevel？
# 预期: 不同结果

# 场景 4.3: 修改器链断裂
# 删除中间修改器
# 后续修改器是否正常工作
```

---

## 场景 5: 时间轴和动画系统

**目标**: 测试完整动画工作流，包括关键帧、NLA、驱动器

### 工作流

```
Phase 1: 创建动画对象
├── 创建多个对象 (不同类型)
├── 设置初始位置
└── 验证初始状态

Phase 2: 关键帧动画
├── 插入位置关键帧 (frame 1)
├── 移动到新位置
├── 插入位置关键帧 (frame 24)
├── 插入旋转关键帧 (frame 1, 24)
├── 插入缩放关键帧 (frame 1, 24)
└── 验证动画数据

Phase 3: 插值模式测试
├── 设置 BEZIER 插值
├── 设置 LINEAR 插值
├── 设置 CONSTANT 插值
├── 设置自定义插值 (BOUNCE, ELASTIC)
└── 验证曲线形状

Phase 4: NLA 系统测试
├── 创建 Action
├── 添加 NLA Strip
├── 配置 Strip 属性
├── 添加多个 Strip
├── 设置混合模式
└── 验证 NLA 播放

Phase 5: 驱动器测试
├── 添加简单驱动器 (sin(frame))
├── 添加对象间驱动器 (跟随位置)
├── 添加条件驱动器 (if/else)
└── 验证驱动器表达式

Phase 6: 形态键动画
├── 创建形态键
├── 设置形态键值
├── 插入形态键关键帧
└── 验证变形动画

Phase 7: 时间轴操作
├── 设置帧范围 (1-100)
├── 设置 FPS (24, 30, 60)
├── 设置当前帧
├── 验证播放范围
└── 测试帧跳转
```

### 动画边缘情况

```python
# 场景 5.1: 无效关键帧
blender_edit_animation(
    action="insert_keyframe",
    object_name="NonExistent",  # 不存在
    data_path="location",
    frame=1
)
# 预期: 错误 - 对象不存在

# 场景 5.2: 无效数据路径
blender_edit_animation(
    action="insert_keyframe",
    object_name="Cube",
    data_path="invalid_property",  # 不存在
    frame=1
)
# 预期: 错误 - 属性不存在

# 场景 5.3: 驱动器语法错误
blender_edit_animation(
    action="add_driver",
    object_name="Cube",
    data_path="location",
    index=0,
    driver_expression="invalid python syntax [[["
)
# 预期: 错误 - 语法错误

# 场景 5.4: NLA Strip 重叠
# 添加时间重叠的 Strip
# 预期: Blender 自动处理或错误

# 场景 5.5: 循环驱动器
# driver_expression = "var" var 引用自身
# 预期: 检测到循环或默认值
```

### 关键帧索引测试

```python
# 测试所有通道
for index in [-1, 0, 1, 2]:  # -1 = 所有通道, 0=X, 1=Y, 2=Z
    blender_edit_animation(
        action="insert_keyframe",
        object_name="Cube",
        data_path="location",
        index=index,
        frame=1
    )
# 预期: -1 创建 3 个关键帧，0/1/2 创建单个
```

---

## 场景 6: 物理和粒子系统

**目标**: 测试物理模拟和粒子系统的完整设置

### 工作流

```
Phase 1: 刚体物理
├── 创建地面 (被动刚体)
├── 创建多个落体 (主动刚体)
├── 配置刚体属性 (质量、摩擦、弹性)
├── 设置初始速度
└── 验证物理属性

Phase 2: 布料模拟
├── 创建平面 (布料)
├── 配置布料属性 (张力、阻尼)
├── 创建碰撞体
├── 配置碰撞设置
└── 验证布料设置

Phase 3: 粒子系统
├── 创建粒子发射器
├── 配置发射参数 (数量、寿命、速度)
├── 配置渲染 (物体、路径)
├── 配置场 (重力、风力)
└── 验证粒子设置

Phase 4: 力场
├── 创建风力场
├── 创建湍流场
├── 创建涡流场
├── 配置力场参数
└── 验证力场影响

Phase 5: 烘焙测试
├── 设置烘焙范围
├── 执行物理烘焙
├── 验证烘焙数据
├── 清除烘焙
└── 重新烘焙

Phase 6: 组合模拟
├── 刚体 + 粒子
├── 布料 + 风力
├── 粒子 + 涡流
└── 验证交互效果
```

### 物理边缘情况

```python
# 场景 6.1: 物理应用于非网格对象
blender_manage_physics(
    action="add",
    object_name="Camera",  # 相机
    physics_type="RIGID_BODY"
)
# 预期: 成功或错误 (取决于 Blender 版本)

# 场景 6.2: 烘焙空场景
blender_manage_physics(
    action="bake",
    object_name="Cube",  # 无物理的对象
    frame_start=1,
    frame_end=24
)
# 预期: 错误 - 无物理

# 场景 6.3: 粒子渲染引用不存在对象
# 粒子渲染为物体，引用不存在对象
# 预期: 错误或默认行为

# 场景 6.4: 极端物理参数
blender_manage_physics(
    action="configure",
    object_name="RigidBody",
    settings={
        "mass": -1,  # 负质量
        "friction": 100,  # 超出范围
    }
)
# 预期: 自动裁剪或错误
```

---

## 场景 7: 约束系统

**目标**: 测试所有约束类型的设置和交互

### 工作流

```
Phase 1: 创建约束对象
├── 创建目标对象
├── 创建约束对象
└── 验证初始状态

Phase 2: 变换约束
├── 添加 Copy Location
├── 添加 Copy Rotation
├── 添加 Copy Scale
├── 添加 Limit Distance
├── 添加 Limit Location
├── 添加 Limit Rotation
└── 验证约束效果

Phase 3: 跟踪约束
├── 添加 Track To
├── 添加 Locked Track
├── 添加 Damped Track
└── 验证跟踪行为

Phase 4: 关系约束
├── 添加 Child Of
├── 添加 Follow Path
├── 添加 Pivot
└── 验证父子关系

Phase 5: IK 约束
├── 创建骨骼链
├── 添加 IK 约束
├── 配置 IK 目标
├── 设置链长
└── 验证 IK 效果

Phase 6: 约束栈测试
├── 添加多个约束
├── 改变约束顺序
├── 启用/禁用约束
├── 验证约束优先级
└── 测试约束冲突
```

### 约束边缘情况

```python
# 场景 7.1: 约束循环
# A 约束到 B，B 约束到 A
# 预期: 检测到循环或 Blender 处理

# 场景 7.2: 不存在的目标
blender_manage_constraints(
    action="add",
    constraint_type="TRACK_TO",
    target_name="Cube",
    settings={"target": "NonExistentObject"}
)
# 预期: 错误或创建无效约束

# 场景 7.3: 骨骼约束到物体
# 骨骼约束目标为普通物体
# 预期: 正常工作

# 场景 7.4: 物体约束到骨骼
# 物体约束目标为骨骼
# 预期: 正常工作
```

---

## 场景 8: 数据系统完整性

**目标**: 验证数据读写的一致性和完整性

### 工作流

```
Phase 1: 创建复杂场景
├── 创建多种类型对象 (MESH, LIGHT, CAMERA, CURVE, EMPTY)
├── 创建材质并分配
├── 创建集合层级
├── 添加修改器
├── 添加动画
└── 创建物理

Phase 2: 读取所有数据
├── blender_get_objects (所有类型)
├── blender_get_object_data (每种类型，所有 include 选项)
├── blender_get_materials (所有材质)
├── blender_get_collections (完整层级)
├── blender_get_images (所有图片)
├── blender_get_scene (所有 include 选项)
└── 验证数据一致性

Phase 3: 修改后验证
├── 修改对象属性
├── 再次读取
├── 验证修改生效
├── 撤销修改
├── 验证撤销成功
└── 检查数据一致性

Phase 4: 批量操作
├── 创建 50 个对象
├── 批量修改属性
├── 批量读取数据
├── 验证所有操作成功
└── 检查性能

Phase 5: 数据引用测试
├── 创建材质引用
├── 创建对象父子
├── 创建集合引用
├── 删除被引用对象
├── 验证引用处理
└── 检查孤立数据
```

### 数据完整性检查

```python
def verify_data_integrity():
    """验证数据完整性的检查清单"""
    
    # 1. 对象数量一致性
    objects = blender_get_objects()
    count = objects["count"]
    assert len(objects["items"]) == count
    
    # 2. 材质引用一致性
    for material in blender_get_materials()["items"]:
        if material["users"] > 0:
            # 检查确实有对象使用
            pass
    
    # 3. 集合层级一致性
    collections = blender_get_collections()
    # 验证父子关系
    
    # 4. 修改器数据一致性
    for obj in objects["items"]:
        if obj["type"] == "MESH":
            data = blender_get_object_data(name=obj["name"], include=["modifiers"])
            modifiers = data.get("modifiers", [])
            # 验证每个修改器有名称和类型
    
    # 5. 动画数据一致性
    for obj in objects["items"]:
        anim = blender_get_animation_data(target=obj["name"])
        if anim:
            # 验证关键帧数据完整性
            pass
```

---

## 场景 9: 材质系统完整测试

**目标**: 测试材质创建、分配、节点编辑的完整流程

### 工作流

```
Phase 1: 材质创建
├── 创建多个材质 (不同名称)
├── 设置 PBR 属性 (颜色、金属度、粗糙度)
├── 设置自发光
├── 验证材质列表
└── 验证材质属性

Phase 2: 材质分配
├── 创建对象
├── 分配材质到单个对象
├── 分配到多个对象
├── 多材质槽测试
├── 取消分配
└── 验证材质用户数

Phase 3: 材质节点编辑
├── 读取材质节点树
├── 添加纹理节点
├── 连接到 BSDF
├── 设置纹理参数
├── 验证视觉效果
└── 捕获视口

Phase 4: 材质复制
├── 复制现有材质
├── 修改副本
├── 验证原材质不变
└── 验证副本独立

Phase 5: 材质删除
├── 删除未使用的材质
├── 删除正在使用的材质 (预期失败或警告)
├── 验证对象材质槽
└── 检查孤立材质

Phase 6: 特殊材质
├── 创建透明材质 (alpha)
├── 创建自发光材质
├── 创建混合材质
└── 验证渲染效果
```

---

## 测试执行策略

### 迭代顺序

```
迭代 1: 场景 1 - 着色器节点深度测试
迭代 2: 场景 2 - 几何节点程序化建模
迭代 3: 场景 3 - 合成节点后期处理
迭代 4: 场景 4 - 修改器栈完整测试
迭代 5: 场景 5 - 时间轴和动画系统
迭代 6: 场景 6 - 物理和粒子系统
迭代 7: 场景 7 - 约束系统
迭代 8: 场景 8 - 数据系统完整性
迭代 9: 场景 9 - 材质系统完整测试

然后:
迭代 10+: 随机选择场景，使用不同参数
```

### 错误分级

| 级别 | 定义 | 示例 |
|------|------|------|
| **Critical** | Blender 崩溃、MCP 连接丢失、数据损坏 | 进程终止、场景无法加载 |
| **Major** | 操作失败、返回错误、结果错误 | 节点连接失败、修改器无效 |
| **Minor** | 错误消息不清晰、性能问题 | 提示不友好、响应慢 |

### 记录要求

每次迭代记录:
1. 测试的场景编号
2. 执行的操作列表
3. 发现的错误（分级）
4. 内存使用
5. 响应时间
6. 视口截图（如果相关）

---

## 清理规则

```bash
# 每次迭代后
rm -f /tmp/mcp_test_session_*.blend  # 删除所有测试文件
rm -rf /tmp/blender_temp_*            # 删除临时目录
find /tmp -name "*.blend" -mmin +30 -delete  # 删除超过30分钟的blend文件
```

---

## 状态跟踪

`/tmp/mcp_test_state.json`:

```json
{
  "iteration": 0,
  "current_scenario": 1,
  "scenarios_completed": [],
  "operations_count": 0,
  "errors": {
    "critical": 0,
    "major": 0,
    "minor": 0
  },
  "issues_created": [],
  "memory_peak_mb": 0,
  "slowest_operation": null,
  "start_time": null
}
```

---

**Do NOT output completion promise** - 循环运行直到取消。
