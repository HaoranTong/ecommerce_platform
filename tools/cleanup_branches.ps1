#!/usr/bin/env pwsh
<#
.SYNOPSIS
    清理无用的Git分支
    
.DESCRIPTION
    删除已合并或不再需要的功能分支，保持分支结构清晰
    
.PARAMETER DryRun
    演练模式，只显示将要删除的分支，不实际执行
    
.PARAMETER DeleteRemote
    同时删除远程分支
    
.NOTES
    创建日期: 2025-10-15
    谨慎使用: 删除分支操作不可逆
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$DeleteRemote,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git分支清理工具 v1.0" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 定义要保留的分支
$protectedBranches = @(
    "main",
    "dev",
    "testgen-baseline",
    "backup-dev-20251015"
)

# 定义要删除的功能分支（已完成的）
$branchesToDelete = @(
    "feature/add-user-auth",
    "feature/add-product-crud",
    "feature/add-shopping-cart",
    "feature/add-order-management",
    "feature/add-member-system",
    "feature/add-inventory-management",
    "feature/phase4-ast-templates",
    "feature/product",
    "archive/ast-templates-phase1-4",
    "status/logs"
)

# 1. 显示当前分支状态
Write-Host "[1/4] 当前本地分支:" -ForegroundColor Yellow
git branch -vv | Where-Object { $_ -notmatch "remotes/" }

Write-Host "`n保护分支（不会删除）:" -ForegroundColor Green
$protectedBranches | ForEach-Object { Write-Host "  ✓ $_" -ForegroundColor Green }

# 2. 检查要删除的分支
Write-Host "`n[2/4] 检查待删除分支..." -ForegroundColor Yellow
$existingBranches = git branch --list | ForEach-Object { $_.Trim().Replace("* ", "") }
$toDelete = @()

foreach ($branch in $branchesToDelete) {
    if ($existingBranches -contains $branch) {
        $toDelete += $branch
        
        # 检查是否已合并到dev
        $merged = git branch --merged dev | Where-Object { $_.Trim() -eq $branch }
        $status = if ($merged) { "[已合并]" } else { "[未合并]" }
        
        Write-Host "  • $branch $status" -ForegroundColor $(if ($merged) { "Gray" } else { "Yellow" })
    }
}

if ($toDelete.Count -eq 0) {
    Write-Host "没有需要删除的分支" -ForegroundColor Green
    exit 0
}

# 3. 确认删除
Write-Host "`n[3/4] 待删除分支数量: $($toDelete.Count)" -ForegroundColor Yellow

if (-not $Force -and -not $DryRun) {
    Write-Host "`n警告: 即将删除以下分支:" -ForegroundColor Red
    $toDelete | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    
    $confirm = Read-Host "`n确认删除? (输入 'DELETE' 确认)"
    if ($confirm -ne "DELETE") {
        Write-Host "操作已取消" -ForegroundColor Yellow
        exit 0
    }
}

# 4. 执行删除
Write-Host "`n[4/4] 删除分支..." -ForegroundColor Yellow

foreach ($branch in $toDelete) {
    if ($DryRun) {
        Write-Host "  [DRY RUN] 将删除本地分支: $branch" -ForegroundColor Cyan
    } else {
        try {
            # 删除本地分支
            git branch -d $branch 2>$null
            if ($LASTEXITCODE -ne 0) {
                # 如果分支未合并，使用强制删除
                git branch -D $branch
                Write-Host "  ✓ 强制删除本地分支: $branch" -ForegroundColor Yellow
            } else {
                Write-Host "  ✓ 删除本地分支: $branch" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ✗ 删除失败: $branch - $_" -ForegroundColor Red
        }
    }
    
    # 删除远程分支
    if ($DeleteRemote) {
        # 检查远程分支是否存在
        $remoteBranches = git branch -r | ForEach-Object { $_.Trim() }
        
        foreach ($remote in @("origin", "github", "gitee")) {
            $remoteBranch = "$remote/$branch"
            if ($remoteBranches -contains $remoteBranch) {
                if ($DryRun) {
                    Write-Host "  [DRY RUN] 将删除远程分支: $remoteBranch" -ForegroundColor Cyan
                } else {
                    try {
                        git push $remote --delete $branch 2>$null
                        Write-Host "  ✓ 删除远程分支: $remoteBranch" -ForegroundColor Green
                    } catch {
                        Write-Host "  ✗ 删除远程分支失败: $remoteBranch" -ForegroundColor Red
                    }
                }
            }
        }
    }
}

# 完成提示
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "清理完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

if (-not $DryRun) {
    Write-Host "`n剩余分支:" -ForegroundColor Yellow
    git branch -vv | Where-Object { $_ -notmatch "remotes/" }
    
    Write-Host "`n建议操作:" -ForegroundColor Yellow
    Write-Host "1. 检查远程分支: git branch -r" -ForegroundColor Gray
    Write-Host "2. 清理远程追踪分支: git remote prune origin" -ForegroundColor Gray
    Write-Host "3. 查看分支图: git log --graph --oneline --all -10" -ForegroundColor Gray
} else {
    Write-Host "`n这是演练模式，没有实际执行。" -ForegroundColor Yellow
    Write-Host "移除 -DryRun 参数以实际执行。" -ForegroundColor Yellow
}
