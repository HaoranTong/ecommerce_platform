#!/usr/bin/env powershell
<#
.SYNOPSIS
    AI工作流程文档同步检查和修复脚本

.DESCRIPTION
    文档标准化信息:
    title: "文档同步检查脚本"
    version: "v1.0.0"
    status: "Active"
    created: "2025-10-02"
    updated: "2025-10-02"
    owner: "文档治理委员会"
    dependencies: ["MASTER.md", "tools/checkpoint-cards.md", "docs/standards/document-management-standards.md"]
    labels: ["synchronization", "validation", "governance"]
    document_type: "自动化脚本"
    usage_scenario: "检查AI工作流程相关文档的一致性，发现并报告冲突"
    usage_method: "在文档更新后运行，确保所有文档保持同步"
    cooperation_docs: "与文档管理标准和信息源优先级策略配合"
    maintenance_note: "文档结构变化时需要更新检查逻辑；新增文档类型时需要扩展检查范围"

.NOTES
    功能说明: 自动检查MASTER.md与其他AI工作流程文档的一致性
    使用方法: 在PowerShell中直接执行此脚本
    使用场景: 文档更新后的一致性验证，定期同步检查
    配合使用: 与信息源优先级策略配合，确保MASTER.md的权威地位
    更新维护: 文档架构变化时同步更新检查逻辑
#>

# sync_documentation.ps1

Write-Host "🔍 开始执行文档同步检查..." -ForegroundColor Cyan

# 1. 检查MASTER.md中定义的检查点
Write-Host "📋 提取MASTER.md中的检查点..." -ForegroundColor Yellow
$masterCheckpoints = @()
$masterContent = Get-Content "MASTER.md" -Raw
$matches = [regex]::Matches($masterContent, '\[CHECK:([^\]]+)\]')
foreach ($match in $matches) {
    $checkpoint = $match.Groups[1].Value
    if ($checkpoint -notin $masterCheckpoints) {
        $masterCheckpoints += $checkpoint
    }
}
Write-Host "MASTER.md中发现的检查点: $($masterCheckpoints -join ', ')" -ForegroundColor Green

# 2. 检查checkpoint-cards.md中定义的检查点
Write-Host "📋 提取checkpoint-cards.md中的检查点..." -ForegroundColor Yellow
$cardsCheckpoints = @()
$cardsContent = Get-Content "tools/checkpoint-cards.md" -Raw
$matches = [regex]::Matches($cardsContent, '###\s+([^:]+):')
foreach ($match in $matches) {
    $checkpoint = $match.Groups[1].Value.Trim()
    $cardsCheckpoints += $checkpoint
}
Write-Host "checkpoint-cards.md中发现的检查点: $($cardsCheckpoints -join ', ')" -ForegroundColor Green

# 3. 检查task_classification配置中的检查点
Write-Host "📋 提取task_classification配置中的检查点..." -ForegroundColor Yellow
$configCheckpoints = @()
if (Test-Path "tools/task_classification/config/checkpoint_mapping.yaml") {
    $configContent = Get-Content "tools/task_classification/config/checkpoint_mapping.yaml" -Raw
    $matches = [regex]::Matches($configContent, '([A-Z-]+\d+)')
    foreach ($match in $matches) {
        $checkpoint = $match.Groups[1].Value
        if ($checkpoint -notin $configCheckpoints) {
            $configCheckpoints += $checkpoint
        }
    }
}
Write-Host "task_classification配置中发现的检查点: $($configCheckpoints -join ', ')" -ForegroundColor Green

# 4. 冲突分析
Write-Host "`n🔍 开始冲突分析..." -ForegroundColor Cyan

# 检查MASTER.md中有但cards中没有的
$missingInCards = $masterCheckpoints | Where-Object { $_ -notin $cardsCheckpoints }
if ($missingInCards) {
    Write-Host "❌ checkpoint-cards.md中缺少的检查点: $($missingInCards -join ', ')" -ForegroundColor Red
} else {
    Write-Host "✅ checkpoint-cards.md包含所有MASTER.md中的检查点" -ForegroundColor Green
}

# 检查cards中有但MASTER.md中没有的  
$extraInCards = $cardsCheckpoints | Where-Object { $_ -notin $masterCheckpoints }
if ($extraInCards) {
    Write-Host "⚠️  checkpoint-cards.md中多余的检查点: $($extraInCards -join ', ')" -ForegroundColor Yellow
    Write-Host "   这些检查点在MASTER.md中未被引用" -ForegroundColor Gray
}

# 检查config中有但MASTER.md中没有的
$extraInConfig = $configCheckpoints | Where-Object { $_ -notin $masterCheckpoints }
if ($extraInConfig) {
    Write-Host "⚠️  task_classification配置中多余的检查点: $($extraInConfig -join ', ')" -ForegroundColor Yellow
}

# 5. 生成同步建议
Write-Host "`n📝 同步建议:" -ForegroundColor Cyan
Write-Host "1. 以MASTER.md为权威标准" -ForegroundColor White
Write-Host "2. checkpoint-cards.md需要添加缺少的检查点" -ForegroundColor White
Write-Host "3. task_classification配置需要更新检查点映射" -ForegroundColor White
Write-Host "4. 未在MASTER.md中引用的检查点需要确认是否保留" -ForegroundColor White

Write-Host "`n🎯 同步检查完成!" -ForegroundColor Green