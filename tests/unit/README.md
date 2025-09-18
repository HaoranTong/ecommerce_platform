# 单元测试 (Unit Tests)

本目录包含所有模块的单元测试文件，专注于测试单个模块或组件的功能。

## 📁 重组后的标准化目录结构

按照 testing-standards.md 规范，测试文件已重新组织为三层结构：

### test_models/ - 模型层单元测试
- `test_inventory_models.py` - 库存管理模型测试
- `test_product_catalog_models.py` - 产品目录模型测试  
- `test_models_sqlite.py` - SQLite数据库模型测试
- `test_data_models_relationships.py` - 数据模型关系测试

### test_services/ - 服务层单元测试  
- `test_member_service.py` - 会员服务功能测试
- `test_point_service.py` - 积分服务功能测试
- `test_benefit_service.py` - 权益服务功能测试
- `test_inventory_service_simple.py` - 库存服务测试

### test_utils/ - 工具类单元测试
- (待添加工具类测试文件)

### 模块级独立测试 (根目录)
- `test_user_auth_standalone.py` - 独立用户认证测试
- `test_inventory_management_standalone.py` - 库存管理独立测试
- `test_order_management_standalone.py` - 订单管理独立测试
- `test_payment_service_standalone.py` - 支付服务独立测试
- `test_quality_control_standalone.py` - 质量控制独立测试
- `test_shopping_cart_standalone.py` - 购物车独立测试

## 测试运行方式

```bash
# 运行所有单元测试
pytest tests/unit/

# 运行特定测试文件
pytest tests/unit/test_auth.py

# 运行特定测试方法
pytest tests/unit/test_auth.py::test_specific_method -v
```

## 测试配置

所有单元测试使用内存SQLite数据库，确保测试的隔离性和速度。测试配置在 `conftest.py` 中定义。

## 新增测试指南

1. 测试文件命名：`test_[模块名].py`
2. 测试类命名：`Test[ClassName]`
3. 测试方法命名：`test_[功能描述]`
4. 使用pytest fixtures进行测试数据准备
5. 保持测试的独立性和可重复性