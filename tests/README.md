# 测试目录说明

## � 最近更新 (2025-09-25)

### 测试文件清理
- ✅ **重复文件清理**: 删除了重复的集成测试文件，保留最完整版本
- ✅ **规范化清理**: 移除不规范的PowerShell测试文件
- ✅ **文档同步**: 更新了所有相关文档和引用链接

### 清理详情
**删除的重复文件**:
- `test_shopping_cart.py` → 保留 `test_shopping_cart_complete.py`
- `test_shopping_cart_full_integration.py` → 合并到 `test_shopping_cart_integration.py`
- `test_order_integration.py` + `test_order_management.py` → 保留 `test_order_management_full_integration.py`
- `test_inventory_integration_strict.py` → 保留 `test_inventory_management_complete.py`

**移除的不规范文件**:
- `test_cart_system.ps1` - PowerShell脚本不应在Python测试目录中

## �📁 目录结构

```
tests/
├── README.md                       # 测试目录说明文档
├── conftest.py                     # pytest全局配置
├── smoke_test.db                   # 烟雾测试数据库文件
├── unit/                           # 单元测试目录 - 70%覆盖率
│   ├── test_models/                # 模型单元测试
│   ├── test_services/              # 服务单元测试
│   └── test_*_standalone.py        # 独立业务测试
├── integration/                    # 集成测试目录 - 20%覆盖率
│   ├── test_api/                   # API集成测试
│   └── test_*.py                   # 模块间集成测试
├── smoke/                          # 烟雾测试目录 - 2%覆盖率
├── e2e/                           # 端到端测试目录 - 6%覆盖率
├── performance/                    # 性能测试目录 - 1%覆盖率
├── security/                       # 安全测试目录 - 1%覆盖率
├── factories/                      # 测试数据工厂目录
└── generated/                      # 自动生成测试目录
```

## 🎯 测试架构说明

本项目采用五层测试架构，严格按照覆盖率要求分层实施：

| 测试层级 | 覆盖率占比 | 目录位置 | 主要用途 |
|----------|------------|----------|----------|
| **单元测试** | 70% | `unit/` | 模块功能验证，Mock测试 |
| **集成测试** | 20% | `integration/` | 模块间协作，API测试 |
| **端到端测试** | 6% | `e2e/` | 完整业务流程验证 |
| **烟雾测试** | 2% | `smoke/` | 系统基本功能检查 |
| **专项测试** | 2% | `performance/`, `security/` | 性能、安全测试 |

## 📋 目录功能说明

### 核心测试目录
- **`unit/`** - 单元测试：包含模型测试、服务测试和独立业务测试
- **`integration/`** - 集成测试：API集成测试和模块间协作测试
- **`smoke/`** - 烟雾测试：快速验证系统基本功能
- **`e2e/`** - 端到端测试：完整用户场景和业务流程测试

### 专项测试目录
- **`performance/`** - 性能测试：负载测试、压力测试、响应时间测试
- **`security/`** - 安全测试：SQL注入防护、XSS防护、权限验证测试

### 辅助目录
- **`factories/`** - 测试数据工厂：统一的测试数据生成和管理，支持用户、商品、库存、预占、事务等完整数据链
- **`generated/`** - 自动生成测试：工具生成的测试模板和完整测试套件

## 📚 相关文档

- **[测试标准文档](../docs/standards/testing-standards.md)** - 完整的测试架构规范和要求
- **[测试环境配置](../docs/development/testing-environment.md)** - 测试环境搭建和配置
- **[工具脚本导航](../tools/README.md)** - 测试相关脚本使用导航
- **[Generated目录管理](../docs/development/test-management.md)** - 自动生成测试管理策略