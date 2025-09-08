Param(
    [string]$FeatureBranch = '',
    [switch]$NoPush
)

Set-StrictMode -Version Latest
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path $scriptDir -Parent
Push-Location $repo
try {
    # determine current branch if not provided
    if (-not $FeatureBranch -or $FeatureBranch -eq '') {
        $branch = git rev-parse --abbrev-ref HEAD
        $FeatureBranch = $branch.Trim()
    }

    Write-Output "feature_finish: feature branch = $FeatureBranch"

    # ensure working tree is clean (allow staged changes)
    $status = git status --porcelain
    if ($status -and ($status -notmatch '^\s*$')) {
        Write-Output "Found local changes. Staging and committing them automatically."
        git add -A
        git commit -m "chore: work finished on $FeatureBranch (auto-commit by feature_finish)" || Write-Output "Nothing to commit or commit failed"
    }

    # push feature branch up
    if ($NoPush) {
        Write-Output "NoPush set: skipping push of feature branch to remotes"
    }
    else {
        Write-Output "Pushing feature branch to remotes: $FeatureBranch"
        git push github $FeatureBranch
        git push gitee $FeatureBranch
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to push feature branch to remotes. Aborting."
            exit 2
        }
    }

    # run smoke tests on feature branch
    Write-Output "Running smoke tests on feature branch..."
    & .\scripts\smoke_test.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Smoke test failed on feature branch. Fix and retry."
        exit 3
    }

    # prepare dev merge
    Write-Output "Preparing to merge $FeatureBranch into dev"
    $preDev = git rev-parse refs/heads/dev

    git checkout dev
    git fetch github
    git pull github dev
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to pull github/dev. Aborting."
        git checkout $FeatureBranch
        exit 4
    }

    # merge feature into dev
    git merge --no-ff $FeatureBranch -m "chore: merge $FeatureBranch into dev (auto by feature_finish)"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Merge conflict when merging $FeatureBranch into dev. Aborting and returning to feature branch."
        git merge --abort || Write-Output "merge --abort failed or not needed"
        git checkout $FeatureBranch
        exit 5
    }

    # run smoke tests on dev
    Write-Output "Running smoke tests on dev after merge..."
    & .\scripts\smoke_test.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Smoke test failed on dev after merge. Reverting merge and returning to feature branch."
        # revert to pre-merge state
        git reset --hard $preDev
        git checkout $FeatureBranch
        exit 6
    }

    # push dev
    if ($NoPush) {
        Write-Output "NoPush set: skipping push of dev to remotes (merge succeeded locally)."
    }
    else {
        Write-Output "Pushing dev to remotes (merge succeeded)..."
        git push github dev
        git push gitee dev
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to push dev to remotes after merge. Please investigate."
            exit 7
        }
    }

    Write-Output "feature_finish completed successfully: $FeatureBranch -> dev"
}
finally {
    Pop-Location
}
