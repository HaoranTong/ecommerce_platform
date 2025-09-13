Param()

# One-shot smoke test for the API.
# - Activates project venv
# - If server not running on 127.0.0.1:8000, starts uvicorn in background
# - Runs POST/GET checks against /api/users
# - Stops uvicorn if the script started it

Set-StrictMode -Version Latest

# 初始化测试状态
$script:TestSuccess = $true

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
    }
    else {
        Write-Output "No venv activate script found at $venvActivate"
    }

    # 🔍 检查点触发：烟雾测试环境检查
    Write-Output "🔍 检查点：验证烟雾测试环境配置..."

    # 烟雾测试使用SQLite，无需外部数据库
    if (-not $env:DATABASE_URL -or $env:DATABASE_URL -eq '') {
        # 烟雾测试使用SQLite文件数据库，无需Docker
        $env:DATABASE_URL = 'sqlite:///./tests/smoke_test.db'
        Write-Output "✅ 烟雾测试使用SQLite数据库: $env:DATABASE_URL"
    }
    else {
        Write-Output "⚠️  检测到外部DATABASE_URL，烟雾测试将使用: $env:DATABASE_URL"
    }
    
    # Redis对于烟雾测试是可选的，如果没有则跳过相关功能
    if (-not $env:REDIS_URL -or $env:REDIS_URL -eq '') {
        $env:REDIS_URL = 'redis://127.0.0.1:6379/0'
        Write-Output "⚠️  REDIS_URL未设置，某些缓存功能可能无法测试: $env:REDIS_URL"
    }
    else {
        Write-Output "✅ 使用Redis配置: $env:REDIS_URL"
    }

    $baseUrl = 'http://127.0.0.1:8000'

    function Test-Server {
        try {
            Invoke-RestMethod -Method Get -Uri "$baseUrl/" -TimeoutSec 2 -ErrorAction Stop | Out-Null
            return $true
        }
        catch {
            return $false
        }
    }

    $startedByScript = $false
    if (-not (Test-Server)) {
        Write-Output "Server not responding; starting uvicorn..."
        $startedByScript = $true
        # Ensure migrations are applied via Alembic (do NOT create tables directly)
        Write-Output "Applying Alembic migrations: alembic upgrade head"
        $env:PYTHONPATH = (Resolve-Path $repo).Path
        try {
            python -m alembic upgrade head
        }
        catch {
            Write-Error "Failed to run alembic upgrade head: $($_.Exception.Message)"
            if ($startedByScript -and $uvProc) { $uvProc | Stop-Process -Force }
            exit 3
        }

        $uvProc = Start-Process -FilePath python -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000' -NoNewWindow -PassThru
        Start-Sleep -Seconds 2
        if (-not (Test-Server)) {
            Write-Error "Failed to start server"
            if ($startedByScript -and $uvProc) { $uvProc | Stop-Process -Force }
            exit 2
        }
    }
    else {
        Write-Output "Server already running."
    }

    # perform a POST with a randomized username to avoid conflicts
    $rnd = Get-Random -Maximum 100000
    $payload = @{ 
        username = "smoke$rnd"; 
        email = "smoke$rnd@example.com"; 
        password = "testpass123" 
    } | ConvertTo-Json
    $apiRegister = "http://127.0.0.1:8000/api/auth/register"
    Write-Output "POST $apiRegister -> payload: $payload"
    try {
        $post = Invoke-RestMethod -Method Post -Uri $apiRegister -Body $payload -ContentType 'application/json' -TimeoutSec 10 -ErrorAction Stop
        Write-Output "POST result: $(ConvertTo-Json $post -Compress)"
    }
    catch {
        Write-Error "POST failed: $($_.Exception.Message)"
        $script:TestSuccess = $false
    }

    try {
        # 登录获取token
        $loginPayload = @{ 
            username = "smoke$rnd"; 
            password = "testpass123" 
        } | ConvertTo-Json
        $apiLogin = "http://127.0.0.1:8000/api/auth/login"
        $loginResult = Invoke-RestMethod -Method Post -Uri $apiLogin -Body $loginPayload -ContentType 'application/json' -TimeoutSec 10 -ErrorAction Stop
        
        # 使用token获取用户信息
        $headers = @{ Authorization = "Bearer $($loginResult.access_token)" }
        $apiMe = "http://127.0.0.1:8000/api/auth/me"
        $userInfo = Invoke-RestMethod -Method Get -Uri $apiMe -Headers $headers -TimeoutSec 10 -ErrorAction Stop
        
        Write-Output "GET $apiMe result: $(ConvertTo-Json $userInfo -Compress)"
        
        # 如果到达这里，说明测试成功
        Write-Output "✅ Smoke test completed successfully"
        $script:TestSuccess = $true
    }
    catch {
        Write-Error "GET failed: $($_.Exception.Message)"
        $script:TestSuccess = $false
    }

}
finally {
    if ($startedByScript -and $uvProc) {
        Write-Output "Stopping uvicorn (pid=$($uvProc.Id))"
        $uvProc | Stop-Process -Force
    }
    Pop-Location
    
    # 确保正确的退出代码
    if ($script:TestSuccess -eq $false) {
        exit 1
    }
}
