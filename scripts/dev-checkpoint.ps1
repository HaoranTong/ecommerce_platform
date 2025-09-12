# 开发强制检查点脚本
# 使用方法: .\scripts\dev-checkpoint.ps1 -Phase "开发阶段" -Module "模块名"

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

function Fail-Checkpoint {
    param($reason)
    Add-Content -Path $logFile -Value "[$timestamp] ❌ FAILED: $reason"
    Write-Host "❌ 检查点失败: $reason" -ForegroundColor Red
    Write-Host "🚫 禁止继续开发，必须先解决问题！" -ForegroundColor Red
    exit 1
}

function Force-ReadDocument {
    param($docPath, $description)
    
    if (-not (Test-Path $docPath)) {
        Fail-Checkpoint "必读文档不存在: $docPath"
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

function Check-NamingCompliance {
    param($module)
    
    Write-Host "🔍 检查命名合规性..." -ForegroundColor Cyan
    
    # 检查是否存在命名映射文档
    $namingDoc = "docs/modules/$module/naming-map.md"
    if (-not (Test-Path $namingDoc)) {
        Fail-Checkpoint "模块命名映射文档不存在: $namingDoc"
    }
    
    Write-CheckpointLog "命名合规性检查通过: $module"
}

# 执行不同阶段的检查
switch ($Phase) {
    "PRE_DEV" {
        Write-Host "🔍 开发前强制检查..." -ForegroundColor Cyan
        
        # 强制阅读核心文档
        Force-ReadDocument "MASTER.md" "项目开发规范总纲"
        Force-ReadDocument "docs/api/api-design-standards.md" "API设计标准"
        
        if ($Module) {
            $moduleDoc = "docs/modules/$Module/overview.md"
            Force-ReadDocument $moduleDoc "$Module 模块概述文档"
            Check-NamingCompliance $Module
        }
        
        Write-CheckpointLog "开发前检查完成，允许开始编码"
    }
    
    "CODE_WRITE" {
        Write-Host "🔍 编码过程检查..." -ForegroundColor Cyan
        
        if (-not $Module) {
            Fail-Checkpoint "编码阶段必须指定模块名"
        }
        
        # 检查是否存在相关API文档
        $apiDoc = "docs/modules/$Module/api-spec.md"
        if (-not (Test-Path $apiDoc)) {
            Fail-Checkpoint "API规范文档不存在，禁止编码: $apiDoc"
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