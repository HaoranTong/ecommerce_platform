# 测试环境配置指南

📝 **文档说明**：
- **内容**：详细的测试环境配置、工具使用、故障排除指南
- **使用者**：开发人员、测试人员
- **更新频率**：测试工具或环境配置变更时更新
- **关联文档**：[测试标准](../standards/testing-standards.md)、[工作流程](../standards/workflow.md)

## 🎯 测试环境架构

### 测试类型与环境配置

| 测试类型 | 数据库配置 | 隔离级别 | 执行时间 | 外部依赖 |
|---------|-----------|---------|---------|---------|
| **单元测试** | SQLite内存 | 函数级别 | 秒级 | 无 |
| **烟雾测试** | SQLite文件 | 模块级别 | 分钟级 | 无 |
| **集成测试** | MySQL Docker | 会话级别 | 分钟级 | Docker |
| **E2E测试** | MySQL Docker | 会话级别 | 分钟级 | Docker |

### 环境隔离原则
- **数据隔离**：不同测试类型使用不同数据库
- **进程隔离**：每个测试函数独立的数据库会话
- **配置隔离**：独立的测试配置文件和环境变量

## 🔧 测试工具详细使用说明

### 1. check_test_env.ps1 - 快速环境检查

#### 功能说明
30秒快速检查测试环境是否就绪，**必须在任何测试前执行**。

#### 检查项目
```powershell
✅ Python虚拟环境状态          # 验证.venv环境激活
✅ 测试依赖包完整性            # pytest, sqlalchemy, fastapi等
✅ 测试目录结构               # tests/unit/, tests/integration/等
✅ pytest配置文件            # tests/conftest.py存在性
✅ SQLite数据库连接           # 内存和文件数据库测试
✅ Docker环境 (可选)          # 集成测试需要
```

#### 使用示例
```powershell
# 基本使用
.\scripts\check_test_env.ps1

# 输出示例 (成功)
🔍 快速测试环境检查
========================================
✅ Python虚拟环境
✅ Python包: pytest
✅ Python包: sqlalchemy
✅ Python包: fastapi
✅ Python包: httpx
✅ 测试目录: tests
✅ 测试目录: tests/unit
✅ 测试目录: tests/integration
✅ 测试目录: tests/e2e
✅ pytest配置文件
✅ SQLite数据库
✅ Docker (集成测试可选)

🎉 所有检查通过！测试环境就绪。
您可以运行以下命令开始测试:
  pytest tests/unit/ -v           # 单元测试
  pytest tests/integration/ -v    # 集成测试
  pytest tests/ -v                # 全部测试
```

### 2. setup_test_env.ps1 - 标准测试流程

#### 功能说明
完整的测试环境设置、验证、执行、清理流程。

#### 参数详解
```powershell
-TestType <类型>    # unit|smoke|integration|all
-SetupOnly         # 仅设置环境，不运行测试
-SkipValidation    # 跳过环境验证 (不推荐)
```

#### 使用场景

**场景1：标准单元测试** 
```powershell
.\scripts\setup_test_env.ps1 -TestType unit

# 执行流程：
# 1. 检查虚拟环境
# 2. 运行环境验证
# 3. 设置SQLite内存数据库
# 4. 执行单元测试 (pytest tests/unit/ -v)
# 5. 生成测试报告
```

**场景2：集成测试环境准备**
```powershell
.\scripts\setup_test_env.ps1 -TestType integration -SetupOnly

# 执行流程：
# 1. 检查Docker环境
# 2. 启动MySQL测试容器
# 3. 等待数据库初始化
# 4. 验证数据库连接
# 5. 环境准备完成 (不运行测试)
```

**场景3：完整集成测试**
```powershell
.\scripts\setup_test_env.ps1 -TestType integration

# 执行流程：
# 1-5. 同上环境准备
# 6. 执行集成测试 (pytest tests/integration/ -v)
# 7. 清理Docker容器
# 8. 生成测试报告
```

**场景4：完整测试套件**
```powershell
.\scripts\setup_test_env.ps1 -TestType all

# 执行流程：
# 1. 准备所有测试环境
# 2. 依次执行：单元测试 → 集成测试 → E2E测试
# 3. 清理所有环境
# 4. 生成综合测试报告
```

### 3. validate_test_config.py - 深度配置验证

#### 功能说明
7步详细验证，深度诊断测试配置问题，用于故障排查。

#### 验证步骤
```python
1. Python环境验证       # Python版本、虚拟环境状态
2. 测试依赖包验证       # 所有必需包的安装状态
3. 应用模块导入验证     # 核心模块导入能力测试
4. 单元测试配置验证     # SQLite内存数据库功能测试
5. 烟雾测试配置验证     # SQLite文件数据库功能测试
6. 集成测试配置验证     # MySQL连接测试 (可选)
7. pytest配置验证      # pytest配置文件和目录结构
```

#### 使用示例
```powershell
python scripts/validate_test_config.py

# 输出示例 (部分)
🔍 测试环境配置验证开始
==================================================
=== Python环境验证 ===
✅ Python版本: 3.11.9
✅ 虚拟环境已激活: E:\ecommerce_platform\.venv
✅ 项目根目录: E:\ecommerce_platform

=== 测试依赖包验证 ===
✅ pytest - 已安装
✅ sqlalchemy - 已安装
✅ fastapi - 已安装

=== 单元测试配置验证 ===
✅ SQLite内存数据库连接成功
✅ 数据库会话创建成功

📊 验证结果: 7个通过, 0个失败
🎉 所有测试环境配置验证通过！可以开始运行测试。
```

## 🚨 故障排除指南

### 常见问题与解决方案

#### 问题1：虚拟环境未激活
```
❌ Python虚拟环境
   当前Python: C:\Python39\python.exe
```
**解决方案**：
```powershell
# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 验证激活
python -c "import sys; print(sys.prefix)"
```

#### 问题2：依赖包缺失
```
❌ Python包: pytest - 未安装
```
**解决方案**：
```powershell
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 或安装完整依赖
pip install -r requirements.txt
```

#### 问题3：测试目录结构问题
```
❌ 测试目录: tests/unit
```
**解决方案**：
```powershell
# 检查目录结构
ls tests/

# 创建缺失目录
mkdir tests/unit, tests/integration, tests/e2e
```

#### 问题4：Docker环境问题
```
⚠️ MySQL测试数据库不可用: Can't connect to MySQL
```
**解决方案**：
```powershell
# 检查Docker状态
docker --version

# 启动Docker Desktop
# 然后重新运行测试
.\scripts\setup_test_env.ps1 -TestType integration
```

#### 问题5：SQLAlchemy模型关系错误
```
❌ One or more mappers failed to initialize - can't proceed
```
**解决方案**：
```powershell
# 运行详细验证
python scripts/validate_test_config.py

# 检查模型导入
python -c "from app.modules.user_auth.models import User; print('OK')"

# 重新生成数据库
rm tests/smoke_test.db
.\scripts\setup_test_env.ps1 -TestType smoke
```

### 环境重置步骤

**完全重置测试环境**：
```powershell
# 第一步：清理测试数据库文件
Remove-Item tests/smoke_test.db -Force -ErrorAction SilentlyContinue

# 第二步：停止并清理Docker容器
docker stop mysql_test 2>$null
docker rm mysql_test 2>$null

# 第三步：重新验证环境
.\scripts\check_test_env.ps1

# 第四步：重新运行测试
.\scripts\setup_test_env.ps1 -TestType unit
```

## 📊 测试执行最佳实践

### 开发阶段测试策略
```powershell
# 开发过程中：频繁运行单元测试
.\scripts\setup_test_env.ps1 -TestType unit

# 功能完成后：运行集成测试
.\scripts\setup_test_env.ps1 -TestType integration

# 提交前：运行完整测试套件
.\scripts\setup_test_env.ps1 -TestType all
```

### 持续集成环境配置
```yaml
# CI/CD管道中的测试步骤
steps:
  - name: Setup Test Environment
    run: .\scripts\check_test_env.ps1
    
  - name: Run Unit Tests
    run: .\scripts\setup_test_env.ps1 -TestType unit
    
  - name: Run Integration Tests
    run: .\scripts\setup_test_env.ps1 -TestType integration
```

### 性能优化建议
1. **单元测试优先**：开发时主要运行单元测试，速度最快
2. **集成测试定期运行**：每日或每次功能完成后运行
3. **Docker容器复用**：集成测试时使用 `-SetupOnly` 准备环境，然后手动运行测试
4. **并行测试**：使用 `pytest-xdist` 进行并行测试执行

## 📚 相关文档

- [测试标准文档](../standards/testing-standards.md) - 测试规范和标准流程
- [工作流程文档](../standards/workflow.md) - 开发工作流程中的测试环节
- [MASTER文档](../../MASTER.md) - 强制性检查点和规范要求