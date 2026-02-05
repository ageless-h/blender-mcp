# Bug: data.create 创建网格对象失败

## 现象

使用 `data.create` 工具创建圆柱体时，虽然返回成功，但创建的网格对象顶点/边/面数量为 0。

### 请求
```json
{
  "type": "mesh",
  "name": "Cylinder",
  "data": {
    "type": "cylinder",
    "radius": 1,
    "depth": 2
  }
}
```

### 响应
```json
{
  "name": "Cylinder",
  "type": "mesh",
  "vertices": 0,
  "edges": 0,
  "polygons": 0
}
```

## 预期行为

创建具有实际几何数据的网格对象（圆柱体应该有多个顶点、边和面）。

## 实际行为

网格对象被创建但没有任何几何数据（0 顶点/边/面）。

## 替代方案

使用 `operator.execute` 工具直接调用 Blender 操作符成功创建：

```json
{
  "operator": "mesh.primitive_cylinder_add",
  "params": {
    "radius": 1,
    "depth": 2,
    "location": [0, 0, 0]
  }
}
```

## 可能原因

- `data.create` 工具可能没有正确处理 `mesh` 类型的几何数据生成
- `data` 参数中的 `type: cylinder` 配置未被正确解析

## 发现时间

2026-02-06
