# 共享组件文档

📝 **文档类型**: 共享组件导航  
📍 **作用**: 提供跨模块共享组件的文档导航和使用说明  
🔗 **使用方法**: 查找共享组件的接口定义和使用方法

## 📂 目录结构

```
shared/
└── base-models/          # 基础数据模型和ORM混入类
```

## 🔧 共享组件说明

### 基础模型 (base-models)
- **功能**: ORM基础类、模型混入、通用数据类型定义
- **文档**: [base-models/](./base-models/)
- **代码位置**: `app/shared/base_models.py`, `app/shared/models.py`
- **依赖关系**: 被所有数据模型继承使用

#### 主要组件
- `BaseModel`: SQLAlchemy基础模型类
- `TimestampMixin`: 时间戳字段混入
- `SoftDeleteMixin`: 软删除功能混入
- `AuditMixin`: 审计字段混入

## 💡 使用示例

```python
from app.shared.base_models import BaseModel, TimestampMixin, SoftDeleteMixin

class Product(BaseModel, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    # 自动继承 created_at, updated_at, is_deleted 等字段
```

## 🔗 相关文档
- [数据库设计规范](../standards/database-standards.md) - 数据模型设计标准
- [核心基础设施](../core/) - 核心组件文档
- [业务模块文档](../modules/) - 业务功能模块
- [API数据模式](../standards/api-standards.md) - API数据结构规范
