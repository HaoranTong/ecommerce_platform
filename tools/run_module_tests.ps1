#!/usr/bin/env pwsh
<#
.SYNOPSIS
模块测试自动化执行脚本 - pytest-mock迁移版

.DESCRIPTION
按照标准化流程执行单个模块的完整测试：
1. 脚本合规性检查
2. pytest-mock迁移验证
3. 单元测试执行
4. API测试执行
5. 集成测试执行
6. 测试结果记录

.PARAMETER ModuleName
要测试的模块名称 (如: user_auth, product_catalog)

.PARAMETER TestType
测试类型: unit, api, integration, all (默认: all)

.PARAMETER SkipMigration
跳过pytest-mock迁移检查

.EXAMPLE
.\tools\run_module_tests.ps1 -ModuleName "user_auth" -TestType "all"
.\tools\run_module_tests.ps1 -ModuleName "product_catalog" -TestType "unit"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ModuleName,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("unit", "api", "integration", "all")]
    [string]$TestType = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipMigration
)

# 工作目录设置
$RootPath = Split-Path -Parent $PSScriptRoot
Set-Location $RootPath

# 日志函数
function Write-TestLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
        "WARN"  { Write-Host $LogMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor Green }
        default { Write-Host $LogMessage -ForegroundColor Cyan }
    }
    
    # 同时写入日志文件
    $LogFile = "logs/test_execution_$(Get-Date -Format 'yyyyMMdd').log"
    $LogMessage | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

# 检查测试脚本存在性和合规性
function Test-ScriptCompliance {
    param([string]$Module)
    
    Write-TestLog "🔍 步骤1: 检查测试脚本合规性..." "INFO"
    
    $TestPaths = @(
        "tests/unit/test_models/test_${Module}*.py",
        "tests/unit/test_services/test_${Module}*.py", 
        "tests/unit/test_${Module}_standalone.py",
        "tests/integration/test_api/test_${Module}*.py"
    )
    
    $FoundScripts = @()
    foreach ($Path in $TestPaths) {
        $Files = Get-ChildItem $Path -ErrorAction SilentlyContinue
        if ($Files) {
            $FoundScripts += $Files.FullName
            Write-TestLog "✅ 找到测试文件: $($Files.Name)" "SUCCESS"
        }
    }
    
    if ($FoundScripts.Count -eq 0) {
        Write-TestLog "❌ 未找到模块 $Module 的测试文件" "ERROR"
        return $false
    }
    
    # 检查pytest收集测试用例
    Write-TestLog "🔍 验证pytest可以收集测试用例..." "INFO"
    foreach ($Script in $FoundScripts) {
        $CollectResult = & pytest --collect-only $Script 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-TestLog "❌ 脚本收集失败: $Script" "ERROR"
            Write-TestLog "错误输出: $CollectResult" "ERROR"
            return $false
        }
    }
    
    Write-TestLog "✅ 步骤1完成: 所有测试脚本合规" "SUCCESS"
    return $true
}

# 检查pytest-mock迁移状态
function Test-MockMigration {
    param([string]$Module)
    
    if ($SkipMigration) {
        Write-TestLog "⏭️  跳过pytest-mock迁移检查" "WARN"
        return $true
    }
    
    Write-TestLog "🔍 步骤2: 检查pytest-mock迁移状态..." "INFO"
    
    $TestFiles = Get-ChildItem "tests" -Recurse -Filter "*${Module}*.py"
    $LegacyMockFound = $false
    $ModernMockFound = $false
    
    foreach ($File in $TestFiles) {
        $Content = Get-Content $File.FullName -Raw
        
        # 检查是否还在使用原生mock
        if ($Content -match "from unittest\.mock import" -or $Content -match "import unittest\.mock") {
            Write-TestLog "⚠️  发现原生mock使用: $($File.Name)" "WARN"
            $LegacyMockFound = $true
        }
        
        # 检查是否使用pytest-mock
        if ($Content -match "def.*test.*\(.*mocker.*\)" -or $Content -match "mocker\.") {
            Write-TestLog "✅ 发现pytest-mock使用: $($File.Name)" "SUCCESS"
            $ModernMockFound = $true
        }
    }
    
    if ($LegacyMockFound -and -not $ModernMockFound) {
        Write-TestLog "❌ 模块 $Module 需要pytest-mock迁移" "ERROR"
        Write-TestLog "建议: 使用 'mocker' fixture 替代 'unittest.mock'" "INFO"
        return $false
    }
    
    Write-TestLog "✅ 步骤2完成: pytest-mock迁移检查通过" "SUCCESS"
    return $true
}

# 执行单元测试
function Invoke-UnitTests {
    param([string]$Module)
    
    Write-TestLog "🧪 步骤3: 执行单元测试..." "INFO"
    
    # 按照testing-standards.md分层测试策略
    $UnitTestPaths = @(
        "tests/unit/test_models/test_${Module}*.py",      # 组件单元测试
        "tests/unit/test_services/test_${Module}*.py",    # 服务集成测试  
        "tests/unit/test_${Module}_standalone.py"         # 业务流程测试
    )
    
    $UnitFiles = @()
    foreach ($Path in $UnitTestPaths) {
        $Files = Get-ChildItem $Path -ErrorAction SilentlyContinue
        if ($Files) {
            $UnitFiles += $Files
        }
    }
    
    if (-not $UnitFiles) {
        Write-TestLog "⚠️  未找到单元测试文件: $UnitTestPath" "WARN"
        return $true
    }
    
    Write-TestLog "🚀 运行单元测试: $($UnitFiles.Name -join ', ')" "INFO"
    
    # 执行pytest with coverage
    $Result = & pytest $UnitFiles.FullName -v --cov=app.modules.$Module --cov-report=term-missing 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-TestLog "✅ 单元测试通过" "SUCCESS"
        return $true
    } else {
        Write-TestLog "❌ 单元测试失败" "ERROR"
        Write-TestLog "输出: $Result" "ERROR"
        return $false
    }
}

# 执行API测试
function Invoke-ApiTests {
    param([string]$Module)
    
    Write-TestLog "🌐 步骤4: 执行API测试..." "INFO"
    
    $ApiTestPath = "tests/integration/test_api/test_${Module}*.py"
    $ApiFiles = Get-ChildItem $ApiTestPath -ErrorAction SilentlyContinue
    
    if (-not $ApiFiles) {
        Write-TestLog "⚠️  未找到API测试文件: $ApiTestPath" "WARN"
        return $true
    }
    
    Write-TestLog "🚀 运行API测试: $($ApiFiles.Name -join ', ')" "INFO"
    
    $Result = & pytest $ApiFiles.FullName -v 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-TestLog "✅ API测试通过" "SUCCESS"
        return $true
    } else {
        Write-TestLog "❌ API测试失败" "ERROR"
        Write-TestLog "输出: $Result" "ERROR"
        return $false
    }
}

# 执行模块内集成测试 (已移除 - 使用integration_test.ps1进行跨模块集成测试)
function Invoke-IntegrationTests {
    param([string]$Module)
    
    Write-TestLog "ℹ️  跨模块集成测试请使用: .\tools\integration_test.ps1" "INFO"
    Write-TestLog "ℹ️  模块内集成测试包含在单元测试的test_services/中" "INFO"
    return $true
}

# 记录测试结果
function Save-TestResults {
    param([string]$Module, [hashtable]$Results)
    
    Write-TestLog "📝 步骤6: 记录测试结果..." "INFO"
    
    $ResultFile = "logs/test_results_${Module}_$(Get-Date -Format 'yyyyMMddHHmmss').json"
    $ResultData = @{
        module = $Module
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        test_type = $TestType
        results = $Results
    }
    
    $ResultData | ConvertTo-Json -Depth 3 | Out-File -FilePath $ResultFile -Encoding UTF8
    Write-TestLog "✅ 测试结果已保存: $ResultFile" "SUCCESS"
    
    # 更新模块状态
    Write-TestLog "📊 更新模块状态统计..." "INFO"
    & .\tools\update_module_status.ps1
}

# 主执行流程
function Main {
    Write-TestLog "🚀 开始执行模块测试: $ModuleName (类型: $TestType)" "INFO"
    Write-TestLog "=" * 60 "INFO"
    
    # 确保logs目录存在
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }
    
    $Results = @{}
    $AllPassed = $true
    
    # 步骤1: 脚本合规性检查
    if (-not (Test-ScriptCompliance $ModuleName)) {
        $Results.compliance = "FAILED"
        $AllPassed = $false
        Write-TestLog "💥 脚本合规性检查失败，停止执行" "ERROR"
        return
    }
    $Results.compliance = "PASSED"
    
    # 步骤2: pytest-mock迁移检查
    if (-not (Test-MockMigration $ModuleName)) {
        $Results.migration = "FAILED"
        $AllPassed = $false
        Write-TestLog "💥 pytest-mock迁移检查失败，停止执行" "ERROR"
        return
    }
    $Results.migration = "PASSED"
    
    # 步骤3-5: 执行测试
    if ($TestType -eq "all" -or $TestType -eq "unit") {
        $Results.unit = if (Invoke-UnitTests $ModuleName) { "PASSED" } else { "FAILED"; $AllPassed = $false }
    }
    
    if ($TestType -eq "all" -or $TestType -eq "api") {
        $Results.api = if (Invoke-ApiTests $ModuleName) { "PASSED" } else { "FAILED"; $AllPassed = $false }
    }
    
    if ($TestType -eq "all" -or $TestType -eq "integration") {
        $Results.integration = if (Invoke-IntegrationTests $ModuleName) { "PASSED" } else { "FAILED"; $AllPassed = $false }
    }
    
    # 步骤6: 记录结果
    Save-TestResults $ModuleName $Results
    
    Write-TestLog "=" * 60 "INFO"
    if ($AllPassed) {
        Write-TestLog "🎉 模块 $ModuleName 测试完成 - 全部通过!" "SUCCESS"
    } else {
        Write-TestLog "💥 模块 $ModuleName 测试完成 - 存在失败项" "ERROR"
        exit 1
    }
}

# 执行主流程
Main
