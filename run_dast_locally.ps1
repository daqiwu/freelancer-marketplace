# Local DAST Testing Script for Windows PowerShell
# Run OWASP ZAP security tests locally before pushing to GitHub

$TARGET_URL = "https://u7tnmpvsm8.ap-southeast-1.awsapprunner.com"
$ZAP_PROXY = "http://localhost:8090"
$CONTAINER_NAME = "zap-local-test"

function Write-Banner {
    param([string]$Text)
    Write-Host "`n$('=' * 60)" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "$('=' * 60)" -ForegroundColor Cyan
}

function Test-Docker {
    Write-Banner "Checking Docker"
    try {
        $version = docker --version
        Write-Host "✅ Docker found: $version" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
        return $false
    }
}

function Start-ZapContainer {
    Write-Banner "Starting OWASP ZAP Container"
    
    # Cleanup existing container
    Write-Host "🧹 Cleaning up existing containers..."
    docker stop $CONTAINER_NAME 2>$null
    docker rm $CONTAINER_NAME 2>$null
    
    # Pull image
    Write-Host "🐳 Pulling OWASP ZAP image..."
    docker pull ghcr.io/zaproxy/zaproxy:stable
    
    # Start container
    Write-Host "🚀 Starting ZAP container..."
    docker run -d `
        --name $CONTAINER_NAME `
        -u zap `
        -p 8090:8080 `
        ghcr.io/zaproxy/zaproxy:stable `
        zap.sh -daemon `
        -host 0.0.0.0 `
        -port 8080 `
        -config api.disablekey=true `
        -config api.addrs.addr.name=.* `
        -config api.addrs.addr.regex=true
    
    Write-Host "⏳ Waiting for ZAP to start (30 seconds)..."
    Start-Sleep -Seconds 30
    
    # Verify
    try {
        $response = Invoke-WebRequest -Uri "$ZAP_PROXY/" -TimeoutSec 5
        Write-Host "✅ ZAP is running" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "⚠️  ZAP might not be fully ready" -ForegroundColor Yellow
        return $false
    }
}

function Test-SecurityHeaders {
    Write-Banner "Security Headers Validation"
    
    $headers = @(
        'Strict-Transport-Security',
        'X-Content-Type-Options',
        'X-Frame-Options',
        'Content-Security-Policy',
        'X-XSS-Protection',
        'Referrer-Policy',
        'Permissions-Policy'
    )
    
    try {
        $url = "$TARGET_URL/health"
        Write-Host "🎯 Testing: $url"
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 10
        Write-Host "📊 Status: $($response.StatusCode)`n" -ForegroundColor Green
        
        $missing = @()
        foreach ($header in $headers) {
            if ($response.Headers[$header]) {
                $value = $response.Headers[$header]
                if ($value.Length -gt 60) { $value = $value.Substring(0, 60) + "..." }
                Write-Host "   ✅ $header`: $value" -ForegroundColor Green
            }
            else {
                Write-Host "   ❌ $header`: MISSING" -ForegroundColor Red
                $missing += $header
            }
        }
        
        if ($missing.Count -eq 0) {
            Write-Host "`n✅ All security headers present!" -ForegroundColor Green
        }
        else {
            Write-Host "`n⚠️  Missing $($missing.Count) header(s)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function Test-Endpoints {
    Write-Banner "API Endpoints Testing"
    
    $endpoints = @('/health', '/docs', '/openapi.json', '/api/v1/', '/auth/login', '/auth/register')
    
    foreach ($endpoint in $endpoints) {
        try {
            $url = "$TARGET_URL$endpoint"
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction SilentlyContinue
            $emoji = if ($response.StatusCode -lt 500) { "✅" } else { "❌" }
            Write-Host "   $emoji $endpoint`: $($response.StatusCode)" -ForegroundColor $(if ($response.StatusCode -lt 500) { "Green" } else { "Red" })
        }
        catch {
            $status = $_.Exception.Response.StatusCode.Value__
            if ($status) {
                $emoji = if ($status -lt 500) { "✅" } else { "❌" }
                Write-Host "   $emoji $endpoint`: $status" -ForegroundColor Yellow
            }
            else {
                Write-Host "   ⚠️  $endpoint`: ERROR" -ForegroundColor Yellow
            }
        }
    }
}

function Invoke-ZapSpider {
    Write-Banner "ZAP Spider Scan"
    
    try {
        Write-Host "🕷️  Starting spider scan..."
        $response = Invoke-RestMethod -Uri "$ZAP_PROXY/JSON/spider/action/scan/" -Body @{url=$TARGET_URL} -TimeoutSec 10
        $scanId = $response.scan
        Write-Host "   Scan ID: $scanId"
        
        do {
            Start-Sleep -Seconds 3
            $status = Invoke-RestMethod -Uri "$ZAP_PROXY/JSON/spider/view/status/" -Body @{scanId=$scanId} -TimeoutSec 10
            $progress = [int]$status.status
            Write-Host "   Progress: $progress%" -NoNewline
            Write-Host "`r" -NoNewline
        } while ($progress -lt 100)
        
        Write-Host "`n✅ Spider scan completed" -ForegroundColor Green
        
        $urls = Invoke-RestMethod -Uri "$ZAP_PROXY/JSON/core/view/urls/" -TimeoutSec 10
        Write-Host "   📍 URLs found: $($urls.urls.Count)" -ForegroundColor Cyan
    }
    catch {
        Write-Host "❌ Spider error: $_" -ForegroundColor Red
    }
}

function Invoke-ZapActiveScan {
    Write-Banner "ZAP Active Scan"
    
    try {
        Write-Host "⚡ Starting active scan (this may take 5-10 minutes)..."
        $response = Invoke-RestMethod -Uri "$ZAP_PROXY/JSON/ascan/action/scan/" -Body @{url=$TARGET_URL} -TimeoutSec 10
        $scanId = $response.scan
        Write-Host "   Scan ID: $scanId"
        
        do {
            Start-Sleep -Seconds 5
            $status = Invoke-RestMethod -Uri "$ZAP_PROXY/JSON/ascan/view/status/" -Body @{scanId=$scanId} -TimeoutSec 10
            $progress = [int]$status.status
            Write-Host "   Progress: $progress%" -NoNewline
            Write-Host "`r" -NoNewline
        } while ($progress -lt 100)
        
        Write-Host "`n✅ Active scan completed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Active scan error: $_" -ForegroundColor Red
    }
}

function Get-ZapAlerts {
    Write-Banner "Security Alerts Summary"
    
    try {
        $alerts = Invoke-RestMethod -Uri "$ZAP_PROXY/JSON/core/view/alerts/" -Body @{baseurl=$TARGET_URL} -TimeoutSec 10
        
        $severity = @{High=0; Medium=0; Low=0; Informational=0}
        foreach ($alert in $alerts.alerts) {
            $risk = if ($alert.risk) { $alert.risk } else { "Informational" }
            $severity[$risk]++
        }
        
        Write-Host "   🔴 High: $($severity.High)" -ForegroundColor Red
        Write-Host "   🟡 Medium: $($severity.Medium)" -ForegroundColor Yellow
        Write-Host "   🟢 Low: $($severity.Low)" -ForegroundColor Green
        Write-Host "   ℹ️  Informational: $($severity.Informational)" -ForegroundColor Cyan
        Write-Host "   📋 Total: $($alerts.alerts.Count)" -ForegroundColor White
        
        # Save reports
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $jsonFile = "zap_local_alerts_$timestamp.json"
        $alerts.alerts | ConvertTo-Json -Depth 10 | Out-File $jsonFile
        Write-Host "`n💾 Alerts saved to: $jsonFile" -ForegroundColor Green
        
        try {
            $html = Invoke-WebRequest -Uri "$ZAP_PROXY/OTHER/core/other/htmlreport/" -TimeoutSec 30
            $htmlFile = "zap_local_report_$timestamp.html"
            $html.Content | Out-File $htmlFile -Encoding UTF8
            Write-Host "📄 HTML report saved to: $htmlFile" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  Could not generate HTML report" -ForegroundColor Yellow
        }
        
        return $severity
    }
    catch {
        Write-Host "❌ Error getting alerts: $_" -ForegroundColor Red
        return @{High=0; Medium=0; Low=0; Informational=0}
    }
}

function Stop-ZapContainer {
    Write-Banner "Cleanup"
    Write-Host "🧹 Stopping ZAP container..."
    docker stop $CONTAINER_NAME 2>$null
    docker rm $CONTAINER_NAME 2>$null
    Write-Host "✅ Cleanup completed" -ForegroundColor Green
}

# Main execution
try {
    Write-Banner "Local DAST Testing - OWASP ZAP"
    Write-Host "🎯 Target: $TARGET_URL" -ForegroundColor Cyan
    Write-Host "⏰ Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
    
    if (-not (Test-Docker)) {
        exit 1
    }
    
    Start-ZapContainer
    
    Test-SecurityHeaders
    Test-Endpoints
    
    Invoke-ZapSpider
    
    Write-Host "`n⏳ Waiting for passive scan (15 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    # Ask for active scan
    Write-Host "`n$('=' * 60)" -ForegroundColor Cyan
    $runActive = Read-Host "⚡ Run active scan? Takes 5-10 minutes (y/n)"
    if ($runActive -eq 'y') {
        Invoke-ZapActiveScan
    }
    else {
        Write-Host "⏭️  Skipping active scan" -ForegroundColor Yellow
    }
    
    $severity = Get-ZapAlerts
    
    Write-Banner "DAST Testing Complete"
    Write-Host "⏰ Finished: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
    
    if ($severity.High -gt 0) {
        Write-Host "`n❌ HIGH SEVERITY ISSUES DETECTED!" -ForegroundColor Red
        Write-Host "   Review reports before deploying." -ForegroundColor Red
    }
    else {
        Write-Host "`n✅ No high severity issues" -ForegroundColor Green
        Write-Host "   Review reports for medium/low issues." -ForegroundColor Yellow
    }
    
    Write-Host "`n📁 Reports generated:" -ForegroundColor Cyan
    Write-Host "   - zap_local_alerts_*.json" -ForegroundColor White
    Write-Host "   - zap_local_report_*.html" -ForegroundColor White
    
    Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Review generated reports" -ForegroundColor White
    Write-Host "   2. Fix high/medium severity issues" -ForegroundColor White
    Write-Host "   3. Push to GitHub for automated DAST in CI/CD" -ForegroundColor White
}
catch {
    Write-Host "`n❌ Fatal error: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
}
finally {
    Stop-ZapContainer
}
