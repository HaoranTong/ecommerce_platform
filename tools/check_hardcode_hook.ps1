# 硬编码检查预提交钩子

# 在每次修改API测试生成器后自动运行检查
function Check-Hardcode {
    Write-Host "🔍 执行硬编码检查..." -ForegroundColor Yellow
    
    $result = python tools/check_hardcode.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 硬编码检查失败！" -ForegroundColor Red
        Write-Host "必须修复所有硬编码问题才能继续" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "✅ 硬编码检查通过" -ForegroundColor Green
    }
}

# 使用方法：在修改api_test_generator.py后运行
# .\tools\check_hardcode_hook.ps1