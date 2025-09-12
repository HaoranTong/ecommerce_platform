# 数据验证模型

Pydantic数据模型定义，用于API请求和响应的数据验证和序列化。

## 📁 目录结构

```
schemas/
├── inventory.py           # 库存相关数据模型
└── __init__.py            # 模块初始化
```

## 📋 模型说明

| 模型文件 | 包含模型 | 用途 |
|---------|---------|------|
| **inventory.py** | 库存查询、更新模型 | 库存操作数据验证 |

## 🔄 数据流转

```
前端请求 → Pydantic验证 → 业务逻辑 → 数据库 → Pydantic序列化 → API响应
```

## 🔗 相关文档

- [API文档](../api/README.md) - 使用这些模型的API接口
- [数据库模型](../models.py) - SQLAlchemy数据库模型