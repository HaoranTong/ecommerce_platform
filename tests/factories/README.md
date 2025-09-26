# 测试数据工厂目录

## 📋 目录说明

本目录包含**双工厂架构**的测试数据生成系统，采用场景化分工策略，确保测试数据的专业性和一致性。

## 📁 文件结构

```
factories/
├── README.md                    # 本说明文档
├── data_factory.py              # 统一测试数据工厂 (集成测试专用)
└── user_auth_factories.py       # 用户认证模块Factory Boy工厂 (单元测试专用)
```

## 🎯 双工厂架构设计

### 📊 **场景化分工策略**

| 工厂类型 | 适用场景 | 技术特点 | 推荐用途 |
|---------|---------|---------|---------|
| **统一工厂**<br/>`data_factory.py` | 集成测试<br/>E2E测试<br/>烟雾测试 | 真实数据库操作<br/>跨模块数据链<br/>数据类型安全 | 业务流程测试<br/>完整功能验证 |
| **Factory Boy工厂**<br/>`user_auth_factories.py` | 单元测试<br/>Mock测试<br/>复杂关系测试 | Factory Boy模式<br/>智能数据生成<br/>关联关系处理 | 纯逻辑测试<br/>权限系统测试 |

### � **使用指南**

#### 集成测试 - 使用统一工厂
```python
# tests/integration/test_order_workflow.py
from tests.factories.data_factory import StandardTestDataFactory

def test_complete_order_workflow(integration_test_db):
    # 创建完整业务数据链
    user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(integration_test_db)
    
    # 进行集成测试
    order_service = OrderService(integration_test_db)
    result = order_service.create_order(user.id, sku.id, quantity=2)
    assert result.success is True
```

#### 单元测试 - 使用Factory Boy工厂
```python
# tests/unit/test_user_permissions.py
from tests.factories.user_auth_factories import UserFactory, RoleFactory, PermissionFactory

def test_user_has_admin_permission(mocker):
    # Factory Boy + Mock的完美组合
    user = UserFactory(is_active=True)
    admin_role = RoleFactory(name='admin')
    admin_permission = PermissionFactory(resource='user', action='manage')
    
    # 测试权限逻辑
    assert user.has_permission('user.manage')
```

### 🎨 **核心优势**

#### 统一工厂优势
- ✅ **跨模块支持**: 支持完整的用户→商品→订单业务链
- ✅ **数据类型安全**: 自动确保sku_id等关键字段类型正确
- ✅ **真实数据库优化**: 针对SQLite/MySQL等真实数据库环境优化
- ✅ **业务完整性**: 支持完整业务流程的数据准备

#### Factory Boy工厂优势  
- ✅ **智能生成**: Factory Boy标准模式，智能推断合理测试值
- ✅ **关系处理**: 自动处理复杂的外键关系和唯一约束
- ✅ **Mock配合**: 与pytest-mock框架完美结合
- ✅ **专业化**: 专门针对用户认证RBAC权限模型设计

## 📚 相关文档

- **[测试标准文档](../../docs/standards/testing-standards.md)** - Factory Boy使用规范和数据库策略
- **[测试环境配置](../../docs/development/testing-environment.md)** - 完整的测试环境配置和工具使用说明
- **[测试数据工厂使用手册](../../docs/tools/test-factory-usage-guide.md)** - 详细的双工厂使用指南和最佳实践

## ⚠️ 重要提醒

### 选择正确的工厂
- **集成测试、E2E测试** → 使用 `data_factory.py`
- **单元测试、Mock测试** → 使用 `user_auth_factories.py` (user_auth模块)
- **其他模块单元测试** → 等待自动生成对应的Factory Boy工厂

### 避免混用
- 不要在单元测试中使用统一工厂 (会创建真实数据库记录)
- 不要在集成测试中过度使用Factory Boy (Mock不适用于集成测试)
- 遵循测试架构的数据库策略选择合适的工厂

## 🔮 未来扩展

随着项目发展，会为其他模块创建专用的Factory Boy工厂：
- `product_catalog_factories.py` - 商品目录模块专用工厂
- `order_management_factories.py` - 订单管理模块专用工厂  
- `shopping_cart_factories.py` - 购物车模块专用工厂

每个专用工厂都将遵循相同的设计原则和使用规范。