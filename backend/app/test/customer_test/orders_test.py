import pytest
from httpx import AsyncClient
import time

@pytest.mark.asyncio
async def test_publish_order_api():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 注册并登录获取token  # Register and login to get token
        timestamp = str(int(time.time()))
        username = f"orderapitestuser_{timestamp}"
        email = f"orderapitestuser_{timestamp}@example.com"
        
        await ac.delete(f"http://localhost:8000/auth/test/cleanup?username={username}")
        register_data = {
            "username": username,
            "email": email,
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

        # 发布订单  # Publish order
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
        print(publish_resp.text)  # 调试用  # For debugging
        assert publish_resp.status_code == 200
        resp_json = publish_resp.json()
        assert resp_json["status"] == "pending"
        assert "order_id" in resp_json
        assert resp_json["message"].startswith("You have successfully published the order:")

@pytest.mark.asyncio
async def test_cancel_order_api():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 注册并登录获取token  # Register and login to get token
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

        # 发布订单  # Publish order
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

        # 取消订单  # Cancel order
        cancel_resp = await ac.post(
            f"http://localhost:8000/customer/orders/cancel/{order_id}",
            headers=headers
        )
        print(cancel_resp.text)  # 调试用  # For debugging
        assert cancel_resp.status_code == 200
        cancel_json = cancel_resp.json()
        assert cancel_json["status"] == "cancelled"
        assert cancel_json["message"].startswith("You have successfully cancelled the order:")

@pytest.mark.asyncio
async def test_list_my_orders_api():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 清理测试用户  # Clean up test user
        await ac.delete("http://localhost:8000/auth/test/cleanup?username=orderapitestuser")
        # 注册  # Register
        register_data = {
            "username": "orderapitestuser",
            "email": "orderapitestuser@example.com",
            "password": "orderapitestpass",
            "role_id": 1
        }
        reg_resp = await ac.post("http://localhost:8000/auth/register", json=register_data)
        assert reg_resp.status_code == 200

        # 登录  # Login
        login_data = {
            "email": "orderapitestuser@example.com",
            "password": "orderapitestpass"
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 发布两个订单  # Publish two orders
        order_data_1 = {
            "title": "Order 1",
            "description": "First order.",
            "price": 10.0,
            "location": "NORTH",
            "address": "Addr 1"
        }
        order_data_2 = {
            "title": "Order 2",
            "description": "Second order.",
            "price": 20.0,
            "location": "SOUTH",
            "address": "Addr 2"
        }
        resp1 = await ac.post("http://localhost:8000/customer/orders/publish", json=order_data_1, headers=headers)
        resp2 = await ac.post("http://localhost:8000/customer/orders/publish", json=order_data_2, headers=headers)
        assert resp1.status_code == 200
        assert resp2.status_code == 200

        # 查询订单列表  # Query order list
        list_resp = await ac.get("http://localhost:8000/customer/orders/my", headers=headers)
        print(list_resp.text)  # 调试用  # For debugging
        assert list_resp.status_code == 200
        orders = list_resp.json()
        assert isinstance(orders, list)
        assert len(orders) >= 2
        assert orders[0]["status"] in ["pending", "accepted", "in_progress"]

@pytest.mark.asyncio
async def test_get_my_order_detail_api():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 清理测试用户  # Clean up test user
        await ac.delete("http://localhost:8000/auth/test/cleanup?username=orderapitestuser")
        # 注册  # Register
        register_data = {
            "username": "orderapitestuser",
            "email": "orderapitestuser@example.com",
            "password": "orderapitestpass",
            "role_id": 1
        }
        reg_resp = await ac.post("http://localhost:8000/auth/register", json=register_data)
        assert reg_resp.status_code == 200

        # 登录  # Login
        login_data = {
            "email": "orderapitestuser@example.com",
            "password": "orderapitestpass"
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 发布订单  # Publish order
        order_data = {
            "title": "Order Detail Test",
            "description": "Detail order.",
            "price": 33.33,
            "location": "EAST",
            "address": "Addr Detail"
        }
        publish_resp = await ac.post("http://localhost:8000/customer/orders/publish", json=order_data, headers=headers)
        assert publish_resp.status_code == 200
        order_id = publish_resp.json()["order_id"]

        # 查询订单详情  # Query order detail
        detail_resp = await ac.get(f"http://localhost:8000/customer/orders/my/{order_id}", headers=headers)
        print(detail_resp.text)  # 调试用  # For debugging
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["id"] == order_id
        assert detail["title"] == "Order Detail Test"
        assert detail["status"] == "pending"
        assert detail["price"] == 33.33
        assert detail["location"] == "EAST"

@pytest.mark.asyncio
async def test_list_order_history_api():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 清理测试用户  # Clean up test user
        await ac.delete("http://localhost:8000/auth/test/cleanup?username=orderhistorytestuser")
        # 注册  # Register
        register_data = {
            "username": "orderhistorytestuser",
            "email": "orderhistorytestuser@example.com",
            "password": "orderhistorytestpass",
            "role_id": 1
        }
        reg_resp = await ac.post("http://localhost:8000/auth/register", json=register_data)
        assert reg_resp.status_code == 200

        # 登录  # Login
        login_data = {
            "email": "orderhistorytestuser@example.com",
            "password": "orderhistorytestpass"
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 发布多条订单，模拟不同状态  # Publish multiple orders, simulate different statuses
        order_data_1 = {
            "title": "History Order 1",
            "description": "First history order.",
            "price": 10.0,
            "location": "NORTH",
            "address": "Addr 1"
        }
        order_data_2 = {
            "title": "History Order 2",
            "description": "Second history order.",
            "price": 20.0,
            "location": "SOUTH",
            "address": "Addr 2"
        }
        resp1 = await ac.post("http://localhost:8000/customer/orders/publish", json=order_data_1, headers=headers)
        resp2 = await ac.post("http://localhost:8000/customer/orders/publish", json=order_data_2, headers=headers)
        assert resp1.status_code == 200
        assert resp2.status_code == 200

        # 取消其中一个订单，制造不同状态  # Cancel one order to create different status
        order_id_2 = resp2.json()["order_id"]
        cancel_resp = await ac.post(f"http://localhost:8000/customer/orders/cancel/{order_id_2}", headers=headers)
        assert cancel_resp.status_code == 200

        # 查询历史订单  # Query order history
        history_resp = await ac.get("http://localhost:8000/customer/orders/history", headers=headers)
        print(history_resp.text)  # 调试用  # For debugging
        assert history_resp.status_code == 200
        orders = history_resp.json()
        assert isinstance(orders, list)
        # 检查至少有两条历史订单  # Check at least two history orders
        assert len(orders) >= 2
        # 检查订单状态覆盖 pending 和 cancelled  # Check order statuses cover pending and cancelled
        statuses = [o["status"] for o in orders]
        assert "pending" in statuses
        assert "cancelled" in statuses