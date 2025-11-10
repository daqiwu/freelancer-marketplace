"""
Security Testing Script - SAST and DAST for Freelancer Marketplace
Tests both static code analysis and dynamic endpoint testing
"""

import subprocess
import sys
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BACKEND_PATH = "."

def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def install_tools():
    """Install required security testing tools"""
    print_header("Installing Security Testing Tools")
    
    tools = ["bandit", "safety", "requests"]
    
    for tool in tools:
        print(f"Installing {tool}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", tool],
                check=True
            )
            print(f"✓ {tool} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {tool}: {e}")
            return False
    
    return True

def run_bandit_scan():
    """Run Bandit SAST scan on backend code"""
    print_header("SAST: Bandit Security Scan")
    
    try:
        # Run bandit with JSON output
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", "app/", "-f", "json", "-o", "bandit_report.json"],
            capture_output=True,
            text=True
        )
        
        # Also run with text output for display
        result_text = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", "app/", "-ll"],  # -ll = only show medium and high severity
            capture_output=True,
            text=True
        )
        
        print(result_text.stdout)
        
        # Parse JSON results
        if os.path.exists("bandit_report.json"):
            with open("bandit_report.json", "r") as f:
                data = json.load(f)
                metrics = data.get("metrics", {})
                total = sum(m.get("SEVERITY.HIGH", 0) + m.get("SEVERITY.MEDIUM", 0) 
                           for m in metrics.values() if isinstance(m, dict))
                
                print(f"\n📊 Summary:")
                print(f"   High Severity Issues: {sum(m.get('SEVERITY.HIGH', 0) for m in metrics.values() if isinstance(m, dict))}")
                print(f"   Medium Severity Issues: {sum(m.get('SEVERITY.MEDIUM', 0) for m in metrics.values() if isinstance(m, dict))}")
                print(f"   Low Severity Issues: {sum(m.get('SEVERITY.LOW', 0) for m in metrics.values() if isinstance(m, dict))}")
        
        return True
    except Exception as e:
        print(f"✗ Bandit scan failed: {e}")
        return False

def run_safety_check():
    """Run Safety check on dependencies"""
    print_header("SAST: Safety Dependency Vulnerability Check")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "safety", "check", "--json"],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                if isinstance(data, list) and len(data) > 0:
                    print(f"⚠️  Found {len(data)} vulnerable dependencies:\n")
                    for vuln in data:
                        print(f"   Package: {vuln.get('package', 'Unknown')}")
                        print(f"   Installed: {vuln.get('installed_version', 'Unknown')}")
                        print(f"   Vulnerability: {vuln.get('vulnerability', 'Unknown')}")
                        print(f"   Fixed in: {vuln.get('fixed_version', 'Unknown')}")
                        print()
                else:
                    print("✓ No known vulnerabilities found in dependencies")
            except json.JSONDecodeError:
                print(result.stdout)
        else:
            print("✓ No known vulnerabilities found in dependencies")
        
        return True
    except Exception as e:
        print(f"✗ Safety check failed: {e}")
        return False

def test_security_headers():
    """Test security headers on endpoints"""
    print_header("DAST: Security Headers Testing")
    
    import requests
    
    endpoints = ["/", "/health", "/docs"]
    
    expected_headers = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": None,  # Just check existence
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": None  # Just check existence
    }
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\nTesting: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"Status Code: {response.status_code}")
            
            print("\n  Security Headers:")
            for header, expected_value in expected_headers.items():
                actual_value = response.headers.get(header)
                
                if actual_value:
                    if expected_value and actual_value == expected_value:
                        print(f"    ✓ {header}: {actual_value}")
                    elif expected_value and actual_value != expected_value:
                        print(f"    ⚠️  {header}: {actual_value}")
                        print(f"       Expected: {expected_value}")
                    else:
                        print(f"    ✓ {header}: Present")
                else:
                    print(f"    ✗ {header}: MISSING")
            
        except requests.RequestException as e:
            print(f"  ✗ Failed to connect: {e}")

def test_authentication_endpoints():
    """Test authentication endpoints for common vulnerabilities"""
    print_header("DAST: Authentication Endpoint Security Testing")
    
    import requests
    
    # Test 1: SQL Injection attempts
    print("\n1. SQL Injection Testing")
    sql_payloads = [
        "' OR '1'='1",
        "admin'--",
        "' OR 1=1--",
        "1' UNION SELECT NULL--"
    ]
    
    for payload in sql_payloads:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": payload, "password": "test"},
                timeout=5
            )
            print(f"   Payload: {payload[:30]:<30} | Status: {response.status_code} | "
                  f"{'✓ Protected' if response.status_code in [400, 401, 422] else '⚠️ Potential Issue'}")
        except Exception as e:
            print(f"   ✗ Error testing payload: {e}")
    
    # Test 2: XSS attempts
    print("\n2. XSS (Cross-Site Scripting) Testing")
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')"
    ]
    
    for payload in xss_payloads:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={"username": payload, "email": "test@test.com", "password": "Test123!", "user_type": "customer"},
                timeout=5
            )
            
            # Check if payload is reflected in response
            if payload in response.text:
                print(f"   ⚠️  Payload reflected in response: {payload[:30]}")
            else:
                print(f"   ✓ Payload sanitized: {payload[:30]}")
        except Exception as e:
            print(f"   ✗ Error testing payload: {e}")
    
    # Test 3: Brute Force Protection
    print("\n3. Brute Force Protection Testing")
    print("   Testing multiple failed login attempts...")
    
    failed_count = 0
    for i in range(10):
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "testuser", "password": f"wrongpass{i}"},
                timeout=5
            )
            if response.status_code == 401:
                failed_count += 1
        except Exception as e:
            pass
    
    print(f"   Made 10 failed login attempts: {'⚠️ No rate limiting detected' if failed_count == 10 else '✓ Some protection in place'}")
    
    # Test 4: Password Strength
    print("\n4. Password Policy Testing")
    weak_passwords = ["123", "password", "abc", "test"]
    
    for pwd in weak_passwords:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={"username": f"test_{pwd}", "email": f"test_{pwd}@test.com", 
                      "password": pwd, "user_type": "customer"},
                timeout=5
            )
            
            if response.status_code in [400, 422]:
                print(f"   ✓ Weak password rejected: '{pwd}'")
            else:
                print(f"   ⚠️  Weak password accepted: '{pwd}'")
        except Exception as e:
            print(f"   ✗ Error testing password: {e}")

def test_common_vulnerabilities():
    """Test for common API vulnerabilities"""
    print_header("DAST: Common Vulnerability Testing")
    
    import requests
    
    # Test 1: Check if /docs is accessible (should be for API documentation)
    print("\n1. API Documentation Exposure")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"   /docs endpoint: {'✓ Accessible' if response.status_code == 200 else '✗ Not accessible'}")
        print(f"   Note: Consider restricting in production")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: HTTP Methods testing
    print("\n2. Unsupported HTTP Methods")
    methods = ["PUT", "DELETE", "PATCH", "OPTIONS"]
    
    for method in methods:
        try:
            response = requests.request(method, f"{BASE_URL}/health", timeout=5)
            if response.status_code == 405:
                print(f"   ✓ {method} properly rejected")
            else:
                print(f"   ⚠️  {method} returned status {response.status_code}")
        except Exception as e:
            pass
    
    # Test 3: CORS Configuration
    print("\n3. CORS Configuration")
    try:
        response = requests.options(
            f"{BASE_URL}/health",
            headers={"Origin": "http://evil.com"},
            timeout=5
        )
        
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        if cors_header == "*":
            print(f"   ⚠️  CORS allows all origins (*) - consider restricting in production")
        elif cors_header:
            print(f"   ✓ CORS configured: {cors_header}")
        else:
            print(f"   ✓ CORS header not present")
    except Exception as e:
        print(f"   ✗ Error: {e}")

def generate_report():
    """Generate final security report"""
    print_header("Security Test Report")
    
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print(f"\nReport Files Generated:")
    print(f"  - bandit_report.json (SAST results)")
    print(f"\nRecommendations:")
    print(f"  1. Review all HIGH and MEDIUM severity findings from Bandit")
    print(f"  2. Update any vulnerable dependencies identified by Safety")
    print(f"  3. Ensure all security headers are properly configured")
    print(f"  4. Implement rate limiting for authentication endpoints")
    print(f"  5. Consider restricting /docs endpoint in production")
    print(f"  6. Review CORS policy for production deployment")
    print(f"  7. Ensure strong password policies are enforced")

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("  FREELANCER MARKETPLACE - SECURITY TESTING SUITE")
    print("  SAST (Static Application Security Testing) + DAST (Dynamic)")
    print("="*80)
    
    # Check if server is running
    import requests
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"\n✓ Server is running at {BASE_URL}")
    except requests.RequestException:
        print(f"\n✗ ERROR: Server is not running at {BASE_URL}")
        print("Please start the server first with: poetry run uvicorn app.main:app")
        sys.exit(1)
    
    # Install tools
    if not install_tools():
        print("\n✗ Failed to install security tools")
        sys.exit(1)
    
    # Run SAST tests
    run_bandit_scan()
    run_safety_check()
    
    # Run DAST tests
    test_security_headers()
    test_authentication_endpoints()
    test_common_vulnerabilities()
    
    # Generate report
    generate_report()
    
    print("\n" + "="*80)
    print("  Security testing completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
