#!/usr/bin/env pwsh
<#
.SYNOPSIS
代码规范完整性检查工具

.DESCRIPTION
检查Python和PowerShell文件的头部说明、函数文档、代码注释是否符合标准格式要求。
确保代码可读性和维护性达到项目标准。

.PARAMETER FilePath
要检查的具体文件路径

.PARAMETER ModulePath
要检查的模块目录路径

.PARAMETER Standard
检查标准级别: basic, standard, strict

.PARAMETER Fix
自动修复可以自动处理的规范问题

.EXAMPLE
tools/check_code_standards.ps1 -FilePath app/modules/user_auth/models.py
tools/check_code_standards.ps1 -ModulePath app/modules/inventory_management
tools/check_code_standards.ps1 -Standard strict -ModulePath app/core

.NOTES
Author: AI Development Team  
Created: 2025-09-18
Version: 1.0
Dependencies: PowerShell 5.0+, Python AST (for Python file analysis)
#>

param(
    [string]$FilePath = "",
    [string]$ModulePath = "",
    [ValidateSet("basic", "standard", "strict")]
    [string]$Standard = "standard",
    [switch]$Fix = $false
)

Write-Host "🔍 代码规范检查工具" -ForegroundColor Cyan
Write-Host "检查标准: $Standard" -ForegroundColor Gray
Write-Host "=" * 60

# 定义检查标准
$Standards = @{
    "basic" = @{
        "DocCoverageMin" = 60
        "CommentRatioMin" = 10
        "RequireFileHeader" = $false
    }
    "standard" = @{
        "DocCoverageMin" = 80
        "CommentRatioMin" = 15
        "RequireFileHeader" = $true
    }
    "strict" = @{
        "DocCoverageMin" = 90
        "CommentRatioMin" = 20
        "RequireFileHeader" = $true
    }
}

$CurrentStandard = $Standards[$Standard]

# 获取要检查的文件列表
$CheckFiles = @()

if ($FilePath) {
    if (Test-Path $FilePath) {
        $CheckFiles += Get-Item $FilePath
    } else {
        Write-Host "❌ 文件不存在: $FilePath" -ForegroundColor Red
        exit 1
    }
} elseif ($ModulePath) {
    if (Test-Path $ModulePath) {
        $CheckFiles = Get-ChildItem $ModulePath -Filter "*.py" -Recurse
        $CheckFiles += Get-ChildItem $ModulePath -Filter "*.ps1" -Recurse
    } else {
        Write-Host "❌ 模块目录不存在: $ModulePath" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ 需要指定 -FilePath 或 -ModulePath 参数" -ForegroundColor Red
    exit 1
}

Write-Host "📊 检查文件数量: $($CheckFiles.Count)" -ForegroundColor Gray

# 初始化统计
$TotalIssues = 0
$ProcessedFiles = 0

# 检查每个文件
foreach ($File in $CheckFiles) {
    $ProcessedFiles++
    Write-Host "`n📄 检查文件 [$ProcessedFiles/$($CheckFiles.Count)]: $($File.Name)" -ForegroundColor Yellow
    
    $Content = Get-Content $File.FullName -Raw
    $FileIssues = 0
    
    # 检查文件头部文档
    if ($CurrentStandard.RequireFileHeader) {
        $HasHeader = $false
        
        if ($File.Extension -eq ".py") {
            if ($Content -match '^\s*"""[\s\S]*?"""' -or $Content -match "^\s*'''[\s\S]*?'''") {
                Write-Host "   ✅ Python文件头部docstring存在" -ForegroundColor Green
                $HasHeader = $true
            } else {
                Write-Host "   ❌ 缺少Python文件头部docstring" -ForegroundColor Red
                $FileIssues++
            }
        } elseif ($File.Extension -eq ".ps1") {
            if ($Content -match '<#[\s\S]*?#>') {
                Write-Host "   ✅ PowerShell文件头部注释存在" -ForegroundColor Green
                $HasHeader = $true
            } else {
                Write-Host "   ❌ 缺少PowerShell文件头部注释块" -ForegroundColor Red
                $FileIssues++
            }
        }
        
        # 自动修复文件头部
        if ($Fix -and -not $HasHeader) {
            Write-Host "   🔧 自动添加文件头部..." -ForegroundColor Cyan
            
            $HeaderTemplate = ""
            if ($File.Extension -eq ".py") {
                $HeaderTemplate = @"
"""
$($File.BaseName)模块

功能说明:
    [待完善]

作者: [待填写]
创建时间: $(Get-Date -Format "yyyy-MM-dd")
版本: 1.0
"""

$Content
"@
            } elseif ($File.Extension -eq ".ps1") {
                $HeaderTemplate = @"
<#
.SYNOPSIS
$($File.BaseName) - [待完善功能说明]

.DESCRIPTION
[待完善详细描述]

.NOTES
Author: [待填写]
Created: $(Get-Date -Format "yyyy-MM-dd")
Version: 1.0
#>

$Content
"@
            }
            
            if ($HeaderTemplate) {
                Set-Content $File.FullName $HeaderTemplate -Encoding UTF8
                Write-Host "   ✅ 已添加文件头部" -ForegroundColor Green
                $FileIssues--
            }
        }
    }
    
    # 检查函数文档覆盖率
    $FunctionPattern = if ($File.Extension -eq ".py") { "def " } else { "function " }
    $DocPattern = if ($File.Extension -eq ".py") { '"""' } else { '<#' }
    
    $Functions = ($Content -split "`n" | Select-String $FunctionPattern).Count
    $Docstrings = ($Content -split "`n" | Select-String $DocPattern).Count
    
    if ($Functions -gt 0) {
        $DocCoverage = [Math]::Round(($Docstrings / $Functions) * 100, 1)
        
        if ($DocCoverage -ge $CurrentStandard.DocCoverageMin) {
            Write-Host "   ✅ 函数文档覆盖率: $DocCoverage% (≥$($CurrentStandard.DocCoverageMin)%)" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 函数文档覆盖率: $DocCoverage% (需要≥$($CurrentStandard.DocCoverageMin)%)" -ForegroundColor Red
            $FileIssues++
        }
    } else {
        Write-Host "   ℹ️  文件中没有函数定义" -ForegroundColor Gray
    }
    
    # 检查注释密度
    $CodeLines = ($Content -split "`n" | Where-Object { 
        $_.Trim() -and 
        $_ -notmatch '^\s*#' -and 
        $_ -notmatch '^\s*"""' -and 
        $_ -notmatch "^\s*'''" 
    }).Count
    
    $CommentLines = ($Content -split "`n" | Select-String '^\s*#').Count
    
    if ($CodeLines -gt 0) {
        $CommentRatio = [Math]::Round(($CommentLines / $CodeLines) * 100, 1)
        
        if ($CommentRatio -ge $CurrentStandard.CommentRatioMin) {
            Write-Host "   ✅ 代码注释密度: $CommentRatio% (≥$($CurrentStandard.CommentRatioMin)%)" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 代码注释密度: $CommentRatio% (需要≥$($CurrentStandard.CommentRatioMin)%)" -ForegroundColor Red
            $FileIssues++
        }
    }
    
    # 检查特殊标记
    $TodoCount = ($Content -split "`n" | Select-String 'TODO:|FIXME:|XXX:').Count
    if ($TodoCount -gt 0) {
        Write-Host "   ⚠️  发现 $TodoCount 个待处理标记 (TODO/FIXME/XXX)" -ForegroundColor Yellow
    }
    
    # 检查sku_id数据类型错误 (合并自check_sku_id_types.ps1)
    if ($File.Extension -eq ".py" -and $File.DirectoryName -like "*tests*") {
        $SkuIdErrors = 0
        $LineNumber = 1
        
        foreach ($Line in ($Content -split "`n")) {
            # 检查字符串类型的sku_id赋值
            if ($Line -match 'sku_id\s*=\s*["''][^"'']*["'']') {
                Write-Host "   ❌ sku_id数据类型错误 (行$LineNumber): 使用字符串而非整数" -ForegroundColor Red
                $SkuIdErrors++
                $FileIssues++
            }
            
            # 检查模型实例化中的sku_id字符串使用
            if ($Line -match '(InventoryStock|InventoryTransaction|InventoryReservation)\s*\(' -and 
                (($Content -split "`n")[$LineNumber..($LineNumber+5)] -join " ") -match 'sku_id\s*=\s*["'']') {
                Write-Host "   ⚠️  模型实例化可能使用字符串sku_id (行$LineNumber)" -ForegroundColor Yellow
                $SkuIdErrors++
            }
            
            $LineNumber++
        }
        
        if ($SkuIdErrors -eq 0) {
            Write-Host "   ✅ sku_id数据类型使用正确" -ForegroundColor Green
        } else {
            Write-Host "   💡 修复建议: 先创建SKU对象，然后使用sku.id (整数)" -ForegroundColor Cyan
        }
    }
    
    # 检查复杂函数 (Python)
    if ($File.Extension -eq ".py") {
        $LongFunctions = ($Content -split "`n" | Select-String "def " | ForEach-Object {
            $functionStart = $_.LineNumber
            # 简单启发式: 如果函数后有很多行可能是长函数
            $nextFunction = ($Content -split "`n")[$functionStart..($functionStart+50)] | Select-String "^def " | Select-Object -First 1
            if ($nextFunction -and $nextFunction.LineNumber - $functionStart -gt 30) {
                $_.Line
            }
        }).Count
        
        if ($LongFunctions -gt 0) {
            Write-Host "   ⚠️  发现 $LongFunctions 个可能过长的函数 (>30行)" -ForegroundColor Yellow
        }
    }
    
    $TotalIssues += $FileIssues
    
    # 文件总结
    if ($FileIssues -eq 0) {
        Write-Host "   🎉 文件规范检查通过" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  发现 $FileIssues 个规范问题" -ForegroundColor Yellow
    }
}

# 总体报告
Write-Host "`n" + "=" * 60
Write-Host "📊 检查总结报告:" -ForegroundColor Yellow
Write-Host "   检查文件数: $ProcessedFiles" -ForegroundColor Gray
Write-Host "   检查标准: $Standard" -ForegroundColor Gray
Write-Host "   发现问题数: $TotalIssues" -ForegroundColor Gray

if ($TotalIssues -eq 0) {
    Write-Host "🎉 所有文件都符合代码规范！" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  共发现 $TotalIssues 个规范问题" -ForegroundColor Yellow
    
    if (-not $Fix) {
        Write-Host "💡 运行建议:" -ForegroundColor Cyan
        Write-Host "   自动修复: tools/check_code_standards.ps1 -Fix" -ForegroundColor Gray
        Write-Host "   严格检查: tools/check_code_standards.ps1 -Standard strict" -ForegroundColor Gray
    }
    
    exit 1
}

Write-Host "🔍 代码规范检查完成" -ForegroundColor Cyan
