# Bug/Limitation: data.create 不支持融球（Metaball）类型

## 现象

尝试使用 `data.create` 创建融球对象时返回 `unsupported_type` 错误。

## 测试案例 1: metaball 类型

### 请求
```json
{
  "type": "metaball",
  "name": "MetaCube",
  "data": {
    "type": "BALL",
    "elements": [{
      "type": "CUBE",
      "co": [0, 0, 0],
      "radius": 1,
      "size_x": 1,
      "size_y": 1,
      "size_z": 1
    }]
  }
}
```

### 响应
```json
Error: unsupported_type
```

## 测试案例 2: meta 类型

### 请求
```json
{
  "type": "meta",
  "name": "MetaCube",
  "data": {
    "type": "BALL",
    "elements": [{
      "type": "CUBE",
      "co": [0, 0, 0],
      "radius": 1
    }]
  }
}
```

### 响应
```json
Error: unsupported_type
```

## 状态

- **类型**: 功能限制 / 未实现
- **影响**: 无法通过 `data.create` 创建任何融球对象
- **替代方案**: 需使用 `operator.execute` 调用 `object.metaball_add`

## 对比

| 对象类型 | data.create 支持状态 | 备注 |
|---------|-------------------|------|
| mesh | ✅ 部分支持 | 可创建对象但几何数据为0 |
| light | ✅ 支持 | 可创建但可能未链接到场景 |
| curve | ✅ 部分支持 | 可创建对象但样条数据丢失 |
| **metaball** | ❌ **不支持** | `unsupported_type` 错误 |

## 发现时间

2026-02-06
