# 集成测试 (Integration Tests)

本目录包含模块间集成测试，重点验证不同组件之间的协作和API端点功能。

## 测试分类

### API集成测试
测试各个API端点的完整功能，包括请求处理、响应格式、错误处理等。

#### 商品与分类管理
- `test_categories.py` - 商品分类API完整测试套件
- `test_products.py` - 商品管理API完整测试套件

#### 用户与购物功能  
- `test_users.py` - 用户管理API完整测试套件
- `test_shopping_cart.py` - 购物车API完整测试套件

### 业务流程集成测试
测试跨模块的完整业务流程和复杂场景。

#### 认证与权限
- `test_auth_integration.py` - 认证系统集成测试

#### 订单与库存
- `test_order_management.py` - 订单管理完整业务流程测试  
- `test_inventory_management_complete.py` - 库存管理完整业务流程测试

### 系统级测试脚本
- `test_cart_system.ps1` - PowerShell脚本，测试购物车系统端到端流程

## 测试环境

集成测试使用：
- TestClient进行HTTP请求模拟
- 真实数据库连接（测试数据库）
- 模拟外部服务依赖

## 运行方式

```bash
# 运行所有集成测试
pytest tests/integration/

# 运行API测试
pytest tests/integration/test_*.py

# 运行PowerShell测试脚本
.\tests\integration\test_cart_system.ps1

# 带详细输出运行
pytest tests/integration/ -v -s
```

## 测试数据管理

集成测试使用独立的测试数据库，每次测试运行前会：
1. 清理现有数据
2. 创建必要的测试数据
3. 执行测试用例
4. 清理测试数据

## 新增集成测试指南

1. 确定测试边界：明确涉及哪些模块
2. 准备测试环境：数据库、外部服务mock
3. 设计测试场景：正常流程、异常情况、边界条件
4. 编写测试用例：使用TestClient和fixtures
5. 验证测试结果：检查响应状态、数据一致性