# 测试目录说明

## 📁 目录结构

```
tests/
├── README.md                       # 测试目录说明 (当前文件)
├── conftest.py                     # pytest全局配置
├── test_users.py                   # 用户功能单元测试
├── test_products.py                # 商品功能单元测试
├── test_categories.py              # 分类功能单元测试
└── integration/                    # 集成测试目录
    └── test_cart_system.ps1        # 购物车系统集成测试脚本
```

## 🧪 测试类型说明

### 单元测试 (Unit Tests)
位于根目录下的 `test_*.py` 文件，测试单个函数或类的功能。

| 测试文件 | 测试内容 | 覆盖范围 |
|----------|----------|----------|
| `test_users.py` | 用户注册、登录、认证等功能 | `app/api/user_routes.py` |
| `test_products.py` | 商品CRUD操作、搜索等功能 | `app/api/product_routes.py` |
| `test_categories.py` | 商品分类管理功能 | `app/api/category_routes.py` |

**运行单元测试:**
```powershell
# 运行所有单元测试
pytest

# 运行特定测试文件
pytest tests/test_users.py

# 详细输出
pytest -v

# 覆盖率报告
pytest --cov=app
```

### 集成测试 (Integration Tests)
位于 `integration/` 目录下，测试多个模块间的协作和端到端功能。

| 测试文件 | 测试内容 | 说明 |
|----------|----------|------|
| `test_cart_system.ps1` | 购物车完整业务流程 | PowerShell脚本，测试从用户注册到购物车操作的完整流程 |

**运行集成测试:**
```powershell
# 方式1: 通过开发工具脚本
.\dev_tools.ps1 test-cart

# 方式2: 直接运行脚本
.\tests\integration\test_cart_system.ps1

# 方式3: 通过开发环境脚本
. .\dev_env.ps1
test-cart
```

## 🚀 测试环境配置

### 前置条件
1. **数据库服务**: MySQL和Redis服务正常运行
2. **API服务**: FastAPI应用已启动 (http://localhost:8000)
3. **测试数据**: 自动创建和清理测试数据

### 环境准备
```powershell
# 1. 启动开发环境
. .\dev_env.ps1

# 2. 检查数据库状态
.\dev_tools.ps1 check-db

# 3. 启动API服务
.\dev_tools.ps1 start-api

# 4. 运行测试
pytest  # 单元测试
.\dev_tools.ps1 test-cart  # 集成测试
```

## 📊 测试覆盖率

### 当前覆盖情况
- **用户模块**: ✅ 基础功能已覆盖
- **商品模块**: ✅ CRUD操作已覆盖  
- **分类模块**: ✅ 基础功能已覆盖
- **购物车模块**: ✅ 完整业务流程已覆盖

### 待完善测试
- **订单模块**: 📝 待添加
- **支付模块**: 📝 待添加
- **库存模块**: 📝 待添加
- **通知模块**: 📝 待添加

## 🔧 测试工具和配置

### pytest配置 (conftest.py)
- 数据库测试连接配置
- 测试数据夹具(fixtures)
- 测试环境初始化和清理

### 集成测试脚本特点
- **自动化**: 无需手动干预，自动执行完整流程
- **数据隔离**: 使用随机数据避免测试间干扰
- **错误处理**: 详细的错误信息和失败定位
- **清理机制**: 测试完成后自动清理测试数据

## 📋 测试最佳实践

### 编写测试原则
1. **独立性**: 每个测试独立运行，不依赖其他测试
2. **可重复**: 多次运行结果一致
3. **快速执行**: 单元测试应该快速完成
4. **清晰命名**: 测试名称清楚表达测试意图

### 测试数据管理
1. **使用fixtures**: 通过pytest fixtures提供测试数据
2. **数据隔离**: 每个测试使用独立的数据集
3. **清理机制**: 测试完成后清理测试数据
4. **真实场景**: 测试数据尽量模拟真实业务场景

### 集成测试建议
1. **关键路径**: 重点测试核心业务流程
2. **边界条件**: 测试异常情况和边界值
3. **性能验证**: 检查响应时间和并发能力
4. **错误恢复**: 验证错误处理和恢复机制

## 🛠️ 添加新测试

### 添加单元测试
1. 在根目录创建 `test_模块名.py` 文件
2. 导入所需的测试依赖和被测试模块
3. 编写测试函数，命名以 `test_` 开头
4. 使用assertions验证预期结果

```python
# 示例: test_new_module.py
import pytest
from app.api.new_module import some_function

def test_some_function():
    result = some_function("input")
    assert result == "expected_output"
```

### 添加集成测试
1. 在 `integration/` 目录创建测试脚本
2. 使用PowerShell或Python编写端到端测试
3. 包含完整的业务流程验证
4. 添加错误处理和清理逻辑

## 📚 相关文档

- [开发工具使用指南](../docs/development/) - 开发环境配置
- [API文档](../docs/api/) - 接口测试参考
- [架构设计](../docs/architecture/) - 系统架构理解
- [开发工作总纲](../docs/MASTER.md) - 完整开发流程
