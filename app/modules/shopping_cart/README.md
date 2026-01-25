# 购物车模块

📝 **模块类型**: 核心业务模块  
📍 **功能**: 购物车商品管理、价格计算、实时同步  
🔗 **技术文档**: [docs/modules/shopping-cart/](../../../docs/modules/shopping-cart/)

## 快速导航

### 📋 完整技术文档 
📍 **位置**: `docs/modules/shopping-cart/`
- [📖 模块概述](../../../docs/modules/shopping-cart/overview.md)
- [📋 业务需求](../../../docs/modules/shopping-cart/requirements.md)
- [🏗️ 设计决策](../../../docs/modules/shopping-cart/design.md)
- [🔌 API规范](../../../docs/modules/shopping-cart/api-spec.md)
- [⚙️ API实施](../../../docs/modules/shopping-cart/api-implementation.md)
- [💻 实现细节](../../../docs/modules/shopping-cart/implementation.md)

### 🔧 代码文件
- `router.py` - API路由定义
- `service.py` - 业务逻辑处理  
- `models.py` - 数据模型定义
- `schemas.py` - 请求/响应模型
- `dependencies.py` - 模块依赖注入
- `repository.py` - 数据访问层
- `exceptions.py` - 自定义异常
- `api.schema.json` - API Schema定义
- `schema.md` - API Schema文档

### 🚀 快速开始
```python
# 导入路由
from app.modules.shopping_cart.router import router

# 注册到主应用  
app.include_router(router, prefix="/api/v1", tags=["购物车"])
```

### 🔌 API端点
- `POST /api/v1/shopping-cart/items` - 添加商品到购物车
- `GET /api/v1/shopping-cart/items` - 获取购物车内容
- `PUT /api/v1/shopping-cart/items/{id}` - 更新商品数量
- `DELETE /api/v1/shopping-cart/items/{id}` - 删除购物车商品

---

⚠️ **文档说明**: 
- 本文件仅作为代码模块导航
- 完整技术文档请查看 `docs/modules/shopping-cart/` 目录
- 所有设计决策和实现细节请参考技术文档

# 在其他模块中使用
service = shopping_cartService(db)
`

## 相关文档

- [API设计标准](../../../docs/standards/api-standards.md)
- [数据库设计规范](../../../docs/standards/database-standards.md)
- [模块开发指南](../../../docs/development/module-development-guide.md)

## 开发状态

- ✅ 模块结构创建
- 🔄 功能开发中
- ⏳ 待完善测试
- ⏳ 待完善文档

## 更新日志

### 2025-09-13
- 创建模块基础结构
- 初始化模块文件
- 添加模块README文档