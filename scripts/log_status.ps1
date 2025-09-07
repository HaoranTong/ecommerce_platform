<#
.SYNOPSIS
Append a structured status entry to docs/status/status.md

.PARAMETER Message
Short summary of the status entry (required)
.PARAMETER Files
Comma-separated list of affected files or paths (optional)
.PARAMETER PrUrl
URL to related PR or issue (optional)
.PARAMETER Author
Author name to record (optional, defaults to 'automation')

Example:
.\scripts\log_status.ps1 -Message "Merged feature/product into dev" -Files "app/models.py, alembic/versions/0002_product.py" -PrUrl "https://github.com/.../pull/123" -Author "CI"
#>
param(
    [Parameter(Mandatory=$true)] [string]$Message,
    [string]$Files = "",
    [string]$PrUrl = "",
    [string]$Author = "automation",
    [string]$Commit = "",
    [string]$Branch = "",
    [string]$Actor = ""
)

$statusPath = Join-Path $PSScriptRoot "..\docs\status\status.md"
if (-not (Test-Path $statusPath)) {
    Write-Error "Status file not found at $statusPath"
    exit 2
}

$now = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')

$entry = "`n## $now — $Author`n`n"
$entry += "- Summary: $Message`n"
if ($Files -ne "") { $entry += "- Files: $Files`n" }
if ($PrUrl -ne "") { $entry += "- PR/Issue: $PrUrl`n" }
$entry += "- Branch: $Branch`n"
$entry += "- Commit: $Commit`n"
if ($Actor -ne "") { $entry += "- Actor: $Actor`n" }
$entry += "`n"

Add-Content -Path $statusPath -Value $entry
Write-Output "Appended status entry to $statusPath"
