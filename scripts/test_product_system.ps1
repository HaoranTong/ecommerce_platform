#!/usr/bin/env pwsh#!/usr/bin/env pwsh

<#<#

.SYNOPSIS.SYNOPSIS

产品目录系统测试脚本 - 已弃用产品目录系统测试脚本 - 已弃用



.DESCRIPTION.DESCRIPTION

⚠️  此脚本已弃用！请使用统一的模块测试脚本。⚠️  此脚本已弃用！请使用统一的模块测试脚本。



新的使用方式:新的使用方式:

    scripts\run_module_tests.ps1 -ModuleName "product_catalog" -TestType "all"    scripts\run_module_tests.ps1 -ModuleName "product_catalog" -TestType "all"

    scripts\run_module_tests.ps1 -ModuleName "product_catalog" -TestType "unit"    scripts\run_module_tests.ps1 -ModuleName "product_catalog" -TestType "unit"

    scripts\run_module_tests.ps1 -ModuleName "product_catalog" -TestType "integration"    scripts\run_module_tests.ps1 -ModuleName "product_catalog" -TestType "integration"



优势:优势:

- 统一的测试执行流程- 统一的测试执行流程

- 更好的参数标准化- 更好的参数标准化

- 与pytest-mock迁移完全兼容- 与pytest-mock迁移完全兼容

- 支持所有模块的一致性测试- 支持所有模块的一致性测试



.NOTES.NOTES

状态: 已弃用 (Deprecated)状态: 已弃用 (Deprecated)

替代方案: run_module_tests.ps1替代方案: run_module_tests.ps1

弃用日期: 2025-09-21弃用日期: 2025-09-21

删除计划: 2025-10-21删除计划: 2025-10-21

#>#>



param(param(

    [string]$TestType = "all",          # 测试类型: all, unit, integration, e2e, smoke    [string]$TestType = "all",          # 测试类型: all, unit, integration, e2e, smoke

    [string]$Environment = "test",      # 环境: test, staging    [string]$Environment = "test",      # 环境: test, staging

    [switch]$Coverage = $false,         # 是否生成覆盖率报告    [switch]$Coverage = $false,         # 是否生成覆盖率报告

    [switch]$Verbose = $false,          # 详细输出    [switch]$Verbose = $false,          # 详细输出

    [switch]$FailFast = $false,         # 遇到失败立即停止    [switch]$FailFast = $false,         # 遇到失败立即停止

    [int]$Workers = 4                   # 并行工作进程数    [int]$Workers = 4                   # 并行工作进程数

))



Write-Host "⚠️  此脚本已弃用！" -ForegroundColor YellowWrite-Host "⚠️  此脚本已弃用！" -ForegroundColor Yellow

Write-Host "请使用新的统一模块测试脚本:" -ForegroundColor CyanWrite-Host "请使用新的统一模块测试脚本:" -ForegroundColor Cyan

Write-Host ""Write-Host ""

Write-Host "推荐用法:" -ForegroundColor GreenWrite-Host "推荐用法:" -ForegroundColor Green

Write-Host "  scripts\run_module_tests.ps1 -ModuleName 'product_catalog' -TestType '$TestType'" -ForegroundColor WhiteWrite-Host "  scripts\run_module_tests.ps1 -ModuleName 'product_catalog' -TestType '$TestType'" -ForegroundColor White

Write-Host ""Write-Host ""

Write-Host "参数映射:" -ForegroundColor CyanWrite-Host "参数映射:" -ForegroundColor Cyan

Write-Host "  -TestType '$TestType' → 保持不变" -ForegroundColor GrayWrite-Host "  -TestType '$TestType' → 保持不变" -ForegroundColor Gray

Write-Host "  -Coverage → 内置支持" -ForegroundColor GrayWrite-Host "  -Coverage → 内置支持" -ForegroundColor Gray

Write-Host "  -Verbose → 内置支持" -ForegroundColor GrayWrite-Host "  -Verbose → 内置支持" -ForegroundColor Gray

Write-Host "  -FailFast → pytest --maxfail=1" -ForegroundColor GrayWrite-Host "  -FailFast → pytest --maxfail=1" -ForegroundColor Gray

Write-Host "  -Workers → pytest -n $Workers" -ForegroundColor GrayWrite-Host "  -Workers → pytest -n $Workers" -ForegroundColor Gray

Write-Host ""Write-Host ""



$ConfirmMigration = Read-Host "是否自动执行推荐命令? (y/N)"$ConfirmMigration = Read-Host "是否自动执行推荐命令? (y/N)"



if ($ConfirmMigration -eq "y" -or $ConfirmMigration -eq "Y") {if ($ConfirmMigration -eq "y" -or $ConfirmMigration -eq "Y") {

    Write-Host "🔄 执行统一模块测试命令..." -ForegroundColor Green    Write-Host "🔄 执行统一模块测试命令..." -ForegroundColor Green

        

    $NewScriptPath = Join-Path $PSScriptRoot "run_module_tests.ps1"    $NewScriptPath = Join-Path $PSScriptRoot "run_module_tests.ps1"

    $Arguments = @("-ModuleName", "product_catalog", "-TestType", $TestType)    $Arguments = @("-ModuleName", "product_catalog", "-TestType", $TestType)

        

    if ($Verbose) { $Arguments += "-Verbose" }    if ($Verbose) { $Arguments += "-Verbose" }

        

    & $NewScriptPath @Arguments    & $NewScriptPath @Arguments

} else {} else {

    Write-Host "❌ 已取消执行" -ForegroundColor Red    Write-Host "❌ 已取消执行" -ForegroundColor Red

    Write-Host "💡 请手动运行推荐的命令" -ForegroundColor Yellow    Write-Host "💡 请手动运行推荐的命令" -ForegroundColor Yellow

    exit 1    exit 1

}}

# 检查环境
Write-Info "🔍 检查测试环境..."

# 1. 检查虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Error "虚拟环境不存在，请先创建虚拟环境"
    exit 1
}

Write-Success "虚拟环境检查通过"

# 2. 激活虚拟环境
Write-Info "🔧 激活虚拟环境..."
& .\.venv\Scripts\Activate.ps1

# 3. 检查依赖包
Write-Info "📦 检查测试依赖包..."
$RequiredPackages = @("pytest", "pytest-cov", "fastapi", "sqlalchemy")
foreach ($package in $RequiredPackages) {
    try {
        $importCmd = "import ${package}; print('${package}: OK')"
        $result = & python -c $importCmd 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success $result
        } else {
            Write-Error "缺少依赖包: $package"
            Write-Info "请运行: pip install $package"
            exit 1
        }
    }
    catch {
        Write-Error "依赖包检查失败: $package"
        exit 1
    }
}

# 4. 检查测试文件
Write-Info "📁 检查测试文件结构..."
$TestFiles = @{
    "单元测试" = "tests\test_product_catalog.py"
    "集成测试" = "tests\test_product_catalog_integration.py" 
    "端到端测试" = "tests\e2e\test_product_workflow_e2e.py"
}

foreach ($type in $TestFiles.Keys) {
    $file = $TestFiles[$type]
    if (Test-Path $file) {
        Write-Success "$type 文件存在: $file"
    } else {
        Write-Warning "$type 文件不存在: $file"
    }
}

# 构建pytest命令
function Build-PytestCommand {
    param(
        [string]$TestPath,
        [string]$TestName,
        [bool]$IncludeCoverage = $false
    )
    
    $cmd = "python -m pytest `"$TestPath`""
    
    if ($Verbose) { $cmd += " -v" }
    if ($FailFast) { $cmd += " -x" }
    if ($Workers -gt 1) { $cmd += " -n $Workers" }
    
    if ($IncludeCoverage) {
        $cmd += " --cov=app.modules.product_catalog"
        $cmd += " --cov-report=html:htmlcov/$TestName"
        $cmd += " --cov-report=term-missing"
        $cmd += " --cov-report=xml:coverage-$TestName.xml"
    }
    
    return $cmd
}

# 执行测试函数
function Execute-Test {
    param(
        [string]$TestType,
        [string]$TestPath,
        [string]$TestName
    )
    
    Write-ColorOutput "`n🧪 执行$TestType..." "Yellow"
    Write-ColorOutput "=" * 40 "Gray"
    
    if (-not (Test-Path $TestPath)) {
        Write-Warning "$TestType 文件不存在: $TestPath"
        return $false
    }
    
    $startTime = Get-Date
    $command = Build-PytestCommand -TestPath $TestPath -TestName $TestName -IncludeCoverage $Coverage
    
    Write-Info "执行命令: $command"
    
    try {
        Invoke-Expression $command
        $success = $LASTEXITCODE -eq 0
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        if ($success) {
            Write-Success "$TestType 执行成功 (耗时: $($duration.ToString('F2'))秒)"
        } else {
            Write-Error "$TestType 执行失败 (耗时: $($duration.ToString('F2'))秒)"
        }
        
        return $success
    }
    catch {
        Write-Error "$TestType 执行异常: $($_.Exception.Message)"
        return $false
    }
}

# 主测试执行逻辑
$testResults = @{}
$overallSuccess = $true

Write-ColorOutput "`n🚀 开始执行测试..." "Green"

switch ($TestType.ToLower()) {
    "unit" {
        Write-Info "执行单元测试..."
        $result = Execute-Test -TestType "单元测试" -TestPath "tests\test_product_catalog.py" -TestName "unit"
        $testResults["单元测试"] = $result
        $overallSuccess = $overallSuccess -and $result
    }
    
    "integration" {
        Write-Info "执行集成测试..."
        $result = Execute-Test -TestType "集成测试" -TestPath "tests\test_product_catalog_integration.py" -TestName "integration"
        $testResults["集成测试"] = $result
        $overallSuccess = $overallSuccess -and $result
    }
    
    "e2e" {
        Write-Info "执行端到端测试..."
        $result = Execute-Test -TestType "端到端测试" -TestPath "tests\e2e\test_product_workflow_e2e.py" -TestName "e2e"
        $testResults["端到端测试"] = $result
        $overallSuccess = $overallSuccess -and $result
    }
    
    "smoke" {
        Write-Info "执行烟雾测试..."
        # 烟雾测试：快速验证核心功能
        $smokeTestPath = "tests\test_product_catalog.py::TestCategoryModel::test_create_category_success"
        $result = Execute-Test -TestType "烟雾测试" -TestPath $smokeTestPath -TestName "smoke"
        $testResults["烟雾测试"] = $result
        $overallSuccess = $overallSuccess -and $result
    }
    
    "all" {
        Write-Info "执行完整测试套件..."
        
        # 1. 单元测试
        $unitResult = Execute-Test -TestType "单元测试" -TestPath "tests\test_product_catalog.py" -TestName "unit"
        $testResults["单元测试"] = $unitResult
        $overallSuccess = $overallSuccess -and $unitResult
        
        if (-not $unitResult -and $FailFast) {
            Write-Error "单元测试失败，停止后续测试"
            break
        }
        
        # 2. 集成测试 
        $integrationResult = Execute-Test -TestType "集成测试" -TestPath "tests\test_product_catalog_integration.py" -TestName "integration"
        $testResults["集成测试"] = $integrationResult
        $overallSuccess = $overallSuccess -and $integrationResult
        
        if (-not $integrationResult -and $FailFast) {
            Write-Error "集成测试失败，停止后续测试"
            break
        }
        
        # 3. 端到端测试
        $e2eResult = Execute-Test -TestType "端到端测试" -TestPath "tests\e2e\test_product_workflow_e2e.py" -TestName "e2e"
        $testResults["端到端测试"] = $e2eResult
        $overallSuccess = $overallSuccess -and $e2eResult
    }
    
    default {
        Write-Error "未知的测试类型: $TestType"
        Write-Info "支持的测试类型: all, unit, integration, e2e, smoke"
        exit 1
    }
}

# 生成测试报告
Write-ColorOutput "`n📊 测试结果汇总" "Magenta"
Write-ColorOutput "=" * 50 "Gray"

foreach ($testType in $testResults.Keys) {
    $result = $testResults[$testType]
    if ($result) {
        Write-Success "$testType : 通过"
    } else {
        Write-Error "$testType : 失败"
    }
}

Write-ColorOutput ""

# 覆盖率报告
if ($Coverage) {
    Write-ColorOutput "📈 覆盖率报告" "Cyan"
    Write-ColorOutput "-" * 30 "Gray"
    
    if (Test-Path "htmlcov") {
        Write-Success "HTML覆盖率报告已生成: htmlcov/"
        Write-Info "在浏览器中打开: htmlcov/index.html"
    }
    
    $xmlFiles = Get-ChildItem -Path "." -Name "coverage-*.xml" -ErrorAction SilentlyContinue
    if ($xmlFiles) {
        Write-Success "XML覆盖率报告: $($xmlFiles -join ', ')"
    }
    
    Write-ColorOutput ""
}

# 性能统计
Write-ColorOutput "⚡ 性能统计" "Cyan" 
Write-ColorOutput "-" * 20 "Gray"
Write-Info "测试执行环境: Windows PowerShell"
Write-Info "并行工作进程: $Workers"
Write-Info "Python版本: $(python --version)"
Write-Info "pytest版本: $(python -c 'import pytest; print(pytest.__version__)')"

# 清理临时文件
Write-Info "🧹 清理临时文件..."
$tempFiles = @("*.db", "*.db-journal", ".pytest_cache")
foreach ($pattern in $tempFiles) {
    Get-ChildItem -Path "." -Name $pattern -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
}
Write-Success "临时文件清理完成"

# 最终结果
Write-ColorOutput "`n" "White"
if ($overallSuccess) {
    Write-ColorOutput "🎉 所有测试执行成功！" "Green"
    Write-ColorOutput "产品目录模块测试通过，可以安全部署。" "Green"
    exit 0
} else {
    Write-ColorOutput "💥 测试执行失败！" "Red"
    Write-ColorOutput "请检查失败的测试并修复问题。" "Red"
    exit 1
}

# 使用示例注释
<#
使用示例：

# 执行所有测试
.\scripts\test_product_system.ps1

# 只执行单元测试
.\scripts\test_product_system.ps1 -TestType unit

# 执行测试并生成覆盖率报告
.\scripts\test_product_system.ps1 -Coverage

# 详细输出模式
.\scripts\test_product_system.ps1 -Verbose

# 快速失败模式
.\scripts\test_product_system.ps1 -FailFast

# 烟雾测试（快速验证）
.\scripts\test_product_system.ps1 -TestType smoke

# 并行执行（8个进程）
.\scripts\test_product_system.ps1 -Workers 8

# 组合使用
.\scripts\test_product_system.ps1 -TestType all -Coverage -Verbose -Workers 4
#>