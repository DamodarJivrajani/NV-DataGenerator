# NV-DataGenerator - One-command startup script
# Usage: .\run.ps1 [-ApiKey "your-nvidia-api-key"]
param(
    [string]$ApiKey = ""
)

$Root = $PSScriptRoot
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "    [OK] $msg" -ForegroundColor Green }
function Write-Err($msg)  { Write-Host "    [ERROR] $msg" -ForegroundColor Red }

# ── 1. Check prerequisites ────────────────────────────────────────────────────
Write-Step "Checking prerequisites"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Err "Python 3.10+ is required. Install from https://python.org"; exit 1
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Err "Node.js 18+ is required. Install from https://nodejs.org"; exit 1
}
Write-OK "Python and Node.js found"

# ── 2. Backend .env ───────────────────────────────────────────────────────────
Write-Step "Configuring backend"
$BackendEnv = Join-Path $BackendDir ".env"
if (-not (Test-Path $BackendEnv)) {
    Copy-Item (Join-Path $BackendDir ".env.example") $BackendEnv
    Write-OK "Created backend/.env from .env.example"
}

if ($ApiKey -ne "") {
    (Get-Content $BackendEnv) -replace "^NVIDIA_API_KEY=.*", "NVIDIA_API_KEY=$ApiKey" |
        Set-Content $BackendEnv
    Write-OK "NVIDIA_API_KEY set in backend/.env"
} else {
    $existing = (Get-Content $BackendEnv) | Where-Object { $_ -match "^NVIDIA_API_KEY=(.+)$" }
    if ($existing -match "^NVIDIA_API_KEY=your-nvidia-api-key-here$" -or $existing -eq "") {
        Write-Host "`n  NVIDIA_API_KEY is not set." -ForegroundColor Yellow
        $key = Read-Host "  Enter your NVIDIA API key (or press Enter to skip)"
        if ($key -ne "") {
            (Get-Content $BackendEnv) -replace "^NVIDIA_API_KEY=.*", "NVIDIA_API_KEY=$key" |
                Set-Content $BackendEnv
            Write-OK "NVIDIA_API_KEY saved to backend/.env"
        }
    }
}

# ── 3. Backend venv & install ─────────────────────────────────────────────────
Write-Step "Setting up Python virtual environment"
$Venv = Join-Path $BackendDir "venv"
if (-not (Test-Path $Venv)) {
    python -m venv $Venv
    Write-OK "Created virtual environment at backend/venv"
} else {
    Write-OK "Virtual environment already exists"
}

$Pip = Join-Path $Venv "Scripts\pip.exe"
Write-Step "Installing backend dependencies (this may take a minute)"
& $Pip install -e $BackendDir --quiet
if ($LASTEXITCODE -ne 0) { Write-Err "pip install failed"; exit 1 }
Write-OK "Backend dependencies installed"

# ── 4. Frontend .env & install ────────────────────────────────────────────────
Write-Step "Setting up frontend"
$FrontendEnv = Join-Path $FrontendDir ".env"
if (-not (Test-Path $FrontendEnv)) {
    Copy-Item (Join-Path $FrontendDir ".env.example") $FrontendEnv
    Write-OK "Created frontend/.env from .env.example"
} else {
    Write-OK "frontend/.env already exists"
}

if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Step "Installing frontend dependencies"
    Push-Location $FrontendDir
    npm install --silent
    Pop-Location
    if ($LASTEXITCODE -ne 0) { Write-Err "npm install failed"; exit 1 }
    Write-OK "Frontend dependencies installed"
} else {
    Write-OK "node_modules already present, skipping npm install"
}

# ── 5. Launch both servers ────────────────────────────────────────────────────
Write-Step "Starting backend (http://localhost:8000)"
$Uvicorn = Join-Path $Venv "Scripts\uvicorn.exe"
$BackendJob = Start-Process -FilePath $Uvicorn `
    -ArgumentList "app.main:app", "--reload", "--port", "8000" `
    -WorkingDirectory $BackendDir `
    -PassThru -NoNewWindow

Write-Step "Starting frontend (http://localhost:5173)"
$FrontendJob = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c npm run dev" `
    -WorkingDirectory $FrontendDir `
    -PassThru -NoNewWindow

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "  App is running!" -ForegroundColor Green
Write-Host "  Frontend : http://localhost:5173" -ForegroundColor Green
Write-Host "  Backend  : http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop both servers." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Green

# Keep script alive; kill child processes on Ctrl+C
try {
    while ($true) { Start-Sleep -Seconds 5 }
} finally {
    Write-Host "`nShutting down..." -ForegroundColor Yellow
    if (-not $BackendJob.HasExited)  { Stop-Process -Id $BackendJob.Id  -Force -ErrorAction SilentlyContinue }
    if (-not $FrontendJob.HasExited) { Stop-Process -Id $FrontendJob.Id -Force -ErrorAction SilentlyContinue }
    Write-Host "Done." -ForegroundColor Green
}
