#!/usr/bin/env pwsh
# 简单列出所有```标记，按奇偶数位置分析

param([Parameter(Mandatory = $true)][string]$FilePath)

Write-Host "🔍 分析 $FilePath 的所有```标记" -ForegroundColor Yellow

$lines = Get-Content $FilePath -ErrorAction SilentlyContinue
$codeBlockMarkers = @()

# 找出所有```标记
for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i].Trim()
    if ($line -match '^```(.*)$') {
        $language = $Matches[1]
        $codeBlockMarkers += [PSCustomObject]@{
            LineNumber = $i + 1
            Position = $codeBlockMarkers.Count + 1
            Language = $language
            IsOdd = (($codeBlockMarkers.Count + 1) % 2) -eq 1
            Line = $line
        }
    }
}

Write-Host "`n📊 找到 $($codeBlockMarkers.Count) 个```标记:" -ForegroundColor Cyan

foreach ($marker in $codeBlockMarkers) {
    $posType = if ($marker.IsOdd) { "开始" } else { "结束" }
    $langInfo = if ($marker.Language -eq "") { "❌ 无语言标识" } else { "✅ $($marker.Language)" }
    
    Write-Host "第$($marker.Position)个 (第$($marker.LineNumber)行): $posType标记 - $langInfo" -ForegroundColor $(if ($marker.IsOdd -and $marker.Language -eq "") { "Red" } else { "Green" })
}

Write-Host "`n🎯 问题分析:" -ForegroundColor Yellow
$oddMarkers = $codeBlockMarkers | Where-Object { $_.IsOdd }
$evenMarkers = $codeBlockMarkers | Where-Object { -not $_.IsOdd }

Write-Host "   奇数位(开始标记): $($oddMarkers.Count) 个" -ForegroundColor Blue
Write-Host "   偶数位(结束标记): $($evenMarkers.Count) 个" -ForegroundColor Blue

$problematicOdd = $oddMarkers | Where-Object { $_.Language -eq "" }
Write-Host "   无语言标识的开始标记: $($problematicOdd.Count) 个" -ForegroundColor Red

if ($oddMarkers.Count -ne $evenMarkers.Count) {
    Write-Host "   ⚠️  代码块不匹配！开始和结束数量不相等" -ForegroundColor Red
}

if ($problematicOdd.Count -gt 0) {
    Write-Host "`n❌ 需要修复的位置:" -ForegroundColor Red
    foreach ($prob in $problematicOdd) {
        Write-Host "   第$($prob.LineNumber)行: $($prob.Line)" -ForegroundColor Red
    }
}
