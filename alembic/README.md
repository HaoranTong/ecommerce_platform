# Alembic数据库迁移目录

## 功能说明
本目录包含SQLAlchemy Alembic数据库迁移文件，用于管理数据库结构版本和迁移。

## 目录结构
```
alembic/
├── versions/          # 迁移版本文件
├── alembic.ini        # Alembic配置文件（在根目录）
└── env.py            # 迁移环境配置
```

## 使用方法
```bash
# 生成新的迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 查看迁移历史
alembic history
```

## 注意事项
- 不要手动修改versions目录下的文件
- 迁移前请备份数据库
- 生产环境迁移需要先在测试环境验证