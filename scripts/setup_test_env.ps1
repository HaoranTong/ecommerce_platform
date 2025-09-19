<#
.SYNOPSIS
    测试环境检查和启动脚本

.DESCRIPTION
    本脚本提供完整的测试环境检查、准备和启动功能：
    1. 验证测试环境配置是否正确
    2. 启动必要的服务（如MySQL Docker容器）
    3. 执行测试环境检查清单
    4. 提供不同测试类型的启动选项

.PARAMETER TestType
    指定测试类型：unit（单元测试）、smoke（烟雾测试）、integration（集成测试）、all（全部）

.PARAMETER SkipValidation
    跳过环境验证，直接启动测试

.PARAMETER SetupOnly
    只进行环境设置，不运行测试

.EXAMPLE
    .\scripts\setup_test_env.ps1 -TestType unit
    # 设置并运行单元测试环境

.EXAMPLE  
    .\scripts\setup_test_env.ps1 -TestType integration -SetupOnly
    # 只设置集成测试环境，不运行测试

.NOTES
    文件名: setup_test_env.ps1
    作者: 系统架构师
    版本: 1.0.0
    创建日期: 2025-09-16
    基于: docs/standards/testing-standards.md
#>

[CmdletBinding()]
Param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("unit", "smoke", "integration", "all")]
    [string]$TestType = "unit",
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipValidation = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$SetupOnly = $false
)

# 测试环境检查和启动脚本
# 根据 testing-standards.md 标准执行完整的测试环境准备和验证

# 强制执行sku_id数据类型检查
Write-Host "🔍 执行强制性sku_id数据类型检查..."
& "$PSScriptRoot/check_sku_id_types.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ sku_id数据类型检查失败，测试被阻止!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ sku_id数据类型检查通过" -ForegroundColor Green

Set-StrictMode -Version Latest

# 全局变量
$script:TestSuccess = $true
$script:DockerStarted = $false
$script:ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

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
        $validationScript = Join-Path $script:ProjectRoot "scripts\validate_test_config.py"
        
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
    
    # 检查MySQL容器状态
    $mysqlContainer = & docker ps --filter "name=mysql_test" --format "{{.Names}}"
    
    if ($mysqlContainer -eq "mysql_test") {
        Write-ColorMessage "MySQL测试容器已运行" "Success"
        return $true
    }
    
    # 检查MySQL测试容器是否已存在
    Write-ColorMessage "检查MySQL测试容器..." "Info"
    $existingContainer = & docker ps -q --filter "name=mysql_test" 2>$null
    
    if ($existingContainer) {
        Write-ColorMessage "MySQL测试容器已存在且运行中，验证连接..." "Success"
        # 验证容器端口配置
        $containerPort = & docker port mysql_test 3306 2>$null
        if ($containerPort -match "3308$") {
            Write-ColorMessage "容器端口配置正确 (3308:3306)" "Success"
        } else {
            Write-ColorMessage "警告：容器端口配置可能不匹配，当前: $containerPort" "Warning"
        }
        $script:DockerStarted = $true
    } else {
        # 检查是否有停止的容器
        $stoppedContainer = & docker ps -aq --filter "name=mysql_test" 2>$null
        if ($stoppedContainer) {
            Write-ColorMessage "启动已存在的MySQL测试容器..." "Info"
            & docker start mysql_test
        } else {
            # 启动新的MySQL测试容器
            Write-ColorMessage "创建新的MySQL测试容器..." "Info"
            & docker run -d --name mysql_test `
                -e MYSQL_ROOT_PASSWORD=test_root_pass `
                -e MYSQL_DATABASE=test_ecommerce `
                -e MYSQL_USER=test_user `
                -e MYSQL_PASSWORD=test_pass `
                -p 3308:3306 `
                mysql:8.0
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
        & docker stop mysql_test 2>$null
        & docker rm mysql_test 2>$null
        Write-ColorMessage "MySQL测试容器已清理" "Success"
    }
}

# 主函数
function Main {
    Write-ColorMessage "🚀 测试环境设置脚本启动" "Info"
    Write-ColorMessage "项目根目录: $script:ProjectRoot" "Info"
    Write-ColorMessage "测试类型: $TestType" "Info"
    
    try {
        Push-Location $script:ProjectRoot
        
        # 1. 初始化虚拟环境
        if (-not (Initialize-VirtualEnvironment)) {
            throw "虚拟环境初始化失败"
        }
        
        # 2. 验证测试环境配置
        if (-not (Test-EnvironmentConfiguration)) {
            throw "测试环境配置验证失败"
        }
        
        # 3. 根据测试类型设置环境
        $setupSuccess = $false
        switch ($TestType) {
            "unit" {
                $setupSuccess = Initialize-UnitTestEnvironment
            }
            "smoke" {
                $setupSuccess = Initialize-SmokeTestEnvironment
            }
            "integration" {
                $setupSuccess = Initialize-IntegrationTestEnvironment
            }
            "all" {
                $setupSuccess = (Initialize-UnitTestEnvironment) -and 
                               (Initialize-SmokeTestEnvironment) -and 
                               (Initialize-IntegrationTestEnvironment)
            }
        }
        
        if (-not $setupSuccess) {
            throw "测试环境设置失败"
        }
        
        Write-ColorMessage "✅ 测试环境设置完成" "Success"
        
        # 4. 运行测试（如果不是仅设置模式）
        if (-not $SetupOnly) {
            if (-not (Invoke-Tests -Type $TestType)) {
                throw "测试执行失败"
            }
        } else {
            Write-ColorMessage "环境设置完成，跳过测试执行（--SetupOnly）" "Info"
        }
        
        Write-ColorMessage "🎉 测试环境脚本执行成功" "Success"
        
    }
    catch {
        Write-ColorMessage "❌ 测试环境脚本执行失败: $_" "Error"
        $script:TestSuccess = $false
    }
    finally {
        Pop-Location
        
        # 清理环境（如果需要）
        if (-not $SetupOnly -and $TestType -eq "integration") {
            Clear-TestEnvironment
        }
    }
    
    return $script:TestSuccess
}

# 脚本入口点
if ($MyInvocation.InvocationName -ne '.') {
    $success = Main
    exit $(if ($success) { 0 } else { 1 })
}