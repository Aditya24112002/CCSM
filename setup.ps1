<#
.SYNOPSIS
    Sets up the CCMS frontend, backend, and local PostgreSQL service.

.DESCRIPTION
    Run from the project root in PowerShell:
        .\setup.ps1

    The script does not create or print secrets. If backend/.env does not exist,
    it creates one from backend/.env.example; add the GROQ key manually when needed.
    Docker Desktop and NVM for Windows must be installed by the user because both
    may require administrator approval. The script detects and uses them when available.
#>

[CmdletBinding()]
param(
    [switch]$SkipDatabase
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendRoot = Join-Path $ProjectRoot "backend"
$VenvPython = Join-Path $BackendRoot ".venv\Scripts\python.exe"

function Require-Command([string]$Name, [string]$InstallHint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found. $InstallHint"
    }
}

function Invoke-Step([string]$Label, [scriptblock]$Action) {
    Write-Host "`n== $Label ==" -ForegroundColor Cyan
    & $Action
}

Set-Location $ProjectRoot
Write-Host "CCMS local setup" -ForegroundColor Green

Invoke-Step "Check Python" {
    Require-Command "python" "Install Python 3.11+ and ensure it is on PATH."
    python --version
}

Invoke-Step "Check Node.js / NVM" {
    if (Get-Command nvm -ErrorAction SilentlyContinue) {
        Write-Host "NVM for Windows detected."
        nvm version
        if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
            nvm install lts
            nvm use lts
        }
    }
    Require-Command "node" "Install Node.js LTS or NVM for Windows, then run this script again."
    Require-Command "npm" "Install Node.js LTS or NVM for Windows, then run this script again."
    node --version
    npm --version
}

Invoke-Step "Create Python virtual environment" {
    if (-not (Test-Path $VenvPython)) {
        python -m venv (Join-Path $BackendRoot ".venv")
    }
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r (Join-Path $BackendRoot "requirements.txt")
}

Invoke-Step "Install frontend dependencies" {
    npm install
}

Invoke-Step "Create local environment file" {
    $EnvFile = Join-Path $BackendRoot ".env"
    $EnvExample = Join-Path $BackendRoot ".env.example"
    if (-not (Test-Path $EnvFile)) {
        Copy-Item $EnvExample $EnvFile
        Write-Host "Created backend/.env. Add GROQ_API_KEY manually for live AI extraction."
    } else {
        Write-Host "backend/.env already exists; leaving it unchanged."
    }
}

if (-not $SkipDatabase) {
    Invoke-Step "Start PostgreSQL with Docker" {
        Require-Command "docker" "Install and start Docker Desktop, then open a new PowerShell window."
        docker compose up -d postgres
        docker compose ps
    }
}

Invoke-Step "Initialize and verify backend database" {
    & $VenvPython -c "from backend.app.database import create_tables; create_tables(); print('Database tables are ready.')"
}

Write-Host "`nSetup complete." -ForegroundColor Green
Write-Host "Backend: .\backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000"
Write-Host "Frontend: npm run dev"
Write-Host "If live AI extraction is needed, add GROQ_API_KEY to backend/.env."
