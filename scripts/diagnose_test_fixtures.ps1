# pytest fixture配置诊断脚本
# 用于快速检测和解决fixture依赖冲突问题
# 关联: [CHECK:TEST-002] docs/status/issues-tracking.md ISS-024

param(
    [string]$TestFile = "",
    [switch]$Fix = $false,
    [switch]$Verbose = $false
)

Write-Host "🔍 pytest fixture配置诊断工具" -ForegroundColor Cyan
Write-Host "关联问题: ISS-024 - pytest fixture依赖冲突" -ForegroundColor Yellow
Write-Host ""

$ConfTestPath = "tests\conftest.py"
$IssuesFound = 0

# 检查1: autouse fixture直接依赖检查
Write-Host "🔍 检查1: autouse fixture依赖问题" -ForegroundColor Green
$AutoUseFixtures = Select-String -Path $ConfTestPath -Pattern "@pytest\.fixture\(autouse=True\)" -Context 0,3

foreach ($Match in $AutoUseFixtures) {
    $LineContent = $Match.Line
    $Context = $Match.Context.PostContext
    
    # 检查是否直接依赖integration_test_engine
    if ($Context -match "integration_test_engine") {
        Write-Host "❌ 发现autouse fixture直接依赖integration_test_engine" -ForegroundColor Red
        Write-Host "   行号: $($Match.LineNumber)" -ForegroundColor Yellow
        Write-Host "   建议: 使用request.getfixturevalue('integration_test_engine')延迟获取" -ForegroundColor Cyan
        $IssuesFound++
    }
}

# 检查2: Mock配置问题
Write-Host "`n🔍 检查2: Mock配置问题" -ForegroundColor Green
$MockPatterns = Select-String -Path $ConfTestPath -Pattern "mocker\.patch\(" 

foreach ($Pattern in $MockPatterns) {
    if ($Pattern.Line -match "'([^']+)'") {
        $MockTarget = $Matches[1]
        Write-Host "📝 Mock目标: $MockTarget" -ForegroundColor Gray
        
        # 检查常见的不存在属性
        if ($MockTarget -match "redis_client\.redis_client|security_logger\.security_logger") {
            Write-Host "❌ 可能的Mock目标属性不存在: $MockTarget" -ForegroundColor Red
            $IssuesFound++
        }
    }
}

# 检查3: 不安全的属性修改
Write-Host "`n🔍 检查3: 不安全的属性修改" -ForegroundColor Green
$UnsafePatterns = Select-String -Path $ConfTestPath -Pattern "__defaults__\s*="

if ($UnsafePatterns) {
    Write-Host "❌ 发现不安全的__defaults__属性修改" -ForegroundColor Red
    foreach ($Pattern in $UnsafePatterns) {
        Write-Host "   行号: $($Pattern.LineNumber)" -ForegroundColor Yellow
        Write-Host "   内容: $($Pattern.Line.Trim())" -ForegroundColor Gray
    }
    $IssuesFound++
}

# 检查4: 测试文件数据库连接类型
if ($TestFile) {
    Write-Host "`n🔍 检查4: 测试文件数据库连接" -ForegroundColor Green
    
    # 运行单个测试看连接类型
    $TestOutput = & python -m pytest $TestFile --collect-only 2>&1
    
    if ($TestOutput -match "mysql|MySQL") {
        Write-Host "❌ 测试文件可能连接到MySQL而非SQLite" -ForegroundColor Red
        Write-Host "   建议: 检查fixture依赖和标记" -ForegroundColor Cyan
        $IssuesFound++
    } else {
        Write-Host "✅ 测试文件配置正常" -ForegroundColor Green
    }
}

# 总结和修复建议
Write-Host "`n📊 诊断结果" -ForegroundColor Cyan
if ($IssuesFound -eq 0) {
    Write-Host "✅ 未发现fixture配置问题" -ForegroundColor Green
} else {
    Write-Host "❌ 发现 $IssuesFound 个潜在问题" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 快速修复指南:" -ForegroundColor Yellow
    Write-Host "1. 查看完整解决方案: docs/status/issues-tracking.md ISS-024"
    Write-Host "2. 检查点参考: [CHECK:TEST-002] fixture配置错误排查"
    Write-Host "3. 模式参考: 使用request.getfixturevalue()延迟获取fixture"
    Write-Host ""
}

# 快速修复选项
if ($Fix -and $IssuesFound -gt 0) {
    Write-Host "🚀 启动自动修复..." -ForegroundColor Cyan
    Write-Host "注意: 此功能需要人工验证，建议手动修复" -ForegroundColor Yellow
    # 这里可以添加自动修复逻辑
}

Write-Host "`n📚 相关资源:" -ForegroundColor Cyan
Write-Host "- 问题追踪: docs/status/issues-tracking.md ISS-024"
Write-Host "- 检查点: docs/standards/checkpoint-cards.md TEST-002"
Write-Host "- 测试标准: docs/standards/testing-standards.md"