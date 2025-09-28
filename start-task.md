# AI初始化任务方案集 (start-task.md)

> **使用说明**: 本文档包含5套不同的AI初始化验证方案，每套都有完整的文档清单和验证问题。用户可根据需要复制粘贴其中一套到对话框，让AI完成初始化任务。建议根据实际开发阶段和重点领域选择合适的方案。

---

## 🎯 方案1: 核心技术栈与架构原则验证

### 文档清单
请阅读以下文档：
1. **PROJECT-FOUNDATION.md** - 项目基础架构设定
2. **README.md** - 项目概览和技术选型
3. **docs/architecture/overview.md** - 技术架构总览和设计原则

### 验证问题
请回答以下问题：
1. 项目采用的核心技术栈是什么？为什么选择Python生态？
2. 架构设计的8大核心原则是什么？请重点说明契约优先和适配器抽象原则的具体含义。
3. 项目的决策优先级是什么？在技术选型时如何平衡业务需求适配度与技术先进性？
4. 项目支持哪些部署环境？云原生兼容性体现在哪些方面？
5. 数据一致性优先原则在项目架构中如何体现？

---

## 🎯 方案2: 目录结构与模块边界验证

### 文档清单
请阅读以下文档：
1. **PROJECT-FOUNDATION.md** - 项目基础架构设定
2. **docs/architecture/module-architecture.md** - 模块架构设计
3. **docs/standards/naming-conventions-standards.md** - 命名规范标准

### 验证问题
请回答以下问题：
1. 根目录下的8个核心目录分别是什么？每个目录的职责边界如何划分？
2. app/目录下的4个核心子目录是什么？adapters/和core/目录各自的职责是什么？
3. 业务模块的垂直切片结构是怎样的？每个模块包含哪些标准子目录？
4. 什么情况下禁止跨目录污染？具体有哪些禁止行为？
5. 模块命名映射规则是什么？目录名与业务名称如何对应？

---

## 🎯 方案3: 数据库设计核心原则验证

### 文档清单
请阅读以下文档：
1. **docs/standards/database-standards.md** - 数据库设计规范
2. **PROJECT-FOUNDATION.md** - 项目基础架构设定
3. **docs/standards/naming-conventions-standards.md** - 命名规范标准

### 验证问题
请回答以下问题：
1. 主键设计的统一标准是什么？为什么禁止使用BIGINT作为主键？
2. 软删除字段的标准设计是什么？deleted_at字段的值含义如何？
3. 外键约束设计有哪些要求？级联操作如何设置？
4. 所有业务表必须包含哪些标准时间戳字段？created_at和updated_at的默认值设置是什么？
5. 索引设计的强制要求是什么？复合索引的字段顺序原则如何？

### 数据库设计全文参考
```python
# SQLAlchemy模型标准模板
from sqlalchemy import Column, String, Boolean, Integer, DateTime, func
from app.core.database import Base

class User(Base):
    """用户模型 - 标准模板示例"""
    __tablename__ = 'users'
    
    # 主键设计 (统一使用INTEGER)
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    
    # 业务字段设计
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(255), unique=True, nullable=False, index=True, comment="邮箱")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    
    # 标准时间戳字段 (强制要求)
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="软删除时间")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
```

---

## 🎯 方案4: API设计与路由规范验证

### 文档清单
请阅读以下文档：
1. **docs/standards/api-standards.md** - API设计规范
2. **docs/architecture/overview.md** - 技术架构总览
3. **docs/standards/naming-conventions-standards.md** - 命名规范标准

### 验证问题
请回答以下问题：
1. RESTful架构的5大原则是什么？资源导向设计的具体含义是什么？
2. 模块化路由的组织原则是什么？业务端点的路径格式如何设计？
3. HTTP方法的语义和幂等性要求是什么？PUT和PATCH的区别在哪里？
4. API版本控制策略是什么？全局API版本前缀格式如何？
5. 标准响应格式包含哪些字段？错误响应的结构是怎样的？

### API设计全文参考
```python
# FastAPI路由组织标准模板
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter()

# 标准CRUD端点设计
@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """获取商品列表 - 标准GET操作"""
    return await product_service.get_products(skip, limit)

@router.post("/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_user)
):
    """创建商品 - 标准POST操作"""
    return await product_service.create_product(product)

@router.put("/products/{product_id}", response_model=ProductResponse)  
async def update_product(
    product_id: int,
    product: ProductUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新商品 - 标准PUT操作（幂等）"""
    return await product_service.update_product(product_id, product)
```

```json
// 标准响应格式
{
  "success": true,
  "message": "操作成功",
  "data": {
    "id": 1,
    "name": "五常大米",
    "price": 99.99
  },
  "meta": {
    "timestamp": "2025-09-28T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

---

## 🎯 方案5: 工作流程与检查点机制验证

### 文档清单
请阅读以下文档：
1. **MASTER.md** - AI工作流程控制文档
2. **docs/tools/checkpoint-cards.md** - 检查点卡片详情
3. **docs/status/current-work-status.md** - 当前工作状态

### 验证问题
请回答以下问题：
1. AI工作流程的6个关键步骤是什么？每个步骤的核心要求是什么？
2. TODO清单创建的强制要求是什么？检查点标记的格式如何？
3. 检查点分为哪几大类别？DEV类和TEST类检查点各有多少个？
4. 异常处理机制包含哪3个步骤？人工干预的4个选项是什么？
5. AI工作的3大核心原则是什么？为什么要求"文档驱动开发"？

### 检查点分类参考
```
🚀 启动类: AI-START
📋 需求分析类: REQ-001 到 REQ-003  
🏗️ 架构设计类: ARCH-001 到 ARCH-004
💻 开发实施类: DEV-001 到 DEV-014
🧪 测试验证类: TEST-001 到 TEST-008
📊 状态管理类: STATUS-001 到 STATUS-004
📖 文档同步类: DOC-001 到 DOC-006
🚨 应急处理类: EMERGENCY-001
```

---

## 📋 使用建议

### 方案选择指南
- **方案1**: 适合项目初期，重点理解技术选型和架构原则
- **方案2**: 适合模块开发阶段，重点掌握目录结构和边界规则
- **方案3**: 适合数据建模阶段，重点掌握数据库设计标准
- **方案4**: 适合API开发阶段，重点掌握接口设计规范
- **方案5**: 适合任务执行阶段，重点掌握工作流程控制

### 使用频率建议
- **每日开发**: 建议使用方案5验证工作流程
- **新功能开发**: 建议使用方案2+方案3组合
- **接口开发**: 建议使用方案4验证API设计
- **架构调整**: 建议使用方案1验证核心原则
- **问题排查**: 建议使用方案5掌握检查点机制

### 复制使用方式
直接复制所需方案的"文档清单"和"验证问题"部分粘贴到对话框，AI会按要求读取文档并回答验证问题，完成初始化任务。