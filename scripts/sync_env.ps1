# 环境变量同步脚本
# 用于管理和同步项目环境变量配置

<#
.SYNOPSIS
    环境变量同步和管理工具

.DESCRIPTION
    本脚本用于管理项目的环境变量配置：
    1. 检查必要的环境变量是否设置
    2. 创建或更新.env文件
    3. 验证环境配置的完整性

.PARAMETER Action
    执行的操作：check（检查）、create（创建）、update（更新）

.EXAMPLE
    .\scripts\sync_env.ps1 -Action check
    # 检查当前环境变量配置

.EXAMPLE
    .\scripts\sync_env.ps1 -Action create
    # 创建新的.env文件

.NOTES
    文件名: sync_env.ps1
    作者: 系统管理员
    版本: 1.0.0
    修复日期: 2025-09-20
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("check", "create", "update")]
    [string]$Action = "check"
)

Set-StrictMode -Version Latest

$script:ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$script:EnvFile = Join-Path $script:ProjectRoot ".env"

# 必需的环境变量列表
$RequiredEnvVars = @(
    "DATABASE_URL",
    "SECRET_KEY",
    "REDIS_URL",
    "LOG_LEVEL"
)

function Write-StatusMessage {
    param([string]$Message, [string]$Type = "Info")
    
    switch ($Type) {
        "Success" { Write-Host "✅ $Message" -ForegroundColor Green }
        "Warning" { Write-Host "⚠️  $Message" -ForegroundColor Yellow }
        "Error"   { Write-Host "❌ $Message" -ForegroundColor Red }
        default   { Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
    }
}

function Test-EnvironmentVariables {
    Write-StatusMessage "检查环境变量配置..." "Info"
    
    $missingVars = @()
    foreach ($envVar in $RequiredEnvVars) {
        $value = [System.Environment]::GetEnvironmentVariable($envVar)
        if ([string]::IsNullOrWhiteSpace($value)) {
            $missingVars += $envVar
            Write-StatusMessage "缺少环境变量: $envVar" "Warning"
        } else {
            Write-StatusMessage "环境变量已设置: $envVar" "Success"
        }
    }
    
    if ($missingVars.Count -eq 0) {
        Write-StatusMessage "所有必需的环境变量均已正确设置" "Success"
        return $true
    } else {
        Write-StatusMessage "发现 $($missingVars.Count) 个缺失的环境变量" "Error"
        return $false
    }
}

function New-EnvFile {
    Write-StatusMessage "创建新的.env文件..." "Info"
    
    $envContent = @"
# 项目环境变量配置文件
# 生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

# 数据库配置
DATABASE_URL=sqlite:///./ecommerce_dev.db
TEST_DATABASE_URL=sqlite:///./test_ecommerce.db

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=detailed

# 应用配置
APP_NAME=E-commerce Platform
APP_VERSION=1.0.0
DEBUG=false

# API配置
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
"@

    try {
        $envContent | Out-File -FilePath $script:EnvFile -Encoding UTF8 -Force
        Write-StatusMessage ".env文件创建成功: $script:EnvFile" "Success"
        return $true
    } catch {
        Write-StatusMessage "创建.env文件失败: $($_.Exception.Message)" "Error"
        return $false
    }
}

# 主执行逻辑
switch ($Action) {
    "check" {
        Write-StatusMessage "执行环境变量检查..." "Info"
        $result = Test-EnvironmentVariables
        
        if (Test-Path $script:EnvFile) {
            Write-StatusMessage ".env文件存在: $script:EnvFile" "Success"
        } else {
            Write-StatusMessage ".env文件不存在，建议运行: .\scripts\sync_env.ps1 -Action create" "Warning"
        }
        
        exit $(if ($result) { 0 } else { 1 })
    }
    
    "create" {
        if (Test-Path $script:EnvFile) {
            Write-StatusMessage ".env文件已存在，使用 -Action update 进行更新" "Warning"
            exit 1
        }
        
        $result = New-EnvFile
        exit $(if ($result) { 0 } else { 1 })
    }
    
    "update" {
        Write-StatusMessage "环境变量更新功能尚未实现" "Warning"
        Write-StatusMessage "请手动编辑 .env 文件或删除后重新创建" "Info"
        exit 0
    }
}
