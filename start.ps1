# 电商平台快速启动脚本 (后台运行版)
# 避免前台占用终端，适合调试和多任务

param(
    [switch]$Background,  # 后台运行应用
    [switch]$Foreground   # 前台运行应用(默认)
)

Write-Host "🚀 快速启动电商平台 (后台模式)..." -ForegroundColor Magenta

# 检查 Docker
Write-Host "🔍 检查 Docker 状态..." -ForegroundColor Blue
try {
    docker info 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker 未运行，请启动 Docker Desktop" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "✅ Docker 运行正常" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker 检查失败" -ForegroundColor Red
    pause
    exit 1
}

# 启动容器
Write-Host "🐳 启动 Docker 容器..." -ForegroundColor Blue
docker-compose down 2>$null
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 容器启动失败" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "✅ 容器启动成功" -ForegroundColor Green

# 等待服务就绪
Write-Host "⏳ 等待服务就绪 (15秒)..." -ForegroundColor Blue
Start-Sleep -Seconds 15

# 激活虚拟环境
Write-Host "🐍 激活虚拟环境..." -ForegroundColor Blue
& .\.venv\Scripts\Activate.ps1

# 设置环境变量
$env:DATABASE_URL = "mysql+pymysql://root:rootpass@127.0.0.1:3307/ecommerce_platform"
$env:ALEMBIC_DSN = $env:DATABASE_URL
$env:REDIS_URL = "redis://127.0.0.1:6379/0"

# 运行迁移
Write-Host "📊 运行数据库迁移..." -ForegroundColor Blue
alembic upgrade head

# 启动应用
Write-Host "🎉 启动 FastAPI 应用..." -ForegroundColor Green

if ($Background -or (-not $Foreground)) {
    # 后台模式
    Write-Host @"
========================
🔧 后台模式启动
访问地址: http://127.0.0.1:8000
API 文档: http://127.0.0.1:8000/docs

应用将在后台运行，终端可以继续使用
停止应用: Get-Process python | Where-Object {$_.ProcessName -eq "python"} | Stop-Process
或停止容器: docker-compose down
"@ -ForegroundColor Cyan

    # 启动后台任务
    $job = Start-Job -ScriptBlock {
        param($env_vars)
        
        # 设置环境变量
        foreach ($var in $env_vars.GetEnumerator()) {
            Set-Item -Path "env:$($var.Key)" -Value $var.Value
        }
        
        # 激活虚拟环境并启动应用
        Set-Location "E:\ecommerce_platform"
        & .\.venv\Scripts\Activate.ps1
        python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    } -ArgumentList @{
        DATABASE_URL = $env:DATABASE_URL
        ALEMBIC_DSN  = $env:ALEMBIC_DSN
        REDIS_URL    = $env:REDIS_URL
    }
    
    # 等待应用启动
    Start-Sleep -Seconds 5
    
    # 检查应用是否启动成功
    $retryCount = 0
    do {
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2 2>$null
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ FastAPI 应用后台启动成功！" -ForegroundColor Green
                Write-Host "📊 任务 ID: $($job.Id)" -ForegroundColor Yellow
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
            Write-Host "⚠️  应用启动检查超时，但可能仍在启动中" -ForegroundColor Yellow
            break
        }
    } while ($true)
    
    Write-Host @"

🎯 后台任务已启动，您现在可以：
  • 在浏览器访问 http://127.0.0.1:8000/docs
  • 继续在此终端执行其他命令
  • 查看任务状态: Receive-Job -Id $($job.Id) -Keep
  • 停止应用: Get-Process python | Stop-Process -Force
"@ -ForegroundColor Green

}
else {
    # 前台模式
    Write-Host @"
========================
访问地址: http://127.0.0.1:8000
API 文档: http://127.0.0.1:8000/docs

⚠️  前台模式：按 Ctrl+C 停止应用
⚠️  注意：复制粘贴内容可能会中断应用
"@ -ForegroundColor Yellow

    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}
