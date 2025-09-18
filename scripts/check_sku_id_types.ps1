#!/usr/bin/env pwsh
<#
.SYNOPSIS
检查所有测试文件中的sku_id数据类型使用错误

.DESCRIPTION
根据模型定义，sku_id字段必须是Integer类型，但测试中经常错误地使用字符串。
此脚本系统性地检查所有此类错误并报告位置。

.NOTES
创建原因: 防止sku_id数据类型错误反复出现
遵循MASTER文档要求的系统性问题解决方法
#>

Write-Host "🔍 系统性检查sku_id数据类型错误..." -ForegroundColor Yellow
Write-Host "=" * 50

$ErrorCount = 0
$FixedFiles = @()

# 检查模式：在测试文件中查找字符串类型的sku_id赋值
$TestFiles = Get-ChildItem -Path "tests" -Recurse -Filter "*.py"

foreach ($File in $TestFiles) {
    $Content = Get-Content $File.FullName -Raw
    $LineNumber = 1
    
    foreach ($Line in (Get-Content $File.FullName)) {
        # 检查是否有字符串类型的sku_id赋值
        if ($Line -match 'sku_id\s*=\s*["''][^"'']*["'']') {
            Write-Host "❌ 错误: $($File.FullName):$LineNumber" -ForegroundColor Red
            Write-Host "   内容: $($Line.Trim())" -ForegroundColor Red
            $ErrorCount++
        }
        
        # 检查是否有InventoryStock等模型直接使用字符串sku_id
        if ($Line -match '(InventoryStock|InventoryTransaction|InventoryReservation)\s*\(' -and 
            (Get-Content $File.FullName | Select-Object -Skip ($LineNumber-1) -First 10) -match 'sku_id\s*=\s*["'']') {
            Write-Host "⚠️  警告: $($File.FullName):$LineNumber" -ForegroundColor Yellow
            Write-Host "   可能在模型实例化中使用字符串sku_id" -ForegroundColor Yellow
        }
        
        $LineNumber++
    }
}

Write-Host "=" * 50
if ($ErrorCount -gt 0) {
    Write-Host "❌ 发现 $ErrorCount 个sku_id数据类型错误!" -ForegroundColor Red
    Write-Host "📋 所有sku_id字段必须使用整数类型，不能使用字符串!" -ForegroundColor Red
    Write-Host "💡 解决方法: 先创建SKU对象，然后使用sku.id (整数)" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "✅ 未发现sku_id数据类型错误" -ForegroundColor Green
    exit 0
}