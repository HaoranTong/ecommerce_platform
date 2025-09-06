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
