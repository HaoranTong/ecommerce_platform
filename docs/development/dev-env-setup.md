# 开发环境配置指南

## 文档说明
- **内容**：本地开发环境搭建、工具配置、开发流程
- **使用者**：开发人员、新入职工程师
- **更新频率**：开发工具和流程变更时更新
- **关联文档**：[测试环境配置](test-env-setup.md)、[生产环境配置](../operations/production-env-setup.md)、[部署指南](../operations/deployment.md)

**[CHECK:DOC-001]** 开发环境配置必须支持一键启动

---

## 📋 快速开始指南

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **内存**: 8GB RAM (推荐16GB)
- **存储**: 50GB可用空间
- **网络**: 稳定的互联网连接

### 一键环境配置
```powershell
# 在项目根目录执行开发环境配置脚本
. .\dev_env.ps1

# 验证环境配置
.\dev_tools.ps1 check-env
```

**[CHECK:DEV-002]** 开发环境必须通过自动化脚本验证

---

## 🐍 Python开发环境

### 虚拟环境配置
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
pip install -r requirements-dev.txt
```

### 依赖管理
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

---

## 💻 IDE和编辑器配置

### VS Code配置

#### 推荐扩展
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

#### 工作区设置
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./.venv/tools/python.exe",
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
  "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

#### 调试配置
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Dev Server",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/.venv/tools/uvicorn.exe",
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
      "name": "Run Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v", "--cov=app"],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

#### 任务配置
```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Install Dependencies",
      "type": "shell",
      "command": "pip",
      "args": ["install", "-r", "requirements-dev.txt"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always"
      }
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "pytest",
      "args": ["tests/", "-v", "--cov=app"],
      "group": "test"
    },
    {
      "label": "Format Code",
      "type": "shell", 
      "command": "black",
      "args": ["app/", "tests/"],
      "group": "build"
    },
    {
      "label": "Start API Server",
      "type": "shell",
      "command": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "group": "build",
      "isBackground": true
    }
  ]
}
```

**[CHECK:DOC-006]** IDE配置必须包含完整的开发工具链

---

## 🐳 Docker开发环境

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
      - /app/.venv  # 防止覆盖虚拟环境
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=mysql+pymysql://root:devpass@mysql:3306/ecommerce_dev
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    depends_on:
      - mysql
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: devpass
      MYSQL_DATABASE: ecommerce_dev
      MYSQL_USER: dev
      MYSQL_PASSWORD: devpass
    ports:
      - "3307:3306"
    volumes:
      - mysql_dev_data:/var/lib/mysql
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    command: --default-authentication-plugin=mysql_native_password
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_dev_data:/data

  # 开发辅助服务
  redis-commander:
    image: rediscommander/redis-commander:latest
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      - redis

volumes:
  mysql_dev_data:
  redis_dev_data:
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements*.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-dev.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 默认命令（开发模式）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## 📋 开发环境变量配置

### .env.development
```bash
# 开发环境配置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
HOT_RELOAD=true

# 本地数据库
DATABASE_URL=mysql+pymysql://root:devpass@localhost:3307/ecommerce_dev
MYSQL_ROOT_PASSWORD=devpass
MYSQL_DATABASE=ecommerce_dev

# 本地Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# 开发JWT配置
JWT_SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24小时，方便开发

# 开发文件配置
UPLOAD_DIR=uploads/
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf

# Mock服务配置
MOCK_EXTERNAL_SERVICES=false
MOCK_PAYMENT_SERVICE=true
MOCK_EMAIL_SERVICE=true

# 开发工具配置
SHOW_DEBUG_TOOLBAR=true
ENABLE_PROFILER=true
```

### 开发环境脚本配置
```powershell
# dev_env.ps1 - 开发环境变量设置
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "mysql+pymysql://root:devpass@localhost:3307/ecommerce_dev"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:JWT_SECRET_KEY = "dev-secret-key"
$env:DEBUG = "true"
$env:LOG_LEVEL = "DEBUG"

Write-Host "✓ 开发环境变量已设置" -ForegroundColor Green
```

**[CHECK:DEV-002]** 开发环境变量必须支持快速切换和本地覆盖

---

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

### pre-commit配置
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

---

## 🔗 Git工作流配置

### Git配置
```bash
# 全局配置
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.autocrlf input
git config --global init.defaultBranch main

# 项目配置
git config core.hooksPath .githooks

# Git别名
git config alias.st status
git config alias.co checkout
git config alias.br branch  
git config alias.ci commit
git config alias.cm 'commit -m'
git config alias.lg 'log --oneline --graph --decorate --all'
```

### Git hooks配置
```bash
#!/bin/bash
# .githooks/pre-commit
echo "运行pre-commit检查..."

# 运行代码格式化
black app/ tests/
isort app/ tests/

# 运行代码检查
pylint app/
mypy app/

# 运行测试
pytest tests/ --cov=app --cov-fail-under=80

echo "Pre-commit检查完成"
```

---

## 🚀 开发脚本和工具

### 环境配置脚本 (dev_env.ps1)
**功能**: 统一配置开发环境，包括虚拟环境激活、环境变量设置、Docker服务检查

**使用方法**:
```powershell
# 在项目根目录执行（注意前面的点和空格）
. .\dev_env.ps1
```

### 开发工具脚本 (dev_tools.ps1)
**功能**: 提供常用的开发任务命令

**可用命令**:
```powershell
# 环境检查
.\dev_tools.ps1 check-env
.\dev_tools.ps1 check-db

# 服务管理
.\dev_tools.ps1 start-api
.\dev_tools.ps1 stop-api
.\dev_tools.ps1 restart-services

# 数据库管理
.\dev_tools.ps1 migrate
.\dev_tools.ps1 reset-db

# 测试执行
.\dev_tools.ps1 test
.\dev_tools.ps1 test-coverage

# 🆕 测试环境管理 (推荐使用)
.\scripts\check_test_env.ps1 -TestMode lite    # 轻量测试环境检查
.\scripts\check_test_env.ps1 -TestMode full    # 完整测试环境检查
.\scripts\setup_test_env.ps1 -TestMode lite    # 设置轻量测试环境
.\scripts\setup_test_env.ps1 -TestMode full    # 设置完整测试环境

# 代码质量
.\dev_tools.ps1 format
.\dev_tools.ps1 lint
```

---

## 🗂️ 项目结构说明

### 标准开发目录结构
```
ecommerce_platform/
├── app/                    # 应用源码
│   ├── __init__.py
│   ├── main.py            # FastAPI应用入口
│   ├── core/              # 核心配置
│   ├── modules/           # 业务模块
│   ├── shared/            # 共享组件
│   └── adapters/          # 外部适配器
├── tests/                  # 测试代码
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   ├── e2e/              # 端到端测试
│   └── fixtures/          # 测试数据
├── docs/                   # 项目文档
├── tools/               # 工具脚本
├── alembic/               # 数据库迁移
├── .vscode/               # VS Code配置
├── .env                   # 环境变量(本地)
├── .env.example          # 环境变量模板
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
├── docker-compose.dev.yml # 开发环境Docker
├── Dockerfile.dev        # 开发Dockerfile
└── pyproject.toml        # Python项目配置
```

---

## 📝 开发环境变量

### 环境变量配置
```bash
# .env (开发环境)
# 应用配置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# 数据库配置
DATABASE_URL=mysql+pymysql://root:devpass@localhost:3307/ecommerce_dev
MYSQL_ROOT_PASSWORD=devpass
MYSQL_DATABASE=ecommerce_dev

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# JWT配置
JWT_SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API配置
API_V1_STR=/api/v1
PROJECT_NAME=电商平台开发环境
VERSION=1.0.0-dev

# 文件上传配置
UPLOAD_DIR=uploads/
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif

# 开发工具配置
HOT_RELOAD=true
SHOW_DEBUG_TOOLBAR=true
```

**[CHECK:DOC-001]** 开发环境变量必须与生产环境隔离

---

## 🔧 常见问题和解决方案

### Python环境问题
```powershell
# 虚拟环境无法激活
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 依赖安装失败
python -m pip install --upgrade pip setuptools wheel
pip cache purge

# 包版本冲突
pip install --force-reinstall package_name
```

### Docker问题
```bash
# Docker Desktop未启动
# 手动启动Docker Desktop并等待完全启动

# 容器端口冲突
docker-compose down
docker-compose up -d

# 镜像构建失败
docker system prune -a
docker-compose build --no-cache
```

### 数据库连接问题
```bash
# 检查MySQL容器状态
docker ps | grep mysql

# 重置数据库
docker-compose down mysql
docker volume rm $(docker volume ls -q | grep mysql)
docker-compose up -d mysql

# 手动连接测试
mysql -h 127.0.0.1 -P 3307 -u root -pdevpass
```

### IDE配置问题
```json
// 如果Python解释器识别失败，手动指定路径
"python.defaultInterpreterPath": "./venv/tools/python.exe"

// 如果代码格式化不工作，检查扩展安装
// Ctrl+Shift+P -> Python: Select Interpreter
```

---

## 🚦 开发工作流程

### 标准开发流程
1. **环境准备**
   ```powershell
   . .\dev_env.ps1
   .\dev_tools.ps1 check-env
   ```

2. **代码开发**
   - 使用VS Code进行开发
   - 遵循代码规范和类型检查
   - 及时运行单元测试

3. **本地测试**
   ```powershell
   .\dev_tools.ps1 test
   .\dev_tools.ps1 test-coverage
   ```

4. **代码提交**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin feature/new-feature
   ```

### 调试技巧
- **API调试**: 使用VS Code的REST Client扩展
- **数据库调试**: 使用MySQL Workbench或命令行工具
- **Redis调试**: 使用Redis Commander Web界面
- **日志调试**: 查看应用日志和Docker logs

**[CHECK:DOC-003]** 开发流程必须包含完整的质量检查

---

## 🎯 性能和监控

### 本地性能监控
```python
# 开发环境性能监控
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 开发环境指标
```bash
# API响应时间测试
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# 数据库连接测试
docker exec mysql mysql -u root -pdevpass -e "SHOW PROCESSLIST;"

# Redis性能测试
docker exec redis redis-cli --latency -h localhost -p 6379
```

---

## 相关文档
- [测试环境配置](../../tests/README.md) - 测试环境搭建和配置
- [生产环境配置](../operations/production-env-setup.md) - 生产环境部署配置  
- [环境变量管理](environment-variables.md) - 环境变量详细管理
- [工具使用手册](../tools/README.md) - 开发脚本详细说明
