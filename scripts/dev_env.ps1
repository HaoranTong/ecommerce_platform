# 开发环境统一配置脚本
# 使用方法: . .\dev_env.ps1 (注意前面的点和空格)

Write-Host "🔧 配置开发环境..." -ForegroundColor Yellow

# 1. 激活虚拟环境
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "❌ 虚拟环境未找到" -ForegroundColor Red
    exit 1
}

# 2. 设置环境变量（根据docker-compose.yml配置）
$env:DATABASE_URL = "mysql+pymysql://root:rootpass@localhost:3307/ecommerce_platform"
$env:MYSQL_ROOT_PASSWORD = "rootpass"
$env:REDIS_URL = "redis://localhost:6379"
$env:SECRET_KEY = "your-secret-key-here-change-in-production"
$env:ALGORITHM = "HS256"
$env:ACCESS_TOKEN_EXPIRE_MINUTES = "30"

Write-Host "✅ 环境变量已设置" -ForegroundColor Green

# 3. 检查Docker服务
Write-Host "🐳 检查Docker服务..." -ForegroundColor Yellow
$mysqlContainer = docker ps --filter "name=ecommerce_platform-mysql-1" --format "{{.Names}}"
$redisContainer = docker ps --filter "name=ecommerce_platform-redis-1" --format "{{.Names}}"

if (-not $mysqlContainer -or -not $redisContainer) {
    Write-Host "⚠️ Docker容器未运行，正在启动..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep 10
}

Write-Host "✅ Docker服务正常" -ForegroundColor Green

# 4. 检查API服务
Write-Host "🚀 检查API服务..." -ForegroundColor Yellow
$apiProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*uvicorn*"}

if ($apiProcess) {
    Write-Host "✅ API服务已运行 (PID: $($apiProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "⚠️ API服务未运行" -ForegroundColor Yellow
    Write-Host "启动命令: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Cyan
}

Write-Host "`n🎯 开发环境就绪！" -ForegroundColor Green
Write-Host "📋 可用命令:" -ForegroundColor Cyan
Write-Host "  - python -c '...' (直接执行Python代码)" -ForegroundColor White
Write-Host "  - alembic upgrade head (数据库迁移)" -ForegroundColor White
Write-Host "  - pytest (运行测试)" -ForegroundColor White
Write-Host "  - uvicorn app.main:app --reload (启动API服务)" -ForegroundColor White
