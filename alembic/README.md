# 数据库迁移管理

Alembic数据库版本控制和迁移脚本管理。

## 📁 目录结构

```
alembic/
├── versions/               # 数据库迁移版本文件
│   ├── 001_initial.py     # 初始数据库结构
│   ├── 002_add_users.py   # 用户表迁移
│   ├── 003_add_products.py # 商品表迁移
│   └── ...                # 其他迁移文件
├── env.py                 # Alembic环境配置
├── script.py.mako         # 迁移脚本模板
└── __pycache__/           # Python缓存文件
```

## 🔧 核心文件说明

| 文件 | 作用 | 维护责任 |
|-----|------|---------|
| **env.py** | Alembic环境配置，数据库连接设置 | 后端开发 |
| **script.py.mako** | 新迁移脚本的生成模板 | 架构师 |
| **versions/*.py** | 具体的数据库迁移脚本 | 对应功能开发者 |

## 🚀 常用操作

```powershell
# 生成新迁移
alembic revision --autogenerate -m "描述信息"

# 应用迁移
alembic upgrade head

# 查看当前版本
alembic current

# 回滚迁移
alembic downgrade -1
```

## 🔗 相关文档

- [数据库设计规范](../docs/standards/database-standards.md)
- [数据模型文档](../docs/modules/data-models/)
- [开发工具使用](../docs/development/tools.md)