定制化电商平台 - Sprint0 模板

说明：该目录为 Sprint0 的 FastAPI 模板工程，用于快速搭建本地开发环境并验证最小下单/支付流程。请根据项目实施方案使用。 

包含：
- FastAPI 应用初始化
- Alembic 初始迁移
- docker-compose 用于快速启动 MySQL 与 Redis
- OpenAPI 规范文件（docs/openapi.yaml）
- 事件 Schema 注册表（docs/event-schemas/）

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
