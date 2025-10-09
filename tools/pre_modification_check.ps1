# 代码修改强制检查脚本
# 用途：在修改代码前强制执行检查清单
# 使用：.\tools\pre_modification_check.ps1 -ModuleName "user_auth" -ChangeType "fix"

param(
    [Parameter(Mandatory=$true)]
    [string]$ModuleName,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("fix", "feature", "refactor", "test")]
    [string]$ChangeType,
    
    [Parameter(Mandatory=$false)]
    [string]$Description = ""
)

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "  代码修改强制检查清单" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

$checklistPath = ".\tools\CODE_MODIFICATION_CHECKLIST.md"
$logFile = ".\logs\modification_checks_$(Get-Date -Format 'yyyyMMdd').log"

# 确保日志目录存在
if (-not (Test-Path ".\logs")) {
    New-Item -ItemType Directory -Path ".\logs" | Out-Null
}

# 记录检查开始
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$timestamp] 开始检查 - 模块: $ModuleName, 类型: $ChangeType" | Out-File -Append $logFile

Write-Host "🎯 检查模块: $ModuleName" -ForegroundColor Yellow
Write-Host "🎯 修改类型: $ChangeType" -ForegroundColor Yellow
Write-Host "🎯 描述: $Description" -ForegroundColor Yellow
Write-Host ""

# ============================================
# 第1步：标准符合性检查
# ============================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "1️⃣  标准符合性检查" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$standardFiles = @(
    ".\docs\standards\testing-standards.md",
    ".\docs\standards\naming-conventions.md",
    ".\docs\standards\coding-standards.md"
)

Write-Host "📖 请确认已查阅以下标准文档：" -ForegroundColor White
foreach ($file in $standardFiles) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $file [不存在]" -ForegroundColor Red
    }
}

Write-Host ""
$response = Read-Host "是否已查阅相关标准？(y/n)"
if ($response -ne "y") {
    Write-Host "❌ 检查失败：必须先查阅标准文档！" -ForegroundColor Red
    "[$timestamp] 检查失败 - 未查阅标准文档" | Out-File -Append $logFile
    exit 1
}

"[$timestamp] ✓ 标准符合性检查通过" | Out-File -Append $logFile

# ============================================
# 第2步：影响范围分析
# ============================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "2️⃣  影响范围分析" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host "🔍 需要分析的影响范围：" -ForegroundColor White
Write-Host "   • 单元测试 (tests/unit/)" -ForegroundColor White
Write-Host "   • 集成测试 (tests/integration/)" -ForegroundColor White
Write-Host "   • E2E测试 (tests/e2e/)" -ForegroundColor White
Write-Host "   • 其他模块依赖" -ForegroundColor White

Write-Host ""
$response = Read-Host "是否已分析完整影响范围？(y/n)"
if ($response -ne "y") {
    Write-Host "❌ 检查失败：必须完成影响范围分析！" -ForegroundColor Red
    "[$timestamp] 检查失败 - 未完成影响范围分析" | Out-File -Append $logFile
    exit 1
}

"[$timestamp] ✓ 影响范围分析完成" | Out-File -Append $logFile

# ============================================
# 第3步：技术约束检查
# ============================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "3️⃣  技术约束检查" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host "⚙️  技术约束检查项：" -ForegroundColor White
Write-Host "   • 异步/同步上下文正确" -ForegroundColor White
Write-Host "   • 事件循环状态清晰" -ForegroundColor White
Write-Host "   • 数据库连接隔离" -ForegroundColor White
Write-Host "   • Redis连接正确" -ForegroundColor White
Write-Host "   • 无循环依赖" -ForegroundColor White

Write-Host ""
$response = Read-Host "是否已检查所有技术约束？(y/n)"
if ($response -ne "y") {
    Write-Host "❌ 检查失败：必须完成技术约束检查！" -ForegroundColor Red
    "[$timestamp] 检查失败 - 未完成技术约束检查" | Out-File -Append $logFile
    exit 1
}

"[$timestamp] ✓ 技术约束检查完成" | Out-File -Append $logFile

# ============================================
# 第4步：方案设计
# ============================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "4️⃣  方案设计" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host "💡 请至少考虑3个备选方案，并记录：" -ForegroundColor White
Write-Host "   • 方案A: 优点/缺点" -ForegroundColor White
Write-Host "   • 方案B: 优点/缺点" -ForegroundColor White
Write-Host "   • 方案C: 优点/缺点" -ForegroundColor White
Write-Host "   • 最终选择及理由" -ForegroundColor White

Write-Host ""
$response = Read-Host "是否已完成方案设计？(y/n)"
if ($response -ne "y") {
    Write-Host "❌ 检查失败：必须完成方案设计！" -ForegroundColor Red
    "[$timestamp] 检查失败 - 未完成方案设计" | Out-File -Append $logFile
    exit 1
}

"[$timestamp] ✓ 方案设计完成" | Out-File -Append $logFile

# ============================================
# 第5步：运行测试验证
# ============================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "5️⃣  测试验证（修改前基线）" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host "🧪 即将运行基线测试..." -ForegroundColor White

# 运行单元测试
Write-Host ""
Write-Host "▶ 运行单元测试..." -ForegroundColor Yellow
$unitTestResult = pytest tests/unit/test_services/test_${ModuleName}_service.py -v --tb=short 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ 单元测试通过" -ForegroundColor Green
    "[$timestamp] ✓ 单元测试基线通过" | Out-File -Append $logFile
} else {
    Write-Host "   ⚠ 单元测试有失败" -ForegroundColor Yellow
    Write-Host "   测试输出已记录到日志" -ForegroundColor Yellow
    "[$timestamp] ⚠ 单元测试基线失败" | Out-File -Append $logFile
    $unitTestResult | Out-File -Append $logFile
}

# 运行集成测试
Write-Host ""
Write-Host "▶ 运行集成测试..." -ForegroundColor Yellow
$integrationTestResult = pytest tests/integration/test_api/test_${ModuleName}_api.py -v --tb=short 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ 集成测试通过" -ForegroundColor Green
    "[$timestamp] ✓ 集成测试基线通过" | Out-File -Append $logFile
} else {
    Write-Host "   ⚠ 集成测试有失败" -ForegroundColor Yellow
    Write-Host "   测试输出已记录到日志" -ForegroundColor Yellow
    "[$timestamp] ⚠ 集成测试基线失败" | Out-File -Append $logFile
    $integrationTestResult | Out-File -Append $logFile
}

Write-Host ""
Write-Host "📊 基线测试完成，请记录当前状态" -ForegroundColor White

$response = Read-Host "是否已记录基线测试结果？(y/n)"
if ($response -ne "y") {
    Write-Host "❌ 检查失败：必须记录基线测试结果！" -ForegroundColor Red
    "[$timestamp] 检查失败 - 未记录基线" | Out-File -Append $logFile
    exit 1
}

# ============================================
# 检查完成
# ============================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ 所有检查通过！" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

Write-Host "📝 检查摘要：" -ForegroundColor White
Write-Host "   ✓ 标准符合性检查" -ForegroundColor Green
Write-Host "   ✓ 影响范围分析" -ForegroundColor Green
Write-Host "   ✓ 技术约束检查" -ForegroundColor Green
Write-Host "   ✓ 方案设计" -ForegroundColor Green
Write-Host "   ✓ 基线测试" -ForegroundColor Green

Write-Host ""
Write-Host "⚠️  重要提醒：" -ForegroundColor Yellow
Write-Host "   1. 修改后必须运行回归测试" -ForegroundColor Yellow
Write-Host "   2. 提交前必须运行质量检查" -ForegroundColor Yellow
Write-Host "   3. 记录修改到检查清单" -ForegroundColor Yellow

Write-Host ""
Write-Host "📋 检查清单位置: $checklistPath" -ForegroundColor Cyan
Write-Host "📋 日志文件位置: $logFile" -ForegroundColor Cyan

"[$timestamp] ✓ 所有检查通过 - 允许修改代码" | Out-File -Append $logFile

Write-Host ""
Write-Host "🚀 现在可以开始修改代码了！" -ForegroundColor Green
Write-Host ""
