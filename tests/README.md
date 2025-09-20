# 测试目录说明

## 📁 目录结构

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
- **[测试环境配置](../docs/development/testing-setup.md)** - 测试环境搭建和工具配置
- **[脚本使用手册](../docs/development/scripts-usage-manual.md)** - 测试工具和脚本使用指南
- **[Generated目录管理](../docs/development/generated-tests-management.md)** - 自动生成测试管理策略