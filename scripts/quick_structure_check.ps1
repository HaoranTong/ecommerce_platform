# 简化版架构检查脚本
param(
    [string]$CheckType = "all"
)

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Check-AppStructure {
    Write-ColorOutput "🔍 检查app目录结构..." "Blue"
    
    $issues = @()
    
    # 检查是否存在旧的三层架构目录
    $oldDirs = @("app/api", "app/models", "app/schemas", "app/services")
    foreach ($dir in $oldDirs) {
        if (Test-Path $dir) {
            $files = Get-ChildItem $dir -File -Recurse | Where-Object { $_.Extension -eq ".py" -and $_.Name -ne "__init__.py" }
            if ($files.Count -gt 0) {
                $issues += "❌ $dir 目录仍有 $($files.Count) 个未迁移的文件: $($files.Name -join ', ')"
            }
        }
    }
    
    # 检查根目录遗留文件
    $rootFiles = Get-ChildItem "app" -File | Where-Object { $_.Extension -eq ".py" -and $_.Name -notin @("main.py", "__init__.py") }
    if ($rootFiles.Count -gt 0) {
        $issues += "❌ app根目录有遗留文件: $($rootFiles.Name -join ', ')"
    }
    
    # 检查模块结构完整性
    $modules = Get-ChildItem "app/modules" -Directory
    $requiredFiles = @("__init__.py", "router.py", "service.py", "models.py", "schemas.py", "dependencies.py")
    
    foreach ($module in $modules) {
        $missingFiles = @()
        foreach ($file in $requiredFiles) {
            if (-not (Test-Path "$($module.FullName)/$file")) {
                $missingFiles += $file
            }
        }
        if ($missingFiles.Count -gt 0) {
            $issues += "❌ 模块 $($module.Name) 缺少文件: $($missingFiles -join ', ')"
        }
        
        # 检查README文件
        if (-not (Test-Path "$($module.FullName)/README.md")) {
            $issues += "❌ 模块 $($module.Name) 缺少 README.md"
        }
    }
    
    return $issues
}

# 执行检查
Write-ColorOutput "🚀 开始架构合规性检查..." "Yellow"
Write-ColorOutput "检查类型: $CheckType" "Gray"

$allIssues = Check-AppStructure

if ($allIssues.Count -eq 0) {
    Write-ColorOutput "✅ 架构结构检查通过！" "Green"
} else {
    Write-ColorOutput "❌ 发现 $($allIssues.Count) 个架构问题:" "Red"
    foreach ($issue in $allIssues) {
        Write-ColorOutput "  $issue" "Red"
    }
}

Write-ColorOutput "🔍 检查完成" "Yellow"