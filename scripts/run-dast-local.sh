#!/bin/bash

# ============================================
# Local DAST Testing Script
# ============================================
# This script runs the same DAST checks as the 
# GitHub Actions workflow, but locally.
#
# Prerequisites:
# - Docker installed
# - curl installed
# - jq installed (for JSON parsing)
# ============================================

set -e

TARGET_URL="https://freelancer-marketplace-api.onrender.com"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Local DAST Security Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Target: $TARGET_URL"
echo "📅 Date: $(date)"
echo ""

# Create output directory
mkdir -p dast-reports
cd dast-reports

# ============================================
# Step 1: Health Check
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 1: Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔍 Checking if application is accessible..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $TARGET_URL/docs)

if [ "$RESPONSE" == "200" ]; then
  echo "✅ Application is healthy (HTTP $RESPONSE)"
else
  echo "❌ Application is not responding (HTTP $RESPONSE)"
  echo "⚠️  Cannot proceed with DAST testing"
  exit 1
fi

echo ""

# ============================================
# Step 2: Security Headers Check
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 2: Security Headers Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🛡️  Checking security headers..."
echo ""

# Get headers and save
curl -sI $TARGET_URL > headers.txt

# Function to check header
check_header() {
  local header=$1
  local importance=$2
  if grep -iq "^$header:" headers.txt; then
    echo "✅ $header: Present"
    grep -i "^$header:" headers.txt | head -1
    return 0
  else
    echo "❌ $header: Missing ($importance)"
    return 1
  fi
}

MISSING=0

check_header "Strict-Transport-Security" "CRITICAL" || ((MISSING++)) || true
echo ""
check_header "X-Content-Type-Options" "HIGH" || ((MISSING++)) || true
echo ""
check_header "X-Frame-Options" "HIGH" || ((MISSING++)) || true
echo ""
check_header "Content-Security-Policy" "HIGH" || ((MISSING++)) || true
echo ""
check_header "X-XSS-Protection" "MEDIUM" || ((MISSING++)) || true
echo ""
check_header "Referrer-Policy" "MEDIUM" || ((MISSING++)) || true
echo ""
check_header "Permissions-Policy" "LOW" || ((MISSING++)) || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $MISSING -eq 0 ]; then
  echo "✅ All security headers present!"
else
  echo "⚠️  $MISSING security header(s) missing"
fi
echo ""

# ============================================
# Step 3: OWASP ZAP Baseline Scan
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 3: OWASP ZAP Baseline Scan"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔒 Starting OWASP ZAP scan..."
echo "   This may take 2-5 minutes..."
echo ""

# Run ZAP in Docker (using slim image - much smaller!)
docker run --rm \
  -v $(pwd):/zap/wrk/:rw \
  -t ghcr.io/zaproxy/zaproxy:stable-slim \
  zap-baseline.py \
  -t $TARGET_URL \
  -r zap-report.html \
  -J zap-report.json \
  -w zap-report.md \
  || true

echo ""
echo "✅ ZAP scan completed"

# Parse results if JSON exists
if [ -f zap-report.json ]; then
  echo ""
  echo "📊 Parsing scan results..."
  
  # Count alerts by risk level
  HIGH=$(jq '[.site[].alerts[] | select(.riskcode == "3")] | length' zap-report.json 2>/dev/null || echo "0")
  MEDIUM=$(jq '[.site[].alerts[] | select(.riskcode == "2")] | length' zap-report.json 2>/dev/null || echo "0")
  LOW=$(jq '[.site[].alerts[] | select(.riskcode == "1")] | length' zap-report.json 2>/dev/null || echo "0")
  INFO=$(jq '[.site[].alerts[] | select(.riskcode == "0")] | length' zap-report.json 2>/dev/null || echo "0")
  
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  OWASP ZAP Results Summary"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "   🔴 High:   $HIGH"
  echo "   🟠 Medium: $MEDIUM"
  echo "   🟡 Low:    $LOW"
  echo "   🔵 Info:   $INFO"
  echo ""
  
  # Show high-risk issues
  if [ "$HIGH" -gt 0 ]; then
    echo "⚠️  HIGH RISK ISSUES FOUND!"
    echo ""
    echo "High-risk vulnerabilities:"
    jq -r '.site[].alerts[] | select(.riskcode == "3") | "  • " + .name' zap-report.json 2>/dev/null || true
    echo ""
  fi
fi

echo ""

# ============================================
# Step 4: SSL/TLS Check
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 4: SSL/TLS Security Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔐 Checking SSL/TLS configuration..."
echo ""

# Basic SSL check with openssl
echo "Certificate Information:"
echo | openssl s_client -connect freelancer-marketplace-api.onrender.com:443 -servername freelancer-marketplace-api.onrender.com 2>/dev/null | openssl x509 -noout -dates -subject -issuer 2>/dev/null || echo "⚠️  Could not retrieve certificate"

echo ""
echo "TLS Protocol Check:"
echo | openssl s_client -connect freelancer-marketplace-api.onrender.com:443 -servername freelancer-marketplace-api.onrender.com 2>/dev/null | grep -i "protocol\|cipher" | head -5 || true

echo ""

# ============================================
# Step 5: API Endpoint Discovery
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 5: API Endpoint Discovery"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📡 Discovering API endpoints from OpenAPI spec..."
curl -s $TARGET_URL/openapi.json > openapi.json

if [ -f openapi.json ]; then
  ENDPOINT_COUNT=$(jq '.paths | keys | length' openapi.json 2>/dev/null || echo "0")
  echo "✅ Found $ENDPOINT_COUNT API endpoints"
  echo ""
  echo "Sample endpoints:"
  jq -r '.paths | keys[]' openapi.json | head -10 || true
else
  echo "⚠️  Could not retrieve OpenAPI specification"
fi

echo ""

# ============================================
# Final Summary
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DAST Testing Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Reports saved to: ./dast-reports/"
echo ""
echo "Generated files:"
ls -lh *.html *.json *.md *.txt 2>/dev/null || echo "  (Check dast-reports directory)"
echo ""
echo "📖 To view the HTML report:"
echo "   Open: dast-reports/zap-report.html in your browser"
echo ""
echo "🔍 Review security issues and fix high-risk vulnerabilities!"
echo ""
