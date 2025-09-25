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
