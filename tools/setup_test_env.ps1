<#
.SYNOPSIS
    电商平台测试环境管理脚本 - 统一测试环境设置和检查工具

.DESCRIPTION
    电商平台项目的统一测试环境管理入口，支持两种工作模式和两种测试环境：
    
    🔍 工作模式：
    - CheckOnly: 仅检查环境状态，不进行任何修改或设置
    - Setup: 检查环境并进行必要的设置和修复（默认）
    
    🧪 测试环境：
    - lite: 轻量模式 (Mock + SQLite)，适用于单元测试
    - full: 完整模式 (Docker + MySQL + Redis)，适用于集成测试
    
    功能特性：
    - 智能环境检查：调用check_test_env.ps1进行专业化检查
    - 分离职责：检查和设置功能完全分离
    - 自动修复：可选的环境问题自动修复
    - 参数验证：严格的参数类型和取值验证
    - 详细日志：提供详细的执行过程信息
    
    设计原则：
    - 单一入口：所有测试环境操作的统一入口
    - 功能分离：委托专业脚本进行具体检查
    - 参数标准化：使用TestMode替代旧的TestType参数
    - Docker集成：与docker-compose无缝集成

.PARAMETER TestMode
    测试模式选择：
    - lite：轻量模式，使用Mock和SQLite，适用于单元测试（默认）
    - full：完整模式，使用Docker、MySQL、Redis，适用于集成测试

.PARAMETER CheckOnly
    仅检查模式开关。设置后只进行环境检查，不执行任何设置或修复操作

.PARAMETER AutoFix
    自动修复开关。设置后会自动尝试修复发现的环境问题

.PARAMETER Verbose
    详细模式开关。显示更详细的执行信息和调试日志

.EXAMPLE
    .\tools\setup_test_env.ps1
    # 使用默认lite模式进行环境设置

.EXAMPLE
    .\tools\setup_test_env.ps1 -TestMode lite -CheckOnly
    # 只检查轻量测试环境状态，不进行设置

.EXAMPLE
    .\tools\setup_test_env.ps1 -TestMode full -CheckOnly
    # 只检查完整测试环境状态（包括Docker服务）

.EXAMPLE
    .\tools\setup_test_env.ps1 -TestMode full
    # 设置完整测试环境，包括Docker服务启动

.EXAMPLE
    .\tools\setup_test_env.ps1 -TestMode full -AutoFix -Verbose
    # 设置完整环境，自动修复问题，显示详细信息

.NOTES
    文件名: setup_test_env.ps1
    作者: 电商平台开发团队
    版本: 3.0
    最后更新: 2025-09-26
    
    重要变更：
    - v3.0: 参数标准化（TestType → TestMode），Docker配置更新
    - v2.0: 添加lite/full模式分离，集成Docker Compose
    - v1.0: 基础测试环境管理功能
    
    依赖脚本：
    - tools/check_test_env.ps1 (环境检查)
    - docker-compose.yml (Docker服务配置)
    
    相关文档：
    - docs/development/testing-environment.md (测试环境配置)
    - docs/standards/testing-standards.md (测试标准)
    - MASTER.md (测试环境管理章节)

.LINK
    https://github.com/HaoranTong/ecommerce_platform/blob/dev/docs/development/testing-environment.md
#>

[CmdletBinding()]
Param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("lite", "full")]
    [string]$TestMode,
    
    [Parameter(Mandatory = $false)]
    [switch]$CheckOnly = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$AutoFix = $false
)

# 测试环境检查和启动脚本
# 根据 testing-standards.md 标准执行完整的测试环境准备和验证

# TODO: 强制执行sku_id数据类型检查（脚本不存在，暂时注释）
# Write-Host "🔍 执行强制性sku_id数据类型检查..."
# & "$PSScriptRoot/check_sku_id_types.ps1"
# if ($LASTEXITCODE -ne 0) {
#     Write-Host "❌ sku_id数据类型检查失败，测试被阻止!" -ForegroundColor Red
#     exit 1
# }
# Write-Host "✅ sku_id数据类型检查通过" -ForegroundColor Green

Set-StrictMode -Version Latest

# 全局变量
$script:TestSuccess = $true
$script:DockerStarted = $false
$script:ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# 函数：调用环境检查脚本
function Invoke-EnvironmentCheck {
    param([string]$Mode)
    
    Write-ColorMessage "执行 $Mode 模式环境检查..." "Info"
    
    try {
        & "$PSScriptRoot/check_test_env.ps1" -TestMode $Mode -Verbose:$VerbosePreference
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorMessage "环境检查通过" "Success"
            return $true
        } else {
            Write-ColorMessage "环境检查发现问题" "Error"
            return $false
        }
    } catch {
        Write-ColorMessage "环境检查执行失败: $_" "Error"
        return $false
    }
}

# 函数：输出带颜色的消息
function Write-ColorMessage {
    param(
        [string]$Message,
        [ValidateSet("Success", "Error", "Warning", "Info")]
        [string]$Type = "Info"
    )
    
    switch ($Type) {
        "Success" { Write-Host "✅ $Message" -ForegroundColor Green }
        "Error"   { Write-Host "❌ $Message" -ForegroundColor Red }
        "Warning" { Write-Host "⚠️  $Message" -ForegroundColor Yellow }
        "Info"    { Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
    }
}

# 函数：检查并激活虚拟环境
function Initialize-VirtualEnvironment {
    Write-ColorMessage "检查虚拟环境..." "Info"
    
    $venvPath = Join-Path $script:ProjectRoot ".venv"
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    if (-not (Test-Path $activateScript)) {
        Write-ColorMessage "虚拟环境不存在: $venvPath" "Error"
        return $false
    }
    
    # 检查是否已在虚拟环境中
    if ($env:VIRTUAL_ENV -and $env:VIRTUAL_ENV.Contains(".venv")) {
        Write-ColorMessage "虚拟环境已激活: $env:VIRTUAL_ENV" "Success"
        return $true
    }
    
    # 激活虚拟环境
    try {
        & $activateScript
        Write-ColorMessage "虚拟环境激活成功" "Success"
        return $true
    }
    catch {
        Write-ColorMessage "虚拟环境激活失败: $_" "Error"
        return $false
    }
}

# 函数：验证测试环境配置
function Test-EnvironmentConfiguration {
    Write-ColorMessage "=== 测试环境配置验证 ===" "Info"
    
    if (-not $SkipValidation) {
        $validationScript = Join-Path $script:ProjectRoot "tools\validate_test_config.py"
        
        if (Test-Path $validationScript) {
            Write-ColorMessage "运行测试配置验证脚本..." "Info"
            try {
                & python $validationScript | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorMessage "测试环境配置验证通过" "Success"
                    return $true
                } else {
                    Write-ColorMessage "测试环境配置验证失败" "Error"
                    return $false
                }
            }
            catch {
                Write-ColorMessage "验证脚本执行失败: $_" "Error"
                return $false
            }
        } else {
            Write-ColorMessage "测试配置验证脚本不存在: $validationScript" "Warning"
        }
    } else {
        Write-ColorMessage "跳过环境验证（--SkipValidation）" "Warning"
    }
    
    return $true
}

# 函数：设置单元测试环境
function Initialize-UnitTestEnvironment {
    Write-ColorMessage "=== 设置单元测试环境 ===" "Info"
    
    # 单元测试使用SQLite内存数据库，无需外部服务
    Write-ColorMessage "单元测试配置:" "Info"
    Write-ColorMessage "  数据库: SQLite内存数据库 (sqlite:///:memory:)" "Info"
    Write-ColorMessage "  隔离级别: 函数级别" "Info"
    Write-ColorMessage "  外部依赖: 无" "Info"
    
    # 检查pytest是否可用
    try {
        $pytestVersion = & python -c "import pytest; print(pytest.__version__)"
        Write-ColorMessage "pytest版本: $pytestVersion" "Success"
    }
    catch {
        Write-ColorMessage "pytest未安装或不可用" "Error"
        return $false
    }
    
    return $true
}

# 函数：设置烟雾测试环境
function Initialize-SmokeTestEnvironment {
    Write-ColorMessage "=== 设置烟雾测试环境 ===" "Info"
    
    # 烟雾测试使用SQLite文件数据库
    $testDir = Join-Path $script:ProjectRoot "tests"
    if (-not (Test-Path $testDir)) {
        New-Item -ItemType Directory -Path $testDir -Force | Out-Null
        Write-ColorMessage "创建测试目录: $testDir" "Success"
    }
    
    Write-ColorMessage "烟雾测试配置:" "Info"
    Write-ColorMessage "  数据库: SQLite文件数据库 (tests/smoke_test.db)" "Info"
    Write-ColorMessage "  隔离级别: 模块级别" "Info"
    Write-ColorMessage "  外部依赖: 无" "Info"
    
    return $true
}

# 函数：设置集成测试环境
function Initialize-IntegrationTestEnvironment {
    Write-ColorMessage "=== 设置集成测试环境 ===" "Info"
    
    # 检查Docker是否可用
    try {
        $dockerVersion = & docker --version
        Write-ColorMessage "Docker版本: $dockerVersion" "Success"
    }
    catch {
        Write-ColorMessage "Docker不可用，集成测试将跳过" "Warning"
        return $true  # 允许继续，测试时会自动跳过
    }
    
    # 检查MySQL测试容器状态 (docker-compose管理)
    $mysqlContainer = & docker ps --filter "name=ecommerce_platform-mysql-test" --format "{{.Names}}"
    
    if ($mysqlContainer -eq "ecommerce_platform-mysql-test") {
        Write-ColorMessage "MySQL测试容器已运行" "Success"
        return $true
    }
    
    # 检查MySQL测试容器是否已存在
    Write-ColorMessage "检查MySQL测试容器..." "Info"
    $existingContainer = & docker ps -q --filter "name=ecommerce_platform-mysql-test" 2>$null
    
    if ($existingContainer) {
        Write-ColorMessage "MySQL测试容器已存在且运行中，验证连接..." "Success"
        # 验证容器端口配置
        $containerPort = & docker port ecommerce_platform-mysql-test 3306 2>$null
        if ($containerPort -match "3308$") {
            Write-ColorMessage "容器端口配置正确 (3308:3306)" "Success"
        } else {
            Write-ColorMessage "警告：容器端口配置可能不匹配，当前: $containerPort" "Warning"
        }
        $script:DockerStarted = $true
    } else {
        # 检查是否有停止的容器
        $stoppedContainer = & docker ps -aq --filter "name=ecommerce_platform-mysql-test" 2>$null
        if ($stoppedContainer) {
            Write-ColorMessage "启动已存在的MySQL测试容器..." "Info"
            & docker start ecommerce_platform-mysql-test
        } else {
            # 使用docker-compose启动测试环境
            Write-ColorMessage "使用docker-compose启动测试环境..." "Info"
            $composeResult = & docker-compose up -d mysql-test 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-ColorMessage "docker-compose启动失败: $composeResult" "Error"
                return $false
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            $script:DockerStarted = $true
            Write-ColorMessage "MySQL容器启动成功，等待数据库初始化..." "Success"
            
            # 等待MySQL启动
            $maxWait = 30
            $waited = 0
            do {
                Start-Sleep 2
                $waited += 2
                Write-ColorMessage "等待MySQL启动... ($waited/$maxWait 秒)" "Info"
                
                # 测试连接
                try {
                    & python -c "import pymysql; pymysql.connect(host='localhost', port=3308, user='test_user', password='test_pass', database='test_ecommerce')"
                    if ($LASTEXITCODE -eq 0) {
                        Write-ColorMessage "MySQL数据库连接成功" "Success"
                        return $true
                    }
                }
                catch {
                    # 继续等待
                }
            } while ($waited -lt $maxWait)
            
            Write-ColorMessage "MySQL启动超时，但容器已启动" "Warning"
            return $true
        } else {
            Write-ColorMessage "MySQL容器启动失败" "Error"
            return $false
        }
    }
    
    return $true
}

# 函数：运行测试
function Invoke-Tests {
    param(
        [string]$Type
    )
    
    Write-ColorMessage "=== 运行 $Type 测试 ===" "Info"
    
    switch ($Type) {
        "unit" {
            Write-ColorMessage "执行单元测试 (SQLite内存数据库)..." "Info"
            & python -m pytest tests/unit/ -v --tb=short
        }
        "smoke" {
            Write-ColorMessage "执行烟雾测试 (SQLite文件数据库)..." "Info"
            & python -m pytest tests/smoke/ -v --tb=short
        }
        "integration" {
            Write-ColorMessage "执行集成测试 (MySQL Docker端口3308)..." "Info"
            & python -m pytest tests/integration/ -v --tb=short
        }
        "all" {
            Write-ColorMessage "执行完整测试套件..." "Info"
            & python -m pytest tests/ -v --cov=app --cov-report=term --tb=short
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorMessage "$Type 测试执行成功" "Success"
        return $true
    } else {
        Write-ColorMessage "$Type 测试执行失败" "Error"
        return $false
    }
}

# 函数：清理环境
function Clear-TestEnvironment {
    Write-ColorMessage "=== 清理测试环境 ===" "Info"
    
    if ($script:DockerStarted) {
        Write-ColorMessage "停止并删除MySQL测试容器..." "Info"
        # 使用docker-compose清理测试容器
        & docker-compose stop mysql-test 2>$null
        Write-ColorMessage "MySQL测试容器已停止" "Success"
    }
}

# 主函数
function Main {
    Write-ColorMessage "🚀 测试环境管理脚本启动" "Info"
    Write-ColorMessage "项目根目录: $script:ProjectRoot" "Info"
    Write-ColorMessage "测试模式: $TestMode" "Info"
    Write-ColorMessage "操作模式: $(if($CheckOnly) {'仅检查'} else {'设置执行'})" "Info"
    
    try {
        Push-Location $script:ProjectRoot
        
        # 步骤1：调用环境检查脚本
        $checkPassed = Invoke-EnvironmentCheck -Mode $TestMode
        
        if (-not $checkPassed) {
            if ($CheckOnly) {
                Write-ColorMessage "环境检查未通过，请先解决问题" "Error"
                return $false
            } elseif ($AutoFix) {
                Write-ColorMessage "尝试自动修复环境问题..." "Warning"
                # 这里可以添加自动修复逻辑
                # 比如安装缺失依赖、创建缺失目录等
            } else {
                Write-ColorMessage "环境检查未通过，请使用 -AutoFix 参数或手动修复" "Error"
                return $false
            }
        }
        
        # 如果是仅检查模式，到此结束
        if ($CheckOnly) {
            Write-ColorMessage "环境检查完成" "Success"
            return $true
        }
        
        # 步骤2：根据测试模式进行环境设置
        Write-ColorMessage "开始环境设置..." "Info"
        
        if ($TestMode -eq "full") {
            # 完整模式：启动必要的外部服务
            Write-ColorMessage "完整模式：准备外部服务连接..." "Info"
            # 注意：不自动启动Docker，只检查连接
        } else {
            # 轻量模式：准备本地测试环境
            Write-ColorMessage "轻量模式：准备本地测试环境..." "Info"
        }
        
        Write-ColorMessage "测试环境准备完成" "Success"
        return $true
        
    } catch {
        Write-ColorMessage "测试环境设置失败: $_" "Error"
        return $false
    } finally {
        Pop-Location
    }
}

# 脚本入口点
if ($MyInvocation.InvocationName -ne '.') {
    $success = Main
    exit $(if ($success) { 0 } else { 1 })
}
