# 测试数据工厂使用手册

## 📋 文档概述

本手册详细介绍**双工厂架构**的测试数据生成策略，帮助开发者选择正确的工厂类型，提升测试效率和质量。

## 🎯 核心理念：场景化分工策略

### 设计哲学
- **专业化分工**: 每种工厂专注于特定的测试场景
- **技术特色化**: 发挥不同技术栈的优势
- **一致性保证**: 统一的使用规范和接口设计

### 架构优势
- ✅ **避免技术混乱**: 清晰的技术边界和使用场景
- ✅ **提升测试效率**: 针对性的数据生成策略
- ✅ **降低维护成本**: 专用工厂更易维护和扩展
- ✅ **保证数据质量**: 每种工厂都针对特定场景优化

## 🏭 双工厂架构详解

### 📊 **架构对比表**

| 特性维度 | Factory Boy工厂<br/>`user_auth_factories.py` | 统一工厂<br/>`data_factory.py` |
|---------|-------------------------------------------|------------------------------|
| **适用测试** | 单元测试<br/>Mock测试<br/>逻辑验证测试 | 集成测试<br/>E2E测试<br/>功能验证测试 |
| **数据库策略** | Mock数据库<br/>内存数据库<br/>不持久化 | 真实数据库<br/>SQLite/MySQL<br/>数据持久化 |
| **技术特点** | Factory Boy标准<br/>智能关系处理<br/>自动数据推断 | 原生SQLAlchemy<br/>跨模块数据链<br/>类型安全保证 |
| **性能特征** | 极速创建<br/>内存操作<br/>无I/O开销 | 适中速度<br/>数据库I/O<br/>真实环境模拟 |
| **数据复杂度** | 单模块数据<br/>复杂关系<br/>权限模型专用 | 多模块数据<br/>完整业务链<br/>跨系统集成 |
| **维护难度** | 低 (标准模式) | 中 (需同步模型变化) |

## 🔧 Factory Boy工厂使用指南

### 📍 **适用场景判断**

使用Factory Boy工厂的标志：
- ✅ 测试文件路径包含 `tests/unit/`
- ✅ 需要测试复杂的RBAC权限逻辑
- ✅ 需要Mock外部依赖
- ✅ 注重测试执行速度
- ✅ 测试纯业务逻辑，不涉及数据持久化

### 🎨 **核心特性与优势**

#### 1. **智能数据生成**
```python
# Factory Boy自动处理复杂逻辑
user = UserFactory(
    username='admin_user',
    # password会自动加密
    # email会自动生成unique值
    # created_at会自动设置为当前时间
)
```

#### 2. **关联关系处理**
```python
# 自动创建关联数据
user_with_role = UserFactory(
    roles__0__name='admin',  # 自动创建admin角色
    roles__0__permissions__0__resource='user',  # 自动创建权限
    roles__0__permissions__0__action='manage'
)
```

#### 3. **Mock框架完美结合**
```python
def test_user_permission_check(mocker):
    # Factory Boy创建测试数据
    user = UserFactory(is_active=True)
    
    # Mock外部服务
    mock_auth = mocker.patch('app.services.AuthService')
    mock_auth.check_permission.return_value = True
    
    # 测试业务逻辑
    assert user.has_admin_access() is True
```

### 🛠️ **实战使用模式**

#### **模式1: 基础数据创建**
```python
# tests/unit/user_auth/test_user_model.py
from tests.factories.user_auth_factories import UserFactory

def test_user_password_encryption():
    """测试用户密码加密功能"""
    user = UserFactory(password='plain_password')
    
    # Factory Boy自动处理加密
    assert user.password_hash != 'plain_password'
    assert user.verify_password('plain_password') is True
```

#### **模式2: 复杂关系测试**
```python
# tests/unit/user_auth/test_rbac_logic.py
from tests.factories.user_auth_factories import UserFactory, RoleFactory, PermissionFactory

def test_role_based_access_control():
    """测试基于角色的访问控制"""
    # 创建权限
    manage_users = PermissionFactory(resource='user', action='manage')
    view_products = PermissionFactory(resource='product', action='view')
    
    # 创建角色并关联权限
    admin_role = RoleFactory(
        name='admin',
        permissions=[manage_users, view_products]
    )
    
    # 创建用户并关联角色
    admin_user = UserFactory(roles=[admin_role])
    
    # 测试权限检查逻辑
    assert admin_user.has_permission('user.manage') is True
    assert admin_user.has_permission('product.view') is True
    assert admin_user.has_permission('order.create') is False
```

#### **模式3: Mock服务集成**
```python
# tests/unit/user_auth/test_auth_service.py
from tests.factories.user_auth_factories import UserFactory
import pytest

def test_user_login_success(mocker):
    """测试用户登录成功逻辑"""
    # 创建测试用户
    user = UserFactory(
        username='testuser',
        is_active=True,
        password='correct_password'
    )
    
    # Mock数据库查询
    mock_db = mocker.patch('app.database.get_session')
    mock_db.return_value.query.return_value.filter.return_value.first.return_value = user
    
    # Mock JWT生成
    mock_jwt = mocker.patch('app.auth.create_access_token')
    mock_jwt.return_value = 'fake_token_12345'
    
    # 测试登录服务
    auth_service = AuthService()
    result = auth_service.login('testuser', 'correct_password')
    
    assert result.success is True
    assert result.token == 'fake_token_12345'
    assert result.user.username == 'testuser'
```

### ⚠️ **Factory Boy使用注意事项**

#### **数据库策略**
```python
# ✅ 正确：使用内存数据库或Mock
@pytest.fixture
def mock_db_session(mocker):
    return mocker.patch('app.database.get_session')

def test_with_factory_boy(mock_db_session):
    user = UserFactory()  # 不会创建真实数据库记录
```

#### **避免的错误**
```python
# ❌ 错误：在Factory Boy测试中使用真实数据库
def test_user_creation(integration_test_db):  # ❌ 不应该使用integration_test_db
    user = UserFactory.create()  # 这会尝试写入真实数据库
```

## 🌐 统一工厂使用指南

### 📍 **适用场景判断**

使用统一工厂的标志：
- ✅ 测试文件路径包含 `tests/integration/`, `tests/e2e/`
- ✅ 需要测试跨模块的数据交互
- ✅ 需要验证完整的业务流程
- ✅ 需要测试真实的数据库操作
- ✅ 需要保证数据类型的完整性

### 🎨 **核心特性与优势**

#### 1. **跨模块数据链支持**
```python
# 一次性创建完整业务数据链
user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(db)

# 数据间的关联关系真实可靠
assert product.category_id == category.id
assert product.brand_id == brand.id
assert sku.product_id == product.id
assert isinstance(sku.id, int)  # 确保类型正确
```

#### 2. **数据类型安全保证**
```python
# 自动确保关键字段类型正确
sku = StandardTestDataFactory.create_sku_data(db, product_id=123)
assert isinstance(sku.id, int)  # 保证sku_id为int类型
assert isinstance(sku.price, Decimal)  # 保证价格为Decimal类型
```

#### 3. **真实数据库环境优化**
```python
# 针对真实数据库环境的优化
def create_user_data(db: Session, **overrides) -> User:
    # 处理数据库约束
    # 处理唯一性约束
    # 处理外键关系
    # 自动提交事务
```

### 🛠️ **实战使用模式**

#### **模式1: 集成测试数据准备**
```python
# tests/integration/test_order_management.py
from tests.factories.data_factory import StandardTestDataFactory

def test_order_creation_workflow(integration_test_db):
    """测试订单创建完整流程"""
    # 准备完整的测试数据
    user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(
        integration_test_db
    )
    
    # 创建购物车数据
    cart = StandardTestDataFactory.create_shopping_cart_data(
        integration_test_db,
        user_id=user.id
    )
    
    cart_item = StandardTestDataFactory.create_cart_item_data(
        integration_test_db,
        cart_id=cart.id,
        sku_id=sku.id,
        quantity=2
    )
    
    # 测试订单服务
    order_service = OrderService(integration_test_db)
    result = order_service.create_order_from_cart(cart.id)
    
    # 验证订单创建结果
    assert result.success is True
    assert result.order.user_id == user.id
    assert len(result.order.items) == 1
    assert result.order.items[0].sku_id == sku.id
```

#### **模式2: E2E测试完整业务链**
```python
# tests/e2e/test_shopping_workflow.py
from tests.factories.data_factory import StandardTestDataFactory

def test_complete_shopping_experience(e2e_test_db):
    """测试完整购物体验流程"""
    # 创建基础数据
    user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(
        e2e_test_db
    )
    
    # 模拟用户购物流程
    shopping_service = ShoppingService(e2e_test_db)
    
    # 1. 用户浏览商品
    products = shopping_service.browse_products(category.id)
    assert product in products
    
    # 2. 添加到购物车
    cart_result = shopping_service.add_to_cart(user.id, sku.id, quantity=1)
    assert cart_result.success is True
    
    # 3. 创建订单
    order_result = shopping_service.checkout(user.id)
    assert order_result.success is True
    
    # 4. 验证库存扣减
    e2e_test_db.refresh(sku)
    assert sku.current_stock == 99  # 初始100，购买1个
```

#### **模式3: API接口集成测试**
```python
# tests/integration/test_user_api.py
from tests.factories.data_factory import StandardTestDataFactory
from fastapi.testclient import TestClient

def test_user_registration_api(integration_test_db, test_client: TestClient):
    """测试用户注册API集成"""
    # 准备测试数据
    user_data = StandardTestDataFactory.create_user_data(
        integration_test_db,
        username='testuser',
        email='test@example.com'
    )
    
    # 测试API调用
    response = test_client.post('/api/users/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'securepassword'
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data['username'] == 'newuser'
    
    # 验证数据库状态
    new_user = integration_test_db.query(User).filter_by(username='newuser').first()
    assert new_user is not None
    assert new_user.email == 'new@example.com'
```

### 🔄 **高级数据管理模式**

#### **批量数据创建**
```python
def test_bulk_operations(integration_test_db):
    """测试批量操作"""
    # 批量创建用户
    users = []
    for i in range(10):
        user = StandardTestDataFactory.create_user_data(
            integration_test_db,
            username=f'user_{i}',
            email=f'user{i}@test.com'
        )
        users.append(user)
    
    # 批量创建订单
    for user in users:
        _, _, _, _, sku = StandardTestDataFactory.create_complete_chain(integration_test_db)
        order = StandardTestDataFactory.create_order_data(
            integration_test_db,
            user_id=user.id,
            sku_id=sku.id
        )
```

#### **数据依赖管理**
```python
def test_complex_dependencies(integration_test_db):
    """测试复杂依赖关系"""
    # 创建基础数据
    user1 = StandardTestDataFactory.create_user_data(integration_test_db, username='user1')
    user2 = StandardTestDataFactory.create_user_data(integration_test_db, username='user2')
    
    # 创建共享商品
    _, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(
        integration_test_db
    )
    
    # 用户1的订单
    order1 = StandardTestDataFactory.create_order_data(
        integration_test_db,
        user_id=user1.id,
        sku_id=sku.id
    )
    
    # 用户2的订单 (使用相同SKU)
    order2 = StandardTestDataFactory.create_order_data(
        integration_test_db,
        user_id=user2.id,
        sku_id=sku.id
    )
    
    # 测试库存扣减逻辑
    inventory_service = InventoryService(integration_test_db)
    result = inventory_service.process_orders([order1, order2])
    assert result.success is True
```

## 🚀 最佳实践与进阶技巧

### 📋 **工厂选择决策树**

```
开始测试编写
     ↓
是否需要数据库持久化？
     ↓         ↓
    是         否
     ↓         ↓
是否跨模块？    使用Factory Boy
     ↓         (user_auth_factories.py)
    是
     ↓
  统一工厂
(data_factory.py)
```

### 🎯 **性能优化策略**

#### **Factory Boy优化**
```python
# ✅ 使用build()而非create()来避免数据库操作
user = UserFactory.build()  # 仅在内存中创建

# ✅ 批量创建
users = UserFactory.build_batch(10)
```

#### **统一工厂优化**
```python
# ✅ 重用基础数据
base_user, category, brand, product, _ = StandardTestDataFactory.create_complete_chain(db)

# 创建多个SKU时重用product
sku1 = StandardTestDataFactory.create_sku_data(db, product_id=product.id)
sku2 = StandardTestDataFactory.create_sku_data(db, product_id=product.id)
```

### 🔍 **调试与故障排除**

#### **常见问题诊断**
```python
# 问题1: Factory Boy数据没有保存到数据库
# 原因: Factory Boy默认不持久化数据
# 解决: 检查是否在正确的测试类型中使用

# 问题2: 统一工厂创建数据太慢
# 原因: 过度创建不必要的关联数据
# 解决: 使用更精确的工厂方法

# 问题3: 数据类型错误
# 原因: Factory Boy可能生成字符串而非整数ID
# 解决: 使用统一工厂确保类型正确
```

#### **数据验证模式**
```python
def test_data_integrity():
    """验证工厂创建数据的完整性"""
    user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(db)
    
    # 类型验证
    assert isinstance(user.id, int)
    assert isinstance(product.price, Decimal)
    
    # 关系验证
    assert product.category_id == category.id
    assert sku.product_id == product.id
    
    # 约束验证
    assert user.email is not None
    assert '@' in user.email
```

## 🔮 扩展与维护指南

### 📈 **工厂扩展原则**

1. **Factory Boy工厂扩展**：为新模块创建专用Factory Boy工厂
2. **统一工厂扩展**：为新模块添加对应的create_xxx_data方法
3. **保持一致性**：遵循现有的命名规范和接口设计
4. **文档同步**：及时更新相关文档和使用指南

### 🛠️ **未来发展规划**

```
当前状态:
├── user_auth_factories.py (Factory Boy)
└── data_factory.py (统一工厂)

未来扩展:
├── user_auth_factories.py 
├── product_catalog_factories.py (新增)
├── order_management_factories.py (新增)
├── shopping_cart_factories.py (新增)
└── data_factory.py (持续扩展)
```

### 📚 **相关资源**

- **[Factory Boy官方文档](https://factoryboy.readthedocs.io/)** - Factory Boy标准用法
- **[pytest-mock使用指南](https://pytest-mock.readthedocs.io/)** - Mock框架集成
- **[SQLAlchemy测试策略](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)** - 数据库测试最佳实践
- **[项目测试标准](../standards/testing-standards.md)** - 项目特定的测试规范

---

## 📞 技术支持

如有问题，请参考：
1. **[测试工具手册](testing-tools.md)** - 工具使用说明
2. **[factories目录README](../../tests/factories/README.md)** - 快速参考
3. **测试代码示例** - 查看现有测试代码中的使用模式