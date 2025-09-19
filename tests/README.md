# 测试目录说明

## 📁 目录结构

```
tests/
├── README.md                       # 测试目录说明 (当前文件)
├── conftest.py                     # pytest全局配置
├── conftest_inventory.py           # 库存模块测试配置
├── conftest_standalone.py          # 独立测试配置
├── inventory_test_utils.py         # 库存测试工具
├── smoke_test.db                   # 烟雾测试数据库
├── smoke/                          # 烟雾测试目录 (快速部署验证) ✅
│   ├── test_health.py              # 系统健康检查
│   └── test_basic_api.py           # 基础API功能验证
├── unit/                           # 单元测试目录 (已完成标准化重组 ✅)
│   ├── test_models/                # 模型单元测试 (8个文件)
│   │   ├── test_inventory_models.py
│   │   ├── test_inventory_architecture.py
│   │   ├── test_product_catalog_models.py
│   │   ├── test_models_sqlite.py
│   │   ├── test_data_models_relationships.py
│   │   ├── test_user_auth.py
│   │   ├── test_user_auth_architecture.py
│   │   └── test_user_auth_complete.py
│   ├── test_services/              # 服务单元测试 (6个文件)
│   │   ├── test_member_service.py
│   │   ├── test_point_service.py
│   │   ├── test_benefit_service.py
│   │   ├── test_inventory_service_simple.py (✅ Pydantic V2已修复)
│   │   ├── test_payment_service.py
│   │   └── test_payment_service_fixed.py
│   ├── test_utils/                 # 工具单元测试 (待扩展)
│   └── [独立测试文件] (5个*_standalone.py文件)
│       ├── test_inventory_management_standalone.py
│       ├── test_order_management_standalone.py
│       ├── test_payment_service_standalone.py
│       ├── test_quality_control_standalone.py
│       ├── test_shopping_cart_standalone.py
│       └── test_user_auth_standalone.py
├── integration/                    # 集成测试目录
│   ├── test_api/                   # API集成测试
│   │   └── test_inventory_integration.py
│   ├── test_auth_integration.py
│   ├── test_cart_system.ps1
│   ├── test_categories.py
│   ├── test_inventory_api.py
│   ├── test_inventory_integration_strict.py
│   ├── test_inventory_management_complete.py
│   ├── test_order_integration.py
│   ├── test_order_integration_strict.py
│   ├── test_order_management.py
│   ├── test_products.py
│   ├── test_product_catalog.py
│   ├── test_shopping_cart.py
│   └── test_users.py
└── e2e/                           # 端到端测试目录
    └── test_product_workflow_e2e.py
```

## 🧪 测试类型说明

### 烟雾测试 (Smoke Tests)
位于 `smoke/` 目录下，快速验证系统基本功能是否正常，使用SQLite文件数据库。

| 测试文件 | 测试内容 | 覆盖范围 |
|----------|----------|----------|
| `smoke/test_health.py` | 系统健康检查 | API连通性、数据库连接、环境变量 |
| `smoke/test_basic_api.py` | 基础API验证 | 用户注册、健康检查、遗留端点 |

**执行命令:**
```powershell
# 使用pytest直接运行
pytest tests/smoke/ -v

# 使用脚本运行 (推荐)
.\scripts\smoke_test.ps1
```

### 单元测试 (Unit Tests)
位于 `unit/` 目录下，测试单个函数、类或模块的功能，使用Mock和SQLite内存数据库。

#### 模型测试
| 测试文件 | 测试内容 | 覆盖范围 |
|----------|----------|----------|
| `test_models/test_inventory_models.py` | 库存模型业务逻辑 | InventoryStock, InventoryReservation等 |
| `test_product_catalog_models.py` | 商品目录模型 | Category, Brand, Product, SKU等 |

#### 服务测试
| 测试文件 | 测试内容 | 覆盖范围 |
|----------|----------|----------|
| `test_services/test_inventory_service.py` | 库存管理服务逻辑 | InventoryService类方法 |
| `test_payment_service.py` | 支付服务逻辑 | PaymentService类方法 |

#### 认证模块测试
| 测试文件 | 测试内容 | 覆盖范围 |
|----------|----------|----------|
| `test_user_auth.py` | 核心认证功能 | 登录验证、账户锁定等 |
| `test_user_auth_architecture.py` | 认证架构合规性 | 模型关系、数据库标准 |
| `test_user_auth_complete.py` | 完整认证测试 | User, Role, Permission模型 |
| `test_user_auth_standalone.py` | 独立认证测试 | 避免循环导入的独立测试 |

## � 快速开始

**测试环境工具**: 请使用 `scripts/` 目录下的测试工具
**标准测试流程**: 请参考 [测试标准文档](../docs/standards/testing-standards.md)
**环境配置说明**: 请参考 [测试环境配置](../docs/development/testing-setup.md)

### 集成测试 (Integration Tests)
位于 `integration/` 目录下，测试多个模块间的协作和API端点功能，使用TestClient和真实数据库。

#### API集成测试
| 测试文件 | 测试内容 | 说明 |
|----------|----------|------|
| `test_categories.py` | 商品分类API完整流程 | 分类CRUD操作API测试 |
| `test_products.py` | 商品管理API完整流程 | 商品CRUD和搜索API测试 |
| `test_shopping_cart.py` | 购物车API完整流程 | 购物车操作API测试 |
| `test_users.py` | 用户管理API完整流程 | 用户注册登录API测试 |

#### 业务集成测试
| 测试文件 | 测试内容 | 说明 |
|----------|----------|------|
| `test_auth_integration.py` | 认证系统集成测试 | JWT、权限系统完整测试 |
| `test_order_management.py` | 订单管理完整业务流程 | 订单创建、状态变更等 |
| `test_inventory_management_complete.py` | 库存管理完整业务流程 | 库存操作、预留、扣减等 |

#### 系统测试脚本
| 测试文件 | 测试内容 | 说明 |
|----------|----------|------|
| `test_cart_system.ps1` | 购物车系统测试 | PowerShell脚本，端到端业务流程 |

### 端到端测试 (E2E Tests)
位于 `e2e/` 目录下，测试完整的用户场景和业务流程。

| 测试文件 | 测试内容 | 说明 |
|----------|----------|------|
| `test_product_workflow_e2e.py` | 商品管理完整工作流 | 从商品创建到销售的完整流程 |

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
