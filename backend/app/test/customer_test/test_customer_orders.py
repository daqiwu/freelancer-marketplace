import time
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

DEPLOY_URL = "https://freelancer-marketplace-api.onrender.com"


@pytest.mark.asyncio
async def test_publish_order_api():
    async with AsyncClient(base_url=DEPLOY_URL, timeout=30.0) as ac:
        # 注册并登录获取token  # Register and login to get token
        timestamp = str(int(time.time()))
        username = f"orderapitestuser_{timestamp}"
        email = f"orderapitestuser_{timestamp}@example.com"

        await ac.delete(f"{DEPLOY_URL}/auth/test/cleanup?username={username}")
        register_data = {
            "username": username,
            "email": email,
            "password": "orderapitestpass",
            "role_id": 1,
        }
        reg_resp = await ac.post(
            f"{DEPLOY_URL}/auth/register", json=register_data
        )
        assert reg_resp.status_code == 200

        login_data = {
            "email": email,
            "password": "orderapitestpass",
        }
        login_resp = await ac.post(f"{DEPLOY_URL}/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # 发布订单  # Publish order
        order_data = {
            "title": "API Test Order",
            "description": "Order for API test.",
            "price": 99.99,
            "location": "NORTH",
            "address": "Test Address",
            "service_type": "it_technology",
        }
        headers = {"Authorization": f"Bearer {token}"}
        publish_resp = await ac.post(
            f"{DEPLOY_URL}/customer/orders/publish",
            json=order_data,
            headers=headers,
        )
        print(publish_resp.text)  # 调试用  # For debugging
        assert publish_resp.status_code == 200
        resp_json = publish_resp.json()
        assert resp_json["status"] == "pending_review"
        assert "order_id" in resp_json
        assert resp_json["message"].startswith(
            "You have successfully published the order:"
        )


@pytest.mark.asyncio
async def test_cancel_order_api():
    async with AsyncClient(base_url=DEPLOY_URL, timeout=30.0) as ac:
        # 注册并登录获取token  # Register and login to get token
        timestamp = str(int(time.time()))
        username = f"ordercanceltest_{timestamp}"
        email = f"ordercanceltest_{timestamp}@example.com"

        await ac.delete(f"{DEPLOY_URL}/auth/test/cleanup?username={username}")
        register_data = {
            "username": username,
            "email": email,
            "password": "orderapitestpass",
            "role_id": 1,
        }
        reg_resp = await ac.post(
            f"{DEPLOY_URL}/auth/register", json=register_data
        )
        assert reg_resp.status_code == 200

        login_data = {
            "email": email,
            "password": "orderapitestpass",
        }
        login_resp = await ac.post(f"{DEPLOY_URL}/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 发布订单  # Publish order
        order_data = {
            "title": "API Cancel Test Order",
            "description": "Order for cancel API test.",
            "price": 88.88,
            "location": "NORTH",
            "address": "Cancel Test Address",
            "service_type": "cleaning_repair",
        }
        publish_resp = await ac.post(
            f"{DEPLOY_URL}/customer/orders/publish",
            json=order_data,
            headers=headers,
        )
        assert publish_resp.status_code == 200
        order_id = publish_resp.json()["order_id"]

        # 取消订单  # Cancel order
        cancel_resp = await ac.post(
            f"{DEPLOY_URL}/customer/orders/cancel/{order_id}", headers=headers
        )
        print(cancel_resp.text)  # 调试用  # For debugging
        assert cancel_resp.status_code == 200
        cancel_json = cancel_resp.json()
        assert cancel_json["status"] == "cancelled"
        assert cancel_json["message"].startswith(
            "You have successfully cancelled the order:"
        )


@pytest.mark.asyncio
async def test_list_my_orders_api():
    async with AsyncClient(base_url="DEPLOY_URL") as ac:
        # 清理测试用户  # Clean up test user
        timestamp = str(int(time.time()))
        username = f"orderlisttest_{timestamp}"
        email = f"orderlisttest_{timestamp}@example.com"

        await ac.delete(f"{DEPLOY_URL}/auth/test/cleanup?username={username}")
        # 注册  # Register
        register_data = {
            "username": username,
            "email": email,
            "password": "orderapitestpass",
            "role_id": 1,
        }
        reg_resp = await ac.post(
            f"{DEPLOY_URL}/auth/register", json=register_data
        )
        assert reg_resp.status_code == 200

        # 登录  # Login
        login_data = {
            "email": email,
            "password": "orderapitestpass",
        }
        login_resp = await ac.post(f"{DEPLOY_URL}/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 发布两个订单  # Publish two orders
        order_data_1 = {
            "title": "Order 1",
            "description": "First order.",
            "price": 10.0,
            "location": "NORTH",
            "address": "Addr 1",
            "service_type": "education_training",
        }
        order_data_2 = {
            "title": "Order 2",
            "description": "Second order.",
            "price": 20.0,
            "location": "SOUTH",
            "address": "Addr 2",
            "service_type": "life_health",
        }
        resp1 = await ac.post(
            f"{DEPLOY_URL}/customer/orders/publish",
            json=order_data_1,
            headers=headers,
        )
        resp2 = await ac.post(
            f"{DEPLOY_URL}/customer/orders/publish",
            json=order_data_2,
            headers=headers,
        )
        assert resp1.status_code == 200
        assert resp2.status_code == 200

        # 查询订单列表  # Query order list
        list_resp = await ac.get(
            f"{DEPLOY_URL}/customer/orders/my", headers=headers
        )
        print(list_resp.text)  # 调试用  # For debugging
        assert list_resp.status_code == 200
        orders = list_resp.json()
        assert isinstance(orders, list)
        assert len(orders) >= 2
        assert orders[0]["status"] in [
            "pending_review",
            "pending",
            "accepted",
            "in_progress",
        ]


@pytest.mark.asyncio
async def test_get_my_order_detail_api():
    async with AsyncClient(base_url="DEPLOY_URL") as ac:
        # 清理测试用户  # Clean up test user
        timestamp = str(int(time.time()))
        username = f"orderdetailtest_{timestamp}"
        email = f"orderdetailtest_{timestamp}@example.com"

        await ac.delete(f"{DEPLOY_URL}/auth/test/cleanup?username={username}")
        # 注册  # Register
        register_data = {
            "username": username,
            "email": email,
            "password": "orderapitestpass",
            "role_id": 1,
        }
        reg_resp = await ac.post(
            f"{DEPLOY_URL}/auth/register", json=register_data
        )
        assert reg_resp.status_code == 200

        # 登录  # Login
        login_data = {
            "email": email,
            "password": "orderapitestpass",
        }
        login_resp = await ac.post(f"{DEPLOY_URL}/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 发布订单  # Publish order
        order_data = {
            "title": "Order Detail Test",
            "description": "Detail order.",
            "price": 33.33,
            "location": "EAST",
            "service_type": "design_consulting",
            "address": "Addr Detail",
        }
        publish_resp = await ac.post(
            f"{DEPLOY_URL}/customer/orders/publish",
            json=order_data,
            headers=headers,
        )
        assert publish_resp.status_code == 200
        order_id = publish_resp.json()["order_id"]

        # 查询订单详情  # Query order detail
        detail_resp = await ac.get(
            f"{DEPLOY_URL}/customer/orders/my/{order_id}", headers=headers
        )
        print(detail_resp.text)  # 调试用  # For debugging
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["id"] == order_id
        assert detail["title"] == "Order Detail Test"
        assert detail["status"] == "pending_review"
        assert detail["price"] == 33.33
        assert detail["location"] == "EAST"


@pytest.mark.asyncio
async def test_list_order_history_api():
    async with AsyncClient(base_url="DEPLOY_URL") as ac:
        # 清理测试用户  # Clean up test user
        timestamp = str(int(time.time()))
        username = f"orderhistorytest_{timestamp}"
        email = f"orderhistorytest_{timestamp}@example.com"

        await ac.delete(f"{DEPLOY_URL}/auth/test/cleanup?username={username}")
        # 注册  # Register
        register_data = {
            "username": username,
            "email": email,
            "password": "orderhistorytestpass",
            "role_id": 1,
        }
        reg_resp = await ac.post(
            f"{DEPLOY_URL}/auth/register", json=register_data
        )
        assert reg_resp.status_code == 200

        # 登录  # Login
        login_data = {
            "email": email,
            "password": "orderhistorytestpass",
        }
        login_resp = await ac.post(f"{DEPLOY_URL}/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 发布多条订单，模拟不同状态  # Publish multiple orders, simulate different statuses
        order_data_1 = {
            "title": "History Order 1",
            "description": "First history order.",
            "price": 10.0,
            "location": "NORTH",
            "address": "Addr 1",
            "service_type": "other",
        }
        order_data_2 = {
            "title": "History Order 2",
            "description": "Second history order.",
            "price": 20.0,
            "location": "SOUTH",
            "address": "Addr 2",
            "service_type": "it_technology",
        }
        resp1 = await ac.post(
            f"{DEPLOY_URL}/customer/orders/publish",
            json=order_data_1,
            headers=headers,
        )
        resp2 = await ac.post(
            f"{DEPLOY_URL}/customer/orders/publish",
            json=order_data_2,
            headers=headers,
        )
        assert resp1.status_code == 200
        assert resp2.status_code == 200

        # 取消其中一个订单，制造不同状态  # Cancel one order to create different status
        order_id_2 = resp2.json()["order_id"]
        cancel_resp = await ac.post(
            f"{DEPLOY_URL}/customer/orders/cancel/{order_id_2}",
            headers=headers,
        )
        assert cancel_resp.status_code == 200

        # 查询历史订单  # Query order history
        history_resp = await ac.get(
            f"{DEPLOY_URL}/customer/orders/history", headers=headers
        )
        print(history_resp.text)  # 调试用  # For debugging
        assert history_resp.status_code == 200
        orders = history_resp.json()
        assert isinstance(orders, list)
        # 检查至少有两条历史订单  # Check at least two history orders
        assert len(orders) >= 2
        # 检查订单状态覆盖 pending_review/pending 和 cancelled  # Check order statuses cover pending_review/pending and cancelled
        statuses = [o["status"] for o in orders]
        assert "pending_review" in statuses or "pending" in statuses
        assert "cancelled" in statuses


class TestCustomerOrders:
    """客户订单功能测试"""

    def test_publish_order_success(self, client, customer_token):
        """测试发布订单成功"""
        future_time = datetime.now() + timedelta(days=1)
        response = client.post(
            "/customer/orders/publish",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "title": "House Cleaning",
                "description": "Need professional cleaning",
                "service_type": "cleaning",
                "price": 100.0,
                "location": "NORTH",
                "address": "123 Main St",
                "service_start_time": future_time.isoformat(),
                "service_end_time": (future_time + timedelta(hours=2)).isoformat()
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "House Cleaning"
        assert data["status"] == "pending_review"

    def test_publish_order_with_sensitive_info(self, client, customer_token):
        """测试包含敏感信息的订单被拒绝"""
        future_time = datetime.now() + timedelta(days=1)
        response = client.post(
            "/customer/orders/publish",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "title": "Test Order",
                "description": "Call me at 13812345678",
                "service_type": "cleaning",
                "price": 100.0,
                "location": "NORTH",
                "address": "123 Main St",
                "service_start_time": future_time.isoformat(),
                "service_end_time": (future_time + timedelta(hours=2)).isoformat()
            }
        )
        assert response.status_code == 400

    def test_publish_order_negative_price(self, client, customer_token):
        """测试负价格订单被拒绝"""
        future_time = datetime.now() + timedelta(days=1)
        response = client.post(
            "/customer/orders/publish",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "title": "Test Order",
                "description": "Test",
                "service_type": "cleaning",
                "price": -10.0,
                "location": "NORTH",
                "address": "123 Main St",
                "service_start_time": future_time.isoformat(),
                "service_end_time": (future_time + timedelta(hours=2)).isoformat()
            }
        )
        assert response.status_code == 400

    def test_get_my_orders(self, client, customer_token, sample_order):
        """测试获取我的订单列表"""
        response = client.get(
            "/customer/orders/my",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_order_detail(self, client, customer_token, sample_order):
        """测试获取订单详情"""
        response = client.get(
            f"/customer/orders/my/{sample_order.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_order.id

    def test_cancel_order_success(self, client, customer_token, sample_order):
        """测试取消订单成功"""
        response = client.post(
            f"/customer/orders/cancel/{sample_order.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_submit_review_success(self, client, customer_token, completed_order):
        """测试提交评价成功"""
        # 先支付订单
        client.post(
            f"/customer/orders/pay/{completed_order.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        # 提交评价
        response = client.post(
            "/customer/orders/review",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "order_id": completed_order.id,
                "stars": 5,
                "content": "Excellent service!"
            }
        )
        assert response.status_code == 200
