#!/usr/bin/env pwsh
<#
.SYNOPSIS
标准文档综合维护工具 - 批量维护操作和状态管理

.DESCRIPTION
提供标准文档体系的综合维护功能，包括：
1. 健康检查 - 完整的多维度验证和问题诊断
2. 版本更新 - 批量更新过时的版本信息头
3. 状态报告 - 生成详细的维护状态和统计报告
4. 备份管理 - 创建和管理标准文档的版本快照

配合Phase 3.3维护机制使用，提供比validate_standards.ps1更全面的维护功能。

.PARAMETER Action
维护操作类型：
- check: 健康检查（默认）- 执行完整验证+问题诊断
- update: 版本更新 - 批量更新版本信息头和过时内容
- report: 状态报告 - 生成维护统计和质量指标
- backup: 备份管理 - 创建标准文档快照
- restore: 恢复管理 - 从备份恢复标准文档

.PARAMETER Target
可选参数，指定具体的维护目标：
- 对于check: 可指定单个文档路径
- 对于update: 可指定更新类型(version/content/all)
- 对于report: 可指定报告类型(summary/detailed/metrics)
- 对于backup: 可指定备份标识符

.PARAMETER OutputPath
可选参数，指定报告或备份的输出路径，默认为当前目录

.EXAMPLE
# 完整健康检查
scripts/maintain_standards.ps1 -Action check

.EXAMPLE
# 批量更新版本信息
scripts/maintain_standards.ps1 -Action update -Target version

.EXAMPLE
# 生成详细维护报告
scripts/maintain_standards.ps1 -Action report -Target detailed -OutputPath "docs/reports/"

.EXAMPLE
# 创建标准文档备份
scripts/maintain_standards.ps1 -Action backup -Target "phase3-complete"

.NOTES
创建时间: 2025-09-23 Phase 3.3
维护者: AI Assistant & Architecture Team
用途: 标准文档体系的综合维护和质量保证
依赖: validate_standards.ps1, PowerShell 7.0+

相关文档:
- docs/standards/maintenance-guide.md (维护手册)
- docs/standards/README.md (L0标准文档导航)
- PROJECT-FOUNDATION.md (FOUNDATION级项目基础设定)
- scripts/validate_standards.ps1 (核心验证工具)
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("check", "update", "report", "backup", "restore")]
    [string]$Action = "check",
    
    [string]$Target = "",
    [string]$OutputPath = "."
)

Write-Host "🔧 标准文档综合维护工具 - $Action" -ForegroundColor Cyan
Write-Host "=" * 60

# 全局配置
$StandardsPath = "docs/standards"
$BackupPath = "backups/standards"
$ReportPath = Join-Path $OutputPath "reports"

# 确保必要目录存在
@($BackupPath, $ReportPath) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -Path $_ -ItemType Directory -Force | Out-Null
    }
}

# 获取所有标准文档信息
function Get-StandardsInventory {
    $standards = @()
    
    Get-ChildItem "$StandardsPath/*.md" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        
        # 解析版本信息头
        $versionMatch = [regex]::Match($content, '<!--version info: v([\d.]+), created: ([\d-]+), level: (L\d), dependencies: ([^>]*)-->')
        
        $standards += [PSCustomObject]@{
            Name = $_.Name
            Path = $_.FullName
            Size = $_.Length
            LastModified = $_.LastWriteTime
            Version = if ($versionMatch.Success) { $versionMatch.Groups[1].Value } else { "未知" }
            Created = if ($versionMatch.Success) { $versionMatch.Groups[2].Value } else { "未知" }
            Level = if ($versionMatch.Success) { $versionMatch.Groups[3].Value } else { "未知" }
            Dependencies = if ($versionMatch.Success) { $versionMatch.Groups[4].Value } else { "未知" }
            HasVersionHeader = $versionMatch.Success
        }
    }
    
    return $standards
}

# 健康检查功能
function Invoke-HealthCheck {
    param([string]$SingleFile = "")
    
    Write-Host "🔍 执行标准文档健康检查..." -ForegroundColor Yellow
    Write-Host ""
    
    # 1. 基础验证
    Write-Host "📋 基础验证 - validate_standards.ps1" -ForegroundColor Green
    
    try {
        if ($SingleFile) {
            Write-Host "   🎯 单文档模式: $SingleFile"
            $validationResult = & "scripts/validate_standards.ps1" -Action "content" -DocPath $SingleFile 2>&1
        } else {
            $validationResult = & "scripts/validate_standards.ps1" -Action "format" 2>&1
        }
        $validationSuccess = $LASTEXITCODE -eq 0
    } catch {
        Write-Host "   ⚠️ 验证脚本调用失败: $($_.Exception.Message)" -ForegroundColor Yellow
        $validationSuccess = $false
    }
    
    Write-Host "   验证结果: $(if ($validationSuccess) { '✅ 通过' } else { '❌ 失败' })"
    Write-Host ""
    
    # 2. 文档库存检查
    Write-Host "📦 文档库存分析" -ForegroundColor Green
    $inventory = Get-StandardsInventory
    
    $l0Count = ($inventory | Where-Object { $_.Level -eq "L0" }).Count
    $l1Count = ($inventory | Where-Object { $_.Level -eq "L1" }).Count  
    $l2Count = ($inventory | Where-Object { $_.Level -eq "L2" }).Count
    $unknownCount = ($inventory | Where-Object { $_.Level -eq "未知" }).Count
    
    Write-Host "   L0导航层: $l0Count 个 $(if ($l0Count -eq 1) { '✅' } else { '⚠️' })"
    Write-Host "   L1核心层: $l1Count 个 $(if ($l1Count -eq 2) { '✅' } else { '⚠️' })"
    Write-Host "   L2领域层: $l2Count 个 ✅"
    Write-Host "   格式异常: $unknownCount 个 $(if ($unknownCount -eq 0) { '✅' } else { '❌' })"
    Write-Host "   文档总数: $($inventory.Count) 个"
    Write-Host ""
    
    # 3. 版本信息检查
    Write-Host "🏷️ 版本信息完整性" -ForegroundColor Green
    $noVersionHeader = $inventory | Where-Object { -not $_.HasVersionHeader }
    $outdatedDocs = $inventory | Where-Object { 
        $_.HasVersionHeader -and $_.LastModified -gt [DateTime]::ParseExact($_.Created, "yyyy-MM-dd", $null).AddDays(7)
    }
    
    if ($noVersionHeader.Count -eq 0) {
        Write-Host "   ✅ 所有文档都有版本信息头" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $($noVersionHeader.Count) 个文档缺少版本信息头:" -ForegroundColor Red
        $noVersionHeader | ForEach-Object { Write-Host "     - $($_.Name)" -ForegroundColor Gray }
    }
    
    if ($outdatedDocs.Count -gt 0) {
        Write-Host "   ⚠️ $($outdatedDocs.Count) 个文档版本信息可能过时" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # 4. 依赖关系深度分析
    Write-Host "🔗 依赖关系深度分析" -ForegroundColor Green
    $l2Docs = $inventory | Where-Object { $_.Level -eq "L2" }
    $dependencyIssues = @()
    
    foreach ($doc in $l2Docs) {
        $deps = $doc.Dependencies -split ','
        $hasNamingConventions = $deps -contains "naming-conventions-standards.md"
        $hasProjectFoundation = $deps -contains "PROJECT-FOUNDATION.md"
        
        if (-not $hasNamingConventions -or -not $hasProjectFoundation) {
            $dependencyIssues += $doc.Name
        }
    }
    
    if ($dependencyIssues.Count -eq 0) {
        Write-Host "   ✅ 所有L2文档依赖关系正确" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $($dependencyIssues.Count) 个L2文档依赖不完整:" -ForegroundColor Red
        $dependencyIssues | ForEach-Object { Write-Host "     - $_" -ForegroundColor Gray }
    }
    Write-Host ""
    
    # 5. 文件完整性检查
    Write-Host "📁 文件完整性检查" -ForegroundColor Green
    $criticalFiles = @(
        "docs/standards/README.md",
        "PROJECT-FOUNDATION.md", 
        "docs/standards/naming-conventions-standards.md",
        "scripts/validate_standards.ps1",
        "docs/standards/maintenance-guide.md"
    )
    
    $missingCritical = @()
    foreach ($file in $criticalFiles) {
        if (-not (Test-Path $file)) {
            $missingCritical += $file
        }
    }
    
    if ($missingCritical.Count -eq 0) {
        Write-Host "   ✅ 所有关键文件存在" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $($missingCritical.Count) 个关键文件缺失:" -ForegroundColor Red
        $missingCritical | ForEach-Object { Write-Host "     - $_" -ForegroundColor Gray }
    }
    Write-Host ""
    
    # 6. 健康评分
    $totalChecks = 5
    $passedChecks = 0
    
    if ($validationSuccess) { $passedChecks++ }
    if ($unknownCount -eq 0) { $passedChecks++ }
    if ($noVersionHeader.Count -eq 0) { $passedChecks++ }
    if ($dependencyIssues.Count -eq 0) { $passedChecks++ }
    if ($missingCritical.Count -eq 0) { $passedChecks++ }
    
    $healthScore = [math]::Round(($passedChecks / $totalChecks) * 100, 1)
    $healthGrade = switch ($healthScore) {
        { $_ -ge 90 } { "优秀 ✅" }
        { $_ -ge 75 } { "良好 ⚡" }
        { $_ -ge 60 } { "及格 ⚠️" }
        default { "需要改进 ❌" }
    }
    
    Write-Host "📊 标准文档体系健康评分" -ForegroundColor Cyan
    Write-Host "   评分: $healthScore% ($passedChecks/$totalChecks 项检查通过)" -ForegroundColor $(if ($healthScore -ge 75) { "Green" } else { "Yellow" })
    Write-Host "   等级: $healthGrade"
    
    return @{
        Success = $validationSuccess
        HealthScore = $healthScore
        Issues = @{
            NoVersionHeader = $noVersionHeader
            DependencyIssues = $dependencyIssues
            MissingCritical = $missingCritical
            OutdatedDocs = $outdatedDocs
        }
        Inventory = $inventory
    }
}

# 版本更新功能
function Invoke-VersionUpdate {
    param([string]$UpdateTarget = "version")
    
    Write-Host "🔄 批量版本更新 - $UpdateTarget" -ForegroundColor Yellow
    Write-Host ""
    
    $inventory = Get-StandardsInventory
    $updatedCount = 0
    
    switch ($UpdateTarget) {
        "version" {
            Write-Host "📝 更新版本信息头格式..." -ForegroundColor Green
            
            foreach ($doc in $inventory) {
                if (-not $doc.HasVersionHeader) {
                    Write-Host "   ➕ 添加版本头: $($doc.Name)" -ForegroundColor Yellow
                    
                    # 读取文件内容
                    $content = Get-Content $doc.Path -Raw
                    
                    # 确定文档级别
                    $level = switch ($doc.Name) {
                        "README.md" { "L0" }
                        { $_ -in @("naming-conventions-standards.md", "workflow-standards.md") } { "L1" }
                        default { "L2" }
                    }
                    
                    # 确定依赖关系
                    $dependencies = switch ($level) {
                        "L0" { "none" }
                        "L1" { if ($doc.Name -eq "naming-conventions-standards.md") { "PROJECT-FOUNDATION.md" } else { "none" } }
                        "L2" { "naming-conventions-standards.md,PROJECT-FOUNDATION.md" }
                    }
                    
                    # 生成版本头
                    $versionHeader = "<!--version info: v1.0.0, created: $(Get-Date -Format 'yyyy-MM-dd'), level: $level, dependencies: $dependencies-->`n`n"
                    
                    # 插入版本头
                    $newContent = $versionHeader + $content
                    Set-Content -Path $doc.Path -Value $newContent -Encoding UTF8
                    
                    $updatedCount++
                }
            }
        }
        
        "content" {
            Write-Host "📝 检查内容一致性更新需求..." -ForegroundColor Green
            Write-Host "   ℹ️ 内容更新需要人工审查，此功能提供更新建议"
            
            # 分析哪些文档可能需要内容更新
            $updateCandidates = $inventory | Where-Object {
                $_.LastModified -lt (Get-Date).AddDays(-30) -and $_.Level -ne "L0"
            }
            
            if ($updateCandidates.Count -gt 0) {
                Write-Host "   📋 建议审查以下文档的内容时效性:"
                $updateCandidates | ForEach-Object {
                    Write-Host "     - $($_.Name) (最后更新: $($_.LastModified.ToString('yyyy-MM-dd')))"
                }
            } else {
                Write-Host "   ✅ 所有文档内容相对较新"
            }
        }
        
        "all" {
            Write-Host "🔄 执行全面更新..." -ForegroundColor Green
            Invoke-VersionUpdate -UpdateTarget "version"
            Invoke-VersionUpdate -UpdateTarget "content"
        }
    }
    
    Write-Host ""
    Write-Host "✅ 版本更新完成，共更新 $updatedCount 个文档" -ForegroundColor Green
    
    # 更新后验证
    if ($updatedCount -gt 0) {
        Write-Host "🔍 执行更新后验证..." -ForegroundColor Yellow
        & "scripts/validate_standards.ps1" -Action format | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 更新后验证通过" -ForegroundColor Green
        } else {
            Write-Host "⚠️ 更新后验证发现问题，请检查" -ForegroundColor Yellow
        }
    }
}

# 状态报告功能
function Invoke-StatusReport {
    param([string]$ReportType = "summary")
    
    Write-Host "📊 生成状态报告 - $ReportType" -ForegroundColor Yellow
    Write-Host ""
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $reportFile = Join-Path $ReportPath "standards-maintenance-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
    
    # 收集数据
    $healthCheck = Invoke-HealthCheck -ErrorAction SilentlyContinue
    $inventory = Get-StandardsInventory
    
    # 生成报告内容
    $reportContent = switch ($ReportType) {
        "summary" {
            @"
# 标准文档维护状态报告 - 摘要版

**生成时间**: $timestamp  
**报告类型**: 摘要版  
**维护工具**: maintain_standards.ps1

## 📊 总体状况

- **健康评分**: $($healthCheck.HealthScore)%
- **文档总数**: $($inventory.Count) 个
- **L0导航层**: $(($inventory | Where-Object { $_.Level -eq 'L0' }).Count) 个
- **L1核心层**: $(($inventory | Where-Object { $_.Level -eq 'L1' }).Count) 个  
- **L2领域层**: $(($inventory | Where-Object { $_.Level -eq 'L2' }).Count) 个

## 🎯 质量指标

- ✅ 版本信息完整性: $(if ($healthCheck.Issues.NoVersionHeader.Count -eq 0) { '100%' } else { "$([math]::Round((1 - $healthCheck.Issues.NoVersionHeader.Count / $inventory.Count) * 100, 1))%" })
- ✅ 依赖关系正确性: $(if ($healthCheck.Issues.DependencyIssues.Count -eq 0) { '100%' } else { '存在问题' })
- ✅ 关键文件完整性: $(if ($healthCheck.Issues.MissingCritical.Count -eq 0) { '100%' } else { '存在缺失' })

## 🔧 待处理事项

$(if ($healthCheck.Issues.NoVersionHeader.Count -gt 0) { "- ❌ $($healthCheck.Issues.NoVersionHeader.Count) 个文档缺少版本信息头" })
$(if ($healthCheck.Issues.DependencyIssues.Count -gt 0) { "- ❌ $($healthCheck.Issues.DependencyIssues.Count) 个文档依赖关系不完整" })
$(if ($healthCheck.Issues.MissingCritical.Count -gt 0) { "- ❌ $($healthCheck.Issues.MissingCritical.Count) 个关键文件缺失" })
$(if ($healthCheck.Issues.OutdatedDocs.Count -gt 0) { "- ⚠️ $($healthCheck.Issues.OutdatedDocs.Count) 个文档版本信息可能过时" })

---
*报告由maintain_standards.ps1自动生成*
"@
        }
        
        "detailed" {
            @"
# 标准文档维护状态报告 - 详细版

**生成时间**: $timestamp  
**报告类型**: 详细版  
**维护工具**: maintain_standards.ps1 v1.0.0

## 📊 总体状况

### 健康评分: $($healthCheck.HealthScore)%

$($healthCheck.Success -eq $true ? '✅' : '❌') 基础验证通过  
$(($inventory | Where-Object { $_.Level -eq '未知' }).Count -eq 0 ? '✅' : '❌') 文档格式规范  
$($healthCheck.Issues.NoVersionHeader.Count -eq 0 ? '✅' : '❌') 版本信息完整  
$($healthCheck.Issues.DependencyIssues.Count -eq 0 ? '✅' : '❌') 依赖关系正确  
$($healthCheck.Issues.MissingCritical.Count -eq 0 ? '✅' : '❌') 关键文件完整

## 📋 文档库存详情

| 文档名称 | 级别 | 版本 | 创建日期 | 大小 | 最后修改 |
|----------|------|------|----------|------|----------|
$($inventory | ForEach-Object { "| $($_.Name) | $($_.Level) | $($_.Version) | $($_.Created) | $([math]::Round($_.Size/1024, 1))KB | $($_.LastModified.ToString('yyyy-MM-dd')) |" } | Out-String)

## 🔍 问题详情

### 版本信息缺失 ($($healthCheck.Issues.NoVersionHeader.Count) 个)
$($healthCheck.Issues.NoVersionHeader | ForEach-Object { "- $($_.Name)" } | Out-String)

### 依赖关系问题 ($($healthCheck.Issues.DependencyIssues.Count) 个)  
$($healthCheck.Issues.DependencyIssues | ForEach-Object { "- $_" } | Out-String)

### 关键文件缺失 ($($healthCheck.Issues.MissingCritical.Count) 个)
$($healthCheck.Issues.MissingCritical | ForEach-Object { "- $_" } | Out-String)

### 版本过时文档 ($($healthCheck.Issues.OutdatedDocs.Count) 个)
$($healthCheck.Issues.OutdatedDocs | ForEach-Object { "- $($_.Name) (修改: $($_.LastModified.ToString('yyyy-MM-dd')))" } | Out-String)

## 🔧 维护建议

1. **立即处理**: 修复所有❌标记的问题
2. **优化建议**: 审查⚠️标记的潜在问题  
3. **定期维护**: 每周执行健康检查
4. **版本管理**: 及时更新文档版本信息

## 📈 趋势分析

- 文档增长趋势: $(if ($inventory.Count -gt 8) { '稳定增长' } else { '基础完备' })
- 维护活跃度: $(if (($inventory | Where-Object { $_.LastModified -gt (Get-Date).AddDays(-7) }).Count -gt 0) { '活跃' } else { '稳定' })
- 质量趋势: $(if ($healthCheck.HealthScore -gt 80) { '持续改善' } else { '需要关注' })

---
*详细报告由maintain_standards.ps1自动生成*  
*下次建议检查时间: $(Get-Date).AddDays(7).ToString('yyyy-MM-dd')*
"@
        }
        
        "metrics" {
            @"
# 标准文档质量指标报告

**生成时间**: $timestamp  
**数据周期**: 当前状态快照

## 📊 核心指标

### 文档数量指标
- **总文档数**: $($inventory.Count)
- **L0导航文档**: $(($inventory | Where-Object { $_.Level -eq 'L0' }).Count)  
- **L1核心文档**: $(($inventory | Where-Object { $_.Level -eq 'L1' }).Count)
- **L2领域文档**: $(($inventory | Where-Object { $_.Level -eq 'L2' }).Count)

### 质量指标
- **健康评分**: $($healthCheck.HealthScore)%
- **版本信息完整率**: $([math]::Round((1 - $healthCheck.Issues.NoVersionHeader.Count / $inventory.Count) * 100, 1))%
- **依赖关系正确率**: $(if ($healthCheck.Issues.DependencyIssues.Count -eq 0) { '100%' } else { "$([math]::Round((1 - $healthCheck.Issues.DependencyIssues.Count / ($inventory | Where-Object { $_.Level -eq 'L2' }).Count) * 100, 1))%" })
- **关键文件完整率**: $(if ($healthCheck.Issues.MissingCritical.Count -eq 0) { '100%' } else { "$([math]::Round((1 - $healthCheck.Issues.MissingCritical.Count / 5) * 100, 1))%" })

### 维护指标  
- **近期活跃文档**: $(($inventory | Where-Object { $_.LastModified -gt (Get-Date).AddDays(-30) }).Count) 个
- **版本过时文档**: $($healthCheck.Issues.OutdatedDocs.Count) 个
- **平均文档大小**: $([math]::Round(($inventory | Measure-Object -Property Size -Average).Average / 1024, 1)) KB

### 目标达成情况

| 指标 | 当前值 | 目标值 | 状态 |
|------|--------|--------|------|
| 健康评分 | $($healthCheck.HealthScore)% | ≥90% | $(if ($healthCheck.HealthScore -ge 90) { '✅ 达成' } else { '🎯 努力中' }) |
| 版本完整率 | $([math]::Round((1 - $healthCheck.Issues.NoVersionHeader.Count / $inventory.Count) * 100, 1))% | 100% | $(if ($healthCheck.Issues.NoVersionHeader.Count -eq 0) { '✅ 达成' } else { '🎯 努力中' }) |
| 依赖正确率 | $(if ($healthCheck.Issues.DependencyIssues.Count -eq 0) { '100%' } else { 'xx%' }) | 100% | $(if ($healthCheck.Issues.DependencyIssues.Count -eq 0) { '✅ 达成' } else { '🎯 努力中' }) |

---
*指标报告由maintain_standards.ps1自动生成*
"@
        }
    }
    
    # 保存报告
    $reportContent | Out-File -FilePath $reportFile -Encoding UTF8
    
    Write-Host "📄 报告已生成: $reportFile" -ForegroundColor Green
    Write-Host "📏 报告大小: $([math]::Round((Get-Item $reportFile).Length / 1024, 1)) KB"
    
    # 显示报告摘要
    if ($ReportType -eq "summary") {
        Write-Host ""
        Write-Host "📋 报告摘要:" -ForegroundColor Cyan
        Write-Host "   健康评分: $($healthCheck.HealthScore)%"
        Write-Host "   待处理问题: $(($healthCheck.Issues.NoVersionHeader.Count + $healthCheck.Issues.DependencyIssues.Count + $healthCheck.Issues.MissingCritical.Count)) 个"
    }
    
    return $reportFile
}

# 备份管理功能
function Invoke-BackupManagement {
    param([string]$BackupTag = "auto-$(Get-Date -Format 'yyyyMMdd-HHmmss')")
    
    Write-Host "💾 创建标准文档备份 - $BackupTag" -ForegroundColor Yellow
    Write-Host ""
    
    $backupDir = Join-Path $BackupPath $BackupTag
    New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
    
    # 复制所有标准文档
    Write-Host "📂 复制标准文档..."
    Copy-Item -Path "$StandardsPath/*" -Destination $backupDir -Recurse -Force
    
    # 创建备份清单
    $inventory = Get-StandardsInventory
    $manifest = @{
        BackupTag = $BackupTag
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        DocumentCount = $inventory.Count
        Documents = $inventory | Select-Object Name, Version, Level, Size
        HealthScore = (Invoke-HealthCheck -ErrorAction SilentlyContinue).HealthScore
    }
    
    $manifestFile = Join-Path $backupDir "backup-manifest.json"
    $manifest | ConvertTo-Json -Depth 3 | Out-File $manifestFile -Encoding UTF8
    
    # 压缩备份（可选）
    $archivePath = "$backupDir.zip"
    Compress-Archive -Path $backupDir -DestinationPath $archivePath -Force
    Remove-Item -Path $backupDir -Recurse -Force
    
    Write-Host "✅ 备份完成: $archivePath" -ForegroundColor Green
    Write-Host "📊 备份统计: $($inventory.Count) 个文档, $([math]::Round((Get-Item $archivePath).Length / 1024 / 1024, 2)) MB"
    
    # 清理旧备份（保留最近10个）
    $allBackups = Get-ChildItem "$BackupPath/*.zip" | Sort-Object LastWriteTime -Descending
    if ($allBackups.Count -gt 10) {
        Write-Host "🧹 清理旧备份..."
        $allBackups | Select-Object -Skip 10 | ForEach-Object {
            Write-Host "   删除: $($_.Name)"
            Remove-Item $_.FullName -Force
        }
    }
    
    return $archivePath
}

# 恢复管理功能
function Invoke-RestoreManagement {
    param([string]$BackupTag)
    
    if (-not $BackupTag) {
        Write-Host "📋 可用备份列表:" -ForegroundColor Yellow
        Get-ChildItem "$BackupPath/*.zip" | Sort-Object LastWriteTime -Descending | ForEach-Object {
            Write-Host "   - $($_.BaseName) ($($_.LastWriteTime.ToString('yyyy-MM-dd HH:mm')))"
        }
        return
    }
    
    Write-Host "♻️ 从备份恢复 - $BackupTag" -ForegroundColor Yellow
    Write-Host ""
    
    $backupFile = Join-Path $BackupPath "$BackupTag.zip"
    if (-not (Test-Path $backupFile)) {
        Write-Host "❌ 备份文件不存在: $backupFile" -ForegroundColor Red
        return
    }
    
    # 创建当前状态备份
    Write-Host "💾 创建恢复前备份..."
    $preRestoreBackup = Invoke-BackupManagement -BackupTag "pre-restore-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    
    # 恢复备份
    Write-Host "📂 恢复标准文档..."
    $tempDir = Join-Path $env:TEMP "standards-restore-temp"
    Expand-Archive -Path $backupFile -DestinationPath $tempDir -Force
    
    # 删除现有文档并恢复
    Remove-Item "$StandardsPath/*" -Force -Recurse
    Copy-Item -Path "$tempDir/*" -Destination $StandardsPath -Recurse -Force
    Remove-Item -Path $tempDir -Recurse -Force
    
    Write-Host "✅ 恢复完成" -ForegroundColor Green
    Write-Host "🔍 验证恢复结果..."
    
    # 验证恢复结果
    & "scripts/validate_standards.ps1" -Action full | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 恢复后验证通过" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 恢复后验证发现问题" -ForegroundColor Yellow
    }
    
    Write-Host "💡 恢复前备份已保存: $preRestoreBackup"
}

# 主执行逻辑
try {
    switch ($Action) {
        "check" { 
            $result = Invoke-HealthCheck -SingleFile $Target
            exit $(if ($result.Success) { 0 } else { 1 })
        }
        "update" { 
            Invoke-VersionUpdate -UpdateTarget $(if ($Target) { $Target } else { "version" })
        }
        "report" { 
            $reportFile = Invoke-StatusReport -ReportType $(if ($Target) { $Target } else { "summary" })
            Write-Host "📄 报告路径: $reportFile" -ForegroundColor Cyan
        }
        "backup" { 
            $backupPath = Invoke-BackupManagement -BackupTag $(if ($Target) { $Target } else { "manual-$(Get-Date -Format 'yyyyMMdd-HHmmss')" })
            Write-Host "💾 备份路径: $backupPath" -ForegroundColor Cyan
        }
        "restore" { 
            Invoke-RestoreManagement -BackupTag $Target
        }
    }
    
    Write-Host ""
    Write-Host "🎉 维护操作完成" -ForegroundColor Green
} catch {
    Write-Host "❌ 维护操作失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
