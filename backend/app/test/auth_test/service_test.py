import time

import pytest
from httpx import AsyncClient

DEPLOY_URL = "https://freelancer-marketplace-api.onrender.com"

@pytest.mark.asyncio
async def test_register_success():
    timestamp = int(time.time())
    async with AsyncClient(base_url=DEPLOY_URL, timeout=30.0) as ac:
        # 清理测试用户
        username = f"apitestuser_{timestamp}"
        await ac.delete("/auth/test/cleanup", params={"username": username})

        # 注册
        register_data = {
            "username": username,
            "email": f"apitestuser_{timestamp}@example.com",
            "password": "apitestpass",
            "role_id": 1,
        }
        reg_resp = await ac.post("/auth/register", json=register_data)
        print("register:", reg_resp.text)
        assert reg_resp.status_code == 200
        resp_json = reg_resp.json()
        assert resp_json["username"] == username
        assert resp_json["email"] == f"apitestuser_{timestamp}@example.com"


@pytest.mark.asyncio
async def test_login_success():
    timestamp = int(time.time())
    async with AsyncClient(base_url=DEPLOY_URL, timeout=30.0) as ac:
        # 清理并注册测试用户
        username = f"loginapitest_{timestamp}"
        email = f"loginapitest_{timestamp}@example.com"
        await ac.delete("/auth/test/cleanup", params={"username": username})

        register_data = {
            "username": username,
            "email": email,
            "password": "apitestpass",
            "role_id": 1,
        }
        reg_resp = await ac.post("/auth/register", json=register_data)
        assert reg_resp.status_code == 200

        # 登录
        login_data = {"email": email, "password": "apitestpass"}
        login_resp = await ac.post("/auth/login", json=login_data)
        print("login:", login_resp.text)
        assert login_resp.status_code == 200
        resp_json = login_resp.json()
        assert "access_token" in resp_json
        assert resp_json["token_type"] == "bearer"
