<#
.SYNOPSIS
集成测试执行脚本 - 使用MySQL Docker容器进行完整集成测试

.DESCRIPTION
执行完整的集成测试流程，验证多模块协作和数据库集成：
- 自动管理MySQL Docker容器生命周期
- 激活项目虚拟环境
- 配置集成测试环境变量
- 执行pytest集成测试
- 提供灵活的容器管理选项

主要功能：
- Docker容器自动启动和停止
- MySQL数据库连接验证  
- 集成测试环境配置
- 测试结果记录和报告

.PARAMETER SkipDocker
跳过Docker容器管理，假设MySQL容器已经运行
适用于在已有Docker环境中执行测试的场景

.PARAMETER KeepContainer
测试完成后保持Docker容器运行状态
适用于需要检查测试后数据状态或调试的场景

.EXAMPLE
.\tools\integration_test.ps1
执行完整集成测试，自动管理Docker容器

.EXAMPLE
.\tools\integration_test.ps1 -SkipDocker
在现有Docker环境中执行集成测试

.EXAMPLE  
.\tools\integration_test.ps1 -KeepContainer
执行集成测试并保持容器运行以便调试

.NOTES
Author: AI Development Team
Created: 2025-09-30
Version: 1.0
Dependencies: Docker Desktop, Python 3.8+, pytest
Environment: 需要Docker环境和MySQL容器
#>

# 集成测试脚本
# 使用MySQL Docker容器进行完整的集成测试
# 自动管理Docker容器生命周期

Param(
    [Parameter(Mandatory = $false)]
    [switch]$SkipDocker = $false,  # 跳过Docker管理，假设容器已运行
    
    [Parameter(Mandatory = $false)]
    [switch]$KeepContainer = $false  # 测试后保持容器运行
)

Set-StrictMode -Version Latest

# 🔍 检查点触发：集成测试环境检查
Write-Output "🔍 检查点：验证集成测试环境配置..."

# 初始化测试状态
$script:TestSuccess = $true
$script:DockerStarted = $false

# 计算项目根目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path $scriptDir -Parent
Write-Output "项目根目录: $repo"

Push-Location $repo
try {
    # 激活虚拟环境
    $venvActivate = Join-Path $repo '.venv\Scripts\Activate.ps1'
    if (Test-Path $venvActivate) {
        Write-Output "✅ 激活虚拟环境: $venvActivate"
        & $venvActivate
    }
    else {
        Write-Output "⚠️  未找到虚拟环境: $venvActivate"
    }

    # 检查Docker是否可用
    if (-not $SkipDocker) {
        Write-Output "🐳 检查Docker服务..."
        try {
            $dockerVersion = docker --version
            Write-Output "✅ Docker可用: $dockerVersion"
        }
        catch {
            Write-Output "❌ Docker不可用，请确保Docker已安装并运行"
            $script:TestSuccess = $false
            return
        }

        # 启动MySQL测试容器
        Write-Output "🚀 启动MySQL测试容器..."
        try {
            # 停止并删除已存在的测试容器
            docker stop mysql_integration_test 2>$null
            docker rm mysql_integration_test 2>$null

            # 启动新的测试容器
            docker run -d --name mysql_integration_test `
                -e MYSQL_ROOT_PASSWORD=test_root_pass `
                -e MYSQL_DATABASE=test_ecommerce `
                -e MYSQL_USER=test_user `
                -e MYSQL_PASSWORD=test_pass `
                -p 3307:3306 `
                mysql:8.0

            if ($LASTEXITCODE -eq 0) {
                Write-Output "✅ MySQL测试容器启动成功"
                $script:DockerStarted = $true
                
                # 等待数据库就绪
                Write-Output "⏳ 等待数据库启动..."
                Start-Sleep -Seconds 15
                
                # 验证数据库连接
                $maxRetries = 30
                $retryCount = 0
                do {
                    try {
                        docker exec mysql_integration_test mysql -utest_user -ptest_pass -e "SELECT 1;" test_ecommerce 2>$null | Out-Null
                        if ($LASTEXITCODE -eq 0) {
                            Write-Output "✅ 数据库连接验证成功"
                            break
                        }
                    }
                    catch {
                        # 继续重试
                    }
                    $retryCount++
                    Start-Sleep -Seconds 2
                } while ($retryCount -lt $maxRetries)
                
                if ($retryCount -eq $maxRetries) {
                    Write-Output "❌ 数据库连接验证失败"
                    $script:TestSuccess = $false
                    return
                }
            }
            else {
                Write-Output "❌ MySQL测试容器启动失败"
                $script:TestSuccess = $false
                return
            }
        }
        catch {
            Write-Output "❌ Docker操作失败: $_"
            $script:TestSuccess = $false
            return
        }
    }

    # 设置集成测试环境变量
    $env:DATABASE_URL = 'mysql+pymysql://test_user:test_pass@127.0.0.1:3307/test_ecommerce'
    $env:REDIS_URL = 'redis://127.0.0.1:6379/0'
    Write-Output "✅ 集成测试数据库: $env:DATABASE_URL"

    # 运行数据库迁移
    Write-Output "🔄 运行数据库迁移..."
    try {
        $env:ALEMBIC_DSN = $env:DATABASE_URL
        alembic upgrade head
        if ($LASTEXITCODE -eq 0) {
            Write-Output "✅ 数据库迁移完成"
        }
        else {
            Write-Output "❌ 数据库迁移失败"
            $script:TestSuccess = $false
            return
        }
    }
    catch {
        Write-Output "❌ 数据库迁移异常: $_"
        $script:TestSuccess = $false
        return
    }

    # 运行集成测试
    Write-Output "🧪 运行集成测试..."
    try {
        pytest tests/integration/ -v --tb=short
        if ($LASTEXITCODE -eq 0) {
            Write-Output "✅ 集成测试通过"
        }
        else {
            Write-Output "❌ 集成测试失败"
            $script:TestSuccess = $false
        }
    }
    catch {
        Write-Output "❌ 集成测试异常: $_"
        $script:TestSuccess = $false
    }

    # 运行E2E测试
    Write-Output "🎯 运行端到端测试..."
    try {
        pytest tests/e2e/ -v --tb=short
        if ($LASTEXITCODE -eq 0) {
            Write-Output "✅ E2E测试通过"
        }
        else {
            Write-Output "❌ E2E测试失败"
            $script:TestSuccess = $false
        }
    }
    catch {
        Write-Output "❌ E2E测试异常: $_"
        $script:TestSuccess = $false
    }

}
finally {
    # 清理Docker容器
    if ($script:DockerStarted -and -not $KeepContainer) {
        Write-Output "🧹 清理测试容器..."
        docker stop mysql_integration_test 2>$null
        docker rm mysql_integration_test 2>$null
        Write-Output "✅ 测试容器已清理"
    }
    elseif ($script:DockerStarted -and $KeepContainer) {
        Write-Output "🔒 保持测试容器运行（使用 -KeepContainer 参数）"
        Write-Output "手动清理命令: docker stop mysql_integration_test && docker rm mysql_integration_test"
    }
    
    Pop-Location
}

# 输出测试结果
if ($script:TestSuccess) {
    Write-Output "🎉 集成测试全部通过！"
    exit 0
}
else {
    Write-Output "💥 集成测试失败！"
    exit 1
}
