# 烟雾测试目录

## 📋 目录说明

本目录包含烟雾测试(Smoke Testing)，基于环境感知的动态模块发现机制，用于快速验证系统核心功能和所有注册模块的基本可用性。

## 📁 文件结构

```
smoke/
├── README.md           # 本说明文档
├── test_basic_api.py   # API基础功能验证
├── test_health.py      # 系统健康检查
└── __pycache__/        # Python缓存目录
```

## 🎯 烟雾测试设计特色

### 🚀 动态模块发现
- **OpenAPI驱动**: 通过解析`/openapi.json`规范自动发现所有已注册模块
- **零硬编码**: 无需手动维护模块列表，新模块自动被测试
- **当前发现**: 自动测试8个业务模块（用户认证、商品管理、订单管理等）
- **路径解析**: 智能提取`/api/v1/{module-name}/`格式的API端点

### 🌍 环境感知策略
- **development**: 内存数据库 (`sqlite:///:memory:`) - 开发阶段快速验证
- **ci_pipeline**: 临时文件数据库 - CI/CD自动化测试环境
- **post_deployment**: 生产数据库连接 - 部署后验证模式

### 🔧 无业务逻辑依赖
- **纯端点验证**: 只验证API端点存在性，不涉及具体业务数据
- **404友好**: 404状态码视为正常（端点存在但无数据）
- **最小权限**: 不需要有效用户凭证或业务数据准备

## � 测试模块详述

### test_basic_api.py - API基础功能验证
**测试函数统计**: 5个测试函数

1. **test_api_health_check()** 
   - 验证: `/api/health` 端点响应 (HTTP 200)
   - 作用: 确认API服务基本可用性

2. **test_dynamic_module_endpoints()**
   - 验证: 通过OpenAPI自动发现的8个模块端点
   - 发现模块:
     ```
     ✅ inventory-management (库存管理): 14个端点
     ✅ member-system (会员系统): 17个端点  
     ✅ order-management (订单管理): 7个端点
     ✅ payment-service (支付服务): 5个端点
     ✅ product-catalog (商品管理): 7个端点
     ✅ quality-control (质量控制): 2个端点
     ✅ shopping-cart (购物车): 3个端点
     ✅ user-auth (用户认证): 8个端点
     ```
   - 验证方式: GET请求各模块根路径，预期404/405状态码

3. **test_basic_database_connectivity()**
   - 验证: 数据库基本连接性 (`SELECT 1`)
   - 环境策略: 根据烟雾测试模式选择数据库类型

4. **test_api_documentation_endpoints()** 
   - 验证: API文档端点可访问性
   - 端点: `/docs`, `/redoc`, `/openapi.json`

5. **test_critical_database_tables()**
   - 验证: 5个关键业务表存在性
   - 表清单: `users`, `roles`, `products`, `orders`, `carts`

### test_health.py - 系统健康检查
**测试函数统计**: 5个测试函数

1. **test_application_health()**
   - 检查: 应用服务健康状态
   - 端点: `/api/health`, `/` (根路径备选)
   - 容错: 200/404都视为正常

2. **test_api_documentation_access()**
   - 检查: API文档界面可访问性
   - 验证: Swagger UI (`/docs`) 和 ReDoc (`/redoc`)

3. **test_database_connection_smoke()**
   - 检查: 数据库连接响应性能
   - 验证: `SELECT datetime('now')` 时间查询

4. **test_environment_variables()**
   - 检查: 关键环境变量配置完整性
   - 变量: `DATABASE_URL`, `SECRET_KEY`, `REDIS_URL`, `ENVIRONMENT`
   - 策略: 缺失时使用默认值，不强制失败

5. **test_response_time_basic()**
   - 检查: 基础性能基准
   - 标准: 文档页面加载时间 < 5秒
   - 端点: `/docs` 页面响应时间

## 🚀 执行方法

### 推荐方式 - 环境感知执行
```powershell
# 使用烟雾测试脚本(自动环境检测和服务器管理)
.\tools\smoke_test.ps1

# 指定环境模式
$env:SMOKE_TEST_MODE = "development"
.\tools\smoke_test.ps1

# CI/CD环境
$env:SMOKE_TEST_MODE = "ci_pipeline"  
.\tools\smoke_test.ps1

# 生产环境验证
$env:SMOKE_TEST_MODE = "post_deployment"
.\tools\smoke_test.ps1
```

### 直接执行 - 需要服务器已运行
```powershell
# 执行所有烟雾测试
pytest tests/smoke/ -v -s

# 执行特定模块
pytest tests/smoke/test_basic_api.py -v
pytest tests/smoke/test_health.py -v

# 快速失败模式
pytest tests/smoke/ -x --tb=short
```

### 详细输出模式
```powershell
# 查看动态模块发现过程
pytest tests/smoke/test_basic_api.py::test_dynamic_module_endpoints -v -s

# 环境变量检查详情  
pytest tests/smoke/test_health.py::test_environment_variables -v -s
```

## ⚡ 执行标准和性能

### 性能指标
- **总执行时间**: 全部测试在90秒内完成（包含服务器启动）
- **纯测试时间**: pytest执行约1.5秒（10个测试）
- **模块发现**: 从65个API路径中发现8个模块
- **超时设置**: 每个HTTP请求3-5秒超时

### 环境适配性能
| 模式 | 数据库类型 | 启动时间 | 执行特点 |
|------|-----------|----------|----------|
| development | 内存数据库 | 5-10秒 | 最快，完整测试 |
| ci_pipeline | 临时文件 | 10-15秒 | 中等，可重现 |
| post_deployment | 生产数据库 | 2-5秒 | 最快，只读验证 |

### 稳定性保障
- **连接重试**: 网络请求支持3秒超时
- **服务检测**: 自动检测服务状态，避免重复启动
- **优雅降级**: OpenAPI失败时使用预定义模块列表
- **错误隔离**: 单个模块失败不影响其他模块测试

## 🔧 技术实现特点

### 动态发现机制
```python
# 核心发现逻辑
openapi_response = requests.get(f"{base_url}/openapi.json")
openapi_spec = openapi_response.json()
paths = openapi_spec.get("paths", {})

# 提取模块名
for path in paths:
    if path.startswith("/api/v1/"):
        module_name = path.split("/")[3]  # /api/v1/module-name/...
        discovered_modules.add(module_name)
```

### 环境感知配置
```python
# conftest.py 中的数据库配置
@pytest.fixture(scope="session")
def smoke_test_db():
    mode = os.environ.get("SMOKE_TEST_MODE", "development")
    if mode == "development":
        # 内存数据库，测试后自动清理
        yield engine_memory
    elif mode == "ci_pipeline":
        # 临时文件数据库
        yield engine_file
    else:
        # 生产数据库（只读模式）
        yield engine_production
```

### 备用机制
- **OpenAPI失败**: 使用预定义的7个核心模块列表
- **服务器无响应**: 跳过测试并提示使用完整脚本
- **数据库连接失败**: 降级为基本连接测试

## 📊 测试结果示例

### 成功执行输出
```
🔍 动态发现的模块数量: 8
📦 模块列表: ['inventory-management', 'member-system', 'order-management', 'payment-service', 'product-catalog', 'quality-control', 'shopping-cart', 'user-auth']

✅ inventory-management: 端点存在 (404)
✅ member-system: 端点存在 (404)  
✅ order-management: 端点存在 (404)
✅ payment-service: 端点存在 (404)
✅ product-catalog: 端点存在 (404)
✅ quality-control: 端点存在 (404)
✅ shopping-cart: 端点存在 (404)
✅ user-auth: 端点存在 (404)

==================== 10 passed in 1.48s =====================
```

### PowerShell脚本输出
```
🔍 检测到显式环境变量: SMOKE_TEST_MODE=development
🔧 开发模式：使用内存数据库，快速验证
✅ 数据库策略: 内存数据库 (sqlite:///:memory:)
✅ 启用自动创建数据库表: AUTO_CREATE_TABLES=1
ℹ️  检测到服务已在运行，将复用现有服务
✅ Pytest smoke tests passed
🎉 烟雾测试完成：所有测试通过
```

## 🚨 故障排除和维护

### 常见问题
1. **服务器连接失败**
   - 检查: `http://127.0.0.1:8000/api/health`
   - 解决: 使用 `.\tools\smoke_test.ps1` 自动启动服务器

2. **模块发现数量不对**
   - 检查: `http://127.0.0.1:8000/openapi.json` 可访问性
   - 原因: 可能有模块未正确注册到FastAPI应用

3. **数据库连接错误**
   - 开发模式: 自动使用内存数据库，无需配置
   - 生产模式: 检查 `DATABASE_URL` 环境变量

### 维护指南
- **新增模块**: 无需修改测试代码，自动发现
- **更新OpenAPI**: 重启服务后自动获取新规范
- **环境变量**: 通过 `test_environment_variables` 验证配置
- **性能基准**: 根据实际环境调整响应时间阈值

## 📚 相关文档和集成

### 项目文档
- **[主README](../../README.md)** - 项目总体说明
- **[开发工具](../../tools/README.md)** - 开发和测试工具说明
- **[数据库迁移](../../alembic/README.md)** - 数据库版本管理

### 测试集成
- **单元测试**: `tests/unit/` - 模块级详细测试
- **集成测试**: `tests/integration/` - 跨模块交互测试  
- **端到端测试**: `tests/e2e/` - 完整用户流程测试
- **性能测试**: `tests/performance/` - 负载和性能基准

### CI/CD集成
```yaml
# GitHub Actions 示例
- name: Smoke Tests
  run: |
    $env:SMOKE_TEST_MODE = "ci_pipeline"
    .\tools\smoke_test.ps1
```

本烟雾测试系统实现了**真正的动态化、环境感知、零维护**的API验证框架，为系统部署和持续集成提供快速可靠的质量保障。