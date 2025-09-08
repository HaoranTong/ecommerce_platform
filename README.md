# 定制化电商平台

支持五常大米等农产品销售的电商平台，基于 FastAPI + SQLAlchemy + MySQL 架构。

## 🚀 快速启动

### 一键启动

```powershell
# 后台启动（推荐，避免终端被占用）
.\start.ps1

# 前台启动（开发调试时使用）
.\start.ps1 -Foreground
```

### 访问服务

启动成功后可以访问：
- **应用首页**: http://127.0.0.1:8000/
- **API 文档**: http://127.0.0.1:8000/docs  
- **ReDoc 文档**: http://127.0.0.1:8000/redoc
- **健康检查**: http://127.0.0.1:8000/api/health

### 停止服务

```powershell
# 停止 FastAPI 应用
Get-Process python | Where-Object {$_.ProcessName -eq "python"} | Stop-Process

# 停止 Docker 容器
docker-compose down
```

## 📋 手动启动步骤

如果需要手动启动或出现问题，可以按以下步骤操作：

### 1. 创建虚拟环境
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 启动 Docker 服务
```powershell
# 启动 MySQL 和 Redis
docker-compose up -d

# 等待服务就绪（约 10-15 秒）
Start-Sleep -Seconds 10
```

### 3. 设置环境变量
```powershell
$env:DATABASE_URL = "mysql+pymysql://root:rootpass@127.0.0.1:3307/ecommerce_platform"
$env:ALEMBIC_DSN = $env:DATABASE_URL
$env:REDIS_URL = "redis://127.0.0.1:6379/0"
```

### 4. 运行数据库迁移
```powershell
alembic upgrade head
```

### 5. 启动应用
```powershell
# 开发模式（热重载）
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 生产模式
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 📡 服务端点

启动成功后，可以访问以下端点：

- **应用首页**: http://127.0.0.1:8000/
- **API 文档**: http://127.0.0.1:8000/docs  
- **ReDoc 文档**: http://127.0.0.1:8000/redoc
- **健康检查**: http://127.0.0.1:8000/api/health

## 🏗️ 项目架构

### 技术栈
- **后端框架**: FastAPI + SQLAlchemy 2.x + Alembic
- **数据库**: MySQL 8.0 (Docker 容器)
- **缓存**: Redis 7 (Docker 容器)
- **API 规范**: OpenAPI 3.0
- **事件架构**: JSON Schema 事件定义

### 目录结构
```
ecommerce_platform/
├── app/                    # 应用代码
│   ├── main.py            # FastAPI 应用入口
│   ├── models.py          # SQLAlchemy 数据模型
│   ├── api/               # API 路由和 Schema
│   └── db.py              # 数据库配置
├── alembic/               # 数据库迁移
├── docs/                  # 项目文档
│   ├── openapi.yaml       # API 规范
│   ├── event-schemas/     # 事件 Schema 定义
│   ├── technical/         # 技术文档
│   └── status/            # 项目状态
├── scripts/               # 自动化脚本
├── start.ps1              # 完整启动脚本
├── quick-start.ps1        # 快速启动脚本
├── stop.ps1               # 停止服务脚本
├── status.ps1             # 状态检查脚本
└── docker-compose.yml     # Docker 容器配置
```

## 🔧 开发工具

### 启动脚本
项目提供了一个统一的启动脚本 `start.ps1`，支持两种模式：

```powershell
# 后台模式（默认，推荐）
.\start.ps1

# 前台模式（开发调试）
.\start.ps1 -Foreground
```

**后台模式特点**：
- ✅ 不占用终端，可以继续执行其他命令
- ✅ 避免复制粘贴时中断应用
- ✅ 适合演示和测试

**前台模式特点**：
- 📝 直接显示应用日志
- 🐛 便于调试
- ⚠️ 复制粘贴可能中断应用

### 常用开发命令
```powershell
# 查看容器状态
docker-compose ps

# 查看应用日志
docker-compose logs -f

# 重建容器
docker-compose down && docker-compose up -d

# 进入 MySQL 容器
docker-compose exec mysql mysql -u root -p

# 进入 Redis 容器
docker-compose exec redis redis-cli

# 检查应用状态
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health"
```

## 🐛 故障排除

### 常见问题

1. **Docker 启动失败**
   ```powershell
   # 检查 Docker Desktop 是否运行
   docker info
   
   # 手动启动 Docker Desktop
   start "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   ```

2. **端口占用**
   ```powershell
   # 检查端口占用
   netstat -ano | findstr :3307
   netstat -ano | findstr :6379
   netstat -ano | findstr :8000
   
   # 强制停止占用进程
   taskkill /PID <PID> /F
   ```

3. **数据库连接失败**
   ```powershell
   # 检查 MySQL 容器状态
   docker-compose exec mysql mysqladmin ping -u root -p
   
   # 重置数据库
   docker-compose down -v
   docker-compose up -d
   ```

4. **迁移失败**
   ```powershell
   # 检查迁移状态
   alembic current
   alembic history
   
   # 强制设置迁移版本
   alembic stamp head
   ```

### 环境要求

- **操作系统**: Windows 10/11
- **Python**: 3.11+
- **Docker**: Docker Desktop with WSL2
- **PowerShell**: 5.1+ 或 PowerShell Core 7+

```powershell
& .\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

快速烟雾测试（smoke test）：

项目包含一个简单的 PowerShell 脚本用于本地烟雾测试，位于 `scripts/smoke_test.ps1`。
用法（在 Windows PowerShell 中）:

```powershell
cd /d E:\ecommerce_platform
& .\scripts\smoke_test.ps1
```

脚本会激活本地 `.venv`（如果存在），检测或启动应用，执行一个临时用户的 POST/GET 测试，并在必要时停止服务器。建议在合并到 `main` 或每次本地集成后运行此脚本以确认主干健康。

3) 可选：如果希望在容器内以开发模式运行应用（bind-mount 代码并启用 reload），使用：

```powershell
docker-compose up --build backend
```

说明：已添加 `docker-compose.override.yml` 用于开发覆盖，包含 `backend` 服务的 bind-mount 与 reload 配置；生产环境在 CI 中可忽略该覆盖文件或使用 `docker-compose -f docker-compose.yml`。

-----------------------------
分支与本地开发规范（单人/小团队）

- 所有新功能与改动应在 feature/* 分支上进行开发与本地验证（例如 `feature/add-certificate`）。
- `dev` 与 `main` 为受保护的集成/主干分支，不应直接在其上做日常开发或启动临时建表操作。
-- 在本地调试时，请通过 Alembic 生成并应用迁移（`alembic revision --autogenerate -m "..."` + `alembic upgrade head`）。
-- 不要使用临时脚本或在运行时自动创建表来跳过迁移流程；所有 schema 变更必须通过 Alembic 管理并受版本控制。
快速烟雾测试（smoke test）：
-----------------------------

我们为单人开发场景准备了两个本地脚本，帮助你在本地完成 feature -> dev 的合并和 dev -> main 的发布。云端仅作为备份，不会自动创建 PR 或合并。

1) feature_finish.ps1 — 在 feature 分支完成一个小任务后使用

用法（在 feature 分支上执行，或者通过 -FeatureBranch 指定分支名）：

```powershell
# 当前在 feature/xxx 分支
.\scripts\feature_finish.ps1

# 或者在任何分支执行并指定要合并的 feature 分支
.\scripts\feature_finish.ps1 -FeatureBranch 'feature/xxx'
```

脚本行为（简述）：
- 自动将本地未提交的变动添加并提交（会生成一条自动提交信息）
- 将 feature 分支 push 到远端
- 在 feature 分支上运行 smoke test（`scripts/smoke_test.ps1`）——失败则中止
- 切换到 `dev`，pull origin/dev，然后 merge feature -> dev（若冲突则中止并返回 feature）
- 在 dev 上运行 smoke test（失败时会回退到 merge 前的 dev 状态并返回 feature）
- 若 dev smoke test 通过，则 push origin/dev 并结束

示例：

```powershell
git checkout feature/login-improve
# 开发完成并本地测试通过后
.\scripts\feature_finish.ps1
```

2) release_to_main.ps1 — 在准备好将 dev 发布到 main 时使用

用法（先 dry run 再真正发布）：

```powershell
# 只查看合并计划，不做实际改动
.\scripts\release_to_main.ps1 -DryRun

# 真正执行合并并发布（会在失败时回滚 main）
.\scripts\release_to_main.ps1 -RunNow
```

脚本行为（简述）：
- 检查并要求工作区干净
- 在 dev 上运行 smoke test（失败则中止）
- 切换到 main 并保存 pre-merge commit hash
- 合并 dev -> main 并 push origin/main
- 在 main 上运行 smoke test（若失败则 force-reset main 到 pre-merge 并 push --force）

注意事项：
- 脚本不会自动解决合并冲突；若遇冲突，请手动在本地解决后再重试脚本
- 这些脚本设计为本地执行（单人工作流），请在本地终端运行并观察输出

以上命令在 Windows PowerShell / PowerShell Core 下可直接复制执行。若你同意，我可以将这些变更推到 `dev`（或直接合并到 `main`）并在仓库里更新 README（我会使用 dev 推送）。

---

附注 — 端口映射与 .env 配置

本仓库的 `docker-compose.yml` 默认为 MySQL 做了宿主端口到容器端口的映射：

```
# docker-compose.yml
# services:
#   mysql:
#     ports:
#       - "3307:3306"
```

这是为了避免与宿主机上可能存在、并监听在 3306 的 MySQL 实例冲突。请在本地使用 `.env` 中的 `DATABASE_URL`（示例指向 `127.0.0.1:3307`）或在你明确知道宿主机口没有占用 3306 时手动修改 compose 的映射。
