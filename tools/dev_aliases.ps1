# PowerShell快速别名配置
# 用途：简化常用检查命令
# 使用：将此内容添加到 $PROFILE

# 修改前检查
function Check-Before-Modify {
    param(
        [string]$Module = "user_auth",
        [string]$Type = "fix"
    )
    .\tools\pre_modification_check.ps1 -ModuleName $Module -ChangeType $Type
}
Set-Alias cbm Check-Before-Modify

# 完整测试
function Test-All {
    Write-Host "运行完整测试套件..." -ForegroundColor Cyan
    pytest tests/ -v --tb=short
}
Set-Alias ta Test-All

# 单元测试
function Test-Unit {
    param([string]$Module = "")
    if ($Module) {
        pytest tests/unit/test_services/test_${Module}_service.py -v
    } else {
        pytest tests/unit/ -v
    }
}
Set-Alias tu Test-Unit

# 集成测试
function Test-Integration {
    param([string]$Module = "")
    if ($Module) {
        pytest tests/integration/test_api/test_${Module}_api.py -v
    } else {
        pytest tests/integration/ -v
    }
}
Set-Alias ti Test-Integration

# 质量检查
function Check-Quality {
    Write-Host "运行代码质量检查..." -ForegroundColor Cyan
    python tools/check_quality.py
    python tools/check_naming_compliance.ps1
}
Set-Alias cq Check-Quality

# 显示检查清单
function Show-Checklist {
    code .\tools\CODE_MODIFICATION_CHECKLIST.md
}
Set-Alias sc Show-Checklist

Write-Host "✅ 开发助手别名已加载" -ForegroundColor Green
Write-Host "   cbm  - 修改前检查 (Check Before Modify)" -ForegroundColor Cyan
Write-Host "   ta   - 完整测试 (Test All)" -ForegroundColor Cyan
Write-Host "   tu   - 单元测试 (Test Unit)" -ForegroundColor Cyan
Write-Host "   ti   - 集成测试 (Test Integration)" -ForegroundColor Cyan
Write-Host "   cq   - 质量检查 (Check Quality)" -ForegroundColor Cyan
Write-Host "   sc   - 显示检查清单 (Show Checklist)" -ForegroundColor Cyan
