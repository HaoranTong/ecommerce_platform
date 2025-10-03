<#
.SYNOPSIS
开发工具集合脚本 - 日常开发辅助命令集

.DESCRIPTION
提供常用的开发辅助命令，简化日常开发操作：
- 数据库状态检查和管理
- API服务启动和停止
- 测试环境重置
- 数据库迁移执行

所有命令都使用统一的环境配置(dev_env.ps1)，确保环境一致性。

支持的命令：
- check-db: 检查数据库表结构和连接状态
- migrate: 执行数据库迁移
- test-cart: 测试购物车功能
- start-api: 启动API服务器
- stop-api: 停止API服务器  
- reset-env: 重置开发环境

.PARAMETER Command
必需参数。要执行的开发命令，支持以下选项：
- check-db: 检查数据库表结构
- migrate: 执行数据库迁移
- test-cart: 测试购物车功能
- start-api: 启动API服务
- stop-api: 停止API服务
- reset-env: 重置开发环境

.EXAMPLE
.\tools\dev_tools.ps1 check-db
检查数据库表结构和字段信息

.EXAMPLE
.\tools\dev_tools.ps1 migrate
执行数据库迁移操作

.EXAMPLE
.\tools\dev_tools.ps1 start-api
启动FastAPI开发服务器

.NOTES
Author: AI Development Team
Created: 2025-09-30
Version: 1.0
Dependencies: dev_env.ps1, Python 3.8+, FastAPI
Environment: 需要配置dev_env.ps1环境文件
#>

# 开发工具集合脚本
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('check-db', 'migrate', 'test-cart', 'start-api', 'stop-api', 'reset-env')]
    [string]$Command
)

# 导入环境配置
. .\dev_env.ps1

switch ($Command) {
    'check-db' {
        Write-Host "📊 检查数据库表结构..." -ForegroundColor Yellow
        python -c "
from app.models import Product
from app.database import engine
from sqlalchemy import inspect

try:
    inspector = inspect(engine)
    if 'products' in inspector.get_table_names():
        columns = inspector.get_columns('products')
        print('✅ Product表字段:')
        for col in columns:
            print('  - ' + col['name'] + ': ' + str(col['type']))
    else:
        print('❌ products表不存在')
except Exception as e:
    print('❌ 数据库连接失败: ' + str(e))
"
    }
    
    'migrate' {
        Write-Host "🔄 执行数据库迁移..." -ForegroundColor Yellow
        alembic upgrade head
    }
    
    'test-cart' {
        Write-Host "🛒 执行购物车测试..." -ForegroundColor Yellow
        Write-Host "⚠️ 购物车PowerShell测试已移除，使用Python测试替代:" -ForegroundColor Yellow
        Write-Host "   pytest tests/integration/test_shopping_cart_complete.py" -ForegroundColor Cyan
        pytest tests/integration/test_shopping_cart_complete.py
    }
    
    'start-api' {
        Write-Host "🚀 启动API服务..." -ForegroundColor Yellow
        $existingProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*uvicorn*"}
        if ($existingProcess) {
            Write-Host "⚠️ API服务已在运行 (PID: $($existingProcess.Id))" -ForegroundColor Yellow
            Write-Host "是否要重启? (y/N):" -NoNewline
            $choice = Read-Host
            if ($choice -eq 'y' -or $choice -eq 'Y') {
                Stop-Process -Id $existingProcess.Id -Force
                Start-Sleep 2
                uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
            }
        } else {
            uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        }
    }
    
    'stop-api' {
        Write-Host "🛑 停止API服务..." -ForegroundColor Yellow
        $processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*uvicorn*"}
        if ($processes) {
            $processes | Stop-Process -Force
            Write-Host "✅ API服务已停止" -ForegroundColor Green
        } else {
            Write-Host "ℹ️ 没有运行的API服务" -ForegroundColor Blue
        }
    }
    
    'reset-env' {
        Write-Host "🔄 重置开发环境..." -ForegroundColor Yellow
        
        # 停止API服务
        Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*uvicorn*"} | Stop-Process -Force
        
        # 重启Docker容器
        docker-compose down
        docker-compose up -d
        Start-Sleep 10
        
        # 重新加载环境
        . .\dev_env.ps1
        
        Write-Host "✅ 环境重置完成" -ForegroundColor Green
    }
}
