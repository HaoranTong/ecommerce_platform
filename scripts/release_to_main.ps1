Param(
    [switch]$RunNow
)

Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path $scriptDir -Parent
Push-Location $repo
try {
    Write-Output "Release script starting in $repo"

    # Activate venv if present
    $venvActivate = Join-Path $repo '.venv\Scripts\Activate.ps1'
    if (Test-Path $venvActivate) { & $venvActivate }

    # Ensure working tree is clean
    $status = git status --porcelain
    if ($status) {
        Write-Error "Working tree not clean. Commit or stash changes before release."
        exit 1
    }

    # Update dev
    git checkout dev
    git pull origin dev

    # Run smoke test on dev
    Write-Output "Running smoke test on dev..."
    & .\scripts\smoke_test.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Smoke test on dev failed (exit $LASTEXITCODE). Aborting release."
        exit $LASTEXITCODE
    }

    # Merge into main
    Write-Output "Merging dev into main..."
    git checkout main
    git pull origin main
    git merge --no-ff dev -m "chore(release): merge dev into main"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Merge failed. Resolve conflicts manually."
        exit 2
    }

    git push origin main

    # Record merge into status log
    Write-Output "Recording release merge into status log..."
    pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\log_status.ps1 -Message "Merged dev into main" -Files "" -PrUrl "" -Author "release-bot"

    # Run smoke test on main
    Write-Output "Running smoke test on main..."
    & .\scripts\smoke_test.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Smoke test on main failed (exit $LASTEXITCODE)."
        exit $LASTEXITCODE
    }

    Write-Output "Release to main completed successfully."

    # Record release completion
    pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\log_status.ps1 -Message "Release to main completed" -Files "" -PrUrl "" -Author "release-bot"
} finally {
    Pop-Location
}
