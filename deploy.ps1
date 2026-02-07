<#
.SYNOPSIS
    Deploy PIVS (NZ Political Image Verification System) on Windows.

.DESCRIPTION
    Starts PostgreSQL, FastAPI backend, Next.js frontend, and nginx reverse proxy.
    Designed for a Windows machine with port 80 forwarded from the router.

    Public IP: 103.224.130.189
    Router must forward: port 80 -> this machine's LAN IP on port 80

.PARAMETER Stop
    Stops all PIVS services.

.PARAMETER Status
    Shows the status of all PIVS services.

.EXAMPLE
    .\deploy.ps1            # Start all services
    .\deploy.ps1 -Stop      # Stop all services
    .\deploy.ps1 -Status    # Check service status
#>

param(
    [switch]$Stop,
    [switch]$Status
)

$ErrorActionPreference = "Stop"

# ── Paths ─────────────────────────────────────────────────────────────
$PROJECT_ROOT  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SERVER_DIR    = Join-Path $PROJECT_ROOT "server"
$CLIENT_DIR    = Join-Path $PROJECT_ROOT "client"
$NGINX_DIR     = Join-Path $PROJECT_ROOT "nginx"
$VENV_PYTHON   = Join-Path $SERVER_DIR "venv\Scripts\python.exe"
$VENV_UVICORN  = Join-Path $SERVER_DIR "venv\Scripts\uvicorn.exe"
$PG_BIN        = "C:\Program Files\PostgreSQL\16\bin"
$PG_DATA       = Join-Path $env:USERPROFILE "pgdata"
$NGINX_EXE     = Join-Path $PROJECT_ROOT "nginx-win\nginx.exe"
$STORAGE_DIR   = Join-Path $SERVER_DIR "storage"
$LOG_DIR       = Join-Path $PROJECT_ROOT "logs"

# ── Public IP and Ports ───────────────────────────────────────────────
$PUBLIC_IP     = "103.224.130.189"
$API_PORT      = 8000
$CLIENT_PORT   = 3000
$PG_PORT       = 5432

# ── PID file locations ────────────────────────────────────────────────
$PID_DIR       = Join-Path $PROJECT_ROOT ".pids"

# ── Colours ───────────────────────────────────────────────────────────
function Write-Step  { param($msg) Write-Host "`n[$((Get-Date).ToString('HH:mm:ss'))] " -NoNewline -ForegroundColor DarkGray; Write-Host $msg -ForegroundColor Cyan }
function Write-OK    { param($msg) Write-Host "  OK: $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "  WARN: $msg" -ForegroundColor Yellow }
function Write-Fail  { param($msg) Write-Host "  FAIL: $msg" -ForegroundColor Red }

# ── Helpers ───────────────────────────────────────────────────────────
function Save-Pid { param($name, $pid) New-Item -Path $PID_DIR -ItemType Directory -Force | Out-Null; Set-Content -Path (Join-Path $PID_DIR "$name.pid") -Value $pid }
function Get-SavedPid { param($name) $f = Join-Path $PID_DIR "$name.pid"; if (Test-Path $f) { return [int](Get-Content $f) }; return $null }
function Stop-SavedProcess {
    param($name)
    $pid = Get-SavedPid $name
    if ($pid) {
        try {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc) { Stop-Process -Id $pid -Force; Write-OK "Stopped $name (PID $pid)" }
            else       { Write-Warn "$name (PID $pid) was not running" }
        } catch { Write-Warn "$name: $($_.Exception.Message)" }
        Remove-Item (Join-Path $PID_DIR "$name.pid") -Force -ErrorAction SilentlyContinue
    } else { Write-Warn "No PID file for $name" }
}

# ══════════════════════════════════════════════════════════════════════
#  STOP
# ══════════════════════════════════════════════════════════════════════
if ($Stop) {
    Write-Host "`nStopping PIVS services..." -ForegroundColor Cyan

    Write-Step "Stopping nginx"
    if (Test-Path $NGINX_EXE) {
        $nginxDir = Split-Path $NGINX_EXE
        Push-Location $nginxDir
        & $NGINX_EXE -s quit 2>$null
        Pop-Location
        Write-OK "nginx signalled to quit"
    } else { Stop-SavedProcess "nginx" }

    Write-Step "Stopping Next.js client"
    Stop-SavedProcess "client"
    # Also kill any orphan node processes on port 3000
    $clientConns = Get-NetTCPConnection -LocalPort $CLIENT_PORT -ErrorAction SilentlyContinue
    if ($clientConns) { $clientConns | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } }

    Write-Step "Stopping FastAPI server"
    Stop-SavedProcess "server"

    Write-Step "Stopping PostgreSQL"
    $pgCtl = Join-Path $PG_BIN "pg_ctl.exe"
    if (Test-Path $pgCtl) {
        & $pgCtl -D $PG_DATA stop -m fast 2>$null
        Write-OK "PostgreSQL stopped"
    }

    Write-Host "`nAll services stopped.`n" -ForegroundColor Green
    exit 0
}

# ══════════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════════
if ($Status) {
    Write-Host "`nPIVS Service Status" -ForegroundColor Cyan
    Write-Host ("=" * 50)

    # PostgreSQL
    $pgReady = Join-Path $PG_BIN "pg_isready.exe"
    $pgResult = & $pgReady -p $PG_PORT 2>&1
    if ($LASTEXITCODE -eq 0) { Write-OK "PostgreSQL ......... running on port $PG_PORT" }
    else { Write-Fail "PostgreSQL ......... not responding on port $PG_PORT" }

    # FastAPI
    try { $health = Invoke-RestMethod -Uri "http://127.0.0.1:$API_PORT/health" -TimeoutSec 3; Write-OK "FastAPI ............ running on port $API_PORT" }
    catch { Write-Fail "FastAPI ............ not responding on port $API_PORT" }

    # Next.js
    try { $null = Invoke-WebRequest -Uri "http://127.0.0.1:$CLIENT_PORT" -TimeoutSec 3 -ErrorAction Stop; Write-OK "Next.js ............ running on port $CLIENT_PORT" }
    catch { if ($_.Exception.Response.StatusCode) { Write-OK "Next.js ............ running on port $CLIENT_PORT" } else { Write-Fail "Next.js ............ not responding on port $CLIENT_PORT" } }

    # nginx
    $nginxProc = Get-Process -Name "nginx" -ErrorAction SilentlyContinue
    if ($nginxProc) { Write-OK "nginx .............. running (PID $($nginxProc.Id -join ', '))" }
    else { Write-Fail "nginx .............. not running" }

    # Public access
    Write-Host ""
    Write-Host "  Public URL:  http://$PUBLIC_IP" -ForegroundColor White
    Write-Host "  API docs:    http://$PUBLIC_IP/docs" -ForegroundColor White
    Write-Host ""
    exit 0
}

# ══════════════════════════════════════════════════════════════════════
#  DEPLOY / START
# ══════════════════════════════════════════════════════════════════════
Write-Host ""
Write-Host "  ====================================================" -ForegroundColor Cyan
Write-Host "  NZ Political Image Verification System - Deploy" -ForegroundColor Cyan
Write-Host "  Public IP: $PUBLIC_IP" -ForegroundColor Cyan
Write-Host "  ====================================================" -ForegroundColor Cyan

New-Item -Path $PID_DIR -ItemType Directory -Force | Out-Null
New-Item -Path $LOG_DIR -ItemType Directory -Force | Out-Null

# ── 1. Generate production secrets if .env missing ────────────────────
Write-Step "Checking production environment file"
$envFile = Join-Path $SERVER_DIR ".env"

if (-not (Test-Path $envFile) -or (Select-String -Path $envFile -Pattern "dev-secret" -Quiet)) {
    Write-Warn "Generating production secrets..."

    $secretKey     = & $VENV_PYTHON -c "import secrets; print(secrets.token_urlsafe(48))"
    $masterKey     = & $VENV_PYTHON -c "import secrets; print(secrets.token_hex(32))"
    $pgPassword    = & $VENV_PYTHON -c "import secrets; print(secrets.token_urlsafe(24))"

    @"
# Production environment -- generated by deploy.ps1 on $(Get-Date -Format 'yyyy-MM-dd HH:mm')
DATABASE_URL=postgresql+asyncpg://pivs:${pgPassword}@localhost:${PG_PORT}/pivs
SECRET_KEY=${secretKey}
MASTER_ENCRYPTION_KEY=${masterKey}
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./storage
VERIFICATION_BASE_URL=http://${PUBLIC_IP}/verify
EMAIL_PROCESSING_ENABLED=false
"@ | Set-Content -Path $envFile -Encoding UTF8

    Write-OK "Production .env created at $envFile"
    Write-Warn "PostgreSQL password set to: $pgPassword (save this)"
} else {
    Write-OK ".env already exists with production secrets"
}

# Read the PG password from .env for database setup
$pgPasswordFromEnv = (Select-String -Path $envFile -Pattern "DATABASE_URL=.*://pivs:(.+)@" | ForEach-Object { $_.Matches.Groups[1].Value })

# ── 2. Storage directories ────────────────────────────────────────────
Write-Step "Creating storage directories"
$storageDirs = @("assets", "badges", "qrcodes", "promoter", "email_incoming", "email_results")
foreach ($dir in $storageDirs) {
    New-Item -Path (Join-Path $STORAGE_DIR $dir) -ItemType Directory -Force | Out-Null
}
Write-OK "Storage directories ready at $STORAGE_DIR"

# ── 3. PostgreSQL ─────────────────────────────────────────────────────
Write-Step "Starting PostgreSQL"

# Check if the Windows service is running
$pgService = Get-Service -Name "postgresql-x64-16" -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -eq "Running") {
    Write-OK "PostgreSQL service already running on port $PG_PORT"
} else {
    # Try to start the Windows service first
    if ($pgService) {
        try {
            Start-Service "postgresql-x64-16"
            Start-Sleep -Seconds 3
            Write-OK "PostgreSQL service started"
        } catch {
            Write-Warn "Could not start service, trying pg_ctl..."
            $pgCtl = Join-Path $PG_BIN "pg_ctl.exe"

            # Initialize data dir if needed
            if (-not (Test-Path (Join-Path $PG_DATA "PG_VERSION"))) {
                $initdb = Join-Path $PG_BIN "initdb.exe"
                & $initdb -D $PG_DATA -U postgres -E UTF8 --locale=C | Out-Null
                Write-OK "Initialized PostgreSQL data directory"
            }

            & $pgCtl -D $PG_DATA -l (Join-Path $LOG_DIR "postgresql.log") start
            Start-Sleep -Seconds 3
            Write-OK "PostgreSQL started via pg_ctl"
        }
    } else {
        # No service, use pg_ctl
        $pgCtl = Join-Path $PG_BIN "pg_ctl.exe"
        if (-not (Test-Path (Join-Path $PG_DATA "PG_VERSION"))) {
            $initdb = Join-Path $PG_BIN "initdb.exe"
            & $initdb -D $PG_DATA -U postgres -E UTF8 --locale=C | Out-Null
        }
        & $pgCtl -D $PG_DATA -l (Join-Path $LOG_DIR "postgresql.log") -o "-p $PG_PORT" start
        Start-Sleep -Seconds 3
        Write-OK "PostgreSQL started via pg_ctl on port $PG_PORT"
    }
}

# Ensure pivs user and database exist
Write-Step "Configuring database"
$psql = Join-Path $PG_BIN "psql.exe"
$userCheck = & $psql -U postgres -h localhost -p $PG_PORT -tAc "SELECT 1 FROM pg_roles WHERE rolname='pivs'" 2>$null
if ($userCheck -ne "1") {
    & $psql -U postgres -h localhost -p $PG_PORT -c "CREATE USER pivs WITH PASSWORD '$pgPasswordFromEnv' CREATEDB;" 2>$null
    Write-OK "Created 'pivs' database user"
} else {
    # Update password to match .env
    & $psql -U postgres -h localhost -p $PG_PORT -c "ALTER USER pivs WITH PASSWORD '$pgPasswordFromEnv';" 2>$null
    Write-OK "Database user 'pivs' exists, password synced"
}

$dbCheck = & $psql -U postgres -h localhost -p $PG_PORT -tAc "SELECT 1 FROM pg_database WHERE datname='pivs'" 2>$null
if ($dbCheck -ne "1") {
    & $psql -U postgres -h localhost -p $PG_PORT -c "CREATE DATABASE pivs OWNER pivs;" 2>$null
    Write-OK "Created 'pivs' database"
} else {
    Write-OK "Database 'pivs' exists"
}

# ── 4. Seed database if empty ─────────────────────────────────────────
Write-Step "Checking database seed status"
$partyCount = & $psql -U postgres -h localhost -p $PG_PORT -d pivs -tAc "SELECT COUNT(*) FROM parties" 2>$null
if (-not $partyCount -or [int]$partyCount -eq 0) {
    Write-Warn "Database empty, running seed script..."
    $env:PYTHONIOENCODING = "utf-8"
    Push-Location $SERVER_DIR
    & $VENV_PYTHON -c "
import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from seed import seed
asyncio.run(seed())
"
    Pop-Location
    Write-OK "Database seeded"
} else {
    Write-OK "Database already has $partyCount parties"
}

# ── 5. Build Next.js client for production ────────────────────────────
Write-Step "Building Next.js client"

# Set the API URL for the production build -- since nginx proxies /api/*
# the client should call the same origin (no CORS needed in production)
$env:NEXT_PUBLIC_API_URL = "http://$PUBLIC_IP"

Push-Location $CLIENT_DIR
if (-not (Test-Path "node_modules")) {
    Write-Warn "Installing client dependencies..."
    npm install --production=false 2>&1 | Out-Null
}

# Build for production
Write-Host "  Building... " -NoNewline
npm run build 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Next.js build failed. Check logs."
    npm run build 2>&1
    Pop-Location
    exit 1
}
Pop-Location
Write-OK "Next.js built for production"

# ── 6. Start FastAPI backend ──────────────────────────────────────────
Write-Step "Starting FastAPI backend"

# Kill any existing process on the API port
$existing = Get-NetTCPConnection -LocalPort $API_PORT -ErrorAction SilentlyContinue
if ($existing) {
    $existing | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
}

$serverLog = Join-Path $LOG_DIR "server.log"
$serverProc = Start-Process -FilePath $VENV_UVICORN `
    -ArgumentList "app.main:app", "--host", "127.0.0.1", "--port", "$API_PORT", "--workers", "4", "--log-level", "info" `
    -WorkingDirectory $SERVER_DIR `
    -RedirectStandardOutput $serverLog `
    -RedirectStandardError (Join-Path $LOG_DIR "server-error.log") `
    -PassThru -WindowStyle Hidden

Save-Pid "server" $serverProc.Id
Write-OK "FastAPI started (PID $($serverProc.Id)), logs: $serverLog"

# Wait for server to be ready
$retries = 0
do {
    Start-Sleep -Seconds 2
    try { $null = Invoke-RestMethod -Uri "http://127.0.0.1:$API_PORT/health" -TimeoutSec 2; break }
    catch { $retries++ }
} while ($retries -lt 10)

if ($retries -ge 10) { Write-Fail "FastAPI did not start. Check $serverLog"; exit 1 }
Write-OK "FastAPI health check passed"

# ── 7. Start Next.js in production mode ───────────────────────────────
Write-Step "Starting Next.js client"

$existing = Get-NetTCPConnection -LocalPort $CLIENT_PORT -ErrorAction SilentlyContinue
if ($existing) {
    $existing | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
}

$clientLog = Join-Path $LOG_DIR "client.log"
$clientProc = Start-Process -FilePath "npx" `
    -ArgumentList "next", "start", "--port", "$CLIENT_PORT" `
    -WorkingDirectory $CLIENT_DIR `
    -RedirectStandardOutput $clientLog `
    -RedirectStandardError (Join-Path $LOG_DIR "client-error.log") `
    -PassThru -WindowStyle Hidden

Save-Pid "client" $clientProc.Id
Write-OK "Next.js started (PID $($clientProc.Id)), logs: $clientLog"

Start-Sleep -Seconds 5

# ── 8. Install and start nginx ────────────────────────────────────────
Write-Step "Setting up nginx"

$nginxRoot = Join-Path $PROJECT_ROOT "nginx-win"
if (-not (Test-Path $NGINX_EXE)) {
    Write-Warn "nginx not found at $nginxRoot. Downloading..."
    $nginxZip = Join-Path $env:TEMP "nginx.zip"
    $nginxVersion = "1.27.4"
    Invoke-WebRequest -Uri "https://nginx.org/download/nginx-${nginxVersion}.zip" -OutFile $nginxZip
    Expand-Archive -Path $nginxZip -DestinationPath $env:TEMP -Force
    Move-Item -Path (Join-Path $env:TEMP "nginx-${nginxVersion}") -Destination $nginxRoot -Force
    Remove-Item $nginxZip -Force
    Write-OK "nginx $nginxVersion installed to $nginxRoot"
}

# Copy our config
$nginxConf = Join-Path $NGINX_DIR "nginx-windows.conf"
Copy-Item -Path $nginxConf -Destination (Join-Path $nginxRoot "conf\nginx.conf") -Force
Write-OK "nginx config deployed"

# Stop any existing nginx
$nginxProcs = Get-Process -Name "nginx" -ErrorAction SilentlyContinue
if ($nginxProcs) {
    Push-Location $nginxRoot
    & $NGINX_EXE -s quit 2>$null
    Start-Sleep -Seconds 2
    Pop-Location
    # Force kill if still running
    Get-Process -Name "nginx" -ErrorAction SilentlyContinue | Stop-Process -Force
}

# Start nginx
Push-Location $nginxRoot
Start-Process -FilePath $NGINX_EXE -WindowStyle Hidden
Pop-Location
Start-Sleep -Seconds 2

$nginxProc = Get-Process -Name "nginx" -ErrorAction SilentlyContinue
if ($nginxProc) { Write-OK "nginx started (PID $($nginxProc.Id -join ', '))" }
else { Write-Fail "nginx failed to start. Check $nginxRoot\logs\error.log" }

# ── 9. Final verification ────────────────────────────────────────────
Write-Step "Running deployment checks"

try { $health = Invoke-RestMethod -Uri "http://127.0.0.1/health" -TimeoutSec 5; Write-OK "nginx -> API proxy working" }
catch { Write-Warn "nginx -> API proxy not responding (may need port 80 access)" }

try { $page = Invoke-WebRequest -Uri "http://127.0.0.1/" -TimeoutSec 5; Write-OK "nginx -> Client proxy working" }
catch { if ($_.Exception.Response) { Write-OK "nginx -> Client proxy working" } else { Write-Warn "nginx -> Client proxy not responding" } }

# ── Summary ───────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ====================================================" -ForegroundColor Green
Write-Host "  PIVS Deployment Complete" -ForegroundColor Green
Write-Host "  ====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Public URL:      http://$PUBLIC_IP" -ForegroundColor White
Write-Host "  Party Portal:    http://$PUBLIC_IP/party" -ForegroundColor White
Write-Host "  API Docs:        http://$PUBLIC_IP/docs" -ForegroundColor White
Write-Host "  Health Check:    http://$PUBLIC_IP/health" -ForegroundColor White
Write-Host ""
Write-Host "  Logs:            $LOG_DIR" -ForegroundColor Gray
Write-Host "  Storage:         $STORAGE_DIR" -ForegroundColor Gray
Write-Host ""
Write-Host "  Router Port Forwarding Required:" -ForegroundColor Yellow
Write-Host "    Port 80 (TCP) -> $(hostname):80" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Management:" -ForegroundColor Gray
Write-Host "    .\deploy.ps1 -Status   # Check all services" -ForegroundColor Gray
Write-Host "    .\deploy.ps1 -Stop     # Stop all services" -ForegroundColor Gray
Write-Host ""
