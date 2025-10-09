import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_my_profile_customer():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 清理测试用户  # Clean up test user
        await ac.delete("http://localhost:8000/auth/test/cleanup?username=profiletestcustomer")
        # 注册  # Register
        register_data = {
            "username": "profiletestcustomer",
            "email": "profiletestcustomer@example.com",
            "password": "profiletestpass",
            "role_id": 1
        }
        reg_resp = await ac.post("http://localhost:8000/auth/register", json=register_data)
        assert reg_resp.status_code == 200

        # 登录  # Login
        login_data = {
            "email": "profiletestcustomer@example.com",
            "password": "profiletestpass"
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 补充：注册后插入客户资料  # Insert customer profile after register
        # 这里假设有一个测试接口用于插入 profile
        await ac.post("http://localhost:8000/profile/test/create_customer_profile", json={
            "username": "profiletestcustomer",
            "location": "NORTH",
            "address": "Test Address",
            "budget_preference": 100,
            "balance": 0
        })

        # 获取个人信息  # Get profile info
        resp = await ac.get("http://localhost:8000/profile/me", headers=headers)
        print(resp.text)  # 调试用  # For debugging
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "profiletestcustomer"
        assert data["role"] == "customer"
        assert "customer_profile" in data
        assert data["customer_profile"]["balance"] == 0

@pytest.mark.asyncio
async def test_get_my_profile_provider():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 清理测试用户  # Clean up test user
        await ac.delete("http://localhost:8000/auth/test/cleanup?username=profiletestprovider")
        # 注册  # Register
        register_data = {
            "username": "profiletestprovider",
            "email": "profiletestprovider@example.com",
            "password": "profiletestpass",
            "role_id": 2
        }
        reg_resp = await ac.post("http://localhost:8000/auth/register", json=register_data)
        assert reg_resp.status_code == 200

        # 登录  # Login
        login_data = {
            "email": "profiletestprovider@example.com",
            "password": "profiletestpass"
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 补充：注册后插入服务商资料  # Insert provider profile after register
        await ac.post("http://localhost:8000/profile/test/create_provider_profile", json={
            "username": "profiletestprovider",
            "skills": "Python,SQL",
            "experience_years": 5,
            "hourly_rate": 80,
            "availability": "Weekdays"
        })

        # 获取个人信息  # Get profile info
        resp = await ac.get("http://localhost:8000/profile/me", headers=headers)
        print(resp.text)  # 调试用  # For debugging
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "profiletestprovider"
        assert data["role"] == "provider"
        assert "provider_profile" in data

# 管理员不需要 profile，原测试可保留
@pytest.mark.asyncio
async def test_get_my_profile_admin():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 清理测试用户  # Clean up test user
        await ac.delete("http://localhost:8000/auth/test/cleanup?username=profiletestadmin")
        # 注册  # Register
        register_data = {
            "username": "profiletestadmin",
            "email": "profiletestadmin@example.com",
            "password": "profiletestpass",
            "role_id": 3
        }
        reg_resp = await ac.post("http://localhost:8000/auth/register", json=register_data)
        assert reg_resp.status_code == 200

        # 登录  # Login
        login_data = {
            "email": "profiletestadmin@example.com",
            "password": "profiletestpass"
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 获取个人信息  # Get profile info
        resp = await ac.get("http://localhost:8000/profile/me", headers=headers)
        print(resp.text)  # 调试用  # For debugging
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "profiletestadmin"
        assert data["role"] == "admin"
        assert "customer_profile" not in data
        assert "provider_profile" not in data