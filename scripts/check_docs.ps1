# 文档完整性检查脚本
# 用法: .\scripts\check_docs.ps1 [-Path <路径>] [-CheckModuleCompleteness] [-Detailed]

param(
    [Parameter(Mandatory = $false)]
    [string]$Path = "docs",           # 检查路径，默认检查整个docs目录
    
    [Parameter(Mandatory = $false)]
    [switch]$CheckModuleCompleteness = $false,  # 检查模块文档完整性
    
    [Parameter(Mandatory = $false)]
    [switch]$Detailed = $false        # 详细输出
)

# 文档检查配置
$DocumentConfig = @{
    # 模块必需的7个文档
    RequiredModuleDocs = @(
        "README.md",
        "overview.md",
        "requirements.md",
        "design.md",
        "api-spec.md",
        "api-implementation.md",
        "implementation.md"
    )
    
    # 核心文档路径
    CoreDocs = @(
        "docs\README.md",
        "docs\requirements\business.md",
        "docs\architecture\overview.md",
        "app\main.py"
    )
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    
    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Cyan" = [ConsoleColor]::Cyan
        "Magenta" = [ConsoleColor]::Magenta
        "White" = [ConsoleColor]::White
    }
    
    if ($colorMap.ContainsKey($Color)) {
        Write-Host $Message -ForegroundColor $colorMap[$Color]
    } else {
        Write-Host $Message
    }
}

function Test-ModuleDocumentCompleteness {
    param([string]$ModulePath)
    
    $moduleName = Split-Path $ModulePath -Leaf
    $issues = @()
    $warnings = @()
    
    Write-ColorOutput "🔍 检查模块: $moduleName" "Blue"
    
    # 检查必需文档
    foreach ($docName in $DocumentConfig.RequiredModuleDocs) {
        $docPath = Join-Path $ModulePath $docName
        
        if (-not (Test-Path $docPath)) {
            $issues += @{
                Type = "缺失文档"
                Module = $moduleName
                File = $docName
                Issue = "模块缺少必需文档"
                Severity = "Error"
            }
        } else {
            $docSize = (Get-Item $docPath).Length
            if ($docSize -eq 0) {
                $warnings += @{
                    Type = "空文档"
                    Module = $moduleName
                    File = $docName
                    Issue = "文档文件为空"
                    Severity = "Warning"
                }
            } elseif ($docSize -lt 100) {
                $warnings += @{
                    Type = "内容过少"
                    Module = $moduleName
                    File = $docName
                    Issue = "文档内容可能不完整（< 100字节）"
                    Severity = "Info"
                }
            }
        }
    }
    
    return @{
        Module = $moduleName
        Issues = $issues
        Warnings = $warnings
        Status = if ($issues.Count -eq 0) { "✅ 完整" } else { "❌ 不完整" }
        CompletionRate = "{0:P0}" -f (($DocumentConfig.RequiredModuleDocs.Count - $issues.Count) / $DocumentConfig.RequiredModuleDocs.Count)
    }
}

function Check-AllModulesCompleteness {
    $modulesPath = "docs\modules"
    
    if (-not (Test-Path $modulesPath)) {
        Write-ColorOutput "❌ 模块文档目录不存在: $modulesPath" "Red"
        return
    }
    
    $moduleDirectories = Get-ChildItem $modulesPath -Directory
    $results = @()
    
    Write-ColorOutput "`n📋 检查所有模块文档完整性" "Blue"
    Write-ColorOutput "=========================" "Blue"
    
    foreach ($moduleDir in $moduleDirectories) {
        $result = Test-ModuleDocumentCompleteness -ModulePath $moduleDir.FullName
        $results += $result
        
        if ($Detailed) {
            Write-ColorOutput "   $($result.Status) $($moduleDir.Name) (完成度: $($result.CompletionRate))" "Cyan"
            
            if ($result.Issues.Count -gt 0) {
                foreach ($issue in $result.Issues) {
                    Write-ColorOutput "      ❌ $($issue.File): $($issue.Issue)" "Red"
                }
            }
            
            if ($result.Warnings.Count -gt 0) {
                foreach ($warning in $result.Warnings) {
                    Write-ColorOutput "      ⚠️  $($warning.File): $($warning.Issue)" "Yellow"
                }
            }
        }
    }
    
    # 汇总报告
    $totalModules = $results.Count
    $completeModules = ($results | Where-Object { $_.Issues.Count -eq 0 }).Count
    $totalIssues = ($results | ForEach-Object { $_.Issues.Count } | Measure-Object -Sum).Sum
    $totalWarnings = ($results | ForEach-Object { $_.Warnings.Count } | Measure-Object -Sum).Sum
    
    Write-ColorOutput "`n📊 模块文档完整性汇总" "Blue"
    Write-ColorOutput "=========================" "Blue"
    Write-ColorOutput "📦 总模块数: $totalModules" "Cyan"
    Write-ColorOutput "✅ 完整模块: $completeModules" "Green"
    Write-ColorOutput "❌ 不完整模块: $($totalModules - $completeModules)" "Red"
    Write-ColorOutput "🔍 总问题数: $totalIssues" "Red"
    Write-ColorOutput "⚠️  总警告数: $totalWarnings" "Yellow"
    Write-ColorOutput "📈 整体完成率: $('{0:P0}' -f ($completeModules / $totalModules))" "Cyan"
    
    if ($totalIssues -gt 0) {
        Write-ColorOutput "`n🔧 修复建议:" "Blue"
        Write-ColorOutput "   使用以下命令为缺失文档的模块生成完整文档:" "Yellow"
        
        $incompleteModules = $results | Where-Object { $_.Issues.Count -gt 0 }
        foreach ($module in $incompleteModules) {
            Write-ColorOutput "   .\scripts\create_module_docs.ps1 -ModuleName $($module.Module) -Force" "Cyan"
        }
    }
}

Write-ColorOutput "📄 文档完整性检查工具" "Blue"
Write-ColorOutput "=========================" "Blue"

# 基础文档检查
Write-ColorOutput "🔍 检查路径: $Path" "Cyan"

if (Test-Path $Path) {
    # 检查文档数量
    $docCount = (Get-ChildItem $Path -Recurse -Filter "*.md").Count
    Write-ColorOutput "📋 发现 $docCount 个Markdown文档" "Cyan"
    
    # 检查空文档
    $emptyDocs = Get-ChildItem $Path -Recurse -Filter "*.md" | Where-Object { $_.Length -eq 0 }
    if ($emptyDocs.Count -gt 0) {
        Write-ColorOutput "⚠️  发现 $($emptyDocs.Count) 个空文档:" "Yellow"
        if ($Detailed) {
            $emptyDocs | ForEach-Object { Write-ColorOutput "   - $($_.FullName)" "Red" }
        }
    } else {
        Write-ColorOutput "✅ 没有空文档" "Green"
    }
} else {
    Write-ColorOutput "❌ 指定路径不存在: $Path" "Red"
}

# 检查核心文档
Write-ColorOutput "`n🏗️ 检查核心文档:" "Blue"
foreach ($doc in $DocumentConfig.CoreDocs) {
    if (Test-Path $doc) {
        $size = (Get-Item $doc).Length
        $sizeText = if ($size -gt 1024) { "$([math]::Round($size/1024, 1))KB" } else { "${size}字节" }
        Write-ColorOutput "✅ $doc ($sizeText)" "Green"
    } else {
        Write-ColorOutput "❌ $doc (缺失)" "Red"
    }
}

# 模块文档完整性检查
if ($CheckModuleCompleteness) {
    Check-AllModulesCompleteness
}

# 检查文档结构一致性
Write-ColorOutput "`n🔗 检查文档结构一致性:" "Blue"
$docStructureIssues = @()

# 检查docs目录结构
$expectedDirs = @("modules", "architecture", "standards", "templates", "development", "operations", "requirements", "status", "analysis", "core", "shared")
foreach ($dir in $expectedDirs) {
    $dirPath = Join-Path "docs" $dir
    if (-not (Test-Path $dirPath)) {
        $docStructureIssues += "缺少目录: $dirPath"
    } else {
        Write-ColorOutput "✅ 目录存在: $dir" "Green"
    }
}

if ($docStructureIssues.Count -gt 0) {
    Write-ColorOutput "⚠️  发现 $($docStructureIssues.Count) 个结构问题:" "Yellow"
    foreach ($issue in $docStructureIssues) {
        Write-ColorOutput "   - $issue" "Red"
    }
} else {
    Write-ColorOutput "✅ 文档目录结构完整" "Green"
}

# 输出总结
Write-ColorOutput "`n📊 检查结果总结:" "Blue"
Write-ColorOutput "=========================" "Blue"

$totalIssues = 0
if ($emptyDocs.Count -gt 0) { $totalIssues += $emptyDocs.Count }
if ($docStructureIssues.Count -gt 0) { $totalIssues += $docStructureIssues.Count }

if ($totalIssues -eq 0) {
    Write-ColorOutput "🎉 所有检查通过！文档结构完整且规范。" "Green"
} else {
    Write-ColorOutput "⚠️  发现 $totalIssues 个问题需要修复。" "Yellow"
    Write-ColorOutput "`n🔧 建议的修复操作:" "Blue"
    Write-ColorOutput "   1. 使用 .\scripts\create_module_docs.ps1 补全缺失的模块文档" "Cyan"
    Write-ColorOutput "   2. 填充空文档的内容" "Cyan"
    Write-ColorOutput "   3. 创建缺失的目录结构" "Cyan"
}

Write-ColorOutput "`n✨ 文档检查完成！" "Green"
