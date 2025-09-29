# 开发测试过程问题解决方案

> 🛠️ **经验总结文档** - 收集开发测试过程中遇到的通用问题和解决方案，持续更新

## 📋 文档说明

本文档专门收集和整理在开发测试过程中遇到的**通用问题**和**最佳解决方案**，与工具脚本故障排查手册(`tools/troubleshooting.md`)不同：

- **本文档**: 开发测试过程中的业务问题、环境问题、流程问题的解决方案
- **工具故障排查**: 工具脚本执行失败的技术问题排查

## 🔧 环境配置问题

### Python虚拟环境问题
**问题**: 虚拟环境激活后仍使用系统Python
**解决方案**:
```powershell
# 1. 完全删除现有虚拟环境
Remove-Item .venv -Recurse -Force

# 2. 重新创建虚拟环境
python -m venv .venv

# 3. 激活并验证
.venv\Scripts\Activate.ps1
where python  # 确认路径指向虚拟环境
```

### Docker服务启动问题
**问题**: Docker Desktop启动失败或服务不可用
**解决方案**:
```powershell
# 1. 检查Docker服务状态
Get-Service *docker*

# 2. 重启Docker Desktop
Restart-Service -Name "com.docker.service"

# 3. 验证Docker可用性
docker --version
docker ps
```

## 🧪 测试环境问题

### 数据库连接问题
**问题**: 测试时数据库连接失败
**解决方案**:
```powershell
# 1. 检查数据库服务
docker-compose ps

# 2. 重启数据库服务
docker-compose restart mysql

# 3. 检查连接配置
echo $env:DATABASE_URL
```

### Mock数据不生效问题
**问题**: 测试中Mock数据没有按预期工作
**解决方案**:
```python
# 确保Mock在被测代码之前导入
import pytest
from unittest.mock import patch, MagicMock

@patch('module.external_service')
def test_function(mock_service):
    # Mock配置要在函数调用之前
    mock_service.return_value = expected_data
    
    # 执行测试
    result = function_under_test()
    
    # 验证Mock被调用
    mock_service.assert_called_once()
```

## 📦 依赖管理问题

### 包版本冲突问题
**问题**: pip install时出现版本冲突
**解决方案**:
```powershell
# 1. 检查冲突的包
pip check

# 2. 升级有冲突的包
pip install --upgrade package-name

# 3. 如果仍有问题，重新安装
pip uninstall package-name
pip install package-name
```

## 🔄 开发流程问题

### 代码格式化问题
**问题**: black和isort格式化结果不一致
**解决方案**:
```powershell
# 1. 配置.pre-commit-config.yaml统一格式化
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

# 2. 手动执行格式化
black . --check
isort . --profile black --check-only
```

### Git提交问题
**问题**: pre-commit钩子失败导致无法提交
**解决方案**:
```powershell
# 1. 跳过pre-commit检查（临时）
git commit -m "message" --no-verify

# 2. 修复格式问题后重新提交
pre-commit run --all-files
git add .
git commit -m "fix: 修复代码格式问题"
```

## 🚀 性能优化问题

### 测试执行缓慢
**问题**: 测试执行时间过长
**解决方案**:
```powershell
# 1. 并行执行测试
pytest -n auto  # 使用pytest-xdist插件

# 2. 只运行指定模块测试
pytest tests/unit/user_auth/ -v

# 3. 使用标记运行快速测试
pytest -m "not slow" -v
```

### 数据库测试性能
**问题**: 数据库测试创建数据慢
**解决方案**:
```python
# 使用事务回滚而非删除数据
@pytest.fixture
def db_transaction():
    with Session() as session:
        trans = session.begin()
        try:
            yield session
        finally:
            trans.rollback()

# 使用内存数据库进行单元测试
DATABASE_URL = "sqlite:///:memory:"
```

## 🔧 IDE配置问题

### VS Code Python解释器问题
**问题**: VS Code无法识别虚拟环境中的包
**解决方案**:
```powershell
# 1. 手动选择Python解释器
# Ctrl+Shift+P -> Python: Select Interpreter
# 选择 .\.venv\Scripts\python.exe

# 2. 重新加载窗口
# Ctrl+Shift+P -> Developer: Reload Window
```

### 调试配置问题
**问题**: 断点不生效或调试器无法启动
**解决方案**:
```json
// .vscode/launch.json 调试配置
{
  "name": "Debug FastAPI",
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/.venv/Scripts/uvicorn.exe",
  "args": [
    "app.main:app",
    "--reload",
    "--host", "127.0.0.1",
    "--port", "8000"
  ],
  "envFile": "${workspaceFolder}/.env",
  "console": "integratedTerminal",
  "justMyCode": false,
  "stopOnEntry": false
}
```

## 📊 测试数据问题

### Factory Boy数据生成问题
**问题**: 工厂生成的数据不符合预期
**解决方案**:
```python
# 检查工厂定义中的Faker提供商
class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker('email')
    # 确保使用正确的Faker提供商
    phone = factory.Faker('phone_number', locale='zh_CN')
```

### 测试数据清理问题
**问题**: 测试后数据残留影响其他测试
**解决方案**:
```python
# 使用pytest fixtures确保数据清理
@pytest.fixture(autouse=True)
def clean_database():
    yield
    # 测试后清理
    db.session.rollback()
    db.session.close()
```

## 🌐 网络相关问题

### API测试超时
**问题**: HTTP请求测试经常超时
**解决方案**:
```python
# 设置适当的超时和重试
import httpx

async def test_api_endpoint():
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get("http://localhost:8000/api/test")
        assert response.status_code == 200
```

### Redis连接问题
**问题**: 测试时Redis连接不稳定
**解决方案**:
```python
# 使用FakeRedis进行单元测试
import fakeredis
import pytest

@pytest.fixture
def redis_client():
    return fakeredis.FakeRedis()
```
**解决方案**:
```powershell
# 按照标准顺序执行格式化
isort .
black .
```

### Git提交前检查失败
**问题**: pre-commit hook检查失败
**解决方案**:
```powershell
# 1. 手动运行检查找出问题
.\tools\check_code_standards.ps1

# 2. 修复问题后重新提交
git add .
git commit -m "fix: 修复代码规范问题"
```

## 🚨 性能问题

### 测试执行缓慢
**问题**: 单元测试执行时间过长
**解决方案**:
1. **使用合适的测试模式**:
   ```powershell
   # 轻量模式用于快速测试
   .\tools\setup_test_env.ps1 -TestMode lite
   ```

2. **优化测试数据**:
   ```python
   # 使用更小的数据集进行测试
   @pytest.fixture
   def small_dataset():
       return create_test_data(size=10)  # 而不是1000
   ```

## 📊 数据问题

### 测试数据不一致
**问题**: 不同测试之间数据状态相互影响
**解决方案**:
```python
# 使用事务回滚确保测试隔离
@pytest.fixture
def db_session():
    transaction = connection.begin()
    yield session
    transaction.rollback()
```

## 🔍 调试问题

### 断点调试不生效
**问题**: VSCode断点不触发
**解决方案**:
1. 确保使用正确的Python解释器路径
2. 检查launch.json配置:
```json
{
    "python": "${workspaceFolder}/.venv/Scripts/python.exe"
}
```

## 💡 最佳实践总结

### 问题预防
1. **环境隔离**: 始终使用虚拟环境
2. **配置管理**: 使用环境变量管理配置
3. **数据隔离**: 测试数据与开发数据分离
4. **版本锁定**: 使用requirements.txt锁定依赖版本

### 问题定位
1. **日志分析**: 查看详细错误日志
2. **步骤重现**: 记录问题重现步骤
3. **环境检查**: 确认环境配置正确
4. **版本确认**: 检查相关组件版本

---

> 💡 **提示**: 遇到新问题时，请将解决方案添加到本文档，帮助团队积累经验