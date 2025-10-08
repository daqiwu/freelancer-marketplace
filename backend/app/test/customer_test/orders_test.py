import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_publish_order_api():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 注册并登录获取token
        await ac.delete("http://localhost:8000/auth/test/cleanup?username=orderapitestuser")
        register_data = {
            "username": "orderapitestuser",
            "email": "orderapitestuser@example.com",
            "password": "orderapitestpass",
            "role_id": 1
        }
        reg_resp = await ac.post("http://localhost:8000/auth/register", json=register_data)
        assert reg_resp.status_code == 200

        login_data = {
            "email": "orderapitestuser@example.com",
            "password": "orderapitestpass"
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # 发布订单
        order_data = {
            "title": "API Test Order",
            "description": "Order for API test.",
            "price": 99.99,
            "location": "NORTH",
            "address": "Test Address"
        }
        headers = {"Authorization": f"Bearer {token}"}
        publish_resp = await ac.post(
            "http://localhost:8000/customer/orders/publish",
            json=order_data,
            headers=headers
        )
        print(publish_resp.text)
        assert publish_resp.status_code == 200
        resp_json = publish_resp.json()
        assert resp_json["status"] == "pending"
        assert "order_id" in resp_json
        assert resp_json["message"].startswith("You have successfully published the order:")

@pytest.mark.asyncio
async def test_cancel_order_api():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 注册并登录获取token
        await ac.delete("http://localhost:8000/auth/test/cleanup?username=orderapitestuser")
        register_data = {
            "username": "orderapitestuser",
            "email": "orderapitestuser@example.com",
            "password": "orderapitestpass",
            "role_id": 1
        }
        reg_resp = await ac.post("http://localhost:8000/auth/register", json=register_data)
        assert reg_resp.status_code == 200

        login_data = {
            "email": "orderapitestuser@example.com",
            "password": "orderapitestpass"
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 发布订单
        order_data = {
            "title": "API Cancel Test Order",
            "description": "Order for cancel API test.",
            "price": 88.88,
            "location": "NORTH",
            "address": "Cancel Test Address"
        }
        publish_resp = await ac.post(
            "http://localhost:8000/customer/orders/publish",
            json=order_data,
            headers=headers
        )
        assert publish_resp.status_code == 200
        order_id = publish_resp.json()["order_id"]

        # 取消订单
        cancel_resp = await ac.post(
            f"http://localhost:8000/customer/orders/cancel/{order_id}",
            headers=headers
        )
        print(cancel_resp.text)
        assert cancel_resp.status_code == 200
        cancel_json = cancel_resp.json()
        assert cancel_json["status"] == "cancelled"
        assert cancel_json["message"].startswith("You have successfully cancelled the order:")