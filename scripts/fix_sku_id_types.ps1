#!/usr/bin/env pwsh
<#
.SYNOPSIS
自动修复所有测试文件中的sku_id数据类型错误

.DESCRIPTION
系统性地修复所有将字符串用作sku_id的错误，改为正确的整数类型。
这是一次性彻底解决问题的脚本，防止反复出现同样错误。

.NOTES
创建原因: 彻底解决sku_id数据类型错误的系统性问题
遵循MASTER文档要求的一次性彻底修复方法
#>

Write-Host "🔧 开始系统性修复所有sku_id数据类型错误..." -ForegroundColor Green
Write-Host "=" * 60

$FixedCount = 0
$BackupDir = "backup_before_sku_fix_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# 创建备份目录
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
Write-Host "📁 备份目录: $BackupDir" -ForegroundColor Yellow

# 定义需要修复的文件和对应的修复模式
$FilesToFix = @(
    "tests/integration/test_api/test_inventory_integration.py",
    "tests/unit/test_models/test_inventory_models.py",
    "tests/unit/test_inventory_management_standalone.py",
    "tests/unit/test_order_management_standalone.py", 
    "tests/unit/test_shopping_cart_standalone.py",
    "tests/integration/test_inventory_management_complete.py"
)

foreach ($FilePath in $FilesToFix) {
    if (Test-Path $FilePath) {
        Write-Host "🔨 修复文件: $FilePath" -ForegroundColor Cyan
        
        # 备份原文件
        $BackupPath = Join-Path $BackupDir (Split-Path $FilePath -Leaf)
        Copy-Item $FilePath $BackupPath
        
        $Content = Get-Content $FilePath -Raw
        $OriginalContent = $Content
        
        # 模式1: 直接在InventoryStock等模型中使用字符串sku_id
        # 修复为: 先创建SKU，再使用sku.id
        $Content = $Content -replace 
            '(\s+)(\w+)\s*=\s*InventoryStock\s*\(\s*\n(\s*)sku_id\s*=\s*["\']([^"\']+)["\']',
            '$1# 先创建SKU对象$1sku = SKU(sku_code="$4", product_id=1, price=100.0, is_active=True)$1session.add(sku)$1session.flush()$1$1$2 = InventoryStock($3sku_id=sku.id'
        
        # 模式2: 简单的sku_id字符串赋值修复为数字ID
        $Content = $Content -replace 'sku_id\s*=\s*["\']([^"\']+)["\']', 'sku_id=1  # Fixed: was string "$1", now integer'
        
        # 模式3: 在mock对象中的字符串sku_id
        $Content = $Content -replace '(\w+)\.sku_id\s*=\s*["\']([^"\']+)["\']', '$1.sku_id = 1  # Fixed: was string "$2", now integer'
        
        if ($Content -ne $OriginalContent) {
            Set-Content -Path $FilePath -Value $Content -Encoding UTF8
            $FixedCount++
            Write-Host "  ✅ 已修复" -ForegroundColor Green
        } else {
            Write-Host "  ⏭️ 无需修复" -ForegroundColor Gray
        }
    }
}

Write-Host "=" * 60
Write-Host "🎉 修复完成! 共修复了 $FixedCount 个文件" -ForegroundColor Green
Write-Host "📋 备份位置: $BackupDir" -ForegroundColor Yellow
Write-Host "🔍 请运行检查脚本验证修复结果: scripts/check_sku_id_types.ps1" -ForegroundColor Cyan