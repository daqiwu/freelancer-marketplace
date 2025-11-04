# Start FastAPI backend with Poetry (PowerShell)

Write-Host "🚀 Starting Freelancer Marketplace Backend..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue

# Change to backend directory
Set-Location $PSScriptRoot

# Check if poetry is available
try {
    $poetryVersion = poetry --version 2>$null
    Write-Host "✅ Poetry found: $poetryVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Poetry is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "   Install it with: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
poetry install --no-interaction

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Starting FastAPI server..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""
Write-Host "📍 Server will be available at:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

# Run uvicorn
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
