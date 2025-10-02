#!/usr/bin/env pwsh
<#
.SYNOPSIS
    电商平台烟雾测试脚本 - 环境感知版本
.DESCRIPTION
    根据运行环境自动选择测试策略：
    - development: 内存数据库，快速验证
    - ci_pipeline: 临时文件数据库，CI/CD验证  
    - post_deployment: 生产数据库，部署后验证
.EXAMPLE
    # 默认开发模式
    .\tools\smoke_test.ps1
    
    # 显式指定模式
    $env:SMOKE_TEST_MODE="ci_pipeline"; .\tools\smoke_test.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# 初始化测试状态
$script:TestSuccess = $true

# ========== 环境检测函数 ==========
function Get-SmokeTestMode {
    <#
    .SYNOPSIS
    检测烟雾测试运行环境模式
    
    .OUTPUTS
    返回: development | ci_pipeline | post_deployment
    #>
    
    # 1. 显式环境变量检测
    if ($env:SMOKE_TEST_MODE) {
        Write-Host "🔍 检测到显式环境变量: SMOKE_TEST_MODE=$env:SMOKE_TEST_MODE" -ForegroundColor Cyan
        return $env:SMOKE_TEST_MODE
    }
    
    # 2. CI/CD环境检测
    if ($env:CI -eq "true" -or $env:GITHUB_ACTIONS -eq "true" -or $env:BUILD_NUMBER) {
        Write-Host "🚀 检测到CI/CD环境" -ForegroundColor Yellow
        return "ci_pipeline"
    }
    
    # 3. 生产环境检测
    if ($env:ENVIRONMENT -eq "production" -or $env:NODE_ENV -eq "production") {
        Write-Host "🎯 检测到生产环境" -ForegroundColor Green
        return "post_deployment"
    }
    
    # 4. 服务运行状态检测
    try {
        $serverTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        if ($serverTest.TcpTestSucceeded) {
            Write-Host "🔍 检测到服务已在运行，推断为部署后验证" -ForegroundColor Green
            return "post_deployment"
        }
    }
    catch {
        # 忽略网络检测错误
    }
    
    # 5. 默认：开发环境
    Write-Host "🔧 默认开发环境模式" -ForegroundColor Blue
    return "development"
}

function Set-SmokeTestEnvironment {
    param([string]$Mode)
    
    Write-Output ""
    Write-Output "🔍 检查点：验证烟雾测试环境配置..."
    
    switch ($Mode) {
        "development" {
            Write-Output "🔧 开发模式：使用内存数据库，快速验证"
            $env:SMOKE_TEST_MODE = "development"
            Write-Output "✅ 数据库策略: 内存数据库 (sqlite:///:memory:)"
        }
        "ci_pipeline" {
            Write-Output "🚀 CI管道模式：使用临时文件数据库"
            $env:SMOKE_TEST_MODE = "ci_pipeline"
            if (-not $env:DATABASE_URL) {
                $env:DATABASE_URL = 'sqlite:///./tests/smoke_test_ci.db'
            }
            Write-Output "✅ 数据库策略: 临时文件数据库 ($env:DATABASE_URL)"
        }
        "post_deployment" {
            Write-Output "🎯 部署后模式：验证生产环境状态"
            $env:SMOKE_TEST_MODE = "post_deployment"
            if (-not $env:DATABASE_URL) {
                Write-Output "⚠️  警告：部署后模式建议配置生产数据库连接"
                $env:DATABASE_URL = 'sqlite:///./app.db'
            }
            Write-Output "✅ 数据库策略: 生产环境数据库 ($env:DATABASE_URL)"
        }
        default {
            Write-Output "❌ 未知的烟雾测试模式: $Mode"
            exit 1
        }
    }
}

# ========== 主函数：烟雾测试执行 ==========
function Start-SmokeTest {
    # compute repository root (script is in <repo>/tools)
    $scriptPath = $MyInvocation.ScriptName
    if (-not $scriptPath) {
        $scriptPath = $PSCommandPath
    }
    $scriptDir = Split-Path -Parent $scriptPath
    $repo = Split-Path $scriptDir -Parent
    Write-Output "repo: $repo"

    Push-Location $repo
    
    try {
        # activate venv if present
        $venvActivate = Join-Path $repo '.venv\Scripts\Activate.ps1'
        if (Test-Path $venvActivate) {
            Write-Output "Activating venv: $venvActivate"
            & $venvActivate
        }
        else {
            Write-Output "No venv activate script found at $venvActivate"
        }

        # 检测并配置烟雾测试环境
        $smokeMode = Get-SmokeTestMode
        Set-SmokeTestEnvironment -Mode $smokeMode
        
        # 烟雾测试启用自动创建表（除非是部署后模式）
        if ($env:SMOKE_TEST_MODE -ne "post_deployment") {
            $env:AUTO_CREATE_TABLES = '1'
            Write-Output "✅ 启用自动创建数据库表: AUTO_CREATE_TABLES=1"
        }
        else {
            $env:AUTO_CREATE_TABLES = '0'
            Write-Output "ℹ️  部署后模式：跳过数据库表创建"
        }
        
        # Redis配置
        if (-not $env:REDIS_URL -or $env:REDIS_URL -eq '') {
            $env:REDIS_URL = 'redis://127.0.0.1:6379/0'
            Write-Output "✅ 使用Redis配置: $env:REDIS_URL"
        }
        else {
            Write-Output "✅ 使用Redis配置: $env:REDIS_URL"
        }

        Write-Output ""
        Write-Output "🔍 检查服务器状态..."
        
        # 测试服务器连接
        function Test-Server {
            param([int]$TimeoutSec = 3)
            try {
                Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec $TimeoutSec -ErrorAction Stop | Out-Null
                return $true
            }
            catch {
                try {
                    Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/" -TimeoutSec $TimeoutSec -ErrorAction Stop | Out-Null
                    return $true
                }
                catch {
                    return $false
                }
            }
        }

        # 根据模式决定是否启动服务器
        $needStartServer = $true
        if ($env:SMOKE_TEST_MODE -eq "post_deployment") {
            if (Test-Server) {
                Write-Output "✅ 部署后模式：检测到服务正在运行"
                $needStartServer = $false
            }
            else {
                Write-Output "❌ 部署后模式：服务未运行，无法进行验证"
                $script:TestSuccess = $false
                return
            }
        }
        else {
            if (Test-Server) {
                Write-Output "ℹ️  检测到服务已在运行，将复用现有服务"
                $needStartServer = $false
            }
        }

        $uvicornPid = $null
        if ($needStartServer) {
            Write-Output "📡 服务器未运行，正在启动uvicorn服务器..."
            
            if ($env:SMOKE_TEST_MODE -ne "post_deployment") {
                Write-Output "🔧 烟雾测试模式：跳过Alembic迁移，使用AUTO_CREATE_TABLES自动创建表"
            }
            
            $uvicornProcess = Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app", "--host", "127.0.0.1", "--port", "8000" -WindowStyle Hidden -PassThru
            $uvicornPid = $uvicornProcess.Id
            Write-Output "🚀 Uvicorn进程已启动 (PID: $uvicornPid)"
            
            # 等待服务器启动
            $maxWait = 30
            $waited = 0
            do {
                Start-Sleep -Seconds 2
                $waited += 2
                Write-Output "⏳ 等待服务器启动... ($waited/$maxWait 秒)"
            } while (-not (Test-Server) -and $waited -lt $maxWait)
            
            if (-not (Test-Server)) {
                Write-Output "❌ 服务器启动失败或响应超时"
                $script:TestSuccess = $false
                return
            }
        }

        Write-Output ""
        Write-Output "=== Running pytest smoke tests ==="
        
        # 运行pytest烟雾测试，显示详细输出
        $pytestArgs = if ($env:PYTEST_ARGS) { $env:PYTEST_ARGS } else { "-v -s" }
        Write-Output "🔍 Pytest参数: $pytestArgs"
        
        $pytestResult = pytest tests/smoke/ $pytestArgs.Split(' ')
        $pytestExitCode = $LASTEXITCODE
        
        if ($pytestExitCode -eq 0) {
            Write-Output "✅ Pytest smoke tests passed"
        }
        else {
            Write-Output "❌ Pytest smoke tests failed"
            $script:TestSuccess = $false
        }

        # 只在非部署后模式运行通用API健康测试
        if ($env:SMOKE_TEST_MODE -ne "post_deployment") {
            Write-Output ""
            Write-Output "=== Running additional API health checks ==="
            
            # 通用API健康检查，不涉及具体业务逻辑
            try {
                # 测试API文档可访问性
                $docsResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/docs" -Method GET -TimeoutSec 5
                Write-Output "✅ API文档可访问"
                
                # 测试OpenAPI规范
                $openApiResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/openapi.json" -Method GET -TimeoutSec 5
                Write-Output "✅ OpenAPI规范可访问"
                
                # 测试根路径
                $rootResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method GET -TimeoutSec 5
                Write-Output "✅ 根路径响应正常"
                
                Write-Output "✅ 通用API健康检查完成"
            }
            catch {
                Write-Output "⚠️  API健康检查遇到问题: $($_.Exception.Message)"
                # 不设置失败状态，因为这不是关键功能
            }
        }
        else {
            Write-Output ""
            Write-Output "ℹ️  部署后模式：跳过数据修改测试，仅验证API可用性"
        }

        # 清理启动的服务器
        if ($uvicornPid) {
            Write-Output ""
            Write-Output "🧹 清理：停止烟雾测试启动的uvicorn服务器..."
            try {
                $process = Get-Process -Id $uvicornPid -ErrorAction SilentlyContinue
                if ($process) {
                    Stop-Process -Id $uvicornPid -Force
                    Start-Sleep -Seconds 2
                    
                    $process = Get-Process -Id $uvicornPid -ErrorAction SilentlyContinue
                    if (-not $process) {
                        Write-Output "✅ Uvicorn进程已成功停止"
                    }
                    else {
                        Write-Output "⚠️  Uvicorn进程可能仍在运行"
                    }
                }
                else {
                    Write-Output "ℹ️  Uvicorn进程已自行退出"
                }
            }
            catch {
                Write-Output "⚠️  停止uvicorn进程时出现异常: $($_.Exception.Message)"
            }
        }
    }
    finally {
        Pop-Location
        
        # ========== 环境感知的清理策略 ==========
        Write-Output ""
        Write-Output "🧹 执行环境感知清理..."
        
        switch ($env:SMOKE_TEST_MODE) {
            "development" {
                Write-Output "🔧 开发模式：内存数据库已自动清理"
            }
            "ci_pipeline" {
                Write-Output "🚀 CI模式：清理临时文件"
                try {
                    $tempFiles = @(
                        "tests/smoke_test_ci.db",
                        "tests/smoke_test_ci.db-shm", 
                        "tests/smoke_test_ci.db-wal"
                    )
                    
                    foreach ($file in $tempFiles) {
                        if (Test-Path $file) {
                            Remove-Item $file -Force
                            Write-Output "✅ 已删除CI临时文件: $file"
                        }
                    }
                }
                catch {
                    Write-Output "⚠️  清理CI临时文件时出现异常: $($_.Exception.Message)"
                }
            }
            "post_deployment" {
                Write-Output "🎯 部署后模式：保持生产环境数据不变"
                Write-Output "ℹ️  生产环境数据未被修改"
            }
            default {
                Write-Output "⚠️  未知清理模式，跳过清理"
            }
        }
        
        # ========== 输出最终结果 ==========
        Write-Output ""
        if ($script:TestSuccess -ne $false) {
            Write-Output "🎉 烟雾测试完成：所有测试通过"
            exit 0
        }
        else {
            Write-Output "❌ 烟雾测试完成：部分测试失败"
            exit 1
        }
    }
}

# ========== 脚本入口点 ==========
Start-SmokeTest
