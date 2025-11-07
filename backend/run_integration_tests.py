#!/usr/bin/env python3
"""
Integration Test Runner for Local Development

This script runs integration tests against a running backend server.
Ensure your backend is running at http://localhost:8000 before running this script.

Usage:
    python run_integration_tests.py                    # Test against localhost:8000
    python run_integration_tests.py --url http://localhost:8000  # Custom URL
    python run_integration_tests.py --all              # Run all tests including slow ones
"""

import argparse
import sys
import subprocess
import time
import requests
from pathlib import Path


def check_server(url: str, max_attempts: int = 10) -> bool:
    """Check if backend server is running and accessible."""
    print(f"\n🔍 Checking if backend is running at {url}...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(f"{url}/docs", timeout=2)
            if response.status_code == 200:
                print(f"✅ Backend server is running and accessible!")
                return True
        except requests.exceptions.ConnectionError:
            if attempt < max_attempts:
                print(f"   Attempt {attempt}/{max_attempts} failed, retrying in 1 second...")
                time.sleep(1)
            else:
                print(f"❌ Cannot connect to backend server at {url}")
                print(f"   Please start your backend with: poetry run uvicorn app.main:app --reload")
                return False
        except Exception as e:
            print(f"❌ Error checking server: {e}")
            return False
    
    return False


def run_tests(server_url: str, run_all: bool = False) -> int:
    """Run integration tests against the specified server."""
    
    # Define test paths
    integration_tests = [
        "app/test/admin_test/",
        "app/test/auth_test/service_test.py",
        "app/test/customer_test/",
        "app/test/profile_test.py",
    ]
    
    # Build pytest command
    cmd = [
        "poetry", "run", "pytest",
        *integration_tests,
        "-v",
        "--tb=short",
        "--color=yes",
    ]
    
    if not run_all:
        cmd.append("-m")
        cmd.append("not slow")
    
    print(f"\n🧪 Running integration tests...")
    print(f"   Server URL: {server_url}")
    print(f"   Command: {' '.join(cmd)}")
    print("━" * 60)
    
    # Set environment variable for tests
    env = {"TEST_SERVER_URL": server_url}
    
    # Run tests
    result = subprocess.run(cmd, env=env)
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run integration tests against a running backend server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_integration_tests.py                    # Default: http://localhost:8000
  python run_integration_tests.py --url http://localhost:8080
  python run_integration_tests.py --all              # Include slow tests
  python run_integration_tests.py --no-check         # Skip server check
        """
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Backend server URL (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests including slow ones"
    )
    
    parser.add_argument(
        "--no-check",
        action="store_true",
        help="Skip server availability check"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  FREELANCER MARKETPLACE - INTEGRATION TEST RUNNER")
    print("=" * 60)
    
    # Check if server is running (unless --no-check is specified)
    if not args.no_check:
        if not check_server(args.url):
            print("\n💡 Tip: Start your backend server first:")
            print("   cd backend")
            print("   poetry run uvicorn app.main:app --reload")
            return 1
    
    # Run integration tests
    exit_code = run_tests(args.url, args.all)
    
    # Print summary
    print("\n" + "━" * 60)
    if exit_code == 0:
        print("✅ All integration tests PASSED!")
    else:
        print("❌ Some integration tests FAILED")
        print(f"   Exit code: {exit_code}")
    print("━" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
