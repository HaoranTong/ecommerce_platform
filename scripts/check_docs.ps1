# 简单文档检查脚本
# 用法: .\scripts\check_docs.ps1

Write-Host "检查文档..." -ForegroundColor Green

# 检查文档数量
$docCount = (Get-ChildItem docs -Recurse -Filter "*.md").Count
Write-Host "发现 $docCount 个文档" -ForegroundColor Cyan

# 检查空文档
$emptyDocs = Get-ChildItem docs -Recurse -Filter "*.md" | Where-Object { $_.Length -eq 0 }
if ($emptyDocs.Count -gt 0) {
    Write-Host "发现 $($emptyDocs.Count) 个空文档:" -ForegroundColor Yellow
    $emptyDocs | ForEach-Object { Write-Host "  - $($_.FullName)" -ForegroundColor Red }
} else {
    Write-Host "✅ 没有空文档" -ForegroundColor Green
}

# 检查主要文档是否存在
$requiredDocs = @(
    "docs\README.md",
    "docs\requirements\business.md",
    "docs\architecture\overview.md",
    "app\main.py"
)

Write-Host "`n检查核心文件:" -ForegroundColor Cyan
foreach ($doc in $requiredDocs) {
    if (Test-Path $doc) {
        $size = (Get-Item $doc).Length
        Write-Host "✅ $doc ($size 字节)" -ForegroundColor Green
    } else {
        Write-Host "❌ $doc (缺失)" -ForegroundColor Red
    }
}

Write-Host "`n检查完成!" -ForegroundColor Green
