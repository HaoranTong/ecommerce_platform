<#
.SYNOPSIS
    统一开发环境配置脚本

.DESCRIPTION
    本脚本整合了开发环境配置和环境变量同步功能：
    1. 激活虚拟环境
    2. 设置和同步环境变量
    3. 检查Docker服务状态
    4. 验证API服务状态
    5. 创建或更新.env文件

.PARAMETER Action
    执行的操作：
    - setup: 完整环境配置（默认）
    - check: 仅检查环境状态
    - sync: 仅同步环境变量
    - create-env: 创建.env文件

.PARAMETER CreateEnvFile
    是否创建.env文件（默认: false）

.EXAMPLE
    .\scripts\setup_dev_env.ps1
    # 完整开发环境配置

.EXAMPLE
    .\scripts\setup_dev_env.ps1 -Action check
    # 检查环境状态

.EXAMPLE
    .\scripts\setup_dev_env.ps1 -Action create-env
    # 创建.env文件

.NOTES
    文件名: setup_dev_env.ps1
    作者: 系统管理员
    版本: 1.0.0
    创建日期: 2025-09-25
    说明: 合并了dev_env.ps1和sync_env.ps1功能
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("setup", "check", "sync", "create-env")]
    [string]$Action = "setup",
    
    [Parameter(Mandatory = $false)]
    [switch]$CreateEnvFile = $false
)

Set-StrictMode -Version Latest

$script:ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$script:EnvFile = Join-Path $script:ProjectRoot ".env"

# 必需的环境变量列表
$RequiredEnvVars = @(
    "DATABASE_URL",
    "SECRET_KEY", 
    "REDIS_URL",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES"
)

function Write-StatusMessage {
    param([string]$Message, [string]$Type = "Info")
    
    switch ($Type) {
        "Success" { Write-Host "✅ $Message" -ForegroundColor Green }
        "Warning" { Write-Host "⚠️  $Message" -ForegroundColor Yellow }
        "Error"   { Write-Host "❌ $Message" -ForegroundColor Red }
        "Info"    { Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
        default   { Write-Host "$Message" -ForegroundColor White }
    }
}

function Initialize-VirtualEnvironment {
    Write-StatusMessage "🔧 配置虚拟环境..." "Info"
    
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        . .\.venv\Scripts\Activate.ps1
        Write-StatusMessage "虚拟环境已激活" "Success"
        return $true
    } else {
        Write-StatusMessage "虚拟环境未找到" "Error"
        Write-StatusMessage "请先运行: python -m venv .venv" "Warning"
        return $false
    }
}

function Set-DevelopmentEnvironmentVariables {
    Write-StatusMessage "🔧 设置环境变量..." "Info"
    
    # 设置基础环境变量（根据docker-compose.yml配置）
    $env:DATABASE_URL = "mysql+pymysql://root:rootpass@localhost:3307/ecommerce_platform"
    $env:MYSQL_ROOT_PASSWORD = "rootpass"
    $env:REDIS_URL = "redis://localhost:6379"
    $env:SECRET_KEY = "your-secret-key-here-change-in-production"
    $env:ALGORITHM = "HS256"
    $env:ACCESS_TOKEN_EXPIRE_MINUTES = "30"
    
    Write-StatusMessage "环境变量已设置" "Success"
}

function Test-EnvironmentVariables {
    Write-StatusMessage "🔍 检查环境变量配置..." "Info"
    
    $missingVars = @()
    $configuredVars = @()
    
    foreach ($envVar in $RequiredEnvVars) {
        $value = [System.Environment]::GetEnvironmentVariable($envVar)
        if ([string]::IsNullOrWhiteSpace($value)) {
            $missingVars += $envVar
            Write-StatusMessage "缺少环境变量: $envVar" "Warning"
        } else {
            $configuredVars += $envVar
            Write-StatusMessage "环境变量已设置: $envVar" "Success"
        }
    }
    
    Write-StatusMessage "已配置变量: $($configuredVars.Count)/$($RequiredEnvVars.Count)" "Info"
    
    if ($missingVars.Count -eq 0) {
        Write-StatusMessage "所有必需的环境变量均已正确设置" "Success"
        return $true
    } else {
        Write-StatusMessage "发现 $($missingVars.Count) 个缺失的环境变量" "Error"
        return $false
    }
}

function New-EnvironmentFile {
    Write-StatusMessage "📄 创建.env文件..." "Info"
    
    $envContent = @"
# 项目环境变量配置文件
# 生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

# 数据库配置
DATABASE_URL=mysql+pymysql://root:rootpass@localhost:3307/ecommerce_platform
MYSQL_ROOT_PASSWORD=rootpass
TEST_DATABASE_URL=sqlite:///./test_ecommerce.db

# Redis缓存配置
REDIS_URL=redis://localhost:6379

# 安全配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 日志配置
LOG_LEVEL=INFO

# 开发环境配置
ENVIRONMENT=development
DEBUG=true

# API配置
API_HOST=0.0.0.0
API_PORT=8000
"@

    try {
        Set-Content -Path $script:EnvFile -Value $envContent -Encoding UTF8
        Write-StatusMessage ".env文件已创建: $script:EnvFile" "Success"
        return $true
    } catch {
        Write-StatusMessage "创建.env文件失败: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Test-DockerServices {
    Write-StatusMessage "🐳 检查Docker服务..." "Info"
    
    try {
        $mysqlContainer = docker ps --filter "name=ecommerce_platform-mysql-1" --format "{{.Names}}" 2>$null
        $redisContainer = docker ps --filter "name=ecommerce_platform-redis-1" --format "{{.Names}}" 2>$null

        if (-not $mysqlContainer -or -not $redisContainer) {
            Write-StatusMessage "Docker容器未运行，正在启动..." "Warning"
            docker-compose up -d
            Start-Sleep 10
            Write-StatusMessage "Docker服务已启动" "Success"
        } else {
            Write-StatusMessage "Docker服务正常运行" "Success"
        }
        
        return $true
    } catch {
        Write-StatusMessage "Docker检查失败: $($_.Exception.Message)" "Error"
        Write-StatusMessage "请确保Docker已安装并运行" "Warning"
        return $false
    }
}

function Test-APIService {
    Write-StatusMessage "🚀 检查API服务..." "Info"
    
    try {
        $apiProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*uvicorn*"}

        if ($apiProcess) {
            Write-StatusMessage "API服务已运行 (PID: $($apiProcess.Id))" "Success"
        } else {
            Write-StatusMessage "API服务未运行" "Warning"
            Write-StatusMessage "启动命令: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" "Info"
        }
        
        return $true
    } catch {
        Write-StatusMessage "API服务检查失败: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Show-DevelopmentSummary {
    Write-StatusMessage "`n🎯 开发环境配置完成！" "Success"
    Write-StatusMessage "📋 可用命令:" "Info"
    Write-Host "  - python -c '...' (直接执行Python代码)" -ForegroundColor White
    Write-Host "  - alembic upgrade head (数据库迁移)" -ForegroundColor White
    Write-Host "  - pytest (运行测试)" -ForegroundColor White
    Write-Host "  - uvicorn app.main:app --reload (启动API服务)" -ForegroundColor White
}

# 主执行逻辑
switch ($Action) {
    "setup" {
        Write-StatusMessage "=== 开发环境完整配置 ===" "Info"
        
        $success = $true
        $success = $success -and (Initialize-VirtualEnvironment)
        Set-DevelopmentEnvironmentVariables
        $success = $success -and (Test-EnvironmentVariables)
        $success = $success -and (Test-DockerServices)
        $success = $success -and (Test-APIService)
        
        if ($CreateEnvFile -or $success) {
            New-EnvironmentFile | Out-Null
        }
        
        Show-DevelopmentSummary
        
        if (-not $success) {
            Write-StatusMessage "某些配置步骤失败，请检查上述输出" "Warning"
            exit 1
        }
    }
    
    "check" {
        Write-StatusMessage "=== 环境状态检查 ===" "Info"
        
        $venvOk = Test-Path ".venv\Scripts\Activate.ps1"
        $envVarsOk = Test-EnvironmentVariables
        $dockerOk = Test-DockerServices
        $apiOk = Test-APIService
        
        Write-StatusMessage "`n📊 环境状态摘要:" "Info"
        Write-Host "  - 虚拟环境: $(if ($venvOk) { '✅' } else { '❌' })" -ForegroundColor White
        Write-Host "  - 环境变量: $(if ($envVarsOk) { '✅' } else { '❌' })" -ForegroundColor White
        Write-Host "  - Docker服务: $(if ($dockerOk) { '✅' } else { '❌' })" -ForegroundColor White
        Write-Host "  - API服务: $(if ($apiOk) { '✅' } else { '❌' })" -ForegroundColor White
    }
    
    "sync" {
        Write-StatusMessage "=== 环境变量同步 ===" "Info"
        Set-DevelopmentEnvironmentVariables
        Test-EnvironmentVariables
    }
    
    "create-env" {
        Write-StatusMessage "=== 创建环境文件 ===" "Info"
        if (New-EnvironmentFile) {
            Write-StatusMessage "环境文件创建成功" "Success"
        } else {
            Write-StatusMessage "环境文件创建失败" "Error"
            exit 1
        }
    }
}

Write-StatusMessage "脚本执行完成" "Success"
