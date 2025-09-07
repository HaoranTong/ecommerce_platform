定制化电商平台 - Sprint0 模板

说明：该目录为 Sprint0 的 FastAPI 模板工程，用于快速搭建本地开发环境并验证最小下单/支付流程。请根据项目实施方案使用。 

包含：
- FastAPI 应用初始化
- Alembic 初始迁移（空）
- docker-compose 用于快速启动 MySQL 与 Redis
- OpenAPI 入口文件（docs/openapi.yaml）

docker-compose up -d
本地运行示例（PowerShell）：

# 创建虚拟环境并激活
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 启动 MySQL/Redis
docker-compose up -d

# 运行 Alembic 迁移
alembic upgrade head

# 运行应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

小程序开发：使用微信开发者工具，HTTP 调用需配置本地反向代理或使用云调试代理。

开发环境（PowerShell，Windows）

1) 创建并激活虚拟环境：

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

2) 安装依赖：

```powershell
pip install -r requirements.txt
```

3) 使用 `.env`：复制示例并编辑本地值：

```powershell
Copy-Item .env.example .env
# 编辑 .env 中的 DATABASE_URL / REDIS_URL 等
notepad .env
```

4) 运行应用：

```powershell
uvicorn app.main:app --reload --host $env:HOST --port $env:PORT
```

关于 direnv：当前项目默认不使用 direnv。若你的 shell 中出现 `direnv` 的提示，可以忽略该提示，或在个人 shell 配置中移除 direnv 初始化。项目推荐使用上述显式的 venv 激活与 `.env` 管理流程。

开发（建议混合模式，使用 docker 来运行数据库与缓存，应用在本机运行以便热重载）

1) 启动依赖服务（MySQL, Redis）：

```powershell
docker-compose up -d mysql redis
```

2) 在本地激活虚拟环境并运行应用（快速热重载）：

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
