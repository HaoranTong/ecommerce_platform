Param(
    [string]$Message = '',
    [string]$Files = '',
    [string]$PrUrl = '',
    [string]$Author = '',
    [string]$Commit = '',
    [string]$Branch = '',
    [string]$Actor = ''
)

Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path $scriptDir -Parent
Push-Location $repo
try {
    $docsDir = Join-Path $repo 'docs\status'
    if (-not (Test-Path $docsDir)) { New-Item -ItemType Directory -Path $docsDir | Out-Null }
    $statusFile = Join-Path $docsDir 'status.md'
    if (-not (Test-Path $statusFile)) {
        "# Status log`n" | Out-File -FilePath $statusFile -Encoding utf8
    }

    $ts = (Get-Date).ToString('u')
    $line = "- [$ts] Message: $Message | PR: $PrUrl | Commit: $Commit | Branch: $Branch | Actor: $Actor | Files: $Files | Author: $Author"
    Add-Content -Path $statusFile -Value $line -Encoding utf8
    Write-Output "Wrote status: $line"
}
finally {
    Pop-Location
}
