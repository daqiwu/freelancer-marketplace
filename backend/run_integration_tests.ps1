# Integration Test Runner for Windows/PowerShell
# Run integration tests against your local backend server

param(
    [string]$ServerUrl = "http://localhost:8000",
    [switch]$All,
    [switch]$NoCheck,
    [switch]$Help
)

# Color output functions
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }

if ($Help) {
    Write-Host @"
Integration Test Runner for Freelancer Marketplace Backend

USAGE:
    .\run_integration_tests.ps1 [OPTIONS]

OPTIONS:
    -ServerUrl <url>   Backend server URL (default: http://localhost:8000)
    -All               Run all tests including slow ones
    -NoCheck           Skip server availability check
    -Help              Show this help message

EXAMPLES:
    .\run_integration_tests.ps1
    .\run_integration_tests.ps1 -ServerUrl http://localhost:8080
    .\run_integration_tests.ps1 -All
    .\run_integration_tests.ps1 -NoCheck

"@
    exit 0
}

Write-Host "=" * 60 -ForegroundColor Blue
Write-Info "  FREELANCER MARKETPLACE - INTEGRATION TEST RUNNER"
Write-Host "=" * 60 -ForegroundColor Blue

# Check if server is running
if (-not $NoCheck) {
    Write-Info "`n🔍 Checking if backend is running at $ServerUrl..."
    
    $serverReady = $false
    for ($i = 1; $i -le 10; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "$ServerUrl/docs" -TimeoutSec 2 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "✅ Backend server is running and accessible!"
                $serverReady = $true
                break
            }
        }
        catch {
            if ($i -lt 10) {
                Write-Host "   Attempt $i/10 failed, retrying in 1 second..."
                Start-Sleep -Seconds 1
            }
        }
    }
    
    if (-not $serverReady) {
        Write-Error "`n❌ Cannot connect to backend server at $ServerUrl"
        Write-Warning "`n💡 Tip: Start your backend server first:"
        Write-Host "   cd backend"
        Write-Host "   poetry run uvicorn app.main:app --reload"
        exit 1
    }
}

# Build pytest command
$testPaths = @(
    "app/test/admin_test/",
    "app/test/auth_test/service_test.py",
    "app/test/customer_test/",
    "app/test/profile_test.py"
)

$pytestArgs = @(
    "run", "pytest"
) + $testPaths + @(
    "-v",
    "--tb=short",
    "--color=yes"
)

if (-not $All) {
    $pytestArgs += @("-m", "not slow")
}

Write-Info "`n🧪 Running integration tests..."
Write-Host "   Server URL: $ServerUrl"
Write-Host "   Command: poetry $($pytestArgs -join ' ')"
Write-Host "-" * 60

# Set environment variable
$env:TEST_SERVER_URL = $ServerUrl

# Change to backend directory
Push-Location -Path (Join-Path $PSScriptRoot ".")

# Run tests
poetry @pytestArgs
$exitCode = $LASTEXITCODE

# Restore location
Pop-Location

# Print summary
Write-Host "`n" + ("-" * 60)
if ($exitCode -eq 0) {
    Write-Success "✅ All integration tests PASSED!"
} else {
    Write-Error "❌ Some integration tests FAILED"
    Write-Host "   Exit code: $exitCode"
}
Write-Host ("-" * 60)

exit $exitCode
