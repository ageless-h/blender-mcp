# Blender MCP 几何节点测试报告

测试日期：2026-04-16
测试环境：Blender 5.1.0, MCP Server (master branch)

---

## 测试概述

对几何节点进行了完整测试，包括：
- 节点添加测试
- 几何节点修改器创建
- 节点树访问测试

---

## 测试结果汇总

| 分类 | 测试数量 | 通过 | 失败 | 通过率 |
|------|----------|------|------|--------|
| 输入节点 | 7 | 7 | 0 | **100%** |
| 输出节点 | 1 | 1 | 0 | **100%** |
| 几何操作节点 | 12 | 12 | 0 | **100%** |
| 实例节点 | 2 | 2 | 0 | **100%** |
| 点节点 | 2 | 2 | 0 | **100%** |
| 曲线节点 | 4 | 4 | 0 | **100%** |
| 网格图元节点 | 8 | 8 | 0 | **100%** |
| 工具节点 | 7 | 7 | 0 | **100%** |
| **总计** | **43** | **43** | **0** | **100%** |

---

## 详细测试结果

### 一、输入节点 (Input)

| 节点名称 | bl_idname | 添加 | 状态 |
|----------|-----------|------|------|
| 位置 | GeometryNodeInputPosition | ✅ | 通过 |
| 索引 | GeometryNodeInputIndex | ✅ | 通过 |
| ID | GeometryNodeInputID | ✅ | 通过 |
| 随机值 | GeometryNodeInputRandom | ✅ | 通过 |
| 法向 | GeometryNodeInputNormal | ✅ | 通过 |
| 物体信息 | GeometryNodeObjectInfo | ✅ | 通过 |
| 集合信息 | GeometryNodeCollectionInfo | ✅ | 通过 |

**通过率: 7/7 (100%)**

---

### 二、输出节点 (Output)

| 节点名称 | bl_idname | 添加 | 状态 |
|----------|-----------|------|------|
| 查看器 | GeometryNodeViewer | ✅ | 通过 |

**通过率: 1/1 (100%)**

---

### 三、几何操作节点 (Geometry Operations)

| 节点名称 | bl_idname | 添加 | 状态 |
|----------|-----------|------|------|
| 变换几何体 | GeometryNodeTransform | ✅ | 通过 |
| 设置位置 | GeometryNodeSetPosition | ✅ | 通过 |
| 合并几何体 | GeometryNodeJoinGeometry | ✅ | 通过 |
| 分离几何体 | GeometryNodeSeparateGeometry | ✅ | 通过 |
| 删除几何体 | GeometryNodeDeleteGeometry | ✅ | 通过 |
| 边界框 | GeometryNodeBoundBox | ✅ | 通过 |
| 按距离合并 | GeometryNodeMergeByDistance | ✅ | 通过 |
| 细分表面 | GeometryNodeSubdivisionSurface | ✅ | 通过 |
| 布尔网格 | GeometryNodeMeshBoolean | ✅ | 通过 |
| 挤出网格 | GeometryNodeExtrudeMesh | ✅ | 通过 |
| 设置材质 | GeometryNodeSetMaterial | ✅ | 通过 |
| 存储命名属性 | GeometryNodeStoreNamedAttribute | ✅ | 通过 |

**通过率: 12/12 (100%)**

---

### 四、实例节点 (Instances)

| 节点名称 | bl_idname | 添加 | 状态 |
|----------|-----------|------|------|
| 点上实例 | GeometryNodeInstanceOnPoints | ✅ | 通过 |
| 实现实例 | GeometryNodeRealizeInstances | ✅ | 通过 |

**通过率: 2/2 (100%)**

---

### 五、点节点 (Point)

| 节点名称 | bl_idname | 添加 | 状态 |
|----------|-----------|------|------|
| 网格到点 | GeometryNodeMeshToPoints | ✅ | 通过 |
| 点分布 | GeometryNodeDistributePointsOnFaces | ✅ | 通过 |

**通过率: 2/2 (100%)**

---

### 六、曲线节点 (Curve)

| 节点名称 | bl_idname | 添加 | 状态 |
|----------|-----------|------|------|
| 曲线到网格 | GeometryNodeCurveToMesh | ✅ | 通过 |
| 网格到曲线 | GeometryNodeMeshToCurve | ✅ | 通过 |
| 修剪曲线 | GeometryNodeTrimCurve | ✅ | 通过 |
| 重采样曲线 | GeometryNodeResampleCurve | ✅ | 通过 |

**通过率: 4/4 (100%)**

---

### 七、网格图元节点 (Mesh Primitives)

| 节点名称 | bl_idname | 添加 | 状态 |
|----------|-----------|------|------|
| 网格网格 | GeometryNodeMeshGrid | ✅ | 通过 |
| 网格立方体 | GeometryNodeMeshCube | ✅ | 通过 |
| 网格圆形 | GeometryNodeMeshCircle | ✅ | 通过 |
| 网格圆柱 | GeometryNodeMeshCylinder | ✅ | 通过 |
| 网格锥体 | GeometryNodeMeshCone | ✅ | 通过 |
| 网格球 | GeometryNodeMeshUVSphere | ✅ | 通过 |
| 网格二十面体球 | GeometryNodeMeshIcoSphere | ✅ | 通过 |
| 网格线 | GeometryNodeMeshLine | ✅ | 通过 |

**通过率: 8/8 (100%)**

---

### 八、工具节点 (Utilities)

| 节点名称 | bl_idname | 添加 | 状态 |
|----------|-----------|------|------|
| 数学 | ShaderNodeMath | ✅ | 通过 |
| 矢量数学 | ShaderNodeVectorMath | ✅ | 通过 |
| 布尔数学 | FunctionNodeBooleanMath | ✅ | 通过 |
| 开关 | GeometryNodeSwitch | ✅ | 通过 |
| 比较 | FunctionNodeCompare | ✅ | 通过 |
| 颜色渐变 | ShaderNodeValToRGB | ✅ | 通过 |
| 混合 | ShaderNodeMix | ✅ | 通过 |

**通过率: 7/7 (100%)**

---

## 测试要点

### 节点树访问方式

几何节点树需要特殊的目标格式：
```
tree_type: "GEOMETRY"
context: "MODIFIER"
target: "<object_name>/<modifier_name>"
```

例如：`target: "TestGeo/GeometryNodes"`

### 自动创建节点组

当首次向空的几何节点修改器添加节点时，系统会自动创建节点组。

---

## 测试结论

### 成功点
- ✅ 所有 43 种几何节点都能成功**添加**到几何节点树
- ✅ 节点添加功能正常
- ✅ 几何节点修改器创建正常

### 注意事项
- 几何节点树需要 `context="MODIFIER"` 和 `target="object/modifier"` 格式
- 组输入/输出节点在创建节点组时自动添加

---

*测试执行时间: 2026-04-16*
*测试框架: Blender MCP 自动化测试*
