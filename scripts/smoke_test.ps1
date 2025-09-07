Param()

# One-shot smoke test for the API.
# - Activates project venv
# - If server not running on 127.0.0.1:8000, starts uvicorn in background
# - Runs POST/GET checks against /api/users
# - Stops uvicorn if the script started it

Set-StrictMode -Version Latest
# compute repository root (script is in <repo>/scripts)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path $scriptDir -Parent
Write-Output "repo: $repo"

Push-Location $repo
try {
    # activate venv if present
    $venvActivate = Join-Path $repo '.venv\Scripts\Activate.ps1'
    if (Test-Path $venvActivate) {
        Write-Output "Activating venv: $venvActivate"
        & $venvActivate
    } else {
        Write-Output "No venv activate script found at $venvActivate"
    }

    $baseUrl = 'http://127.0.0.1:8000'
    $apiUsers = "$baseUrl/api/users"

    function Test-Server {
        try {
            Invoke-RestMethod -Method Get -Uri "$baseUrl/" -TimeoutSec 2 -ErrorAction Stop | Out-Null
            return $true
        } catch {
            return $false
        }
    }

    $startedByScript = $false
    if (-not (Test-Server)) {
        Write-Output "Server not responding; starting uvicorn..."
        $startedByScript = $true
        $uvProc = Start-Process -FilePath python -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -NoNewWindow -PassThru
        Start-Sleep -Seconds 2
        if (-not (Test-Server)) {
            Write-Error "Failed to start server"
            if ($startedByScript -and $uvProc) { $uvProc | Stop-Process -Force }
            exit 2
        }
    } else {
        Write-Output "Server already running."
    }

    # perform a POST with a randomized username to avoid conflicts
    $rnd = Get-Random -Maximum 100000
    $payload = @{ username = "smoke$rnd"; email = "smoke$rnd@example.com" } | ConvertTo-Json
    Write-Output "POST $apiUsers -> payload: $payload"
    try {
        $post = Invoke-RestMethod -Method Post -Uri $apiUsers -Body $payload -ContentType 'application/json' -TimeoutSec 10 -ErrorAction Stop
        Write-Output "POST result: $(ConvertTo-Json $post -Compress)"
    } catch {
        Write-Error "POST failed: $($_.Exception.Message)"
    }

    try {
        $list = Invoke-RestMethod -Method Get -Uri $apiUsers -TimeoutSec 10 -ErrorAction Stop
        Write-Output "GET /api/users result count: $($list.Count)"
        Write-Output (ConvertTo-Json $list -Depth 3)
    } catch {
        Write-Error "GET failed: $($_.Exception.Message)"
    }

} finally {
    if ($startedByScript -and $uvProc) {
        Write-Output "Stopping uvicorn (pid=$($uvProc.Id))"
        $uvProc | Stop-Process -Force
    }
    Pop-Location
}
