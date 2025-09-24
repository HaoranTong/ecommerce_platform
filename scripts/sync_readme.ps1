#!/usr/bin/env pwsh
<#
.SYNOPSIS
自动同步README文档的工具脚本

.DESCRIPTION
在创建、重命名、删除文档或代码文件时，自动同步更新同级目录的README.md文档。
确保文档目录索引与实际文件保持一致。

.PARAMETER Path
要检查同步的目录路径，默认为当前目录

.PARAMETER CheckOnly
仅检查同步状态，不进行自动更新

.PARAMETER AutoUpdate
自动更新README.md文件（需要确认）

.EXAMPLE
scripts/sync_readme.ps1 -Path docs/design/modules/user_auth
scripts/sync_readme.ps1 -CheckOnly -Path scripts
scripts/sync_readme.ps1 -AutoUpdate -Path docs/standards

.NOTES
Author: AI Development Team
Created: 2025-09-18
Version: 1.0
Dependencies: PowerShell 5.0+
#>

param(
    [string]$Path = ".",
    [switch]$CheckOnly = $false,
    [switch]$AutoUpdate = $false
)

Write-Host "📁 README文档同步工具" -ForegroundColor Cyan
Write-Host "检查目录: $Path" -ForegroundColor Gray
Write-Host "=" * 60

# 检查目录是否存在
if (-not (Test-Path $Path)) {
    Write-Host "❌ 目录不存在: $Path" -ForegroundColor Red
    exit 1
}

# 获取目录中的所有文件
$AllFiles = Get-ChildItem $Path -File | Where-Object { $_.Name -ne "README.md" }
$ReadmePath = Join-Path $Path "README.md"

Write-Host "📊 目录分析结果:" -ForegroundColor Yellow
Write-Host "   文件总数: $($AllFiles.Count)" -ForegroundColor Gray
Write-Host "   README存在: $((Test-Path $ReadmePath) -eq $true)" -ForegroundColor Gray

# 检查README.md是否存在
if (-not (Test-Path $ReadmePath)) {
    Write-Host "❌ 缺少README.md文件" -ForegroundColor Red
    
    if ($AutoUpdate) {
        Write-Host "🔧 创建默认README.md..." -ForegroundColor Cyan
        $DefaultContent = @"
# $(Split-Path $Path -Leaf)

## 文件说明

$(foreach ($file in $AllFiles) {
"- `$($file.Name)` - [待完善说明]"
})

## 使用指南

[待完善]

## 更新日志

- $(Get-Date -Format "yyyy-MM-dd"): 自动生成README文档
"@
        Set-Content $ReadmePath $DefaultContent -Encoding UTF8
        Write-Host "✅ 已创建默认README.md" -ForegroundColor Green
    }
    
    if ($CheckOnly) {
        Write-Host "💡 建议: 运行 'scripts/sync_readme.ps1 -AutoUpdate -Path $Path' 创建README" -ForegroundColor Yellow
    }
    
    return
}

# 读取现有README内容
$ReadmeContent = Get-Content $ReadmePath -Raw

# 分析文件同步状态
$UndocumentedFiles = @()
$DocumentedFiles = @()

foreach ($File in $AllFiles) {
    if ($ReadmeContent -match [Regex]::Escape($File.Name)) {
        $DocumentedFiles += $File.Name
    } else {
        $UndocumentedFiles += $File.Name
    }
}

# 报告同步状态
Write-Host "📋 同步状态分析:" -ForegroundColor Yellow

if ($DocumentedFiles.Count -gt 0) {
    Write-Host "   ✅ 已文档化文件 ($($DocumentedFiles.Count)个):" -ForegroundColor Green
    $DocumentedFiles | ForEach-Object { Write-Host "      - $_" -ForegroundColor Gray }
}

if ($UndocumentedFiles.Count -gt 0) {
    Write-Host "   ❌ 未文档化文件 ($($UndocumentedFiles.Count)个):" -ForegroundColor Red
    $UndocumentedFiles | ForEach-Object { Write-Host "      - $_" -ForegroundColor Red }
    
    if ($AutoUpdate) {
        Write-Host "🔧 自动添加未文档化的文件..." -ForegroundColor Cyan
        
        # 在README末尾添加新文件
        $NewEntries = "`n## 新增文件`n`n"
        foreach ($File in $UndocumentedFiles) {
            $NewEntries += "- `$File` - [待完善说明]`n"
        }
        $NewEntries += "`n*注: 请完善上述文件的具体说明*`n"
        
        Add-Content $ReadmePath $NewEntries -Encoding UTF8
        Write-Host "✅ 已添加 $($UndocumentedFiles.Count) 个文件到README" -ForegroundColor Green
    }
    
    if ($CheckOnly) {
        Write-Host "💡 建议: 运行 'scripts/sync_readme.ps1 -AutoUpdate -Path $Path' 自动更新" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✅ 所有文件都已在README中说明" -ForegroundColor Green
}

# 检查子目录README
$SubDirs = Get-ChildItem $Path -Directory
$MissingSubReadmes = @()

foreach ($SubDir in $SubDirs) {
    $SubReadmePath = Join-Path $SubDir.FullName "README.md"
    if (Test-Path $SubReadmePath) {
        Write-Host "   ✅ 子目录README: $($SubDir.Name)" -ForegroundColor Green
    } else {
        $MissingSubReadmes += $SubDir.Name
        Write-Host "   ⚠️  缺少子目录README: $($SubDir.Name)" -ForegroundColor Yellow
    }
}

# 总结报告
Write-Host "=" * 60
if ($UndocumentedFiles.Count -eq 0 -and $MissingSubReadmes.Count -eq 0) {
    Write-Host "🎉 文档同步状态良好！" -ForegroundColor Green
} else {
    Write-Host "⚠️  发现 $($UndocumentedFiles.Count + $MissingSubReadmes.Count) 个同步问题" -ForegroundColor Yellow
    
    if (-not $CheckOnly -and -not $AutoUpdate) {
        Write-Host "💡 运行选项:" -ForegroundColor Cyan
        Write-Host "   检查模式: scripts/sync_readme.ps1 -CheckOnly -Path $Path" -ForegroundColor Gray
        Write-Host "   自动更新: scripts/sync_readme.ps1 -AutoUpdate -Path $Path" -ForegroundColor Gray
    }
}

Write-Host "📁 README同步检查完成" -ForegroundColor Cyan
