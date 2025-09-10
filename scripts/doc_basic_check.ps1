# 简单的文档质量检查脚本
param([string]$Path = "docs")

Write-Host "文档质量检查开始..." -ForegroundColor Cyan
Write-Host "检查路径: $Path" -ForegroundColor Blue
Write-Host ""

# 获取所有markdown文件
$mdFiles = Get-ChildItem -Path $Path -Filter "*.md" -Recurse

if ($mdFiles.Count -eq 0) {
    Write-Host "未找到任何Markdown文档" -ForegroundColor Red
    exit
}

$results = @()

foreach ($file in $mdFiles) {
    $relativePath = $file.FullName.Replace((Get-Location).Path, "").TrimStart('\')
    
    # 检查文件大小
    $size = $file.Length
    if ($size -eq 0) {
        $quality = "空文档"
        $color = "Red"
    } elseif ($size -lt 500) {
        $quality = "内容较少"
        $color = "Yellow"
    } else {
        $quality = "正常"
        $color = "Green"
    }
    
    # 检查是否有内容
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    $hasHeaders = if ($content -match "^#") { "有标题" } else { "无标题" }
    
    Write-Host "文档: $relativePath" -ForegroundColor White
    Write-Host "  大小: $size 字节 - $quality" -ForegroundColor $color
    Write-Host "  结构: $hasHeaders" -ForegroundColor White
    Write-Host ""
}

Write-Host "检查完成! 共检查 $($mdFiles.Count) 个文档" -ForegroundColor Green
