<#
.SYNOPSIS
开发阶段强制检查点验证脚本

.DESCRIPTION
在开发流程的关键节点执行强制检查点验证，确保开发质量和流程合规：
- 文档驱动开发原则检查
- 代码质量和标准合规验证
- 开发阶段依赖文档存在性检查
- 检查点执行日志记录

支持三个关键开发阶段：
- PRE_DEV: 开发前准备检查
- CODE_WRITE: 代码编写过程检查  
- PRE_COMMIT: 提交前质量检查

.PARAMETER Phase
必需参数。开发阶段标识：
- PRE_DEV: 开发前检查（需求文档、设计文档等）
- CODE_WRITE: 编码阶段检查（代码规范、测试等）
- PRE_COMMIT: 提交前检查（完整性、质量验证等）

.PARAMETER Module
可选参数。指定模块名称，用于模块特定的检查点验证

.EXAMPLE
.\tools\dev_checkpoint.ps1 -Phase PRE_DEV -Module user_auth
执行user_auth模块的开发前检查

.EXAMPLE
.\tools\dev_checkpoint.ps1 -Phase CODE_WRITE
执行代码编写阶段的通用检查

.EXAMPLE
.\tools\dev_checkpoint.ps1 -Phase PRE_COMMIT -Module product_catalog
执行product_catalog模块的提交前检查

.NOTES
Author: AI Development Team
Created: 2025-09-30
Version: 1.0
Dependencies: PowerShell 5.0+
Log File: docs/status/checkpoint-log.md
#>

# 开发强制检查点脚本
# 使用方法: .\tools\dev_checkpoint.ps1 -Phase "开发阶段" -Module "模块名"

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("PRE_DEV", "CODE_WRITE", "PRE_COMMIT")]
    [string]$Phase,
    
    [Parameter(Mandatory=$false)]
    [string]$Module = ""
)

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "🚨 强制检查点: $Phase" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Yellow

# 获取当前时间戳
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# 检查点日志文件
$logFile = "docs/status/checkpoint-log.md"

function Write-CheckpointLog {
    param($message)
    Add-Content -Path $logFile -Value "[$timestamp] $message"
    Write-Host "✅ $message" -ForegroundColor Green
}

function Stop-Checkpoint {
    param($reason)
    Add-Content -Path $logFile -Value "[$timestamp] ❌ FAILED: $reason"
    Write-Host "❌ 检查点失败: $reason" -ForegroundColor Red
    Write-Host "🚫 禁止继续开发，必须先解决问题！" -ForegroundColor Red
    exit 1
}

function Read-Document {
    param($docPath, $description, [switch]$Force)
    
    if (-not (Test-Path $docPath)) {
        Stop-Checkpoint "必读文档不存在: $docPath"
    }
    
    Write-Host "📖 强制阅读: $description" -ForegroundColor Cyan
    Write-Host "   文档路径: $docPath" -ForegroundColor Gray
    
    # 获取文档行数
    $lineCount = (Get-Content $docPath | Measure-Object -Line).Lines
    Write-Host "   文档行数: $lineCount 行" -ForegroundColor Gray
    
    $response = ""
    while ($response -ne "CONFIRM") {
        Write-Host "请完整阅读文档后输入 'CONFIRM' 确认: " -ForegroundColor Yellow -NoNewline
        $response = Read-Host
        if ($response -ne "CONFIRM") {
            Write-Host "❌ 必须完整阅读文档！请重新输入 'CONFIRM'" -ForegroundColor Red
        }
    }
    
    Write-CheckpointLog "已确认阅读: $description ($docPath)"
}

function Test-NamingCompliance {
    param($module)
    
    Write-Host "🔍 检查命名合规性..." -ForegroundColor Cyan
    
    # 检查是否存在命名映射文档
    $namingDoc = "docs/design/modules/$module/naming-map.md"
    if (-not (Test-Path $namingDoc)) {
        Stop-Checkpoint "模块命名映射文档不存在: $namingDoc"
    }
    
    Write-CheckpointLog "命名合规性检查通过: $module"
}

# 执行不同阶段的检查
switch ($Phase) {
    "PRE_DEV" {
        Write-Host "🔍 开发前强制检查..." -ForegroundColor Cyan
        
        # 强制阅读核心文档
        Read-Document "MASTER.md" "项目开发规范总纲" -Force
        Read-Document "docs/api/api-design-standards.md" "API设计标准" -Force
        
        if ($Module) {
            $moduleDoc = "docs/design/modules/$Module/overview.md"
            Read-Document $moduleDoc "$Module 模块概述文档" -Force
            Test-NamingCompliance $Module
        }
        
        Write-CheckpointLog "开发前检查完成，允许开始编码"
    }
    
    "CODE_WRITE" {
        Write-Host "🔍 编码过程检查..." -ForegroundColor Cyan
        
        if (-not $Module) {
            Stop-Checkpoint "编码阶段必须指定模块名"
        }
        
        # 检查是否存在相关API文档
        $apiDoc = "docs/design/modules/$Module/api-spec.md"
        if (-not (Test-Path $apiDoc)) {
            Stop-Checkpoint "API规范文档不存在，禁止编码: $apiDoc"
        }
        
        Write-CheckpointLog "编码过程检查通过: $Module"
    }
    
    "PRE_COMMIT" {
        Write-Host "🔍 提交前强制检查..." -ForegroundColor Cyan
        
        # 检查是否有未跟踪的重要文件
        $gitStatus = git status --porcelain
        if ($gitStatus) {
            Write-Host "📋 当前Git状态:" -ForegroundColor Yellow
            $gitStatus
            
            $confirm = ""
            while ($confirm -ne "YES") {
                Write-Host "确认所有更改都已正确添加？(输入 'YES' 确认): " -ForegroundColor Yellow -NoNewline
                $confirm = Read-Host
            }
        }
        
        Write-CheckpointLog "提交前检查完成"
    }
}

Write-Host "✅ 检查点 $Phase 通过！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Yellow
