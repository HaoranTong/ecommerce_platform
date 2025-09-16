# 单元测试 (Unit Tests)

本目录包含所有模块的单元测试文件，专注于测试单个模块或组件的功能。

## 测试覆盖范围

### 认证与用户管理
- `test_auth.py` - 认证系统核心功能测试
- `test_user_auth.py` - 用户认证流程测试
- `test_user_auth_complete.py` - 用户认证完整测试套件

### 数据模型与关系
- `test_data_models_relationships.py` - 数据模型关系测试
- `test_models_sqlite.py` - SQLite数据库模型测试

### 核心服务
- `test_inventory_api.py` - 库存API功能测试
- `test_payment_service.py` - 支付服务功能测试
- `test_notification_service.py` - 通知服务功能测试

### 专项功能测试
- `test_user_auth_architecture.py` - 用户认证架构测试
- `test_user_auth_standalone.py` - 独立用户认证测试
- `test_security_logging.py` - 安全日志功能测试

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