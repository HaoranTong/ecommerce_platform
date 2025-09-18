#!/usr/bin/env pwsh
<#
.SYNOPSIS
批量修复sku_id数据类型错误脚本

.DESCRIPTION
系统性修复测试文件中的sku_id字符串使用错误，将其替换为正确的Integer ID

.PARAMETER FilePath
要修复的测试文件路径

.EXAMPLE
scripts/fix_sku_id_errors.ps1 -FilePath "tests/unit/test_models/test_inventory_models.py"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath
)

Write-Host "🔧 批量修复sku_id数据类型错误" -ForegroundColor Cyan
Write-Host "📄 处理文件: $FilePath" -ForegroundColor Gray

if (-not (Test-Path $FilePath)) {
    Write-Host "❌ 文件不存在: $FilePath" -ForegroundColor Red
    exit 1
}

# 读取文件内容
$content = Get-Content $FilePath -Raw

# 统计需要修复的错误数量
$stringIdLines = Select-String -Path $FilePath -Pattern 'sku_id\s*=\s*"[^"]*"'
Write-Host "📊 发现 $($stringIdLines.Count) 个sku_id字符串使用错误" -ForegroundColor Yellow

if ($stringIdLines.Count -eq 0) {
    Write-Host "✅ 文件中没有发现sku_id字符串使用错误" -ForegroundColor Green
    exit 0
}

# 修复步骤说明
Write-Host "🚀 开始修复过程..." -ForegroundColor Cyan

# 备份原文件
$backupPath = "$FilePath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $FilePath $backupPath
Write-Host "💾 已创建备份文件: $backupPath" -ForegroundColor Green

# 提供修复指导
Write-Host ""
Write-Host "📋 修复指导方案:" -ForegroundColor Yellow
Write-Host "1. 在每个测试方法开始添加SKU创建代码" -ForegroundColor White
Write-Host "2. 将 sku_id='STRING' 替换为 sku_id=sku.id" -ForegroundColor White
Write-Host "3. 确保导入必要的模型: Product, SKU" -ForegroundColor White
Write-Host ""

# 生成修复模板
Write-Host "📝 SKU创建代码模板:" -ForegroundColor Cyan
Write-Host @"
        # 创建产品和SKU
        from app.modules.product_catalog.models import SKU, Product
        
        product = Product(
            name="测试产品XXX",
            description="测试产品描述", 
            status="active",
            category_id=1
        )
        unit_test_db.add(product)
        unit_test_db.flush()
        
        sku = SKU(
            product_id=product.id,
            sku_code="TEST-SKU-XXX",
            price=100.0,
            cost=60.0,
            weight=1.0
        )
        unit_test_db.add(sku)
        unit_test_db.flush()
"@ -ForegroundColor Gray

Write-Host ""
Write-Host "🔄 然后将 sku_id='TEST-SKU-XXX' 替换为 sku_id=sku.id" -ForegroundColor Yellow
Write-Host ""
Write-Host "📍 需要修复的具体位置:" -ForegroundColor Cyan

# 显示每个错误的位置
$stringIdLines | ForEach-Object {
    Write-Host "   行 $($_.LineNumber): $($_.Line.Trim())" -ForegroundColor Red
}

Write-Host ""
Write-Host "✨ 修复完成后，运行以下命令验证:" -ForegroundColor Green
Write-Host "   scripts/ai-checkpoint.ps1 -CardType TEST-001 -FilePath `"$FilePath`"" -ForegroundColor Gray