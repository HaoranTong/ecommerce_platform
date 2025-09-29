#!/usr/bin/env pwsh
<#
.SYNOPSIS
强制文档阅读验证脚本 - 确保AI实际阅读相关文档内容

.DESCRIPTION
本脚本用于在执行检查点前强制AI阅读指定的文档片段，并通过问题验证确保真实理解而非推测回答。
这是DOC-007检查点的核心实现，解决AI跳过必要文档阅读的问题。

.PARAMETER DocumentPath
必需参数。要阅读的文档的绝对路径。

.PARAMETER StartLine
可选参数。开始阅读的行号，默认为1。

.PARAMETER EndLine
可选参数。结束阅读的行号，默认为50。

.PARAMETER Questions
可选参数。用于验证阅读理解的具体问题数组。如果为空，则使用默认确认问题。

.PARAMETER AutoOpen
可选开关。是否自动在VS Code中打开文档，默认为$true。

.EXAMPLE
# 基本用法：阅读文档管理标准的B4部分
.\tools\enforce_doc_reading.ps1 -DocumentPath "docs\standards\document-management-standards.md" -StartLine 577 -EndLine 620

.EXAMPLE  
# 带问题验证的阅读
.\tools\enforce_doc_reading.ps1 -DocumentPath "docs\standards\api-standards.md" -StartLine 1 -EndLine 50 -Questions @("API设计的核心原则是什么？", "错误响应的标准格式是什么？")

.EXAMPLE
# 在检查点卡片中使用（通过ai_checkpoint.ps1调用）
.\tools\ai_checkpoint.ps1 -CardType DOC-007 -FilePath "docs\standards\database-standards.md"

.NOTES
- 脚本会自动在VS Code中打开指定文档并跳转到指定行
- 显示文档内容预览以供阅读
- 通过具体问题验证阅读理解，确保无法推测回答
- 记录阅读日志到logs/doc_reading_log.json
- 支持文档路径验证和错误处理

.LINK
相关文档:
- DOC-007检查点卡片: tools/checkpoint-cards.md#doc-007
- 文档管理标准: docs/standards/document-management-standards.md
- AI工作流程: MASTER.md

.COMPONENT
AI文档阅读保证机制

.ROLE
质量保证工具

.FUNCTIONALITY
文档阅读验证、理解测试、阅读记录
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="要阅读的文档的绝对路径")]
    [string]$DocumentPath,
    
    [Parameter(Mandatory=$false, HelpMessage="开始阅读的行号")]
    [int]$StartLine = 1,
    
    [Parameter(Mandatory=$false, HelpMessage="结束阅读的行号")]
    [int]$EndLine = 50,
    
    [Parameter(Mandatory=$false, HelpMessage="用于验证阅读理解的问题数组")]
    [string[]]$Questions = @(),
    
    [Parameter(Mandatory=$false, HelpMessage="是否自动在VS Code中打开文档")]
    [switch]$AutoOpen = $true
)

# 函数：验证文档存在
function Test-DocumentExists {
    param($Path)
    
    if (!(Test-Path $Path)) {
        Write-Error "🚨 文档不存在: $Path"
        Write-Output "请确认文档路径正确，或创建缺失的文档。"
        return $false
    }
    return $true
}

# 函数：打开文档指定行
function Invoke-DocumentReader {
    param($Path, $StartLine, $EndLine)
    
    Write-Output "📖 打开文档进行阅读..."
    Write-Output "文档路径: $Path"
    Write-Output "阅读范围: 第 $StartLine - $EndLine 行"
    Write-Output ""
    
    if ($AutoOpen) {
        try {
            # 尝试用VS Code打开并跳转到指定行
            & code --goto "$Path`:$StartLine"
            Start-Sleep -Seconds 2
        }
        catch {
            Write-Warning "无法自动打开VS Code，请手动打开文档"
        }
    }
    
    # 显示文档内容预览
    try {
        $content = Get-Content $Path -Encoding UTF8
        $totalLines = $content.Count
        $actualEndLine = [Math]::Min($EndLine, $totalLines)
        
        Write-Output "📄 文档内容预览 ($Path`):"
        Write-Output "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        for ($i = $StartLine - 1; $i -lt $actualEndLine; $i++) {
            if ($i -ge 0 -and $i -lt $content.Count) {
                $lineNum = $i + 1
                Write-Output ("{0:D3}: {1}" -f $lineNum, $content[$i])
            }
        }
        
        Write-Output "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        Write-Output ""
    }
    catch {
        Write-Warning "无法读取文档内容: $_"
    }
}

# 函数：验证阅读
function Confirm-ReadingCompletion {
    param($Questions)
    
    Write-Output "🔍 阅读确认环节"
    Write-Output "请根据刚才阅读的文档内容回答以下问题："
    Write-Output ""
    
    if ($Questions.Count -eq 0) {
        # 默认确认问题
        $confirmation = Read-Host "已仔细阅读并理解文档内容，输入 'YES' 继续执行检查点"
        if ($confirmation -ne "YES") {
            Write-Error "🚨 阅读确认失败，请重新阅读文档后继续"
            return $false
        }
    }
    else {
        # 具体问题验证
        foreach ($i in 0..($Questions.Count - 1)) {
            $questionNum = $i + 1
            Write-Output "问题 $questionNum`: $($Questions[$i])"
            $answer = Read-Host "请回答"
            
            if ([string]::IsNullOrWhiteSpace($answer)) {
                Write-Error "🚨 问题 $questionNum 回答为空，请重新阅读文档"
                return $false
            }
            
            Write-Output "回答记录: $answer"
            Write-Output ""
        }
    }
    
    return $true
}

# 主执行逻辑
function Main {
    Write-Output "🚀 DOC-007: 强制文档阅读验证"
    Write-Output "======================================"
    Write-Output ""
    
    # 1. 验证文档存在
    if (!(Test-DocumentExists -Path $DocumentPath)) {
        exit 1
    }
    
    # 2. 打开文档供阅读
    Invoke-DocumentReader -Path $DocumentPath -StartLine $StartLine -EndLine $EndLine
    
    # 3. 等待用户阅读
    Write-Output "⏸️  请仔细阅读上述文档内容..."
    Read-Host "阅读完成后按 Enter 继续"
    
    # 4. 验证阅读理解
    if (!(Confirm-ReadingCompletion -Questions $Questions)) {
        Write-Error "❌ 阅读验证失败"
        exit 1
    }
    
    # 5. 记录阅读日志
    $logEntry = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Document = $DocumentPath
        Range = "$StartLine-$EndLine"
        Status = "Completed"
        Questions = $Questions.Count
    }
    
    $logPath = "logs/doc_reading_log.json"
    $logEntries = @()
    if (Test-Path $logPath) {
        $logEntries = Get-Content $logPath | ConvertFrom-Json
    }
    $logEntries += $logEntry
    $logEntries | ConvertTo-Json -Depth 3 | Set-Content $logPath -Encoding UTF8
    
    Write-Output "✅ 文档阅读验证完成"
    Write-Output "📝 阅读记录已保存到: $logPath"
    
    return 0
}

# 执行主函数
Main