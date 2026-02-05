# Bug/Limitation: data.create 不支持蜡笔（Grease Pencil）类型

## 现象

尝试使用 `data.create` 创建蜡笔对象时返回 `unsupported_type` 错误。

## 测试案例 1: grease_pencil 类型

### 请求
```json
{
  "type": "grease_pencil",
  "name": "SuzanneGP",
  "data": {
    "strokes": []
  }
}
```

### 响应
```json
Error: unsupported_type
```

## 测试案例 2: gpencil 类型

### 请求
```json
{
  "type": "gpencil",
  "name": "SuzanneGP",
  "data": {
    "strokes": []
  }
}
```

### 响应
```json
Error: unsupported_type
```

## 状态

- **类型**: 功能限制 / 未实现
- **影响**: 无法通过 `data.create` 创建任何蜡笔对象
- **替代方案**: 需使用 `operator.execute` 调用 `object.gpencil_add`

## 对比

| 对象类型 | data.create 支持状态 | 备注 |
|---------|-------------------|------|
| mesh | ⚠️ 部分支持 | 几何数据为0 |
| light | ⚠️ 支持 | 参数可能未存储，未链接场景 |
| curve | ⚠️ 部分支持 | 样条数据丢失 |
| metaball | ❌ 不支持 | `unsupported_type` 错误 |
| text/font | ❌ 不支持 | `unsupported_type` 或强制转 MESH |
| **grease_pencil** | ❌ **不支持** | `unsupported_type` 错误 |

## 发现时间

2026-02-06
