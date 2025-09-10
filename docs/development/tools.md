# 开发工具配置指南

## 文档说明
- **内容**：开发环境配置、工具链设置、IDE配置、自动化脚本使用指南
- **使用者**：开发人员、新团队成员
- **更新频率**：工具链升级或配置变更时更新
- **关联文档**：[开发工作流程](workflow.md)、[编码标准](standards.md)

---

## 开发环境总览

### 必备工具清单
```bash
# 基础开发环境
Python 3.11+           # 主要开发语言
Docker Desktop          # 容器化开发
Git                    # 版本控制
VS Code                # 推荐IDE
PowerShell 7+          # Windows终端

# Python依赖管理
pip                    # 包管理器
virtualenv/venv        # 虚拟环境

# 数据库工具
MySQL Workbench        # 数据库管理
Redis Commander        # Redis管理

# API开发工具
Postman               # API测试
Swagger UI            # API文档
```

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **内存**: 8GB RAM (推荐16GB)
- **存储**: 50GB可用空间
- **网络**: 稳定的互联网连接

## IDE配置 (VS Code)

### 推荐扩展
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.pylint",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml",
    "ms-vscode.vscode-docker",
    "ms-vscode.powershell",
    "humao.rest-client",
    "tamasfe.even-better-toml"
  ]
}
```

### VS Code设置
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  
  // 格式化设置
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=88"],
  "editor.formatOnSave": true,
  
  // 导入排序
  "python.sortImports.args": ["--profile", "black"],
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  
  // Linting设置
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.lintOnSave": true,
  
  // 类型检查
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  
  // 文件设置
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.trimFinalNewlines": true,
  
  // 终端设置
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "terminal.integrated.profiles.windows": {
    "PowerShell": {
      "source": "PowerShell",
      "icon": "terminal-powershell"
    }
  }
}
```

### 调试配置
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Dev",
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
      "justMyCode": false
    },
    {
      "name": "Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

### 任务配置
```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Install Dependencies",
      "type": "shell",
      "command": "pip",
      "args": ["install", "-r", "requirements.txt"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "pytest",
      "args": ["tests/", "-v", "--cov=app"],
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "Format Code",
      "type": "shell",
      "command": "black",
      "args": ["app/", "tests/"],
      "group": "build"
    },
    {
      "label": "Sort Imports",
      "type": "shell",
      "command": "isort",
      "args": ["app/", "tests/", "--profile", "black"],
      "group": "build"
    }
  ]
}
```

## Python环境配置

### 虚拟环境设置
```powershell
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.\.venv\Scripts\Activate.ps1

# 激活虚拟环境 (Linux/Mac)
source .venv/bin/activate

# 升级pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

### requirements文件管理
```text
# requirements.txt (生产依赖)
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pymysql==1.1.0
redis==5.0.1
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# requirements-dev.txt (开发依赖)
-r requirements.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx==0.25.2
black==23.11.0
isort==5.12.0
pylint==3.0.3
mypy==1.7.1
pre-commit==3.5.0
factory-boy==3.3.0
```

## 代码质量工具

### Black代码格式化
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
  | alembic
)/
'''
```

### isort导入排序
```toml
# pyproject.toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["app", "tests"]
skip = ["alembic"]
```

### pylint配置
```ini
# .pylintrc
[MASTER]
extension-pkg-whitelist=pydantic

[MESSAGES CONTROL]
disable=missing-docstring,
        too-few-public-methods,
        too-many-arguments,
        too-many-instance-attributes,
        import-error

[FORMAT]
max-line-length=88
```

### mypy类型检查
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

## Git配置

### Git Hook设置
```bash
# 安装pre-commit
pip install pre-commit

# 初始化pre-commit hooks
pre-commit install
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
        
  - repo: https://github.com/pycqa/pylint
    rev: v3.0.3
    hooks:
      - id: pylint
        args: ["--rcfile=.pylintrc"]
```

### Git别名配置
```bash
# ~/.gitconfig
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    ca = commit -a
    cm = commit -m
    cam = commit -am
    lg = log --oneline --graph --decorate --all
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
```

## Docker开发环境

### 开发用Docker Compose
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/.venv
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=mysql+pymysql://root:rootpass@mysql:3306/ecommerce_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mysql
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: ecommerce_dev
    ports:
      - "3307:3306"
    volumes:
      - mysql_data:/var/lib/mysql
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mysql_data:
```

### 开发Dockerfile
```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements*.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-dev.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 默认命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## 项目脚本工具

### 开发工具脚本详解

#### dev_env.ps1 - 开发环境配置脚本
**功能**: 统一配置开发环境，包括虚拟环境激活、环境变量设置、Docker服务检查和API服务状态检查。

**使用方法**:
```powershell
# 在项目根目录执行（注意前面的点和空格）
. .\dev_env.ps1
```

**执行流程**:
1. **虚拟环境检查**: 自动检查并激活 `.venv` 虚拟环境
2. **环境变量设置**: 设置数据库连接、Redis连接等必要环境变量
3. **Docker服务检查**: 检查MySQL和Redis容器运行状态，必要时自动启动
4. **API服务检查**: 检查FastAPI服务运行状态，显示进程信息

**配置项说明**:
- `DATABASE_URL`: MySQL数据库连接URL（根据docker-compose.yml配置）
- `MYSQL_ROOT_PASSWORD`: MySQL root用户密码
- `REDIS_URL`: Redis连接URL
- `SECRET_KEY`: JWT Token签名密钥
- `ALGORITHM`: JWT加密算法
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token过期时间

#### dev_tools.ps1 - 开发工具集
**功能**: 提供常用的开发任务命令，包括数据库检查、迁移、测试执行、服务管理等。

**使用方法**:
```powershell
.\dev_tools.ps1 <命令>
```

**可用命令详解**:

```powershell
# 检查数据库连接
.\dev_tools.ps1 check-db
# 执行：连接数据库并显示Product表的字段结构，验证数据库迁移是否成功

# 执行数据库迁移
.\dev_tools.ps1 migrate
# 执行：运行Alembic数据库迁移到最新版本

# 运行购物车测试
.\dev_tools.ps1 test-cart
# 执行：运行完整的购物车功能测试套件，验证所有购物车API功能

# 启动API服务
.\dev_tools.ps1 start-api
# 执行：启动FastAPI开发服务器，自动检查已有服务，提供重启选项，使用热重载

# 停止API服务
.\dev_tools.ps1 stop-api
# 执行：停止所有运行中的FastAPI服务进程

# 重置开发环境
.\dev_tools.ps1 reset-env
# 执行：完整重置开发环境，停止API服务，重启Docker容器，重新加载环境配置
```

#### test_cart_system.ps1 - 购物车测试脚本
**功能**: 完整的购物车系统端到端测试，覆盖所有购物车相关API功能。

**测试覆盖范围**:
1. 用户注册和登录
2. 获取空购物车状态
3. 获取可用商品列表
4. 添加商品到购物车
5. 再次添加相同商品（数量累加）
6. 获取购物车详情
7. 更新购物车商品数量
8. 获取购物车统计
9. 移除购物车商品
10. 验证购物车状态
11. 测试清空购物车功能
12. 测试边界情况（库存不足、无效商品等）

**使用方法**:
```powershell
# 直接执行
.\test_cart_system.ps1

# 或通过开发工具执行
.\dev_tools.ps1 test-cart
```

### 标准开发工作流程

#### 每日开发启动流程
```powershell
# 1. 配置开发环境
. .\dev_env.ps1

# 2. 检查数据库状态
.\dev_tools.ps1 check-db

# 3. 如需要，执行数据库迁移
.\dev_tools.ps1 migrate

# 4. 启动API服务（如未运行）
.\dev_tools.ps1 start-api
```

#### 功能开发和测试流程
```powershell
# 1. 开发代码后测试购物车功能
.\dev_tools.ps1 test-cart

# 2. 检查数据库变更
.\dev_tools.ps1 check-db

# 3. 如需重置环境
.\dev_tools.ps1 reset-env
```

#### 问题排查流程
```powershell
# 1. 重置环境
.\dev_tools.ps1 reset-env

# 2. 重新配置
. .\dev_env.ps1

# 3. 检查数据库连接
.\dev_tools.ps1 check-db

# 4. 重新测试
.\dev_tools.ps1 test-cart
```

### 环境配置脚本
```powershell
# dev_env.ps1 详细功能

# 1. 虚拟环境检查和激活
if (-not (Test-Path ".venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
}

if ($env:VIRTUAL_ENV -eq $null) {
    Write-Host "激活虚拟环境..." -ForegroundColor Green
    & .\.venv\Scripts\Activate.ps1
}

# 2. 依赖检查和安装
$requirements_hash = Get-FileHash requirements.txt -Algorithm MD5
$installed_hash_file = ".venv\requirements.hash"

if (-not (Test-Path $installed_hash_file) -or 
    (Get-Content $installed_hash_file) -ne $requirements_hash.Hash) {
    Write-Host "安装/更新依赖..." -ForegroundColor Yellow
    pip install -r requirements.txt
    $requirements_hash.Hash | Out-File $installed_hash_file
}

# 3. 环境变量设置
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            Set-Item -Path "env:$($Matches[1])" -Value $Matches[2]
        }
    }
    Write-Host "环境变量已加载" -ForegroundColor Green
}

# 4. Docker服务检查
$mysql_running = docker ps --filter "name=mysql" --filter "status=running" -q
$redis_running = docker ps --filter "name=redis" --filter "status=running" -q

if (-not $mysql_running -or -not $redis_running) {
    Write-Host "启动Docker服务..." -ForegroundColor Yellow
    docker-compose up -d mysql redis
    Start-Sleep 10
}
```

## 自动化脚本

### 功能完成脚本
```powershell
# scripts/feature_finish.ps1 流程

param(
    [string]$FeatureBranch = "",
    [switch]$SkipTests = $false
)

# 1. 分支检查
if ($FeatureBranch -eq "") {
    $current_branch = git branch --show-current
    if ($current_branch -notmatch "^feature/") {
        Write-Error "当前不在feature分支"
        exit 1
    }
    $FeatureBranch = $current_branch
}

# 2. 代码提交
git add .
$commit_message = Read-Host "请输入提交信息"
git commit -m $commit_message

# 3. 推送到远程
git push origin $FeatureBranch

# 4. 运行测试
if (-not $SkipTests) {
    Write-Host "运行烟雾测试..." -ForegroundColor Yellow
    & .\scripts\smoke_test.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "测试失败，请修复后重试"
        exit 1
    }
}

# 5. 合并到dev分支
git checkout dev
git pull origin dev
git merge $FeatureBranch

# 6. 推送dev分支
git push origin dev

Write-Host "功能开发完成！" -ForegroundColor Green
```

### 烟雾测试脚本
```powershell
# scripts/smoke_test.ps1 详细实现

# 1. 环境检查
& .\dev_env.ps1

# 2. 服务健康检查
$health_url = "http://127.0.0.1:8000/api/health"
try {
    $response = Invoke-RestMethod -Uri $health_url -Method GET
    if ($response.status -ne "healthy") {
        throw "服务不健康"
    }
    Write-Host "✓ 服务健康检查通过" -ForegroundColor Green
} catch {
    Write-Error "✗ 服务健康检查失败: $_"
    exit 1
}

# 3. 数据库连接测试
try {
    $db_test = & python -c "
from app.database import engine
try:
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('DATABASE_OK')
except Exception as e:
    print(f'DATABASE_ERROR: {e}')
    exit(1)
"
    if ($db_test -match "DATABASE_OK") {
        Write-Host "✓ 数据库连接正常" -ForegroundColor Green
    } else {
        throw $db_test
    }
} catch {
    Write-Error "✗ 数据库连接失败: $_"
    exit 1
}

# 4. 核心API测试
$api_tests = @(
    @{url="/api/v1/users"; method="GET"; description="用户列表"},
    @{url="/api/v1/products"; method="GET"; description="商品列表"},
    @{url="/api/v1/categories"; method="GET"; description="分类列表"}
)

foreach ($test in $api_tests) {
    try {
        $url = "http://127.0.0.1:8000" + $test.url
        $response = Invoke-RestMethod -Uri $url -Method $test.method
        Write-Host "✓ $($test.description) 测试通过" -ForegroundColor Green
    } catch {
        Write-Error "✗ $($test.description) 测试失败: $_"
        exit 1
    }
}

Write-Host "🎉 所有烟雾测试通过！" -ForegroundColor Green
```

## 数据库管理工具

### Alembic配置
```python
# alembic/env.py 关键配置
import os
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.models import Base  # 导入所有模型

# 配置数据库URL
config = context.config
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 比较字段类型变更
            compare_server_default=True,  # 比较默认值变更
        )

        with context.begin_transaction():
            context.run_migrations()
```

### 数据库管理脚本
```powershell
# scripts/db_manage.ps1
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("create", "migrate", "upgrade", "downgrade", "current", "history", "reset")]
    [string]$Action,
    
    [string]$Message = "",
    [string]$Revision = "head"
)

switch ($Action) {
    "create" {
        if ($Message -eq "") {
            $Message = Read-Host "请输入迁移描述"
        }
        alembic revision --autogenerate -m $Message
    }
    "migrate" {
        alembic upgrade head
    }
    "upgrade" {
        alembic upgrade $Revision
    }
    "downgrade" {
        alembic downgrade $Revision
    }
    "current" {
        alembic current
    }
    "history" {
        alembic history --verbose
    }
    "reset" {
        Write-Warning "这将清空数据库！"
        $confirm = Read-Host "确认重置？(yes/no)"
        if ($confirm -eq "yes") {
            alembic downgrade base
            alembic upgrade head
        }
    }
}
```

## 测试工具配置

### pytest配置
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80

markers =
    unit: 单元测试
    integration: 集成测试
    e2e: 端到端测试
    slow: 慢速测试
    skip_ci: CI中跳过的测试
```

### 测试运行脚本
```powershell
# scripts/run_tests.ps1
param(
    [string]$TestType = "all",
    [string]$Module = "",
    [switch]$Coverage = $true,
    [switch]$Parallel = $false
)

# 基础命令
$pytest_cmd = "pytest"

# 根据测试类型添加参数
switch ($TestType) {
    "unit" { $pytest_cmd += " -m unit" }
    "integration" { $pytest_cmd += " -m integration" }
    "e2e" { $pytest_cmd += " -m e2e" }
    "fast" { $pytest_cmd += " -m 'not slow'" }
}

# 指定模块
if ($Module -ne "") {
    $pytest_cmd += " tests/test_$Module.py"
}

# 覆盖率
if ($Coverage) {
    $pytest_cmd += " --cov=app --cov-report=html"
}

# 并行执行
if ($Parallel) {
    $pytest_cmd += " -n auto"
}

# 执行测试
Write-Host "执行命令: $pytest_cmd" -ForegroundColor Yellow
Invoke-Expression $pytest_cmd
```

## API开发工具

### REST Client配置
```http
# api_tests.http
@baseUrl = http://127.0.0.1:8000
@token = your_jwt_token_here

### 健康检查
GET {{baseUrl}}/api/health

### 用户注册
POST {{baseUrl}}/api/v1/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "username": "testuser",
  "password": "password123"
}

### 用户登录
POST {{baseUrl}}/api/v1/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}

### 获取用户信息
GET {{baseUrl}}/api/v1/users/me
Authorization: Bearer {{token}}

### 创建商品
POST {{baseUrl}}/api/v1/products
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "name": "测试商品",
  "description": "这是一个测试商品",
  "price": 99.99,
  "category_id": 1
}
```

## 日志和监控工具

### 日志配置
```python
# app/core/logging.py
import logging
import sys
from pathlib import Path

def setup_logging():
    """配置应用日志"""
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

## 故障排除和调试

### 常见问题解决
```powershell
# 1. 虚拟环境问题
# 删除并重建虚拟环境
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Docker问题
# 重置Docker环境
docker-compose down -v
docker-compose up -d

# 3. 数据库连接问题
# 检查MySQL容器
docker-compose logs mysql

# 重置数据库
docker-compose down -v
docker volume prune -f
docker-compose up -d mysql

# 4. 端口占用问题
# 查找占用端口的进程
netstat -ano | findstr :8000
netstat -ano | findstr :3307

# 停止占用进程
taskkill /PID <PID> /F

# 5. Python包问题
# 清理pip缓存
pip cache purge

# 强制重装包
pip install --force-reinstall -r requirements.txt
```

### 调试技巧
```python
# 1. 使用pdb调试
import pdb; pdb.set_trace()

# 2. 使用logging调试
import logging
logger = logging.getLogger(__name__)
logger.debug("调试信息: %s", variable)

# 3. 使用rich打印调试信息
from rich import print
from rich.console import Console
console = Console()
console.print(data, style="bold red")

# 4. 性能分析
import cProfile
import pstats

def profile_function():
    cProfile.run('your_function()', 'profile_stats')
    stats = pstats.Stats('profile_stats')
    stats.sort_stats('cumulative').print_stats(10)
```

---

## 相关文档
- [开发工作流程](workflow.md) - 开发流程和工具使用
- [编码标准](standards.md) - 代码质量要求
- [测试策略](testing.md) - 测试工具和配置
- [MASTER工作流程](../MASTER.md) - 开发检查点要求
