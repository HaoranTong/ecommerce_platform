<#
.SYNOPSIS
    电商平台测试环境检查工具 - 智能化测试环境验证脚本

.DESCRIPTION
    用于验证电商平台项目测试环境的完整性和可用性。支持两种检查模式：
    - lite模式：轻量级检查，适用于单元测试，仅验证Python环境和基础依赖
    - full模式：完整检查，适用于集成测试，额外验证Docker服务和数据库连接
    
    检查流程：
    1. 虚拟环境激活与验证（必须）
    2. 基础Python依赖检查（必须）
    3. 项目结构验证（必须）
    4. 模式特定检查（lite: SQLite + Mock | full: Docker + MySQL + Redis）
    
    设计特点：
    - 分层检查：按层级进行验证，关键步骤失败立即停止
    - 快速失败：提供明确的错误提示和修复建议
    - 自动检测：智能识别Docker状态和服务运行情况
    - 模式分离：lite和full模式完全独立的检查路径

.PARAMETER TestMode
    测试模式选择：
    - lite：轻量模式，适用于单元测试（默认）
    - full：完整模式，适用于集成测试

.EXAMPLE
    .\scripts\check_test_env.ps1
    # 执行轻量模式检查（默认）

.EXAMPLE
    .\scripts\check_test_env.ps1 -TestMode lite
    # 执行轻量模式检查，验证单元测试环境

.EXAMPLE
    .\scripts\check_test_env.ps1 -TestMode full
    # 执行完整模式检查，验证集成测试环境

.NOTES
    文件名: check_test_env.ps1
    作者: 电商平台开发团队
    版本: 2.0
    最后更新: 2025-09-26
    
    依赖项：
    - Python 3.8+ 虚拟环境
    - Docker Desktop (full模式)
    - docker-compose (full模式)
    
    相关文档：
    - docs/tools/testing-tools.md
    - docs/standards/testing-standards.md
    - MASTER.md (第10章节 测试环境管理)

.LINK
    https://github.com/HaoranTong/ecommerce_platform/blob/dev/docs/tools/testing-tools.md
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("lite", "full")]
    [string]$TestMode = "lite"
)

# 颜色输出函数
function Write-ColorMessage {
    param([string]$Message, [string]$Type = "Info")
    
    switch ($Type) {
        "Success" { Write-Host "✅ $Message" -ForegroundColor Green }
        "Error"   { Write-Host "❌ $Message" -ForegroundColor Red }
        "Warning" { Write-Host "⚠️  $Message" -ForegroundColor Yellow }
        "Info"    { Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
        default   { Write-Host "$Message" }
    }
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "📋 $Title" -ForegroundColor Magenta
    Write-Host ("=" * 50) -ForegroundColor Gray
}

function Write-CheckResult {
    param([string]$Item, [bool]$Success, [string]$Details = "")
    
    if ($Success) {
        Write-ColorMessage "$Item" "Success"
        if ($Details) { Write-Host "   $Details" -ForegroundColor Gray }
    } else {
        Write-ColorMessage "$Item" "Error"
        if ($Details) { Write-Host "   💡 提示: $Details" -ForegroundColor Yellow }
        return $false
    }
    return $true
}

function Test-VirtualEnvironment {
    Write-Section "第1步：虚拟环境激活与验证"
    
    # 尝试激活虚拟环境
    $venvPath = ".venv\Scripts\Activate.ps1"
    if (-not (Test-Path $venvPath)) {
        Write-CheckResult "虚拟环境路径" $false "虚拟环境不存在，请运行: python -m venv .venv"
        return $false
    }
    
    try {
        Write-ColorMessage "正在激活虚拟环境..." "Info"
        & $venvPath
        
        # 验证激活成功
        $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
        if ($pythonPath -and $pythonPath.Contains(".venv")) {
            Write-CheckResult "虚拟环境激活" $true "Python路径: $pythonPath"
        } else {
            Write-CheckResult "虚拟环境激活" $false "激活失败，请手动运行: .venv\Scripts\Activate.ps1"
            return $false
        }
        
        # 检查Python版本
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if (($major -eq 3 -and $minor -ge 8) -or $major -gt 3) {
                Write-CheckResult "Python版本" $true "$pythonVersion"
            } else {
                Write-CheckResult "Python版本" $false "需要Python 3.8+，当前: $pythonVersion"
                return $false
            }
        } else {
            Write-CheckResult "Python版本检查" $false "无法获取Python版本"
            return $false
        }
        
        return $true
    }
    catch {
        Write-CheckResult "虚拟环境激活" $false "激活异常: $_"
        return $false
    }
}

function Test-BaseDependencies {
    Write-Section "第2步：基础依赖验证"
    
    $dependencies = @{
        "pytest" = "测试框架"
        "sqlalchemy" = "数据库ORM" 
        "fastapi" = "Web框架"
        "pydantic" = "数据验证"
        "httpx" = "HTTP客户端"
    }
    
    foreach ($package in $dependencies.Keys) {
        try {
            $result = python -c "import $package; print('OK')" 2>$null
            if ($result -eq 'OK') {
                Write-CheckResult $dependencies[$package] $true "Python包: $package"
            } else {
                Write-CheckResult $dependencies[$package] $false "缺少包: $package，运行 pip install $package"
                return $false
            }
        }
        catch {
            Write-CheckResult $dependencies[$package] $false "导入失败: $package"
            return $false
        }
    }
    
    return $true
}

function Test-ProjectStructure {
    Write-Section "第3步：项目结构验证"
    
    $requiredDirs = @{
        "tests" = "测试根目录"
        "tests/unit" = "单元测试目录"
        "tests/factories" = "测试工厂目录"
        "app" = "应用目录"
    }
    
    $requiredFiles = @{
        "pyproject.toml" = "项目配置文件"
        "tests/conftest.py" = "测试配置文件"
    }
    
    # 检查目录
    foreach ($dir in $requiredDirs.Keys) {
        if (Test-Path $dir) {
            Write-CheckResult $requiredDirs[$dir] $true $dir
        } else {
            Write-CheckResult $requiredDirs[$dir] $false "目录不存在: $dir"
            return $false
        }
    }
    
    # 检查文件
    foreach ($file in $requiredFiles.Keys) {
        if (Test-Path $file) {
            Write-CheckResult $requiredFiles[$file] $true $file
        } else {
            Write-CheckResult $requiredFiles[$file] $false "文件不存在: $file"
            return $false
        }
    }
    
    # 检查pytest配置
    $pytestConfig = Get-Content "pyproject.toml" | Select-String "tool.pytest.ini_options"
    if ($pytestConfig) {
        Write-CheckResult "pytest配置" $true "pyproject.toml中的[tool.pytest.ini_options]"
    } else {
        Write-CheckResult "pytest配置" $false "pyproject.toml中缺少[tool.pytest.ini_options]配置"
        return $false
    }
    
    return $true
}

function Test-LiteMode {
    Write-Section "第4步：轻量模式特定检查"
    
    # Mock和Factory依赖
    $liteDeps = @{
        "pytest-mock" = "Mock功能"
        "factory_boy" = "测试数据工厂"
    }
    
    foreach ($package in $liteDeps.Keys) {
        try {
            # 特殊处理factory_boy包的导入名
            $moduleName = if ($package -eq "factory_boy") { "factory" } else { $package -replace "-", "_" }
            $result = python -c "import $moduleName; print('OK')" 2>$null
            if ($result -eq 'OK') {
                Write-CheckResult $liteDeps[$package] $true "Python包: $package"
            } else {
                Write-CheckResult $liteDeps[$package] $false "缺少包: $package，运行 pip install $package"
                return $false
            }
        }
        catch {
            Write-CheckResult $liteDeps[$package] $false "导入失败: $package"
            return $false
        }
    }
    
    # SQLite内存数据库测试
    try {
        $result = python -c "
import sqlite3
conn = sqlite3.connect(':memory:')
conn.execute('CREATE TABLE test (id INTEGER)')
conn.close()
print('OK')
" 2>$null
        
        Write-CheckResult "SQLite内存数据库" ($result -eq 'OK') "轻量模式数据库"
        return ($result -eq 'OK')
    }
    catch {
        Write-CheckResult "SQLite内存数据库" $false "SQLite测试失败"
        return $false
    }
}

function Test-DockerEnvironment {
    Write-Section "第4步：Docker环境检查"
    
    # 检查Docker是否可用
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-CheckResult "Docker客户端" $true "$dockerVersion"
        } else {
            Write-CheckResult "Docker客户端" $false "Docker未安装或未启动，请启动Docker Desktop"
            return $false
        }
    }
    catch {
        Write-CheckResult "Docker客户端" $false "Docker命令不可用"
        return $false
    }
    
    # 检查Docker Engine
    try {
        docker info > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-CheckResult "Docker引擎" $true "Docker引擎正常运行"
        } else {
            Write-CheckResult "Docker引擎" $false "Docker引擎未启动，请启动Docker Desktop"
            return $false
        }
    }
    catch {
        Write-CheckResult "Docker引擎" $false "Docker引擎检查失败"
        return $false
    }
    
    return $true
}

function Test-DockerServices {
    Write-Section "第5步：Docker服务检查"
    
    # 检查docker-compose配置
    if (-not (Test-Path "docker-compose.yml")) {
        Write-CheckResult "Docker Compose配置" $false "docker-compose.yml文件不存在"
        return $false
    }
    
    Write-CheckResult "Docker Compose配置" $true "docker-compose.yml"
    
    # 尝试启动服务
    Write-ColorMessage "正在检查Docker Compose服务..." "Info"
    try {
        $composeResult = docker-compose ps 2>&1
        if ($composeResult -match "ecommerce_platform-mysql-test.*Up" -and 
            $composeResult -match "ecommerce_platform-mysql-dev.*Up" -and
            $composeResult -match "ecommerce_platform-redis.*Up") {
            Write-CheckResult "Docker Compose服务" $true "所有服务正在运行"
        } else {
            Write-ColorMessage "Docker服务未运行，尝试自动启动..." "Warning"
            docker-compose up -d 2>$null
            Start-Sleep 10
            
            $composeResult = docker-compose ps 2>&1
            if ($composeResult -match "Up.*3306" -and $composeResult -match "Up.*6379") {
                Write-CheckResult "Docker Compose服务" $true "服务已成功启动"
            } else {
                Write-CheckResult "Docker Compose服务" $false "服务启动失败，请手动运行: docker-compose up -d"
                return $false
            }
        }
    }
    catch {
        Write-CheckResult "Docker Compose服务" $false "检查失败: $_"
        return $false
    }
    
    return $true
}

function Test-DatabaseConnections {
    Write-Section "第6步：数据库连接验证"
    
    # 测试MySQL连接
    try {
        $result = python -c "
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
        
        if ($result -eq 'OK') {
            Write-CheckResult "MySQL测试数据库" $true "连接成功 (端口3308)"
        } else {
            Write-CheckResult "MySQL测试数据库" $false "连接失败，请检查Docker服务"
            return $false
        }
    }
    catch {
        Write-CheckResult "MySQL测试数据库" $false "连接检查异常"
        return $false
    }
    
    # 测试Redis连接
    try {
        $result = python -c "
import redis
try:
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    r.ping()
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
" 2>$null
        
        if ($result -eq 'OK') {
            Write-CheckResult "Redis缓存服务" $true "连接成功 (端口6379)"
        } else {
            Write-CheckResult "Redis缓存服务" $false "连接失败，请检查Docker服务"
            return $false
        }
    }
    catch {
        Write-CheckResult "Redis缓存服务" $false "连接检查异常"
        return $false
    }
    
    return $true
}

# 主执行逻辑
function Main {
    Write-ColorMessage "🔍 测试环境检查 - $TestMode 模式" "Info"
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    # 第1步：虚拟环境 (所有模式必需)
    if (-not (Test-VirtualEnvironment)) {
        Write-ColorMessage "❌ 虚拟环境检查失败，请先修复虚拟环境问题" "Error"
        return $false
    }
    
    # 第2步：基础依赖 (所有模式必需)
    if (-not (Test-BaseDependencies)) {
        Write-ColorMessage "❌ 基础依赖检查失败，请安装缺少的Python包" "Error"
        return $false
    }
    
    # 第3步：项目结构 (所有模式必需)
    if (-not (Test-ProjectStructure)) {
        Write-ColorMessage "❌ 项目结构检查失败，请检查项目文件结构" "Error"
        return $false
    }
    
    # 第4步：模式特定检查
    if ($TestMode -eq "lite") {
        if (-not (Test-LiteMode)) {
            Write-ColorMessage "❌ 轻量模式检查失败" "Error"
            return $false
        }
        
        Write-ColorMessage "🎉 轻量模式环境检查通过！" "Success"
        Write-Host ""
        Write-ColorMessage "可以运行以下测试命令:" "Info"
        Write-Host "  pytest tests/unit/ -v           # 单元测试"
        Write-Host "  pytest tests/unit/ --cov=app    # 单元测试 + 覆盖率"
        
    } else {
        # full模式需要Docker
        if (-not (Test-DockerEnvironment)) {
            Write-ColorMessage "❌ Docker环境检查失败，请启动Docker Desktop后重试" "Error"
            return $false
        }
        
        if (-not (Test-DockerServices)) {
            Write-ColorMessage "❌ Docker服务检查失败" "Error"
            return $false
        }
        
        if (-not (Test-DatabaseConnections)) {
            Write-ColorMessage "❌ 数据库连接检查失败" "Error"
            return $false
        }
        
        Write-ColorMessage "🎉 完整模式环境检查通过！" "Success"
        Write-Host ""
        Write-ColorMessage "可以运行以下测试命令:" "Info"
        Write-Host "  pytest tests/unit/ -v           # 单元测试"
        Write-Host "  pytest tests/integration/ -v    # 集成测试"
        Write-Host "  pytest tests/ -v                # 全部测试"
    }
    
    return $true
}

# 执行检查
$checkResult = Main
if ($checkResult) {
    Write-Host ""
    Write-ColorMessage "✅ 测试环境就绪" "Success"
} else {
    Write-Host ""
    Write-ColorMessage "❌ 测试环境存在问题，请按提示修复" "Error"
}

exit $(if ($checkResult) { 0 } else { 1 })