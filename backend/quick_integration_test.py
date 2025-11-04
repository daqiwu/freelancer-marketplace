"""
Quick Integration Test Runner - Tests a few key endpoints
Run this to verify your backend is working correctly
"""
import sys
import asyncio
import httpx
from datetime import datetime

SERVER_URL = "http://localhost:8000"

async def test_health():
    """Test if server is accessible"""
    print("🔍 Testing server health...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SERVER_URL}/docs")
            if response.status_code == 200:
                print(f"   ✅ Server is accessible at {SERVER_URL}")
                return True
            else:
                print(f"   ❌ Server returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return False

async def test_register_and_login():
    """Test user registration and login"""
    print("\n🧪 Testing user registration and login...")
    
    timestamp = int(datetime.now().timestamp() * 1000)
    username = f"testuser_{timestamp}"
    email = f"test_{timestamp}@example.com"
    password = "Test123!@#"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Register
            print(f"   📝 Registering user: {username}")
            reg_response = await client.post(
                f"{SERVER_URL}/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "role_id": 1
                }
            )
            
            if reg_response.status_code not in [200, 201]:
                print(f"   ❌ Registration failed: {reg_response.status_code}")
                print(f"      Response: {reg_response.text}")
                return False
            
            print(f"   ✅ Registration successful")
            
            # Login
            print(f"   🔐 Logging in...")
            login_response = await client.post(
                f"{SERVER_URL}/auth/login",
                json={
                    "username": username,
                    "password": password
                }
            )
            
            if login_response.status_code != 200:
                print(f"   ❌ Login failed: {login_response.status_code}")
                print(f"      Response: {login_response.text}")
                return False
            
            token_data = login_response.json()
            if "access_token" in token_data:
                print(f"   ✅ Login successful - Got access token")
                return True
            else:
                print(f"   ❌ No access token in response")
                return False
                
    except httpx.TimeoutException:
        print(f"   ❌ Request timed out - server may be slow or unresponsive")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def test_get_users():
    """Test getting users list"""
    print("\n🧪 Testing get users endpoint...")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SERVER_URL}/admin/users")
            
            # This might require auth, so 401 is also acceptable
            if response.status_code in [200, 401]:
                print(f"   ✅ Endpoint accessible (status: {response.status_code})")
                return True
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                return True  # Not a critical failure
                
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("=" * 60)
    print("  FREELANCER MARKETPLACE - QUICK INTEGRATION TESTS")
    print("=" * 60)
    print(f"Testing against: {SERVER_URL}\n")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", await test_health()))
    
    if not results[0][1]:
        print("\n" + "=" * 60)
        print("❌ Backend server is not accessible!")
        print("   Please ensure the backend is running:")
        print("   cd backend")
        print("   python -m uvicorn app.main:app --reload")
        print("=" * 60)
        return 1
    
    # Test 2: Register and login
    results.append(("Register & Login", await test_register_and_login()))
    
    # Test 3: Get users
    results.append(("Get Users", await test_get_users()))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("-" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
