#!/usr/bin/env pwsh
<#
.SYNOPSIS
模块开发状态统计脚本 - 【需要更新为手动模式】

.DESCRIPTION
⚠️ 注意：根据MASTER.md要求，状态管理已改为手动更新模式
原功能：自动扫描app/modules目录，统计各模块的API端点数量、代码行数、文件结构等信息
新要求：需要调整为辅助手动更新的工具，而非自动更新

.NOTES  
状态：需要重构以符合手动更新流程
最后检查：2025-09-20

.PARAMETER OutputPath
输出文件路径，默认为docs/status/module-status.md

.PARAMETER Format
输出格式，支持markdown(默认)和json

.EXAMPLE
tools\update_module_status.ps1
tools\update_module_status.ps1 -OutputPath "custom-status.md"
tools\update_module_status.ps1 -Format json

.NOTES
创建时间: 2025-09-19
最后修改: 2025-09-19
依赖工具: PowerShell 5.0+
#>

param(
    [string]$OutputPath = "docs/status/module-status.md",
    [ValidateSet("markdown", "json")]
    [string]$Format = "markdown"
)

# 获取模块统计信息
function Get-ModuleStats {
    param([string]$ModulePath)
    
    $moduleName = Split-Path $ModulePath -Leaf
    $stats = @{
        Name = $moduleName
        ApiEndpoints = 0
        CodeLines = @{
            Router = 0
            Models = 0
            Schemas = 0
            Service = 0
            Total = 0
        }
        Files = @{
            Router = $false
            Models = $false
            Schemas = $false
            Service = $false
        }
        TestCoverage = "❓"
        CompletionRate = 0
        Status = "📝"
    }
    
    # 检查文件存在性和统计代码行数
    $files = @("router.py", "models.py", "schemas.py", "service.py")
    foreach ($file in $files) {
        $filePath = Join-Path $ModulePath $file
        if (Test-Path $filePath) {
            $stats.Files[$file.Replace('.py', '')] = $true
            $content = Get-Content $filePath -Raw -ErrorAction SilentlyContinue
            if ($content) {
                $lines = ($content -split "`n").Count
                $stats.CodeLines[$file.Replace('.py', '')] = $lines
                $stats.CodeLines.Total += $lines
                
                # 统计API端点（仅router.py）
                if ($file -eq "router.py") {
                    $endpoints = ([regex]::Matches($content, '@router\.(get|post|put|delete|patch)')).Count
                    $stats.ApiEndpoints = $endpoints
                }
            }
        }
    }
    
    # 根据API端点数量和文件完整性评估完成度
    if ($stats.ApiEndpoints -gt 0 -and $stats.Files.Router -and $stats.Files.Models) {
        if ($stats.ApiEndpoints -ge 10) {
            $stats.CompletionRate = 100
            $stats.Status = "✅"
        } elseif ($stats.ApiEndpoints -ge 5) {
            $stats.CompletionRate = 80
            $stats.Status = "🔄"
        } else {
            $stats.CompletionRate = 60
            $stats.Status = "🔄"
        }
    } elseif ($stats.Files.Router -or $stats.Files.Models) {
        $stats.CompletionRate = 30
        $stats.Status = "🔄"
    }
    
    return $stats
}

# 主执行逻辑
try {
    Write-Host "🔍 扫描模块目录..." -ForegroundColor Green
    
    $modulesPath = "app/modules"
    if (-not (Test-Path $modulesPath)) {
        throw "模块目录不存在: $modulesPath"
    }
    
    # 获取所有模块
    $moduleDirectories = Get-ChildItem -Path $modulesPath -Directory | Where-Object { $_.Name -notmatch "^(__pycache__|\.)" }
    $moduleStats = @()
    
    foreach ($moduleDir in $moduleDirectories) {
        Write-Host "  📊 统计模块: $($moduleDir.Name)" -ForegroundColor Cyan
        $stats = Get-ModuleStats -ModulePath $moduleDir.FullName
        $moduleStats += $stats
    }
    
    # 排序：按API端点数量降序
    $moduleStats = $moduleStats | Sort-Object ApiEndpoints -Descending
    
    if ($Format -eq "json") {
        # JSON输出
        $jsonOutput = @{
            UpdateTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            TotalModules = $moduleStats.Count
            CompletedModules = ($moduleStats | Where-Object { $_.Status -eq "✅" }).Count
            InProgressModules = ($moduleStats | Where-Object { $_.Status -eq "🔄" }).Count
            NotStartedModules = ($moduleStats | Where-Object { $_.Status -eq "📝" }).Count
            Modules = $moduleStats
        }
        
        $jsonOutput | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
        Write-Host "✅ JSON状态报告已生成: $OutputPath" -ForegroundColor Green
        return
    }
    
    # Markdown输出
    $currentDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $completedCount = ($moduleStats | Where-Object { $_.Status -eq "✅" }).Count
    $inProgressCount = ($moduleStats | Where-Object { $_.Status -eq "🔄" }).Count
    $notStartedCount = ($moduleStats | Where-Object { $_.Status -eq "📝" }).Count
    
    $markdown = @"
# 模块开发状态 (实时更新)

**最后更新**: $currentDate  
**统计工具**: tools\update_module_status.ps1

## 📊 整体进度

- **总模块数**: $($moduleStats.Count)
- **✅ 已完成**: $completedCount 个模块
- **🔄 开发中**: $inProgressCount 个模块  
- **📝 未开始**: $notStartedCount 个模块

**总体完成度**: $([math]::Round(($completedCount / $moduleStats.Count) * 100, 1))%

## 📋 模块详细状态

| 模块名称 | 状态 | API端点 | 总代码行数 | Router | Models | Schemas | Service | 完成度 |
|---------|------|---------|------------|--------|--------|---------|---------|--------|
"@

    foreach ($module in $moduleStats) {
        $routerLines = if ($module.Files.Router) { $module.CodeLines.Router } else { "-" }
        $modelsLines = if ($module.Files.Models) { $module.CodeLines.Models } else { "-" }
        $schemasLines = if ($module.Files.Schemas) { $module.CodeLines.Schemas } else { "-" }
        $serviceLines = if ($module.Files.Service) { $module.CodeLines.Service } else { "-" }
        
        $routerStatus = if ($module.Files.Router) { "✅" } else { "❌" }
        $modelsStatus = if ($module.Files.Models) { "✅" } else { "❌" }
        $schemasStatus = if ($module.Files.Schemas) { "✅" } else { "❌" }
        $serviceStatus = if ($module.Files.Service) { "✅" } else { "❌" }
        
        $markdown += "| $($module.Name) | $($module.Status) | $($module.ApiEndpoints) | $($module.CodeLines.Total) | $routerStatus $routerLines | $modelsStatus $modelsLines | $schemasStatus $schemasLines | $serviceStatus $serviceLines | $($module.CompletionRate)% |`n"
    }

    $markdown += @"

## 🎯 开发优先级建议

### 高优先级 (需要完善)
"@

    $inProgressModules = $moduleStats | Where-Object { $_.Status -eq "🔄" } | Select-Object -First 5
    foreach ($module in $inProgressModules) {
        $markdown += "- **$($module.Name)**: $($module.ApiEndpoints)个端点，需要完善"
        if (-not $module.Files.Models) { $markdown += " [缺少Models]" }
        if (-not $module.Files.Schemas) { $markdown += " [缺少Schemas]" }
        if (-not $module.Files.Service) { $markdown += " [缺少Service]" }
        $markdown += "`n"
    }

    $markdown += @"

### 待开发模块
"@

    $notStartedModules = $moduleStats | Where-Object { $_.Status -eq "📝" }
    foreach ($module in $notStartedModules) {
        $markdown += "- **$($module.Name)**: 待开始开发`n"
    }

    $markdown += @"

## 📈 质量指标

### 代码规模分布
- **大型模块** (>500行): $($moduleStats | Where-Object { $_.CodeLines.Total -gt 500 } | Measure-Object | Select-Object -ExpandProperty Count) 个
- **中型模块** (200-500行): $($moduleStats | Where-Object { $_.CodeLines.Total -ge 200 -and $_.CodeLines.Total -le 500 } | Measure-Object | Select-Object -ExpandProperty Count) 个
- **小型模块** (<200行): $($moduleStats | Where-Object { $_.CodeLines.Total -gt 0 -and $_.CodeLines.Total -lt 200 } | Measure-Object | Select-Object -ExpandProperty Count) 个

### API端点分布
- **大型API** (>10端点): $($moduleStats | Where-Object { $_.ApiEndpoints -gt 10 } | Measure-Object | Select-Object -ExpandProperty Count) 个
- **中型API** (5-10端点): $($moduleStats | Where-Object { $_.ApiEndpoints -ge 5 -and $_.ApiEndpoints -le 10 } | Measure-Object | Select-Object -ExpandProperty Count) 个
- **小型API** (1-4端点): $($moduleStats | Where-Object { $_.ApiEndpoints -ge 1 -and $_.ApiEndpoints -lt 5 } | Measure-Object | Select-Object -ExpandProperty Count) 个

## 📝 更新说明

### 自动更新内容
- API端点统计 (通过正则匹配@router装饰器)
- 代码行数统计 (router.py, models.py, schemas.py, service.py)
- 文件存在性检查
- 完成度自动评估

### 手动更新内容
- 测试覆盖率状态 (需要运行测试后手动更新)
- 特殊状态标记 (如技术债务、重构需求等)

### 更新规则
- **触发时机**: 每次模块代码提交后立即更新
- **更新命令**: `.\tools\update_module_status.ps1`
- **责任人**: 模块开发者负责及时更新

---
*此文档由自动化脚本生成，请不要手动编辑统计数据部分*
"@

    # 确保输出目录存在
    $outputDir = Split-Path $OutputPath -Parent
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    # 写入文件
    $markdown | Out-File -FilePath $OutputPath -Encoding UTF8
    
    Write-Host "✅ 模块状态报告已生成: $OutputPath" -ForegroundColor Green
    Write-Host "📊 统计结果: $($moduleStats.Count)个模块, $completedCount个已完成, $inProgressCount个开发中" -ForegroundColor Yellow
    
} catch {
    Write-Error "❌ 生成模块状态报告失败: $($_.Exception.Message)"
    exit 1
}
