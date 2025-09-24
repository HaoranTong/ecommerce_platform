# 测试环境综合检查脚本 (合并版)
# 在运行任何测试前，全面验证环境是否就绪
# 合并了diagnose_test_fixtures.ps1的fixture诊断功能

<#
.SYNOPSIS
    测试环境综合检查和fixture诊断

.DESCRIPTION
    本脚本提供全面的测试环境检查功能，确保测试前环境就绪：
    1. 检查Python虚拟环境
    2. 验证必要的Python包
    3. 检查测试文件结构
    4. 验证数据库连接能力
    5. pytest fixture依赖诊断 (合并自diagnose_test_fixtures.ps1)
    6. fixture作用域冲突检测

.PARAMETER Verbose
    显示详细的检查信息

.EXAMPLE
    .\scripts\check_test_env.ps1
    # 快速检查测试环境状态

.EXAMPLE
    .\scripts\check_test_env.ps1 -Verbose
    # 显示详细检查信息

.NOTES
    文件名: check_test_env.ps1
    作者: 系统架构师
    版本: 2.0.0 (合并版)
    创建日期: 2025-09-16
    更新日期: 2025-09-21 (合并fixture诊断功能)
    关联: [CHECK:TEST-002] ISS-024 fixture依赖冲突问题
#>

[CmdletBinding()]
param(
    [switch]$Verbose
)

Set-StrictMode -Version Latest

$script:ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$script:ChecksPassed = 0
$script:ChecksFailed = 0

function Write-CheckResult {
    param(
        [string]$Description,
        [bool]$Passed,
        [string]$Details = ""
    )
    
    if ($Passed) {
        Write-Host "✅ $Description" -ForegroundColor Green
        $script:ChecksPassed++
    } else {
        Write-Host "❌ $Description" -ForegroundColor Red
        if ($Details) {
            Write-Host "   $Details" -ForegroundColor Yellow
        }
        $script:ChecksFailed++
    }
}

Write-Host "🔍 快速测试环境检查" -ForegroundColor Cyan
Write-Host "=" * 40

# 1. 检查Python环境
try {
    $pythonPath = & python -c "import sys; print(sys.executable)" 2>$null
    $isVenv = $pythonPath -and $pythonPath.Contains(".venv")
    Write-CheckResult "Python虚拟环境" $isVenv "当前Python: $pythonPath"
} catch {
    Write-CheckResult "Python虚拟环境" $false "Python不可用"
}

# 2. 检查关键包
$packages = @("pytest", "sqlalchemy", "fastapi", "httpx")
foreach ($package in $packages) {
    try {
        & python -c "import $($package.replace('-', '_'))" 2>$null
        $packageOk = $LASTEXITCODE -eq 0
        Write-CheckResult "Python包: $package" $packageOk
    } catch {
        Write-CheckResult "Python包: $package" $false
    }
}

# 3. 检查测试目录结构
$testDirs = @("tests", "tests/unit", "tests/integration", "tests/e2e")
foreach ($dir in $testDirs) {
    $dirPath = Join-Path $script:ProjectRoot $dir
    $exists = Test-Path $dirPath
    Write-CheckResult "测试目录: $dir" $exists
}

# 4. 检查conftest.py
$conftestPath = Join-Path $script:ProjectRoot "tests/conftest.py"
$conftestExists = Test-Path $conftestPath
Write-CheckResult "pytest配置文件" $conftestExists

# 5. 快速SQLite测试
try {
    & python -c "
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:///:memory:')
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    assert result.fetchone()[0] == 1
print('SQLite OK')
" 2>$null
    $sqliteOk = $LASTEXITCODE -eq 0
    Write-CheckResult "SQLite数据库" $sqliteOk
} catch {
    Write-CheckResult "SQLite数据库" $false
}

# 6. pytest fixture依赖诊断 (合并自diagnose_test_fixtures.ps1)
$FixtureIssuesFound = 0

if ($conftestExists) {
    Write-Host "`n🔍 检查pytest fixture配置..." -ForegroundColor Cyan
    
    # 检查autouse fixture直接依赖
    $AutoUseFixtures = Select-String -Path $conftestPath -Pattern "@pytest\.fixture\(autouse=True\)" -Context 0,3 -ErrorAction SilentlyContinue
    
    foreach ($Match in $AutoUseFixtures) {
        $Context = $Match.Context.PostContext
        
        if ($Context -match "integration_test_engine") {
            Write-CheckResult "Fixture依赖配置" $false "autouse fixture直接依赖integration_test_engine (行 $($Match.LineNumber))"
            $FixtureIssuesFound++
        }
    }
    
    # 检查fixture作用域冲突
    $SessionFixtures = Select-String -Path $conftestPath -Pattern "scope=['""]session['""]" -ErrorAction SilentlyContinue
    $FunctionFixtures = Select-String -Path $conftestPath -Pattern "scope=['""]function['""]" -ErrorAction SilentlyContinue
    
    if ($SessionFixtures.Count -gt 0 -and $FunctionFixtures.Count -gt 0) {
        Write-CheckResult "Fixture作用域配置" $true "发现session和function scope混用 (正常)"
    }
    
    if ($FixtureIssuesFound -eq 0) {
        Write-CheckResult "pytest fixture配置" $true "无依赖冲突问题"
    } else {
        Write-CheckResult "pytest fixture配置" $false "发现 $FixtureIssuesFound 个依赖问题"
    }
} else {
    Write-CheckResult "pytest fixture配置" $false "conftest.py不存在"
}

# 7. 检查Docker（用于集成测试）
try {
    & docker --version 2>$null | Out-Null
    $dockerOk = $LASTEXITCODE -eq 0
    Write-CheckResult "Docker (集成测试可选)" $dockerOk "集成测试需要"
} catch {
    Write-CheckResult "Docker (集成测试可选)" $false "集成测试需要"
}

# 总结
Write-Host "`n" + "=" * 40
if ($script:ChecksFailed -eq 0) {
    Write-Host "🎉 所有检查通过！测试环境就绪。" -ForegroundColor Green
    Write-Host "您可以运行以下命令开始测试:" -ForegroundColor Cyan
    Write-Host "  pytest tests/unit/ -v           # 单元测试" -ForegroundColor White
    Write-Host "  pytest tests/integration/ -v    # 集成测试" -ForegroundColor White
    Write-Host "  pytest tests/ -v                # 全部测试" -ForegroundColor White
    exit 0
} else {
    Write-Host "⚠️  发现 $script:ChecksFailed 个问题，$script:ChecksPassed 个检查通过" -ForegroundColor Yellow
    if ($FixtureIssuesFound -gt 0) {
        Write-Host "⚠️  发现 $FixtureIssuesFound 个fixture配置问题" -ForegroundColor Yellow
    }
    Write-Host "请先解决上述问题，然后重新检查。" -ForegroundColor Yellow
    Write-Host "`n建议的修复步骤:" -ForegroundColor Cyan
    Write-Host "1. 激活虚拟环境: .venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "2. 安装依赖: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "3. 运行完整验证: python scripts\validate_test_config.py" -ForegroundColor White
    if ($FixtureIssuesFound -gt 0) {
        Write-Host "4. 修复fixture问题: 参考docs/status/issues-tracking.md ISS-024" -ForegroundColor White
    }
    exit 1
}
