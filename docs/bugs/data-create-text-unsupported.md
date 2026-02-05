# Bug: data.create 创建文本对象失败

## 现象

尝试使用 `data.create` 创建文本对象时，`font` 和 `text` 类型均返回 `unsupported_type` 错误。使用 `object` 类型配合 `object_type="FONT"` 时，对象被强制创建为 `MESH` 类型。

## 测试案例 1: text 类型

### 请求
```json
{
  "type": "text",
  "name": "MyText",
  "data": {
    "body": "Hello Blender",
    "extrude": 0.1,
    "bevel_depth": 0.02,
    "size": 1
  }
}
```

### 响应
```json
Error: unsupported_type
```

## 测试案例 2: font 类型

### 请求
```json
{
  "type": "font",
  "name": "MyText",
  "data": {
    "body": "Hello Blender",
    "extrude": 0.1,
    "bevel_depth": 0.02,
    "size": 1
  }
}
```

### 响应
```json
Error: unsupported_type
```

## 测试案例 3: object 类型强制转换

### 请求
```json
{
  "type": "object",
  "name": "MyText",
  "data": {
    "object_type": "FONT",
    "body": "Hello Blender",
    "extrude": 0.1,
    "bevel_depth": 0.02,
    "size": 1
  }
}
```

### 响应
```json
{
  "name": "MyText",
  "type": "object",
  "object_type": "MESH",
  "data_name": "MyText_mesh"
}
```

## 问题分析

1. **text/font 类型未实现**: 直接返回 `unsupported_type`
2. **参数被忽略**: `object_type="FONT"` 被强制改为 `"MESH"`
3. **数据类型错误**: 创建了 mesh 数据而非文本数据

## 状态

- **影响**: 无法通过 `data.create` 创建文本对象
- **替代方案**: 需使用 `operator.execute` 调用 `object.text_add`

## 对比

| 对象类型 | data.create 支持状态 | 备注 |
|---------|-------------------|------|
| mesh | ⚠️ 部分支持 | 几何数据为0 |
| light | ⚠️ 支持 | 参数可能未存储，未链接场景 |
| curve | ⚠️ 部分支持 | 样条数据丢失 |
| metaball | ❌ 不支持 | `unsupported_type` 错误 |
| **text/font** | ❌ **不支持** | `unsupported_type` 或强制转 MESH |

## 发现时间

2026-02-06
