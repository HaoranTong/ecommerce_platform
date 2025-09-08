Param(
    [switch]$RunNow,
    [switch]$DryRun
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
    git fetch github
    git pull github dev

    # Run smoke test on dev
    Write-Output "Running smoke test on dev..."
    & .\scripts\smoke_test.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Smoke test on dev failed (exit $LASTEXITCODE). Aborting release."
        exit $LASTEXITCODE
    }

    # Merge into main (with safer rollback)
    Write-Output "Merging dev into main..."
    git checkout main
    git fetch github
    git pull github main

    $preMain = git rev-parse refs/heads/main

    if ($DryRun) {
        Write-Output "DryRun: showing merge plan (no changes will be made)"
        git merge --no-ff --no-commit dev || Write-Output "Merge would fail or has conflicts"
        git merge --abort || Write-Output "No merge to abort"
        Write-Output "DryRun complete."
        exit 0
    }

    git merge --no-ff dev -m "chore(release): merge dev into main"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Merge failed. Resolve conflicts manually."
        exit 2
    }

    # Push to both remotes
    Write-Output "Pushing to GitHub..."
    git push github main
    Write-Output "Pushing to Gitee..."
    git push gitee main

    # Record merge into status log
    Write-Output "Recording release merge into status log..."
    pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\log_status.ps1 -Message "Merged dev into main" -Files "" -PrUrl "" -Author "release-bot"

    # Run smoke test on main
    Write-Output "Running smoke test on main..."
    & .\scripts\smoke_test.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Smoke test on main failed (exit $LASTEXITCODE). Rolling back main to pre-merge state."
        git reset --hard $preMain
        git push --force github main
        git push --force gitee main
        exit $LASTEXITCODE
    }

    Write-Output "Release to main completed successfully."

    # Record release completion
    pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\log_status.ps1 -Message "Release to main completed" -Files "" -PrUrl "" -Author "release-bot"
} finally {
    Pop-Location
}
