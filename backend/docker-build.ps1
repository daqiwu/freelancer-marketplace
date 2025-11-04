# Docker Build and Run Script for Poetry-based Backend
# This script demonstrates how to build and run the containerized application

Write-Host "`n================================================" -ForegroundColor Blue
Write-Host "  Freelancer Marketplace - Backend Docker" -ForegroundColor Blue
Write-Host "  Build Tool: Poetry" -ForegroundColor Blue
Write-Host "================================================`n" -ForegroundColor Blue

# Build the Docker image
Write-Host "📦 Building Docker image with Poetry..." -ForegroundColor Yellow
docker build -t freelancer-backend:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image built successfully!`n" -ForegroundColor Green
} else {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

# Optional: Run the container
$response = Read-Host "Do you want to run the container now? (y/n)"
if ($response -match "^[Yy]$") {
    Write-Host "🚀 Starting container..." -ForegroundColor Yellow
    
    # Check for .env file
    $envFile = ""
    if (Test-Path ".env") {
        $envFile = "--env-file .env"
        Write-Host "📝 Using .env file for configuration" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No .env file found. Using default configuration." -ForegroundColor Yellow
    }
    
    # Run the container
    $dockerCmd = "docker run -d --name freelancer-backend -p 8000:8000 $envFile freelancer-backend:latest"
    Invoke-Expression $dockerCmd
    
    Write-Host "✅ Container started!" -ForegroundColor Green
    Write-Host "📊 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "📝 Container logs: docker logs -f freelancer-backend" -ForegroundColor Cyan
    Write-Host "🛑 Stop container: docker stop freelancer-backend" -ForegroundColor Cyan
    Write-Host "🗑️  Remove container: docker rm freelancer-backend" -ForegroundColor Cyan
}

Write-Host "`nDone! 🎉" -ForegroundColor Green
