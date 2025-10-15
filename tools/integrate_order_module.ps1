#!/usr/bin/env pwsh
<#
.SYNOPSIS
    整合订单模块四层架构升级到测试工具稳定分支
    
.DESCRIPTION
    从dev分支选择性合并订单模块代码和文档，保持测试工具的稳定版本
    
.NOTES
    创建日期: 2025-10-15
    执行前提: 当前在testgen-baseline分支
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$SkipBackup
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "订单模块整合脚本 v1.0" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. 检查当前分支
Write-Host "[1/7] 检查当前分支..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ($currentBranch -ne "testgen-baseline") {
    Write-Error "错误: 必须在testgen-baseline分支执行此脚本"
    exit 1
}
Write-Host "✓ 当前分支: $currentBranch" -ForegroundColor Green

# 2. 检查工作区状态
Write-Host "`n[2/7] 检查工作区状态..." -ForegroundColor Yellow
$status = git status --porcelain
if ($status) {
    Write-Host "警告: 工作区有未提交的更改" -ForegroundColor Red
    git status --short
    $continue = Read-Host "是否继续? (y/N)"
    if ($continue -ne "y") {
        Write-Host "操作已取消" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ 工作区状态正常" -ForegroundColor Green

# 3. 创建备份分支
if (-not $SkipBackup) {
    Write-Host "`n[3/7] 创建备份分支..." -ForegroundColor Yellow
    $backupBranch = "backup-dev-20251015"
    
    # 检查备份分支是否已存在
    $branchExists = git branch --list $backupBranch
    if ($branchExists) {
        Write-Host "备份分支 $backupBranch 已存在，跳过创建" -ForegroundColor Yellow
    } else {
        if (-not $DryRun) {
            git branch $backupBranch dev
            Write-Host "✓ 创建备份分支: $backupBranch" -ForegroundColor Green
        } else {
            Write-Host "[DRY RUN] 将创建备份分支: $backupBranch" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "`n[3/7] 跳过备份（--SkipBackup）" -ForegroundColor Yellow
}

# 4. 查看订单模块的差异
Write-Host "`n[4/7] 分析订单模块差异..." -ForegroundColor Yellow
Write-Host "订单模块代码差异:" -ForegroundColor Cyan
git diff --stat testgen-baseline..dev -- app/modules/order_management/

Write-Host "`n订单模块文档差异:" -ForegroundColor Cyan
git diff --stat testgen-baseline..dev -- docs/design/modules/order-management/

# 5. 选择性checkout订单模块文件
Write-Host "`n[5/7] 提取订单模块文件..." -ForegroundColor Yellow

$filesToCheckout = @(
    "app/modules/order_management/"
    "docs/design/modules/order-management/"
)

$optionalFiles = @(
    "ORDER_MANAGEMENT_ACCEPTANCE_REPORT.md"
    "ORDER_MANAGEMENT_BOUNDARY_ANALYSIS.yaml"
    "ORDER_MANAGEMENT_BOUNDARY_SELF_CHECK.yaml"
    "ORDER_MANAGEMENT_DOC_PROGRESS_REPORT.md"
)

if (-not $DryRun) {
    foreach ($file in $filesToCheckout) {
        Write-Host "  提取: $file" -ForegroundColor Gray
        git checkout dev -- $file
    }
    
    # 可选文件（如果存在才提取）
    foreach ($file in $optionalFiles) {
        if (Test-Path $file) {
            Write-Host "  提取: $file (可选)" -ForegroundColor Gray
            git checkout dev -- $file
        }
    }
    
    Write-Host "✓ 文件提取完成" -ForegroundColor Green
} else {
    Write-Host "[DRY RUN] 将提取以下文件:" -ForegroundColor Cyan
    $filesToCheckout | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
}

# 6. 显示待提交的更改
Write-Host "`n[6/7] 待提交的更改:" -ForegroundColor Yellow
if (-not $DryRun) {
    git status --short
} else {
    Write-Host "[DRY RUN] 跳过" -ForegroundColor Cyan
}

# 7. 提交更改
Write-Host "`n[7/7] 提交整合结果..." -ForegroundColor Yellow
if (-not $DryRun) {
    $commitMessage = @"
整合订单模块四层架构升级（从dev分支）

变更内容：
- 引入repository层实现数据访问分离
- 更新service层业务逻辑实现
- 完善models.py、schemas.py、router.py
- 更新订单模块详细设计文档

技术细节：
- 采用四层架构：Route→Service→Repository→Models
- 符合数据访问标准和API设计标准
- 保持测试工具稳定版本（v1.0）

注意事项：
- 不包含订单模块测试代码（待重新生成）
- 保持前3个模块的测试代码完整性
- 测试工具未发生变更

相关文档：
- docs/design/modules/order-management/design.md
- docs/design/modules/order-management/api-spec.md
"@

    git add app/modules/order_management/ docs/design/modules/order-management/
    
    # 添加可选文档（如果存在）
    foreach ($file in $optionalFiles) {
        if (Test-Path $file) {
            git add $file
        }
    }
    
    git commit -m $commitMessage
    
    Write-Host "✓ 提交完成" -ForegroundColor Green
    
    # 显示提交信息
    Write-Host "`n最新提交:" -ForegroundColor Cyan
    git log -1 --oneline
    
} else {
    Write-Host "[DRY RUN] 将创建提交，包含订单模块升级内容" -ForegroundColor Cyan
}

# 完成提示
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "整合完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

if (-not $DryRun) {
    Write-Host "`n下一步操作:" -ForegroundColor Yellow
    Write-Host "1. 验证订单模块代码: cd app/modules/order_management && ls" -ForegroundColor Gray
    Write-Host "2. 查看提交详情: git show HEAD" -ForegroundColor Gray
    Write-Host "3. 推送到远程: git push origin testgen-baseline" -ForegroundColor Gray
    Write-Host "4. 更新dev分支: git checkout dev && git merge testgen-baseline" -ForegroundColor Gray
    Write-Host "5. 生成订单模块测试: python tools/test_generators/generate_all.py order_management" -ForegroundColor Gray
} else {
    Write-Host "`n这是演练模式，没有实际执行。" -ForegroundColor Yellow
    Write-Host "移除 -DryRun 参数以实际执行。" -ForegroundColor Yellow
}
