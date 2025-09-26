#!/usr/bin/env pwsh
# 完全重建数据库和迁移系统

param(
    [switch]$Force   # 强制重置，不提示确认
)

Write-Host "🔥 完全重建数据库系统" -ForegroundColor Red
Write-Host "=======================" -ForegroundColor Red

if (-not $Force) {
    $confirm = Read-Host "⚠️  警告：这将删除所有数据并重建整个数据库架构！是否继续？(y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "❌ 操作已取消" -ForegroundColor Red
        exit 0
    }
}

try {
    # 1. 完全销毁并重建数据库容器
    Write-Host "🗑️  销毁数据库容器和数据..." -ForegroundColor Red
    docker-compose down -v mysql 2>$null  # -v 删除数据卷
    docker volume prune -f 2>$null  # 清理数据卷
    
    Write-Host "🆕 重新创建数据库容器..." -ForegroundColor Blue
    docker-compose up -d mysql 2>$null
    
    # 等待数据库完全启动
    Write-Host "⏳ 等待数据库完全启动 (10秒)..." -ForegroundColor Blue
    Start-Sleep -Seconds 10
    
    # 2. 备份并清理所有迁移文件
    Write-Host "🧹 清理迁移历史..." -ForegroundColor Blue
    $migrationsDir = "alembic\versions"
    $backupDir = "alembic\versions_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    
    if (Test-Path $migrationsDir) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        Copy-Item "$migrationsDir\*" $backupDir -Force
        Remove-Item "$migrationsDir\*.py" -Force
    }
    
    # 3. 重新初始化Alembic
    Write-Host "🔄 重新初始化Alembic..." -ForegroundColor Blue
    
    # 删除alembic_version表
    python -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', port=3307, user='root', password='123456', database='ecommerce_dev')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS alembic_version')
    conn.commit()
    print('✅ Alembic版本表已清理')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'⚠️  版本表清理: {e}')
" 2>$null
    
    # 4. 生成全新的初始迁移
    Write-Host "🆕 生成全新的初始迁移..." -ForegroundColor Green
    alembic revision --autogenerate -m "Initial migration with all modules" 2>$null
    
    # 5. 执行迁移
    Write-Host "⚡ 执行数据库迁移..." -ForegroundColor Green
    alembic upgrade head 2>$null
    
    # 6. 验证迁移状态
    Write-Host "✅ 验证迁移状态..." -ForegroundColor Blue
    $currentRevision = alembic current 2>$null
    
    Write-Host ""
    Write-Host "🎉 数据库重建完成！" -ForegroundColor Green
    Write-Host "📊 当前迁移版本: $($currentRevision | Select-String -Pattern '[a-f0-9]+' | ForEach-Object {$_.Matches[0].Value})" -ForegroundColor Cyan
    Write-Host "📁 旧迁移已备份到: $backupDir" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🚀 现在可以开始开发新模块了！" -ForegroundColor Magenta
    Write-Host "📋 未来添加新模块时，只需运行: alembic revision --autogenerate -m \"Add [module] tables\"" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ 重建失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 请检查Docker状态和数据库连接" -ForegroundColor Yellow
    exit 1
}
