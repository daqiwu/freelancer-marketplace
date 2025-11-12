# app/test/provider_test/orders_test.py
import pytest


class TestProviderOrders:
    """服务商订单功能测试"""

    def test_get_available_orders(self, client, provider_token, published_order):
        """测试获取可接订单"""
        response = client.get(
            "/provider/orders/available",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_filter_available_orders_by_location(self, client, provider_token, published_order):
        """测试按地区筛选订单"""
        response = client.get(
            "/provider/orders/available?location=SOUTH",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        assert response.status_code == 200

    def test_accept_order_success(self, client, provider_token, published_order):
        """测试接受订单成功"""
        response = client.post(
            f"/provider/orders/accept/{published_order.id}",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

    def test_accept_already_accepted_order(self, client, provider_token, accepted_order):
        """测试接受已被接受订单失败"""
        response = client.post(
            f"/provider/orders/accept/{accepted_order.id}",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        assert response.status_code == 400

    def test_update_order_status_to_in_progress(self, client, provider_token, accepted_order):
        """测试更新订单为进行中"""
        response = client.post(
            f"/provider/orders/status/{accepted_order.id}",
            headers={"Authorization": f"Bearer {provider_token}"},
            json={"new_status": "in_progress"}
        )
        assert response.status_code == 200

    def test_get_order_history(self, client, provider_token):
        """测试获取订单历史"""
        response = client.get(
            "/provider/orders/history",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        assert response.status_code == 200

    def test_get_earnings(self, client, provider_token):
        """测试获取收益统计"""
        response = client.get(
            "/provider/earnings",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        assert response.status_code == 200