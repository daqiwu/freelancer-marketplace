"""
Unit tests for profile routes using TestClient.
Tests profile management endpoints without requiring a running server.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_profile_customer(client: AsyncClient):
    """Test customer can get their profile."""
    # Register as customer
    reg_data = {
        "username": "customer_profile_test",
        "email": "customer_profile@test.com",
        "password": "testpass123",
        "role_id": 1,  # Customer
    }
    reg_resp = await client.post("/auth/register", json=reg_data)
    assert reg_resp.status_code == 200
    
    # Login
    login_resp = await client.post(
        "/auth/login",
        json={"email": "customer_profile@test.com", "password": "testpass123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get profile
    resp = await client.get("/profile/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "customer_profile_test"
    assert data["role"]["role_name"] == "customer"


@pytest.mark.asyncio
async def test_get_profile_provider(client: AsyncClient):
    """Test provider can get their profile."""
    # Register as provider
    reg_data = {
        "username": "provider_profile_test",
        "email": "provider_profile@test.com",
        "password": "testpass123",
        "role_id": 2,  # Provider
    }
    reg_resp = await client.post("/auth/register", json=reg_data)
    assert reg_resp.status_code == 200
    
    # Login
    login_resp = await client.post(
        "/auth/login",
        json={"email": "provider_profile@test.com", "password": "testpass123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get profile
    resp = await client.get("/profile/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "provider_profile_test"
    assert data["role"]["role_name"] == "provider"


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client: AsyncClient):
    """Test profile access requires authentication."""
    resp = await client.get("/profile/me")
    assert resp.status_code in [401, 403]


@pytest.mark.asyncio
async def test_update_customer_profile(client: AsyncClient):
    """Test customer can update their profile."""
    # Register and login
    reg_data = {
        "username": "update_customer_test",
        "email": "update_customer@test.com",
        "password": "testpass123",
        "role_id": 1,
    }
    await client.post("/auth/register", json=reg_data)
    
    login_resp = await client.post(
        "/auth/login",
        json={"email": "update_customer@test.com", "password": "testpass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update profile
    update_data = {
        "phone": "+1234567890",
        "address": "123 Test St"
    }
    resp = await client.put("/profile/customer", json=update_data, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["phone"] == "+1234567890"
    assert data["address"] == "123 Test St"


@pytest.mark.asyncio
async def test_update_provider_profile(client: AsyncClient):
    """Test provider can update their profile."""
    # Register and login as provider
    reg_data = {
        "username": "update_provider_test",
        "email": "update_provider@test.com",
        "password": "testpass123",
        "role_id": 2,
    }
    await client.post("/auth/register", json=reg_data)
    
    login_resp = await client.post(
        "/auth/login",
        json={"email": "update_provider@test.com", "password": "testpass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update profile
    update_data = {
        "bio": "Expert developer",
        "skills": "Python, FastAPI, SQLAlchemy",
        "hourly_rate": 50.0
    }
    resp = await client.put("/profile/provider", json=update_data, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bio"] == "Expert developer"
    assert data["skills"] == "Python, FastAPI, SQLAlchemy"
    assert data["hourly_rate"] == 50.0


@pytest.mark.asyncio
async def test_create_customer_profile(client: AsyncClient):
    """Test creating initial customer profile."""
    # Register and login
    reg_data = {
        "username": "new_customer_profile",
        "email": "new_customer@test.com",
        "password": "testpass123",
        "role_id": 1,
    }
    await client.post("/auth/register", json=reg_data)
    
    login_resp = await client.post(
        "/auth/login",
        json={"email": "new_customer@test.com", "password": "testpass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create profile
    profile_data = {
        "phone": "+9876543210",
        "address": "456 New St",
        "city": "Test City",
        "country": "Test Country"
    }
    resp = await client.post("/profile/customer", json=profile_data, headers=headers)
    assert resp.status_code in [200, 201]
    data = resp.json()
    assert data["phone"] == "+9876543210"
    assert data["city"] == "Test City"


@pytest.mark.asyncio
async def test_create_provider_profile(client: AsyncClient):
    """Test creating initial provider profile."""
    # Register and login as provider
    reg_data = {
        "username": "new_provider_profile",
        "email": "new_provider@test.com",
        "password": "testpass123",
        "role_id": 2,
    }
    await client.post("/auth/register", json=reg_data)
    
    login_resp = await client.post(
        "/auth/login",
        json={"email": "new_provider@test.com", "password": "testpass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create profile
    profile_data = {
        "bio": "Experienced freelancer",
        "skills": "JavaScript, React, Node.js",
        "hourly_rate": 75.0,
        "availability": "full-time"
    }
    resp = await client.post("/profile/provider", json=profile_data, headers=headers)
    assert resp.status_code in [200, 201]
    data = resp.json()
    assert data["bio"] == "Experienced freelancer"
    assert data["hourly_rate"] == 75.0


@pytest.mark.asyncio
async def test_get_public_provider_profile(client: AsyncClient):
    """Test getting public provider profile by ID."""
    # Register provider
    reg_data = {
        "username": "public_provider",
        "email": "public_provider@test.com",
        "password": "testpass123",
        "role_id": 2,
    }
    reg_resp = await client.post("/auth/register", json=reg_data)
    provider_id = reg_resp.json()["id"]
    
    # Get public profile
    resp = await client.get(f"/profile/provider/{provider_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "public_provider"


@pytest.mark.asyncio
async def test_update_profile_wrong_role(client: AsyncClient):
    """Test customer cannot update provider profile."""
    # Register as customer
    reg_data = {
        "username": "wrong_role_test",
        "email": "wrong_role@test.com",
        "password": "testpass123",
        "role_id": 1,  # Customer
    }
    await client.post("/auth/register", json=reg_data)
    
    login_resp = await client.post(
        "/auth/login",
        json={"email": "wrong_role@test.com", "password": "testpass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to update provider profile
    update_data = {
        "bio": "Should fail",
        "hourly_rate": 100.0
    }
    resp = await client.put("/profile/provider", json=update_data, headers=headers)
    assert resp.status_code in [403, 400, 422]  # Forbidden or Bad Request
