# 开发环境配置指南

> 🎯 **文档目标**: 提供完整的开发环境搭建和配置指南，确保团队成员能够快速建立一致的开发环境。

## 📋 环境配置总览

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

## 🐍 Python环境配置

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

## 💻 VS Code IDE配置

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

### VS Code设置配置
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

## 🔧 代码质量工具配置

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

## 📦 Docker开发环境

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

## 🔗 Git配置

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

## 🚀 项目开发脚本

### 开发环境配置脚本 (dev_env.ps1)
**功能**: 统一配置开发环境，包括虚拟环境激活、环境变量设置、Docker服务检查等。

**使用方法**:
```powershell
# 在项目根目录执行（注意前面的点和空格）
. .\dev_env.ps1
```

**执行流程**:
1. **虚拟环境检查**: 自动检查并激活 `.venv` 虚拟环境
2. **环境变量设置**: 设置数据库连接、Redis连接等必要环境变量
3. **Docker服务检查**: 检查MySQL和Redis容器运行状态
4. **API服务检查**: 检查FastAPI服务运行状态

### 开发工具集脚本 (dev_tools.ps1)
**功能**: 提供常用的开发任务命令。

**可用命令**:
```powershell
# 检查数据库连接
.\dev_tools.ps1 check-db

# 执行数据库迁移
.\dev_tools.ps1 migrate

# 运行测试
.\dev_tools.ps1 test-cart

# 启动/停止API服务
.\dev_tools.ps1 start-api
.\dev_tools.ps1 stop-api

# 重置开发环境
.\dev_tools.ps1 reset-env
```

## 📝 环境变量配置

### .env文件模板
```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://root:rootpass@localhost:3307/ecommerce_dev
MYSQL_ROOT_PASSWORD=rootpass

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 环境标识
ENVIRONMENT=development
DEBUG=true

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=detailed
```

## 🔄 标准开发工作流程

### 每日开发启动流程
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

### 功能开发和测试流程
```powershell
# 1. 开发代码后运行测试
.\dev_tools.ps1 test-cart

# 2. 检查数据库变更
.\dev_tools.ps1 check-db

# 3. 如需重置环境
.\dev_tools.ps1 reset-env
```

### 问题排查流程
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

## 🆘 常见问题解决

### Python环境问题
```powershell
# 虚拟环境无法激活
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 依赖安装失败
python -m pip install --upgrade pip
pip install --upgrade setuptools wheel
```

### Docker问题
```powershell
# Docker Desktop未启动
# 手动启动Docker Desktop

# 容器端口冲突
docker-compose down
docker-compose up -d
```

### 数据库连接问题
```powershell
# 检查MySQL容器状态
docker ps | grep mysql

# 重启数据库服务
docker-compose restart mysql
```

---

> 📝 **维护说明**: 此文档专注于基础开发环境配置，详细的脚本使用说明请参考 [scripts-usage-manual.md](scripts-usage-manual.md)