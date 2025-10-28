"""
Quick API Test Script for Security Classifier
Run this script to test the security classifier API endpoints
"""

import requests
import json
from pprint import pprint

# Configuration
API_BASE = "http://localhost:8000/api"
USERNAME = "admin"  # Change to your username
PASSWORD = "admin123"  # Change to your password

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def login():
    """Login and get access token"""
    print_header("Step 1: Authenticating")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": USERNAME, "password": PASSWORD}
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        print_success(f"Logged in as {USERNAME}")
        return token
    except Exception as e:
        print_error(f"Login failed: {e}")
        return None

def test_create_issue(token):
    """Test creating a security issue"""
    print_header("Step 2: Creating Security Issue")
    
    issue_data = {
        "title": "CVE-2021-44228 Log4Shell vulnerability",
        "description": "Critical remote code execution vulnerability in Apache Log4j 2. "
                      "Allows attackers to execute arbitrary code by logging a specially crafted string.",
        "affected_component": "pom.xml - log4j-core 2.14.0"
    }
    
    print("Issue data:")
    print(json.dumps(issue_data, indent=2))
    print()
    
    try:
        response = requests.post(
            f"{API_BASE}/security/issues",
            json=issue_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        result = response.json()
        
        print_success("Issue created and classified!")
        print(f"\nClassification Results:")
        print(f"  ID: {result['id']}")
        print(f"  Type: {Colors.BLUE}{result['issue_type']}{Colors.RESET}")
        print(f"  Severity: {Colors.RED if result['severity'] == 'CRITICAL' else Colors.YELLOW}{result['severity']}{Colors.RESET}")
        print(f"  Confidence: {result['confidence_score']}%")
        print(f"  Priority: {result['remediation_priority']}/10")
        print(f"  Effort: {result['estimated_effort']}")
        print(f"\nRemediation Suggestion:")
        print(f"  {result['remediation_suggestion']}")
        
        return result['id']
    except Exception as e:
        print_error(f"Failed to create issue: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None

def test_batch_classify(token):
    """Test batch classification"""
    print_header("Step 3: Batch Classification")
    
    issues = [
        {
            "title": "Outdated npm package detected",
            "description": "The package lodash version 4.17.19 is outdated. Update to 4.17.21",
            "affected_component": "package.json"
        },
        {
            "title": "SQL Injection vulnerability",
            "description": "User input concatenated into SQL query at line 45 without parameterization",
            "affected_component": "app/auth/login.py:45"
        },
        {
            "title": "Missing CORS security headers",
            "description": "Dynamic scan found missing security headers on /api/users endpoint",
            "affected_component": "/api/users"
        }
    ]
    
    print(f"Classifying {len(issues)} issues...")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE}/security/batch-classify",
            json={"issues": issues},
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        results = response.json()
        
        print_success(f"Successfully classified {len(results)} issues!\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   Type: {result['issue_type']}, Severity: {result['severity']}, "
                  f"Confidence: {result['confidence_score']}%")
        
        return True
    except Exception as e:
        print_error(f"Batch classification failed: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def test_get_issues(token):
    """Test getting issues list"""
    print_header("Step 4: Retrieving Issues")
    
    try:
        response = requests.get(
            f"{API_BASE}/security/issues",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        issues = response.json()
        
        print_success(f"Found {len(issues)} security issues")
        
        if issues:
            print("\nRecent issues:")
            for issue in issues[:5]:  # Show first 5
                print(f"  • [{issue['issue_type']}] {issue['title']}")
                print(f"    Severity: {issue['severity']}, Status: {issue['status']}")
        
        return True
    except Exception as e:
        print_error(f"Failed to get issues: {e}")
        return False

def test_get_statistics(token):
    """Test getting statistics"""
    print_header("Step 5: Getting Statistics")
    
    try:
        response = requests.get(
            f"{API_BASE}/security/statistics",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        stats = response.json()
        
        print_success("Statistics retrieved!")
        print(f"\nOverview:")
        print(f"  Total Issues: {stats['total']}")
        print(f"  Average Confidence: {stats['avg_confidence']}%")
        
        print(f"\nBy Type:")
        for type_name, count in stats['by_type'].items():
            print(f"  {type_name}: {count}")
        
        print(f"\nBy Severity:")
        for severity, count in stats['by_severity'].items():
            print(f"  {severity}: {count}")
        
        print(f"\nBy Status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
        
        return True
    except Exception as e:
        print_error(f"Failed to get statistics: {e}")
        return False

def test_update_issue(token, issue_id):
    """Test updating an issue"""
    print_header("Step 6: Updating Issue Status")
    
    if not issue_id:
        print_warning("Skipping - no issue ID available")
        return False
    
    try:
        response = requests.patch(
            f"{API_BASE}/security/issues/{issue_id}",
            json={"status": "RESOLVED"},
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        result = response.json()
        
        print_success(f"Issue #{issue_id} marked as RESOLVED")
        return True
    except Exception as e:
        print_error(f"Failed to update issue: {e}")
        return False

def main():
    """Main test flow"""
    print(f"{Colors.GREEN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   AI Security Classifier - API Test Script              ║")
    print("║   Testing all endpoints and functionality               ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # Login
    token = login()
    if not token:
        print_error("\nTests aborted - authentication failed")
        print("\nPlease ensure:")
        print("  1. Backend server is running (http://localhost:8000)")
        print("  2. Username and password are correct")
        print("  3. User has required permissions")
        return
    
    # Run tests
    issue_id = test_create_issue(token)
    test_batch_classify(token)
    test_get_issues(token)
    test_get_statistics(token)
    test_update_issue(token, issue_id)
    
    # Summary
    print_header("Test Summary")
    print_success("All API tests completed!")
    print(f"\n{Colors.BLUE}Next steps:{Colors.RESET}")
    print("  • Visit http://localhost:8080/security to use the web interface")
    print("  • Check API documentation at http://localhost:8000/docs")
    print("  • Run backend tests: cd backend && pytest tests/ -v")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")

