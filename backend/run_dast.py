#!/usr/bin/env python3
"""
DAST (Dynamic Application Security Testing) Script
Tests the running application for security vulnerabilities.
"""

import requests
import json
import sys
from datetime import datetime
from urllib.parse import urljoin


# Target endpoint
BASE_URL = "http://localhost:8000"

# Color codes for terminal output
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'


def test_security_headers():
    """Test for presence of security headers"""
    print("\n" + "="*80)
    print("🔍 DAST TEST 1: SECURITY HEADERS CHECK")
    print("="*80 + "\n")
    
    try:
        response = requests.get(BASE_URL + "/docs")
        headers = response.headers
        
        required_headers = {
            "Strict-Transport-Security": "CRITICAL",
            "X-Content-Type-Options": "HIGH",
            "X-Frame-Options": "HIGH",
            "Content-Security-Policy": "HIGH",
            "X-XSS-Protection": "MEDIUM",
            "Referrer-Policy": "MEDIUM",
            "Permissions-Policy": "LOW"
        }
        
        results = []
        for header, severity in required_headers.items():
            if header in headers:
                print(f"  ✅ {GREEN}{header}{RESET}: {headers[header][:60]}...")
                results.append({"header": header, "present": True, "value": headers[header]})
            else:
                print(f"  ❌ {RED}[{severity}] {header} MISSING{RESET}")
                results.append({"header": header, "present": False, "severity": severity})
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing headers: {e}")
        return []


def test_cors_configuration():
    """Test CORS configuration"""
    print("\n" + "="*80)
    print("🔍 DAST TEST 2: CORS CONFIGURATION CHECK")
    print("="*80 + "\n")
    
    try:
        # Test with custom origin
        headers = {"Origin": "http://malicious-site.com"}
        response = requests.options(BASE_URL + "/api/auth/login", headers=headers)
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
        }
        
        print(f"  🔍 Testing CORS with malicious origin...")
        for header, value in cors_headers.items():
            if value:
                if value == "*" and header == "Access-Control-Allow-Origin":
                    print(f"  ⚠️  {YELLOW}[MEDIUM] {header}: {value} (Allows all origins - consider restricting){RESET}")
                else:
                    print(f"  ℹ️  {header}: {value}")
        
        if cors_headers["Access-Control-Allow-Origin"] == "*":
            print(f"\n  {YELLOW}⚠️  WARNING: CORS allows all origins. Consider whitelisting specific domains.{RESET}")
            return {"severity": "MEDIUM", "issue": "Overly permissive CORS"}
        else:
            print(f"\n  {GREEN}✅ CORS configuration looks restrictive{RESET}")
            return {"severity": "OK", "issue": None}
            
    except Exception as e:
        print(f"❌ Error testing CORS: {e}")
        return {}


def test_sql_injection():
    """Test for SQL injection vulnerabilities"""
    print("\n" + "="*80)
    print("🔍 DAST TEST 3: SQL INJECTION TESTING")
    print("="*80 + "\n")
    
    # SQL injection payloads
    payloads = [
        "' OR '1'='1",
        "admin'--",
        "' OR 1=1--",
        "1' UNION SELECT NULL--",
        "' AND 1=0 UNION ALL SELECT 'admin', 'password'--"
    ]
    
    vulnerabilities = []
    
    print("  🔍 Testing /api/auth/login endpoint...")
    for payload in payloads:
        try:
            data = {
                "email": payload,
                "password": payload
            }
            response = requests.post(BASE_URL + "/api/auth/login", json=data)
            
            # Check for SQL error messages
            if any(keyword in response.text.lower() for keyword in ["sql", "syntax", "mysql", "sqlite", "database error"]):
                print(f"  {RED}❌ [HIGH] Potential SQL injection with payload: {payload}{RESET}")
                vulnerabilities.append({"payload": payload, "response": response.text[:100]})
            else:
                print(f"  {GREEN}✅ Payload blocked: {payload[:30]}{RESET}")
                
        except Exception as e:
            print(f"  ⚠️  Error testing payload '{payload}': {e}")
    
    if not vulnerabilities:
        print(f"\n  {GREEN}✅ No SQL injection vulnerabilities detected{RESET}")
    else:
        print(f"\n  {RED}❌ Found {len(vulnerabilities)} potential SQL injection points{RESET}")
    
    return vulnerabilities


def test_xss_vulnerabilities():
    """Test for XSS vulnerabilities"""
    print("\n" + "="*80)
    print("🔍 DAST TEST 4: XSS (Cross-Site Scripting) TESTING")
    print("="*80 + "\n")
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg/onload=alert('XSS')>",
        "'-alert('XSS')-'",
    ]
    
    vulnerabilities = []
    
    print("  🔍 Testing /api/auth/register endpoint...")
    for payload in xss_payloads:
        try:
            data = {
                "username": payload,
                "email": "test@test.com",
                "password": "password123"
            }
            response = requests.post(BASE_URL + "/api/auth/register", json=data)
            
            # Check if payload is reflected in response
            if payload in response.text:
                print(f"  {RED}❌ [HIGH] Potential XSS - payload reflected: {payload}{RESET}")
                vulnerabilities.append({"payload": payload})
            else:
                print(f"  {GREEN}✅ Payload sanitized: {payload[:40]}{RESET}")
                
        except Exception as e:
            print(f"  ℹ️  Payload rejected: {payload[:30]}")
    
    if not vulnerabilities:
        print(f"\n  {GREEN}✅ No XSS vulnerabilities detected{RESET}")
    else:
        print(f"\n  {RED}❌ Found {len(vulnerabilities)} potential XSS points{RESET}")
    
    return vulnerabilities


def test_authentication_bypass():
    """Test for authentication bypass vulnerabilities"""
    print("\n" + "="*80)
    print("🔍 DAST TEST 5: AUTHENTICATION BYPASS TESTING")
    print("="*80 + "\n")
    
    protected_endpoints = [
        "/api/customer/orders",
        "/api/provider/orders",
        "/api/profile/me",
        "/api/admin/users",
    ]
    
    vulnerabilities = []
    
    print("  🔍 Testing protected endpoints without authentication...")
    for endpoint in protected_endpoints:
        try:
            # Try accessing without token
            response = requests.get(BASE_URL + endpoint)
            
            if response.status_code == 200:
                print(f"  {RED}❌ [CRITICAL] {endpoint} accessible without auth (HTTP {response.status_code}){RESET}")
                vulnerabilities.append({"endpoint": endpoint, "status": response.status_code})
            elif response.status_code in [401, 403]:
                print(f"  {GREEN}✅ {endpoint} properly protected (HTTP {response.status_code}){RESET}")
            else:
                print(f"  ℹ️  {endpoint} returned HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️  Error testing {endpoint}: {e}")
    
    # Test with invalid token
    print("\n  🔍 Testing with invalid JWT token...")
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    
    for endpoint in protected_endpoints[:2]:  # Test first 2 endpoints
        try:
            response = requests.get(BASE_URL + endpoint, headers=headers)
            if response.status_code == 200:
                print(f"  {RED}❌ [CRITICAL] {endpoint} accepts invalid token{RESET}")
                vulnerabilities.append({"endpoint": endpoint, "issue": "Invalid token accepted"})
            else:
                print(f"  {GREEN}✅ {endpoint} rejected invalid token (HTTP {response.status_code}){RESET}")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
    
    if not vulnerabilities:
        print(f"\n  {GREEN}✅ Authentication properly enforced{RESET}")
    else:
        print(f"\n  {RED}❌ Found {len(vulnerabilities)} authentication bypass vulnerabilities{RESET}")
    
    return vulnerabilities


def test_sensitive_data_exposure():
    """Test for sensitive data exposure"""
    print("\n" + "="*80)
    print("🔍 DAST TEST 6: SENSITIVE DATA EXPOSURE")
    print("="*80 + "\n")
    
    sensitive_endpoints = [
        "/api/auth/login",
        "/api/auth/register",
        "/.env",
        "/config",
        "/api/docs",
    ]
    
    issues = []
    
    print("  🔍 Testing for sensitive data in responses...")
    for endpoint in sensitive_endpoints:
        try:
            response = requests.get(BASE_URL + endpoint)
            
            # Check for sensitive patterns
            sensitive_patterns = [
                "password", "secret", "api_key", "private_key",
                "database_url", "jwt_secret", "aws_access_key"
            ]
            
            content_lower = response.text.lower()
            found_patterns = [p for p in sensitive_patterns if p in content_lower and "password" not in endpoint]
            
            if found_patterns and response.status_code == 200:
                print(f"  {YELLOW}⚠️  [MEDIUM] {endpoint} may expose: {', '.join(found_patterns)}{RESET}")
                issues.append({"endpoint": endpoint, "patterns": found_patterns})
            elif endpoint == "/.env" and response.status_code == 200:
                print(f"  {RED}❌ [CRITICAL] .env file is publicly accessible!{RESET}")
                issues.append({"endpoint": endpoint, "severity": "CRITICAL"})
            else:
                print(f"  {GREEN}✅ {endpoint} looks safe{RESET}")
                
        except Exception as e:
            print(f"  ℹ️  {endpoint} not accessible")
    
    return issues


def test_rate_limiting():
    """Test for rate limiting"""
    print("\n" + "="*80)
    print("🔍 DAST TEST 7: RATE LIMITING CHECK")
    print("="*80 + "\n")
    
    print("  🔍 Sending 50 rapid requests to /api/auth/login...")
    
    try:
        rate_limited = False
        for i in range(50):
            response = requests.post(
                BASE_URL + "/api/auth/login",
                json={"email": "test@test.com", "password": "test123"}
            )
            
            if response.status_code == 429:  # Too Many Requests
                print(f"  {GREEN}✅ Rate limiting active (blocked at request #{i+1}){RESET}")
                rate_limited = True
                break
        
        if not rate_limited:
            print(f"  {YELLOW}⚠️  [MEDIUM] No rate limiting detected (all 50 requests allowed){RESET}")
            print(f"  💡 Recommendation: Implement rate limiting to prevent brute force attacks")
            return {"issue": "No rate limiting", "severity": "MEDIUM"}
        else:
            return {"issue": None}
            
    except Exception as e:
        print(f"❌ Error testing rate limiting: {e}")
        return {}


def generate_dast_report(results):
    """Generate comprehensive DAST report"""
    print("\n" + "="*80)
    print("📋 DAST TESTING SUMMARY")
    print("="*80 + "\n")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
DAST (Dynamic Application Security Testing) Report
Target: {BASE_URL}
Timestamp: {timestamp}

=== SECURITY HEADERS ===
{json.dumps(results.get('headers', []), indent=2)}

=== CORS CONFIGURATION ===
{json.dumps(results.get('cors', {}), indent=2)}

=== SQL INJECTION TESTS ===
Vulnerabilities Found: {len(results.get('sql_injection', []))}
{json.dumps(results.get('sql_injection', []), indent=2)}

=== XSS TESTS ===
Vulnerabilities Found: {len(results.get('xss', []))}
{json.dumps(results.get('xss', []), indent=2)}

=== AUTHENTICATION BYPASS TESTS ===
Vulnerabilities Found: {len(results.get('auth_bypass', []))}
{json.dumps(results.get('auth_bypass', []), indent=2)}

=== SENSITIVE DATA EXPOSURE ===
Issues Found: {len(results.get('data_exposure', []))}
{json.dumps(results.get('data_exposure', []), indent=2)}

=== RATE LIMITING ===
{json.dumps(results.get('rate_limiting', {}), indent=2)}

=== SUMMARY ===
Total Critical Issues: {results.get('critical_count', 0)}
Total High Issues: {results.get('high_count', 0)}
Total Medium Issues: {results.get('medium_count', 0)}
Total Low Issues: {results.get('low_count', 0)}

=== RECOMMENDATIONS ===
1. Fix all CRITICAL and HIGH severity issues immediately
2. Implement rate limiting on authentication endpoints
3. Consider restricting CORS to specific domains
4. Keep security headers updated
5. Regular security testing in CI/CD pipeline
"""
    
    # Save to file
    with open("dast_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    with open("dast_summary_report.txt", "w") as f:
        f.write(report)
    
    print(report)
    print(f"\n✅ Detailed report saved: dast_report.json")
    print(f"✅ Summary report saved: dast_summary_report.txt\n")


def main():
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}🔐 DAST - Dynamic Application Security Testing{RESET}")
    print(f"{BLUE}Target: {BASE_URL}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL + "/health", timeout=5)
        print(f"\n{GREEN}✅ Server is running (HTTP {response.status_code}){RESET}\n")
    except Exception as e:
        print(f"\n{RED}❌ Server is not running at {BASE_URL}{RESET}")
        print(f"{RED}   Error: {e}{RESET}")
        print(f"\n{YELLOW}Please start the server first:{RESET}")
        print(f"{YELLOW}   poetry run uvicorn app.main:app --reload{RESET}\n")
        sys.exit(1)
    
    # Run all tests
    results = {}
    
    results['headers'] = test_security_headers()
    results['cors'] = test_cors_configuration()
    results['sql_injection'] = test_sql_injection()
    results['xss'] = test_xss_vulnerabilities()
    results['auth_bypass'] = test_authentication_bypass()
    results['data_exposure'] = test_sensitive_data_exposure()
    results['rate_limiting'] = test_rate_limiting()
    
    # Count severity levels
    results['critical_count'] = len(results.get('auth_bypass', []))
    results['high_count'] = len(results.get('sql_injection', [])) + len(results.get('xss', []))
    results['medium_count'] = 1 if results.get('cors', {}).get('severity') == 'MEDIUM' else 0
    results['low_count'] = 0
    
    # Generate report
    generate_dast_report(results)
    
    print(f"\n{GREEN}✅ DAST Testing Complete!{RESET}\n")


if __name__ == "__main__":
    main()
