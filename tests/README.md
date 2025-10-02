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
├── conftest.py                     # pytest全局配置 (主配置)
├── conftest_e2e.py                 # 简化测试配置 (应急备用)
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
└── _archive/                       # 测试文件存档目录
```

## 🔧 测试配置文件说明

### conftest.py (主配置文件)
- **功能**: 完整的五层测试架构支持 (710行)
- **环境感知**: 支持3种模式 (development/ci_pipeline/post_deployment)
- **数据库策略**: 5种数据库配置 (Mock/内存/文件/MySQL Docker)
- **Mock框架**: 强制使用pytest-mock
- **使用场景**: 正常开发和测试的主要配置

### conftest_e2e.py (简化配置 - 应急备用)
- **功能**: 最小化测试配置，应急隔离专用
- **设计目的**: 当主配置出现复杂依赖问题时的备用方案
- **使用场景**: 
  - 应急情况：`cp tests/conftest_e2e.py tests/conftest.py`
  - 快速验证：简化环境的开发调试
  - 故障排除：复杂环境问题的问题定位
- **注意**: 仅在应急或特殊情况使用，默认使用主配置

## 📝 详细使用示例

### 正常开发使用（推荐）
```bash
# 运行所有测试（默认使用主配置 conftest.py）
pytest

# 运行特定模块测试
pytest tests/unit/test_user_auth.py -v
pytest tests/integration/test_api.py -v
pytest tests/e2e/test_workflow.py -v
```

### 应急情况使用
```bash
# 1. 备份主配置
cp tests/conftest.py tests/conftest_backup.py

# 2. 使用简化配置
cp tests/conftest_e2e.py tests/conftest.py

# 3. 运行基础测试
pytest tests/factories/ -v
pytest tests/unit/test_models.py -v

# 4. 恢复主配置
cp tests/conftest_backup.py tests/conftest.py
```

### 快速验证使用
```bash
# 方法1：临时指定配置文件
pytest tests/unit/test_user_auth.py --confcutdir=tests -c tests/conftest_e2e.py -v

# 方法2：单独目录测试
cd tests
python -m pytest --confcutdir=. -c conftest_e2e.py unit/ -v

# 方法3：测试特定功能
pytest tests/smoke/test_basic.py -v  # 使用简化环境
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

## � 测试环境配置

### .env.testing
```bash
# 测试环境配置
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=INFO
TESTING=true

# 测试数据库（内存数据库）
DATABASE_URL=mysql+pymysql://root:testpass@mysql-test:3306/ecommerce_test
TEST_DATABASE_URL=sqlite:///./test.db  # 快速单元测试

# 测试Redis
REDIS_URL=redis://redis-test:6379/1
TEST_REDIS_URL=redis://localhost:6379/15

# 测试JWT配置（短过期时间）
JWT_SECRET_KEY=test-secret-key-for-testing-only
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 测试用户配置
TEST_USER_EMAIL=testuser@example.com
TEST_USER_PASSWORD=testpass123
TEST_ADMIN_EMAIL=admin@example.com
TEST_ADMIN_PASSWORD=adminpass123

# 测试文件配置
TEST_UPLOAD_DIR=/tmp/test_uploads/
TEST_MAX_FILE_SIZE=1048576  # 1MB for testing

# Mock服务配置（测试环境全部Mock）
MOCK_EXTERNAL_SERVICES=true
MOCK_PAYMENT_SERVICE=true
MOCK_EMAIL_SERVICE=true
MOCK_SMS_SERVICE=true

# 测试超时配置
TEST_TIMEOUT_UNIT=10
TEST_TIMEOUT_INTEGRATION=30
TEST_TIMEOUT_E2E=120
```

### CI/CD环境变量
```yaml
# GitHub Actions环境变量
env:
  DATABASE_URL: mysql+pymysql://root:testpass@127.0.0.1:3306/ecommerce_test
  REDIS_URL: redis://127.0.0.1:6379/1
  ENVIRONMENT: testing
  JWT_SECRET_KEY: test-secret-for-ci
  MOCK_EXTERNAL_SERVICES: true
```

**[CHECK:TEST-001]** 测试环境配置必须支持隔离和快速重置

## �📋 目录功能说明

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
- **`factories/`** - 测试数据工厂：统一的测试数据生成和管理
- **`_archive/`** - 存档目录：已废弃或历史测试文件的存放位置

## 📚 相关文档

- **[测试标准文档](../docs/standards/testing-standards.md)** - 完整的测试架构规范和要求
- **[测试环境配置](../docs/development/testing-environment.md)** - 测试环境搭建和配置
- **[工具脚本导航](../tools/README.md)** - 测试相关脚本使用导航
- **[测试脚本使用](../docs/development/scripts-usage-manual.md)** - 测试相关脚本的使用指南
- **[测试环境配置](../docs/development/testing-setup.md)** - 测试环境的配置和管理