# 电商平台日常开发启动脚本
# 日常开发使用，假设Docker已手动启动，虚拟环境已创建

param(
    [switch]$Background   # 后台运行应用，默认前台运行
)

Write-Host "🚀 启动电商平台开发环境..." -ForegroundColor Magenta

# 检查 Docker 是否运行
Write-Host "🔍 检查 Docker 状态..." -ForegroundColor Blue
try {
    docker info 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker 未运行，请先手动启动 Docker Desktop" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Docker 运行正常" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker 检查失败，请确保 Docker Desktop 已启动" -ForegroundColor Red
    exit 1
}

# 检查必要的容器是否运行
Write-Host "🐳 检查必要容器状态..." -ForegroundColor Blue
$requiredContainers = @("mysql", "redis")
$runningContainers = docker ps --format "{{.Names}}"

foreach ($container in $requiredContainers) {
    if ($runningContainers -notcontains $container) {
        Write-Host "⚠️  容器 '$container' 未运行，正在启动..." -ForegroundColor Yellow
        docker-compose up -d
        Write-Host "⏳ 等待容器启动 (10秒)..." -ForegroundColor Blue
        Start-Sleep -Seconds 10
        break
    }
}

Write-Host "✅ 容器状态检查完成" -ForegroundColor Green

# 检查虚拟环境
Write-Host "🐍 检查虚拟环境..." -ForegroundColor Blue

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ 虚拟环境不存在！" -ForegroundColor Red
    Write-Host "请先创建虚拟环境：" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    exit 1
}

# 激活虚拟环境
if (-not $env:VIRTUAL_ENV) {
    Write-Host "🔄 激活虚拟环境..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 虚拟环境激活失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ 虚拟环境激活成功" -ForegroundColor Green
} else {
    Write-Host "✅ 虚拟环境已激活: $env:VIRTUAL_ENV" -ForegroundColor Green
}

# 检查依赖
Write-Host "📦 检查依赖..." -ForegroundColor Blue
if (Test-Path "requirements.txt") {
    # 检查核心依赖是否存在
    $corePackages = @("fastapi", "uvicorn", "sqlalchemy")
    $missingPackages = @()
    
    foreach ($package in $corePackages) {
        try {
            python -c "import $package" 2>$null
            if ($LASTEXITCODE -ne 0) {
                $missingPackages += $package
            }
        } catch {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "❌ 缺少关键依赖包: $($missingPackages -join ', ')" -ForegroundColor Red
        Write-Host "请手动安装依赖：pip install -r requirements.txt" -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "✅ 依赖已满足" -ForegroundColor Green
    }
}

# 加载环境变量
Write-Host "⚙️  加载环境变量..." -ForegroundColor Blue
if (Test-Path ".env") {
    # 读取.env文件并设置环境变量
    Get-Content ".env" | ForEach-Object {
        if ($_ -and -not $_.StartsWith("#") -and $_.Contains("=")) {
            $parts = $_ -split "=", 2
            $key = $parts[0].Trim()
            $value = $parts[1].Trim()
            Set-Item -Path "env:$key" -Value $value
        }
    }
    Write-Host "✅ 环境变量加载成功" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env文件不存在，使用默认环境变量" -ForegroundColor Yellow
    # 设置默认环境变量
    $env:DATABASE_URL = "mysql+pymysql://root:123456@localhost:3307/ecommerce_db"
    $env:ALEMBIC_DSN = $env:DATABASE_URL
    $env:REDIS_URL = "redis://localhost:6379/0"
}

# 检查是否需要数据库迁移（可选）
if ($args -contains "-migrate" -or $args -contains "--migrate") {
    Write-Host "📊 运行数据库迁移..." -ForegroundColor Blue
    alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 数据库迁移失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ 数据库迁移完成" -ForegroundColor Green
} else {
    Write-Host "ℹ️  跳过数据库迁移（使用 -migrate 参数启用）" -ForegroundColor Cyan
}

# 启动应用
if ($Background) {
    # 后台模式
    Write-Host @"
========================
🔧 后台模式启动
访问地址: http://localhost:8000
API 文档: http://localhost:8000/docs

应用将在后台运行，终端可以继续使用
停止应用: Get-Process python | Where-Object {`$_.CommandLine -like "*uvicorn*"} | Stop-Process
"@ -ForegroundColor Cyan

    Write-Host "🚀 启动后台进程..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -WindowStyle Hidden
    
    # 等待应用启动
    Start-Sleep -Seconds 3
    
    # 检查应用是否启动成功
    $retryCount = 0
    do {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 2 2>$null
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ FastAPI 应用后台启动成功！" -ForegroundColor Green
                break
            }
        }
        catch {
            Start-Sleep -Seconds 2
            $retryCount++
            Write-Host "." -NoNewline
        }
        
        if ($retryCount -ge 10) {
            Write-Host ""
            Write-Host "⚠️  应用启动检查超时，请手动访问 http://localhost:8000/docs 确认" -ForegroundColor Yellow
            break
        }
    } while ($true)

    Write-Host @"

🎯 后台任务已启动，您现在可以：
  • 在浏览器访问 http://localhost:8000/docs
  • 继续在此终端执行其他命令
  • 停止应用: Get-Process python | Where-Object {`$_.CommandLine -like "*uvicorn*"} | Stop-Process
"@ -ForegroundColor Green

} else {
    # 前台模式（默认）
    Write-Host @"
========================
🎯 前台开发模式启动
访问地址: http://localhost:8000
API 文档: http://localhost:8000/docs

⚠️  前台模式：按 Ctrl+C 停止应用
📝 代码修改会自动重载 (--reload)
"@ -ForegroundColor Yellow

    Write-Host "🎉 启动 FastAPI 应用..." -ForegroundColor Green
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}
