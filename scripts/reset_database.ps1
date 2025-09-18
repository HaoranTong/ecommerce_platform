#!/usr/bin/env pwsh
# 数据库重置脚本 - 用于完全重建数据库和迁移

param(
    [switch]$Force   # 强制重置，不提示确认
)

Write-Host "🔄 数据库重置工具" -ForegroundColor Magenta
Write-Host "================" -ForegroundColor Magenta

if (-not $Force) {
    $confirm = Read-Host "⚠️  警告：这将删除所有数据！是否继续？(y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "❌ 操作已取消" -ForegroundColor Red
        exit 0
    }
}

Write-Host "🗂️  正在重置数据库..." -ForegroundColor Blue

try {
    # 1. 停止并重启数据库容器
    Write-Host "📦 重启数据库容器..." -ForegroundColor Blue
    docker-compose down mysql 2>$null
    docker-compose up -d mysql 2>$null
    
    # 等待数据库启动
    Write-Host "⏳ 等待数据库启动 (5秒)..." -ForegroundColor Blue
    Start-Sleep -Seconds 5
    
    # 2. 删除所有迁移文件（保留基础迁移）
    Write-Host "🧹 清理旧迁移文件..." -ForegroundColor Blue
    $migrationsDir = "alembic\versions"
    Get-ChildItem $migrationsDir -Filter "*.py" | Where-Object { 
        $_.Name -ne "197684180d30_create_base_tables_without_foreign_key_.py" 
    } | Remove-Item -Force
    
    # 3. 重置Alembic版本表
    Write-Host "🔄 重置迁移状态..." -ForegroundColor Blue
    python -c "
import os
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:123456@localhost:3307/ecommerce_dev'
from alembic import command
from alembic.config import Config
config = Config('alembic.ini')
command.stamp(config, 'head')
print('✅ 迁移状态已重置')
" 2>$null
    
    Write-Host "✅ 数据库重置完成！" -ForegroundColor Green
    Write-Host "📋 下一步：运行 'alembic revision --autogenerate -m \"Init all tables\"' 生成完整迁移" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ 重置失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}