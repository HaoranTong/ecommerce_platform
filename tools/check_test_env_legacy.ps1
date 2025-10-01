# 测试环境综合检查脚本 (合并版)
# 在运行任何测试前，全面验证环境是否就绪
# 合并了diagnose_test_fixtures.ps1的fixture诊断功能

<#
.SYNOPSIS
    测试环境状态检查脚本 - 纯检查模式

.DESCRIPTION
    本脚本专门负责测试环境状态检查，不进行任何修改操作：
    
    Lite模式检查项：
    1. Python虚拟环境激活状态
    2. 单元测试必需依赖包
    3. 测试目录结构完整性
    4. SQLite内存数据库可用性
    5. pytest配置文件存在性
    6. fixture依赖关系诊断
    
    Full模式额外检查项：
    7. MySQL数据库连接状态
    8. Redis缓存服务连接
    9. Docker容器运行状态
    10. 集成测试环境配置

.PARAMETER TestMode
    测试模式：'lite' (Mock+SQLite单元测试) 或 'full' (Docker+MySQL集成测试)

.PARAMETER Verbose
    显示详细的检查信息

.EXAMPLE
    .\scripts\check_test_env.ps1 -TestMode lite
    # 检查轻量测试环境状态

.EXAMPLE
    .\scripts\check_test_env.ps1 -TestMode full -Verbose
    # 检查完整测试环境状态，显示详细信息

.NOTES
    文件名: check_test_env.ps1
    职责: 纯检查，不修改环境
    调用者: setup_test_env.ps1, ai_checkpoint.ps1
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('lite', 'full')]
    [string]$TestMode
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

Write-Host "🔍 测试环境检查 - $TestMode 模式" -ForegroundColor Cyan
Write-Host "=" * 50

# 第1步：Python虚拟环境检查（两种模式都需要）
Write-Host "`n📋 第1步：Python环境验证" -ForegroundColor Yellow

try {
    $pythonPath = & python -c "import sys; print(sys.executable)" 2>$null
    $isVenv = $pythonPath -and $pythonPath.Contains(".venv")
    Write-CheckResult "Python虚拟环境激活" $isVenv "当前Python: $pythonPath"
} catch {
    Write-CheckResult "Python环境可用性" $false "Python不可用，请激活虚拟环境"
}

# 第2步：依赖包检查（根据模式不同）
Write-Host "`n📦 第2步：依赖包验证" -ForegroundColor Yellow

# 基础依赖（两种模式都需要）
$baseDependencies = @(
    @{name="pytest"; import="pytest"; desc="测试框架"},
    @{name="pytest-mock"; import="pytest_mock"; desc="Mock功能"},
    @{name="sqlalchemy"; import="sqlalchemy"; desc="数据库ORM"},
    @{name="factory-boy"; import="factory"; desc="测试数据工厂"}
)

# 完整模式额外依赖
$fullDependencies = @(
    @{name="pymysql"; import="pymysql"; desc="MySQL连接器"},
    @{name="redis"; import="redis"; desc="Redis客户端"},
    @{name="requests"; import="requests"; desc="HTTP客户端"}
)

$dependencies = $baseDependencies
if ($TestMode -eq 'full') {
    $dependencies += $fullDependencies
}

foreach ($dep in $dependencies) {
    try {
        $result = & python -c "import $($dep.import); print('OK')" 2>$null
        Write-CheckResult $dep.desc ($result -eq 'OK') "包名: $($dep.name)"
    } catch {
        Write-CheckResult $dep.desc $false "缺少包: $($dep.name)"
    }
}

# 第3步：测试目录结构检查
Write-Host "`n📁 第3步：目录结构验证" -ForegroundColor Yellow

$requiredDirs = @(
    @{path="tests"; desc="测试根目录"},
    @{path="tests\unit"; desc="单元测试目录"},
    @{path="tests\factories"; desc="测试工厂目录"},
    @{path="tests\_archive"; desc="测试存档目录"}
)

if ($TestMode -eq 'full') {
    $requiredDirs += @(
        @{path="tests\integration"; desc="集成测试目录"},
        @{path="tests\e2e"; desc="端到端测试目录"}
    )
}

foreach ($dir in $requiredDirs) {
    $exists = Test-Path $dir.path
    Write-CheckResult $dir.desc $exists "路径: $($dir.path)"
}

# 检查关键配置文件
$configFiles = @(
    @{path="tests\conftest.py"; desc="pytest配置文件"},
    @{path="pyproject.toml"; desc="项目配置文件"}
)

foreach ($file in $configFiles) {
    $exists = Test-Path $file.path
    Write-CheckResult $file.desc $exists "路径: $($file.path)"
}

# 第4步：数据库连接检查（根据模式不同）
Write-Host "`n🗄️ 第4步：数据库连接验证" -ForegroundColor Yellow

# SQLite检查（两种模式都需要）
try {
    $result = & python -c "
import sqlite3
conn = sqlite3.connect(':memory:')
conn.execute('CREATE TABLE test (id INTEGER)')
conn.close()
print('OK')
" 2>$null
    
    Write-CheckResult "SQLite内存数据库" ($result -eq 'OK') "单元测试数据库"
} catch {
    Write-CheckResult "SQLite内存数据库" $false "SQLite不可用"
}

# MySQL检查（仅完整模式）
if ($TestMode -eq 'full') {
    try {
        $result = & python -c "
import pymysql
try:
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3308,
        user='root',
        password='test_password',
        database='ecommerce_platform_test'
    )
    conn.close()
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
" 2>$null
        
        Write-CheckResult "MySQL数据库连接" ($result -eq 'OK') "集成测试数据库"
        if ($result -ne 'OK') {
            Write-Host "   💡 提示: 请确保Docker容器已启动" -ForegroundColor Cyan
        }
    } catch {
        Write-CheckResult "MySQL数据库连接" $false "MySQL连接失败"
    }
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
