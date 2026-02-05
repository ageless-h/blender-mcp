# Bug: data.create 创建曲线时样条数据丢失

## 现象

使用 `data.create` 创建贝塞尔曲线时，虽然返回成功，但曲线没有实际的样条数据（splines_count: 0），几何数据完全丢失。

## 测试案例 1: 简单贝塞尔曲线

### 请求
```json
{
  "type": "curve",
  "name": "BezierCurve",
  "data": {
    "type": "BEZIER",
    "splines": [{
      "type": "BEZIER",
      "bezier_points": [
        {"co": [-1, 0, 0], "handle_left": [-1.5, -0.5, 0], "handle_right": [-0.5, 0.5, 0]},
        {"co": [1, 0, 0], "handle_left": [0.5, 0.5, 0], "handle_right": [1.5, -0.5, 0]}
      ]
    }]
  }
}
```

### 响应
```json
{
  "name": "BezierCurve",
  "type": "curve"
}
```

## 测试案例 2: 圆形闭合贝塞尔曲线

### 请求
```json
{
  "type": "curve",
  "name": "CircleBezier",
  "data": {
    "type": "BEZIER",
    "dimensions": "3D",
    "splines": [{
      "type": "BEZIER",
      "use_cyclic_u": true,
      "bezier_points": [
        {"co": [1, 0, 0], "handle_left": [1, -0.552, 0], "handle_right": [1, 0.552, 0]},
        {"co": [0, 1, 0], "handle_left": [0.552, 1, 0], "handle_right": [-0.552, 1, 0]},
        {"co": [-1, 0, 0], "handle_left": [-0.552, 0, 0], "handle_right": [-1, -0.552, 0]},
        {"co": [0, -1, 0], "handle_left": [-0.552, -1, 0], "handle_right": [0.552, -1, 0]}
      ]
    }]
  }
}
```

### 响应
```json
{
  "name": "CircleBezier",
  "type": "curve"
}
```

### 数据读取验证
```json
{
  "name": "CircleBezier",
  "dimensions": "2D",
  "splines_count": 0,
  "resolution_u": 12
}
```

## 问题分析

1. **样条数据丢失**: `splines_count: 0`，请求的 splines 数组未被处理
2. **维度错误**: 请求 `3D` 被存储为 `2D`
3. **控制点丢失**: 所有 bezier_points 数据未保存

## 影响

- 无法通过 `data.create` 创建任何具有实际几何数据的曲线
- 曲线对象创建成功但为空

## 对比

| 对象类型 | data.create 结果 | 备注 |
|---------|-----------------|------|
| mesh (圆柱体) | ❌ 失败 | 顶点/边/面为0 |
| light (点光源) | ✅ 成功 | 对象创建成功 |
| curve (贝塞尔曲线) | ❌ 失败 | splines_count为0 |

## 发现时间

2026-02-06
